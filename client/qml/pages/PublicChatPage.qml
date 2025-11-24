// pages/PublicChatPage.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1 as Platform
import "../styles"
import "../components"

ColumnLayout {
    id: root
    
    property alias messagesModel: listView.model
    property var typingUsers: []
    property var pendingFile: null
    property string draft: ""
    property int userCount: 0
    
    signal sendMessage(string text, string filePath)
    signal fileSelected(string filePath)
    signal emojiRequested()
    signal typingStateChanged(bool isTyping)
    signal copyRequested(string text)
    
    spacing: Theme.spacing_lg
    
    function setup() {
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
        title: "Select a file to share"
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
            text: "Salon feed"
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
            text: root.userCount > 0 
                ? root.userCount + " guests mingling" 
                : "Awaiting first arrival"
            color: Theme.textSecondary
            font.pixelSize: Theme.scaleFont(12)
            Layout.alignment: Qt.AlignVCenter
        }
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
                    
                    // Bind required properties from model
                    user: model.user || ""
                    text: model.text || ""
                    timestamp: model.timestamp || ""
                    isPrivate: model.isPrivate || false
                    isOutgoing: model.isOutgoing || false
                    displayContext: model.displayContext || (model.user || "")
                    status: model.status || ""
                    
                    // Bind file properties from model
                    fileName: model.fileName || ""
                    fileSize: model.fileSize || 0
                    fileData: model.fileData || ""
                    fileMime: model.fileMime || ""
                    
                    onDownloadRequested: {
                        // Handle download
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
    
    // Typing indicator
    TypingIndicator {
        Layout.fillWidth: true
        typingUsers: root.typingUsers
    }
    
    // Composer
    Composer {
        id: composer
        Layout.fillWidth: true
        placeholderText: "Share something with the lounge"
        pendingFile: root.pendingFile
        
        onSendClicked: {
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