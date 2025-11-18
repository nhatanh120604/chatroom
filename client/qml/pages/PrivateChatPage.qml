// pages/PrivateChatPage.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1 as Platform
import "../styles"
import "../components"

ColumnLayout {
    id: root
    
    property string peerKey: ""
    property string displayName: ""
    property alias messagesModel: listView.model
    property bool isTyping: false
    property var pendingFile: null
    property string draft: ""
    
    signal sendMessage(string text, string filePath)
    signal fileSelected(string filePath)
    signal emojiRequested()
    signal typingStateChanged(bool isTyping)
    signal copyRequested(string text)
    
    spacing: Theme.spacing_lg
    
    function setup(key, title) {
        peerKey = key || ""
        displayName = title || key || ""
        composer.text = root.draft || ""
        scrollToEnd(false)
    }
    
    function scrollToEnd(animated) {
        if (scrollArea.contentHeight > scrollArea.height) {
            if (animated) {
                scrollAnimation.from = scrollArea.contentY
                scrollAnimation.to = Math.max(0, scrollArea.contentHeight - scrollArea.height)
                scrollAnimation.restart()
            } else {
                scrollArea.contentY = Math.max(0, scrollArea.contentHeight - scrollArea.height)
            }
        }
    }
    
    function forceComposerFocus() {
        composer.forceFieldFocus()
    }
    
    // File picker dialog
    Platform.FileDialog {
        id: fileDialog
        title: "Select a file to whisper"
        onAccepted: {
            var path = fileDialog.file ? fileDialog.file.toString() : ""
            if (path.length > 0) {
                root.fileSelected(path)
            }
        }
    }
    
    // Header
    RowLayout {
        Layout.fillWidth: true
        spacing: Theme.spacing_md
        
        Text {
            text: displayName.length > 0 
                ? "Private line with " + displayName 
                : "Private line"
            color: Theme.textPrimary
            font.pixelSize: Theme.scaleFont(18)
            font.bold: true
        }
        
        Rectangle {
            Layout.preferredWidth: 6
            Layout.preferredHeight: 6
            radius: 3
            color: Theme.accent
            Layout.alignment: Qt.AlignVCenter
        }
        
        Text {
            text: "Only you and " + (displayName.length > 0 ? displayName : "this guest") + " can see this thread"
            color: Theme.textSecondary
            font.pixelSize: Theme.scaleFont(12)
            Layout.alignment: Qt.AlignVCenter
            wrapMode: Text.WordWrap
        }
    }
    
    // Typing indicator
    Text {
        Layout.fillWidth: true
        text: root.isTyping && peerKey.length > 0 ? peerKey + " is typing..." : ""
        color: Theme.textSecondary
        font.pixelSize: Theme.scaleFont(12)
        visible: text.length > 0
    }
    
    // Messages area
    Flickable {
        id: scrollArea
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        
        property bool autoStickToBottom: true
        
        contentWidth: messageColumn.width
        contentHeight: messageColumn.height
        boundsBehavior: Flickable.DragAndOvershootBounds
        
        Column {
            id: messageColumn
            width: scrollArea.width
            spacing: Theme.spacing_lg
            
            Repeater {
                id: listView
                delegate: MessageBubble {
                    width: messageColumn.width
                    isFirst: index === 0
                    
                    onDownloadRequested: {
                        console.log("Download requested:", fileName)
                    }
                    
                    onCopyTextRequested: function(text) {
                        root.copyRequested(text)
                    }
                    
                    onCopyWithUserRequested: function(fullText) {
                        root.copyRequested(fullText)
                    }
                }
            }
            
            Item {
                width: parent.width
                height: Theme.spacing_md
            }
        }
        
        ScrollIndicator.vertical: ScrollIndicator {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            
            contentItem: Rectangle {
                radius: 2
                color: Theme.accent
            }
        }
        
        onContentHeightChanged: {
            if (autoStickToBottom) {
                scrollToEnd(true)
            }
        }
        
        onContentYChanged: {
            if ((moving || dragging) && !atYEnd) {
                autoStickToBottom = false
            } else if (!moving && !dragging && atYEnd) {
                autoStickToBottom = true
            }
        }
        
        NumberAnimation {
            id: scrollAnimation
            target: scrollArea
            property: "contentY"
            duration: Theme.duration_normal
            easing.type: Easing.InOutQuad
        }
    }
    
    // Composer
    Composer {
        id: composer
        Layout.fillWidth: true
        placeholderText: displayName.length > 0 
            ? "Whisper to " + displayName 
            : "Whisper to this guest"
        pendingFile: root.pendingFile
        enabled: peerKey.length > 0
        
        onSendClicked: {
            if (peerKey.length === 0) return
            
            var text = composer.text.trim()
            var filePath = root.pendingFile && root.pendingFile.path ? root.pendingFile.path : ""
            
            if (text.length > 0 || filePath.length > 0) {
                root.sendMessage(text, filePath)
                composer.clearText()
                root.draft = ""
                root.pendingFile = null
            }
        }
        
        onFileClicked: fileDialog.open()
        
        onEmojiClicked: root.emojiRequested()
        
        onTextEdited: function(text) {
            root.draft = text
            root.typingStateChanged(text.length > 0)
        }
    }
}