// components/FileAttachment.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Rectangle {
    id: root
    
    property string fileName: ""
    property int fileSize: 0
    property bool canDownload: true
    
    signal downloadClicked()
    signal removeClicked()
    
    radius: Theme.radius_md
    color: Theme.surface
    border.color: Theme.outline
    border.width: 1
    
    implicitHeight: content.implicitHeight + Theme.spacing_md * 2
    
    RowLayout {
        id: content
        anchors.fill: parent
        anchors.margins: Theme.spacing_md
        spacing: Theme.spacing_md
        
        // File icon
        Text {
            text: "📎"
            font.pixelSize: Theme.scaleFont(20)
            color: Theme.accent
            font.family: Theme.emojiFont
        }
        
        // File info
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                text: fileName
                color: Theme.textPrimary
                font.pixelSize: Theme.scaleFont(13)
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            
            Text {
                text: formatFileSize(fileSize)
                color: Theme.textSecondary
                font.pixelSize: Theme.scaleFont(11)
            }
        }
        
        // Download button
        Button {
            visible: canDownload
            text: "Download"
            
            background: Rectangle {
                radius: Theme.radius_sm
                color: parent.enabled ? (parent.hovered ? Theme.accent : Theme.canvas) : Theme.surface
                border.color: Theme.outline
                border.width: 1
                
                Behavior on color {
                    ColorAnimation { duration: Theme.duration_fast }
                }
            }
            
            contentItem: Text {
                text: parent.text
                color: parent.enabled ? Theme.textPrimary : Theme.textSecondary
                font.pixelSize: Theme.scaleFont(12)
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: root.downloadClicked()
        }
        
        // Remove button (for pending attachments)
        ToolButton {
            visible: !canDownload
            Layout.preferredWidth: 28
            Layout.preferredHeight: 28
            text: "✕"
            
            background: Rectangle {
                radius: Theme.radius_md
                color: Theme.surface
                border.color: Theme.outline
                border.width: 1
            }
            
            contentItem: Text {
                text: parent.text
                color: Theme.textSecondary
                font.pixelSize: Theme.scaleFont(12)
                anchors.centerIn: parent
            }
            
            onClicked: root.removeClicked()
        }
    }
    
    function formatFileSize(bytes) {
        if (!bytes || bytes <= 0) return ""
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
        return (bytes / (1024 * 1024)).toFixed(1) + " MB"
    }
}