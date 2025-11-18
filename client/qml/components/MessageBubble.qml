// components/MessageBubble.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Column {
    id: root
    
    // Required properties from model
    required property string user
    required property string text
    required property string timestamp
    required property bool isPrivate
    required property bool isOutgoing
    required property string displayContext
    required property string status
    
    // Optional file properties
    property string fileName: ""
    property string fileMime: ""
    property string fileData: ""
    property int fileSize: 0
    
    property bool isSystem: user === "System"
    property bool isFirst: false
    
    signal downloadRequested()
    signal copyTextRequested(string text)
    signal copyWithUserRequested(string fullText)
    
    width: parent ? parent.width : 0
    spacing: Theme.spacing_sm
    
    opacity: 0
    scale: 0.97
    transformOrigin: Item.TopLeft
    
    Component.onCompleted: entryAnimation.start()
    
    ParallelAnimation {
        id: entryAnimation
        PropertyAnimation {
            target: root
            property: "opacity"
            to: 1
            duration: Theme.duration_normal
            easing.type: Easing.OutQuad
        }
        PropertyAnimation {
            target: root
            property: "scale"
            to: 1
            duration: Theme.duration_normal
            easing.type: Easing.OutBack
        }
    }
    
    // Divider
    Rectangle {
        width: parent.width
        height: isFirst ? 0 : 1
        color: Theme.outline
        opacity: 0.18
    }
    
    // Message content
    Row {
        width: parent.width
        spacing: Theme.spacing_md
        layoutDirection: root.isOutgoing ? Qt.RightToLeft : Qt.LeftToRight
        
        // Avatar
        Avatar {
            width: 40
            height: 40
            username: root.user
            avatarSource: getAvatarSource()
        }
        
        // Message bubble and text
        Column {
            width: parent.width - 52
            spacing: Theme.spacing_sm
            
            // Username
            Text {
                text: displayContext
                color: isPrivate ? Theme.accent : (root.isOutgoing ? Theme.accent : Theme.textSecondary)
                font.pixelSize: Theme.scaleFont(12)
                font.bold: true
                horizontalAlignment: root.isOutgoing ? Text.AlignRight : Text.AlignLeft
                anchors.right: root.isOutgoing ? parent.right : undefined
                anchors.left: root.isOutgoing ? undefined : parent.left
            }
            
            // Message bubble
            Rectangle {
                id: bubble
                width: Math.max(180, Math.min(bubbleContent.implicitWidth + 40, parent.width))
                radius: Theme.radius_lg
                
                color: {
                    if (root.isSystem) return Theme.accentSoft
                    if (isPrivate) return root.isOutgoing ? Theme.card : Theme.accentSoft
                    return root.isOutgoing ? Theme.card : Theme.accentSoft
                }
                
                border.width: 1
                border.color: {
                    if (root.isSystem) return Theme.accent
                    if (isPrivate) return root.isOutgoing ? Theme.canvas : Theme.accent
                    return root.isOutgoing ? Theme.canvas : Theme.accent
                }
                
                implicitHeight: bubbleContent.implicitHeight + 40
                
                anchors.right: root.isOutgoing ? parent.right : undefined
                anchors.left: root.isOutgoing ? undefined : parent.left
                
                property bool hasText: root.text && root.text.length > 0
                property bool hasFile: root.fileName && root.fileName.length > 0
                
                Column {
                    id: bubbleContent
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: Theme.spacing_lg
                    anchors.rightMargin: Theme.spacing_lg
                    anchors.top: parent.top
                    anchors.topMargin: Theme.spacing_lg
                    spacing: bubble.hasText && bubble.hasFile ? Theme.spacing_md : Theme.spacing_sm
                    
                    // Message text
                    Text {
                        visible: bubble.hasText
                        text: root.text
                        color: Theme.textPrimary
                        wrapMode: Text.Wrap
                        width: Math.min(implicitWidth, parent.parent.parent.width - 52 - 40)
                        font.pixelSize: Theme.scaleFont(15)
                        lineHeight: 1.35
                    }
                    
                    // File attachment
                    FileAttachment {
                        visible: bubble.hasFile
                        width: parent.width
                        fileName: root.fileName
                        fileSize: root.fileSize
                        canDownload: root.fileData && root.fileData.length > 0
                        onDownloadClicked: root.downloadRequested()
                    }
                    
                    // Timestamp and status
                    RowLayout {
                        width: parent.width
                        
                        Text {
                            text: root.timestamp
                            color: Theme.textSecondary
                            font.pixelSize: Theme.scaleFont(11)
                            Layout.alignment: Qt.AlignLeft
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        Text {
                            visible: isPrivate && root.isOutgoing
                            text: getStatusText()
                            color: Theme.textSecondary
                            font.pixelSize: Theme.scaleFont(11)
                            Layout.alignment: Qt.AlignRight
                        }
                    }
                }
                
                // System message glow animation
                SequentialAnimation {
                    running: root.isSystem
                    ColorAnimation {
                        target: bubble
                        property: "border.color"
                        to: Theme.accentBold
                        duration: 120
                        easing.type: Easing.OutQuad
                    }
                    ColorAnimation {
                        target: bubble
                        property: "border.color"
                        to: root.isSystem ? Theme.accent : bubble.border.color
                        duration: 420
                        easing.type: Easing.OutCubic
                    }
                }
                
                // Context menu
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.RightButton
                    onClicked: {
                        if (mouse.button === Qt.RightButton) {
                            contextMenu.popup()
                        }
                    }
                }
                
                Menu {
                    id: contextMenu
                    
                    MenuItem {
                        text: "Copy Message"
                        enabled: bubble.hasText
                        onTriggered: root.copyTextRequested(root.text)
                    }
                    
                    MenuItem {
                        text: "Copy with Username"
                        enabled: bubble.hasText
                        onTriggered: root.copyWithUserRequested(root.user + ": " + root.text)
                    }
                    
                    MenuSeparator {
                        visible: bubble.hasFile
                    }
                    
                    MenuItem {
                        text: "Copy Filename"
                        visible: bubble.hasFile
                        enabled: bubble.hasFile
                        onTriggered: root.copyTextRequested(root.fileName)
                    }
                }
            }
        }
    }
    
    function getAvatarSource() {
        // This will be provided by parent context
        return ""
    }
    
    function getStatusText() {
        var state = status ? status.toLowerCase() : ""
        if (state === "seen") return "✓✓ Seen"
        if (state === "delivered") return "✓ Delivered"
        if (state === "sent") return "✓ Sent"
        return ""
    }
}