// components/Avatar.qml
import QtQuick 2.15
import "../styles"

Item {
    id: root
    
    property string username: ""
    property string avatarSource: ""
    property int size: 40
    
    width: size
    height: size
    
    // Custom avatar (if available)
    Rectangle {
        anchors.fill: parent
        radius: width / 2
        visible: avatarSource && avatarSource.length > 0
        color: "transparent"
        clip: true
        
        Image {
            anchors.fill: parent
            source: avatarSource
            fillMode: Image.PreserveAspectCrop
            smooth: true
        }
    }
    
    // Fallback gradient avatar
    Rectangle {
        anchors.fill: parent
        radius: width / 2
        visible: !(avatarSource && avatarSource.length > 0)
        
        gradient: Gradient {
            GradientStop { 
                position: 0.0
                color: Theme.avatarDefault.top
            }
            GradientStop { 
                position: 1.0
                color: Theme.avatarDefault.bottom
            }
        }
        
        border.color: "#60FFFFFF"
        border.width: 1
    }
}