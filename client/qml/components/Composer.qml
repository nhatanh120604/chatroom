// components/Composer.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Rectangle {
    id: root
    
    property alias text: messageField.text
    property alias placeholderText: messageField.placeholderText
    property var pendingFile: null
    property bool enabled: true
    
    signal sendClicked()
    signal emojiClicked()
    signal fileClicked()
    signal textEdited(string text)
    signal focusRequested()
    
    radius: Theme.radius_xl
    color: Theme.surface
    border.color: Theme.outline
    border.width: 1
    implicitHeight: composerContent.implicitHeight + Theme.spacing_xxxl + 4
    
    ColumnLayout {
        id: composerContent
        anchors.fill: parent
        anchors.margins: Theme.spacing_lg
        spacing: Theme.spacing_md
        
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing_lg
            
            // Text input
            Rectangle {
                id: messageFieldFrame
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                radius: Theme.radius_lg
                color: Theme.canvas
                border.color: messageField.activeFocus ? Theme.accent : Theme.outline
                border.width: 1
                
                property real rippleProgress: 0
                
                Behavior on border.color {
                    ColorAnimation {
                        duration: Theme.duration_normal
                        easing.type: Easing.OutQuad
                    }
                }
                
                // Ripple effect
                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: "transparent"
                    opacity: messageField.activeFocus ? 0.35 : 0.0
                    visible: opacity > 0
                    
                    gradient: Gradient {
                        GradientStop {
                            position: Math.max(0.0, messageFieldFrame.rippleProgress - 0.2)
                            color: "#00FFFFFF"
                        }
                        GradientStop {
                            position: Math.max(0.0, Math.min(1.0, messageFieldFrame.rippleProgress))
                            color: Theme.accent
                        }
                        GradientStop {
                            position: Math.min(1.0, messageFieldFrame.rippleProgress + 0.2)
                            color: "#00FFFFFF"
                        }
                    }
                    
                    Behavior on opacity {
                        NumberAnimation {
                            duration: Theme.duration_normal
                            easing.type: Easing.OutQuad
                        }
                    }
                }
                
                NumberAnimation {
                    id: rippleAnimator
                    target: messageFieldFrame
                    property: "rippleProgress"
                    from: 0
                    to: 1
                    duration: 520
                    easing.type: Easing.OutQuad
                }
                
                TextField {
                    id: messageField
                    anchors.fill: parent
                    leftPadding: Theme.spacing_lg
                    rightPadding: Theme.spacing_lg
                    topPadding: Theme.spacing_md
                    bottomPadding: Theme.spacing_md
                    placeholderText: "Share something with the lounge"
                    placeholderTextColor: Theme.textSecondary
                    color: Theme.textPrimary
                    selectionColor: Theme.accent
                    selectedTextColor: Theme.textPrimary
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Theme.scaleFont(14)
                    wrapMode: Text.WordWrap
                    enabled: root.enabled
                    
                    cursorDelegate: Rectangle {
                        width: 2
                        color: Theme.accent
                    }
                    
                    background: null
                    selectByMouse: true
                    
                    onAccepted: root.sendClicked()
                    
                    onActiveFocusChanged: {
                        if (activeFocus) {
                            messageFieldFrame.rippleProgress = 0
                            rippleAnimator.restart()
                        } else {
                            rippleAnimator.stop()
                            messageFieldFrame.rippleProgress = 0
                        }
                    }
                    
                    onTextChanged: root.textEdited(text)
                }
            }
            
            // Emoji button
            ToolButton {
                Layout.preferredWidth: 48
                Layout.preferredHeight: 48
                enabled: root.enabled
                
                background: Rectangle {
                    radius: Theme.radius_lg
                    color: parent.down ? Theme.accentSoft : (parent.hovered ? Theme.surface : Theme.canvas)
                    border.width: 1
                    border.color: parent.down || parent.hovered ? Theme.accent : Theme.outline
                    
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
                }
                
                contentItem: Image {
                    anchors.centerIn: parent
                    width: Theme.scaleFont(24)
                    height: width
                    source: Qt.resolvedUrl("../assets/emoji_icon.svg")
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
                
                onClicked: root.emojiClicked()
            }
            
            // File button
            ToolButton {
                Layout.preferredWidth: 48
                Layout.preferredHeight: 48
                enabled: root.enabled
                
                background: Rectangle {
                    radius: Theme.radius_lg
                    color: parent.down ? Theme.accentSoft : (parent.hovered ? Theme.surface : Theme.canvas)
                    border.width: 1
                    border.color: parent.down || parent.hovered ? Theme.accent : Theme.outline
                    
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
                }
                
                contentItem: Image {
                    anchors.centerIn: parent
                    width: Theme.scaleFont(22)
                    height: width
                    source: Qt.resolvedUrl("../assets/file_icon.svg")
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
                
                onClicked: root.fileClicked()
            }
            
            // Send button
            Button {
                Layout.preferredWidth: 124
                Layout.preferredHeight: 48
                enabled: root.enabled
                
                transformOrigin: Item.Center
                scale: down ? 0.95 : (hovered ? 1.05 : 1.0)
                
                Behavior on scale {
                    NumberAnimation {
                        duration: Theme.duration_fast
                        easing.type: Easing.OutQuad
                    }
                }
                
                background: Rectangle {
                    radius: Theme.radius_xl
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Theme.accentBold }
                        GradientStop { position: 1.0; color: Theme.accent }
                    }
                    
                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#40FFFFFF" }
                            GradientStop { position: 1.0; color: "#00FFFFFF" }
                        }
                        opacity: parent.parent.down ? 0.55 : (parent.parent.hovered ? 0.28 : 0.0)
                        
                        Behavior on opacity {
                            NumberAnimation {
                                duration: Theme.duration_fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                }
                
                contentItem: Text {
                    text: "Send"
                    color: Theme.panel
                    font.pixelSize: Theme.scaleFont(15)
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: root.sendClicked()
            }
        }
        
        // Pending file attachment preview
        FileAttachment {
            visible: root.pendingFile !== null
            Layout.fillWidth: true
            fileName: root.pendingFile ? root.pendingFile.name : ""
            fileSize: root.pendingFile ? root.pendingFile.size : 0
            canDownload: false
            onRemoveClicked: root.pendingFile = null
        }
    }
    
    function forceFieldFocus() {
        messageField.forceActiveFocus()
    }
    
    function clearText() {
        messageField.text = ""
    }
}