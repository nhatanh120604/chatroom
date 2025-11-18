// components/Toast.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 6.6
import "../styles"

Rectangle {
    id: root
    
    anchors.horizontalCenter: parent ? parent.horizontalCenter : undefined
    anchors.bottom: parent ? parent.bottom : undefined
    anchors.bottomMargin: 80
    
    width: Math.min(400, parent ? parent.width - 64 : 400)
    height: content.implicitHeight + Theme.spacing_xxxl
    radius: Theme.radius_lg
    
    color: Theme.panel
    border.color: Theme.accent
    border.width: 1
    
    opacity: 0
    visible: opacity > 0
    z: 10000
    
    property string message: ""
    property string icon: "✓"
    property bool isError: false
    
    // Shadow effect
    layer.enabled: true
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowHorizontalOffset: 0
        shadowVerticalOffset: 8
        shadowBlur: 24
        shadowColor: "#40000000"
    }
    
    RowLayout {
        id: content
        anchors.fill: parent
        anchors.margins: Theme.spacing_lg
        spacing: Theme.spacing_md
        
        Text {
            text: root.icon
            color: root.isError ? Theme.warning : Theme.success
            font.pixelSize: Theme.scaleFont(20)
            font.family: Theme.emojiFont
        }
        
        Text {
            text: root.message
            color: Theme.textPrimary
            font.pixelSize: Theme.scaleFont(14)
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }
    
    // Show animation
    ParallelAnimation {
        id: showAnimation
        PropertyAnimation {
            target: root
            property: "opacity"
            to: 1
            duration: 300
            easing.type: Easing.OutCubic
        }
        PropertyAnimation {
            target: root
            property: "anchors.bottomMargin"
            to: 80
            duration: 300
            easing.type: Easing.OutCubic
        }
    }
    
    // Hide animation
    ParallelAnimation {
        id: hideAnimation
        PropertyAnimation {
            target: root
            property: "opacity"
            to: 0
            duration: 250
            easing.type: Easing.InCubic
        }
        PropertyAnimation {
            target: root
            property: "anchors.bottomMargin"
            to: 40
            duration: 250
            easing.type: Easing.InCubic
        }
    }
    
    Timer {
        id: hideTimer
        interval: 4000
        onTriggered: hideAnimation.start()
    }
    
    function show(msg, isErr) {
        root.message = msg
        root.isError = isErr || false
        root.icon = isErr ? "✗" : "✓"
        root.anchors.bottomMargin = 40
        showAnimation.start()
        hideTimer.restart()
    }
}