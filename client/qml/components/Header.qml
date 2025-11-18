// components/Header.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 6.6
import "../styles"

Item {
    id: root
    
    property string username: ""
    property string connectionState: "offline"
    property bool soundsEnabled: true
    
    signal registerClicked(string username)
    signal disconnectClicked()
    signal avatarClicked()
    signal soundToggled()
    
    implicitHeight: 132
    
    MultiEffect {
        anchors.fill: card
        source: card
        shadowEnabled: true
        shadowHorizontalOffset: 0
        shadowVerticalOffset: 18
        shadowBlur: 32
        shadowColor: "#28000000"
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
            GradientStop { position: 0.0; color: "#1C283B" }
            GradientStop { position: 1.0; color: Theme.panel }
        }
        
        Item {
            anchors.fill: parent
            anchors.margins: Theme.spacing_xxl + 4
            
            GridLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                columns: 2
                columnSpacing: Theme.spacing_xxl + 4
                rowSpacing: 0
                
                // Left side - Welcome text
                ColumnLayout {
                    Layout.row: 0
                    Layout.column: 0
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 10
                    
                    Text {
                        text: root.username.length > 0 
                            ? "Welcome back, " + root.username 
                            : "Aurora Lounge"
                        color: Theme.textPrimary
                        font.pixelSize: Theme.scaleFont(26)
                        font.bold: true
                    }
                    
                    Text {
                        text: root.username.length > 0
                            ? "Share a thought with the lounge—your voice sets tonight's tone."
                            : "Reserve a signature name to slip past the velvet rope."
                        color: Theme.textSecondary
                        font.pixelSize: Theme.scaleFont(14)
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                    
                    RowLayout {
                        spacing: Theme.spacing_md
                        
                        // Status badge
                        Rectangle {
                            Layout.preferredWidth: 160
                            Layout.preferredHeight: 32
                            radius: Theme.radius_lg
                            color: root.username.length > 0 ? Theme.success : Theme.accentSoft
                            
                            Text {
                                anchors.centerIn: parent
                                text: root.username.length > 0 ? "Enrolled guest" : "Guest access"
                                color: root.username.length > 0 ? Theme.textPrimary : Theme.textSecondary
                                font.pixelSize: Theme.scaleFont(12)
                                font.bold: true
                            }
                        }
                        
                        // Clock
                        Rectangle {
                            Layout.preferredWidth: 160
                            Layout.preferredHeight: 32
                            radius: Theme.radius_lg
                            color: "transparent"
                            border.color: Theme.outline
                            border.width: 1
                            
                            Timer {
                                id: clockTimer
                                interval: 1000
                                running: true
                                repeat: true
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: {
                                    clockTimer.triggered()
                                    return Qt.formatDateTime(new Date(), "ddd, MMM d • hh:mm ap")
                                }
                                color: Theme.textSecondary
                                font.pixelSize: Theme.scaleFont(12)
                            }
                        }
                        
                        // Connection status
                        StatusIndicator {
                            connectionState: root.connectionState
                        }
                        
                        // Sound toggle
                        ToolButton {
                            Layout.preferredWidth: 44
                            Layout.preferredHeight: 44
                            text: root.soundsEnabled ? "🔔" : "🔕"
                            font.pixelSize: Theme.scaleFont(20)
                            
                            background: Rectangle {
                                radius: 22
                                color: parent.hovered ? Theme.canvas : "transparent"
                                border.color: parent.hovered ? Theme.outline : "transparent"
                                border.width: 1
                                
                                Behavior on color {
                                    ColorAnimation { duration: Theme.duration_fast }
                                }
                            }
                            
                            onClicked: root.soundToggled()
                        }
                    }
                }
                
                // Right side - User input
                ColumnLayout {
                    Layout.row: 0
                    Layout.column: 1
                    Layout.preferredWidth: 320
                    Layout.alignment: Qt.AlignVCenter
                    spacing: Theme.spacing_md
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 44
                        radius: Theme.radius_lg
                        color: Theme.canvas
                        border.color: usernameField.activeFocus ? Theme.accent : Theme.outline
                        border.width: 1
                        
                        TextField {
                            id: usernameField
                            anchors.fill: parent
                            leftPadding: Theme.spacing_lg
                            rightPadding: Theme.spacing_lg
                            topPadding: 10
                            bottomPadding: 10
                            placeholderText: "Choose your lounge signature"
                            placeholderTextColor: Theme.textSecondary
                            color: Theme.textPrimary
                            selectionColor: Theme.accent
                            selectedTextColor: Theme.textPrimary
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: Theme.scaleFont(14)
                            enabled: root.username.length === 0
                            
                            cursorDelegate: Rectangle {
                                width: 2
                                color: Theme.accent
                            }
                            
                            background: null
                            selectByMouse: true
                            
                            onAccepted: registerButton.clicked()
                        }
                    }
                    
                    RowLayout {
                        spacing: Theme.spacing_md
                        
                        Button {
                            id: registerButton
                            Layout.fillWidth: true
                            Layout.preferredHeight: 44
                            enabled: root.username.length === 0
                            
                            transformOrigin: Item.Center
                            scale: down ? 0.95 : (hovered ? 1.04 : 1.0)
                            
                            Behavior on scale {
                                NumberAnimation {
                                    duration: Theme.duration_fast
                                    easing.type: Easing.OutQuad
                                }
                            }
                            
                            background: Rectangle {
                                radius: Theme.radius_lg
                                
                                gradient: Gradient {
                                    GradientStop { 
                                        position: 0.0
                                        color: registerButton.enabled ? Theme.accentBold : "#3A465D"
                                    }
                                    GradientStop { 
                                        position: 1.0
                                        color: registerButton.enabled ? Theme.accent : "#2A354A"
                                    }
                                }
                                
                                Rectangle {
                                    anchors.fill: parent
                                    radius: parent.radius
                                    gradient: Gradient {
                                        GradientStop { position: 0.0; color: "#40FFFFFF" }
                                        GradientStop { position: 1.0; color: "#00FFFFFF" }
                                    }
                                    opacity: registerButton.down ? 0.5 : (registerButton.hovered && registerButton.enabled ? 0.25 : 0.0)
                                    
                                    Behavior on opacity {
                                        NumberAnimation {
                                            duration: Theme.duration_fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                            }
                            
                            contentItem: Text {
                                text: root.username.length > 0 ? "Registered" : "Enter the lounge"
                                color: Theme.panel
                                font.pixelSize: Theme.scaleFont(14)
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                var name = usernameField.text.trim()
                                if (name.length > 0) {
                                    root.registerClicked(name)
                                }
                            }
                        }
                        
                        Button {
                            visible: root.username.length > 0
                            Layout.preferredWidth: 150
                            Layout.preferredHeight: 44
                            
                            transformOrigin: Item.Center
                            scale: down ? 0.96 : (hovered ? 1.02 : 1.0)
                            
                            Behavior on scale {
                                NumberAnimation {
                                    duration: Theme.duration_fast
                                    easing.type: Easing.OutQuad
                                }
                            }
                            
                            background: Rectangle {
                                radius: Theme.radius_lg
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: Theme.accent }
                                    GradientStop { position: 1.0; color: Theme.accentBold }
                                }
                                
                                Rectangle {
                                    anchors.fill: parent
                                    radius: parent.radius
                                    gradient: Gradient {
                                        GradientStop { position: 0.0; color: "#40FFFFFF" }
                                        GradientStop { position: 1.0; color: "#00FFFFFF" }
                                    }
                                    opacity: parent.parent.down ? 0.45 : (parent.parent.hovered ? 0.2 : 0.0)
                                    
                                    Behavior on opacity {
                                        NumberAnimation {
                                            duration: Theme.duration_fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                            }
                            
                            contentItem: Text {
                                text: "Update avatar"
                                color: Theme.panel
                                font.pixelSize: Theme.scaleFont(13)
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: root.avatarClicked()
                        }
                        
                        ToolButton {
                            Layout.preferredWidth: 44
                            Layout.preferredHeight: 44
                            
                            background: Rectangle {
                                radius: Theme.radius_lg
                                color: Theme.surface
                                border.color: Theme.outline
                            }
                            
                            contentItem: Text {
                                anchors.fill: parent
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                text: "✕"
                                color: Theme.textSecondary
                                font.pixelSize: Theme.scaleFont(20)
                            }
                            
                            onClicked: root.disconnectClicked()
                        }
                    }
                }
            }
        }
    }
}