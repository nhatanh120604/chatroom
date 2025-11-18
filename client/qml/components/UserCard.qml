// components/UserCard.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Rectangle {
    id: root
    
    required property string name
    property string avatarSource: ""
    
    signal clicked()
    
    width: parent ? parent.width : 200
    height: 56
    radius: Theme.radius_lg
    
    color: hovered ? Theme.accentSoft : Theme.card
    border.color: hovered ? Theme.accent : Theme.outline
    border.width: hovered ? 1 : 0
    
    transformOrigin: Item.Center
    scale: hovered ? 1.04 : 1.0
    
    property bool hovered: mouseArea.containsMouse
    
    Behavior on scale {
        NumberAnimation {
            duration: Theme.duration_fast
            easing.type: Easing.OutQuad
        }
    }
    
    Behavior on color {
        ColorAnimation {
            duration: Theme.duration_fast
            easing.type: Easing.OutQuad
        }
    }
    
    Behavior on border.color {
        ColorAnimation {
            duration: Theme.duration_fast
            easing.type: Easing.OutQuad
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: root.clicked()
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: Theme.spacing_md
        
        // Avatar
        Avatar {
            Layout.preferredWidth: 30
            Layout.preferredHeight: 30
            size: 30
            username: root.name
            avatarSource: root.avatarSource
        }
        
        // User info
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                text: root.name
                color: Theme.textPrimary
                font.pixelSize: Theme.scaleFont(14)
                font.bold: true
            }
            
            Text {
                text: "Invite to private line"
                color: Theme.textSecondary
                font.pixelSize: Theme.scaleFont(11)
            }
        }
    }
}