// components/ConversationTabs.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

TabBar {
    id: root
    
    property alias model: repeater.model
    
    signal tabCloseRequested(string key)
    
    contentHeight: 38
    
    background: Rectangle {
        color: "transparent"
        border.width: 0
    }
    
    Repeater {
        id: repeater
        
        delegate: TabButton {
            required property string key
            required property string title
            required property bool isPrivate
            required property bool hasUnread
            required property int unreadCount
            required property int index
            
            implicitHeight: root.contentHeight
            padding: 0
            text: title
            checkable: true
            checked: index === root.currentIndex
            font.pixelSize: Theme.scaleFont(12)
            
            background: Rectangle {
                radius: Theme.radius_lg
                color: checked ? Theme.canvas : Theme.surface
                border.color: checked ? Theme.accent : Theme.outline
                border.width: checked ? 1 : 0
            }
            
            contentItem: Item {
                anchors.fill: parent
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: Theme.spacing_sm
                    
                    Text {
                        text: title
                        color: Theme.textPrimary
                        font.pixelSize: Theme.scaleFont(12)
                        font.bold: checked
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    // Unread badge
                    Rectangle {
                        visible: hasUnread && unreadCount > 0
                        width: Math.max(20, badgeText.width + 10)
                        height: 20
                        radius: 10
                        color: Theme.warning
                        Layout.alignment: Qt.AlignVCenter
                        
                        Text {
                            id: badgeText
                            anchors.centerIn: parent
                            text: unreadCount > 99 ? "99+" : unreadCount.toString()
                            color: Theme.textPrimary
                            font.pixelSize: Theme.scaleFont(10)
                            font.bold: true
                        }
                    }
                    
                    Item {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    // Close button for private tabs
                    Item {
                        Layout.preferredWidth: isPrivate ? 20 : 0
                        Layout.fillHeight: true
                        visible: isPrivate
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.tabCloseRequested(key)
                            
                            Text {
                                anchors.centerIn: parent
                                text: "✕"
                                color: Theme.textSecondary
                                font.pixelSize: Theme.scaleFont(12)
                            }
                        }
                    }
                }
            }
            
            onClicked: root.currentIndex = index
        }
    }
}