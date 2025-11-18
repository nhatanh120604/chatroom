// components/StatusIndicator.qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../styles"

Rectangle {
    id: root
    
    property string connectionState: "offline"
    
    Layout.preferredWidth: 140
    Layout.preferredHeight: 32
    radius: Theme.radius_lg
    border.width: 1
    
    border.color: {
        if (connectionState === "connected") return Theme.success
        if (connectionState === "reconnecting") return Theme.warning
        return Theme.outline
    }
    
    color: "transparent"
    
    Row {
        anchors.centerIn: parent
        spacing: Theme.spacing_sm
        
        // Status dot
        Rectangle {
            width: 8
            height: 8
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            
            color: {
                if (root.connectionState === "connected") return Theme.success
                if (root.connectionState === "reconnecting") return Theme.warning
                return Theme.textSecondary
            }
            
            // Pulse animation for reconnecting
            SequentialAnimation on opacity {
                running: root.connectionState === "reconnecting"
                loops: Animation.Infinite
                PropertyAnimation { to: 0.3; duration: 600 }
                PropertyAnimation { to: 1.0; duration: 600 }
            }
        }
        
        Text {
            text: {
                if (root.connectionState === "connected") return "Connected"
                if (root.connectionState === "reconnecting") return "Reconnecting"
                return "Offline"
            }
            color: Theme.textPrimary
            font.pixelSize: Theme.scaleFont(12)
            font.bold: true
        }
    }
    
    // Tooltip
    MouseArea {
        id: tooltipArea
        anchors.fill: parent
        hoverEnabled: true
    }
    
    Rectangle {
        visible: tooltipArea.containsMouse
        color: Theme.panel
        border.color: Theme.outline
        border.width: 1
        radius: Theme.radius_sm
        width: tooltipText.width + Theme.spacing_lg
        height: tooltipText.height + Theme.spacing_md
        x: parent.width / 2 - width / 2
        y: parent.height + Theme.spacing_sm
        z: 1000
        
        Text {
            id: tooltipText
            anchors.centerIn: parent
            text: {
                if (root.connectionState === "connected")
                    return "Connected to server"
                if (root.connectionState === "reconnecting")
                    return "Attempting to reconnect..."
                return "Not connected to server"
            }
            color: Theme.textSecondary
            font.pixelSize: Theme.scaleFont(11)
        }
    }
}