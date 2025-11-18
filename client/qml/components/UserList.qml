// components/UserList.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 6.6
import "../styles"

Item {
    id: root
    
    property alias model: listView.model
    property int userCount: 0
    
    signal userClicked(string username)
    
    MultiEffect {
        anchors.fill: card
        source: card
        shadowEnabled: true
        shadowHorizontalOffset: 0
        shadowVerticalOffset: 18
        shadowBlur: 32
        shadowColor: "#22000000"
        autoPaddingEnabled: true
    }
    
    Rectangle {
        id: card
        anchors.fill: parent
        radius: Theme.radius_xxl
        transformOrigin: Item.Center
        border.color: Theme.outline
        border.width: 1
        
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.surface }
            GradientStop { position: 1.0; color: Theme.panel }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacing_xxl
            spacing: Theme.spacing_lg
            
            Text {
                text: "Concierge"
                color: Theme.textPrimary
                font.pixelSize: Theme.scaleFont(17)
                font.bold: true
            }
            
            Text {
                text: "Spot a guest, tap to begin a private exchange."
                color: Theme.textSecondary
                font.pixelSize: Theme.scaleFont(12)
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: Theme.outline
                opacity: 0.18
            }
            
            ListView {
                id: listView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Theme.spacing_md
                
                delegate: UserCard {
                    width: listView.width
                    name: model.name
                    avatarSource: getAvatarSource(model.name)
                    onClicked: root.userClicked(model.name)
                }
                
                ScrollIndicator.vertical: ScrollIndicator {
                    contentItem: Rectangle {
                        implicitWidth: 4
                        radius: 2
                        color: Theme.accent
                    }
                }
            }
        }
    }
    
    function getAvatarSource(username) {
        // This will be implemented by parent context
        return ""
    }
}