// components/TypingIndicator.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Item {
    id: root
    
    property var typingUsers: []
    
    implicitHeight: typingText.visible ? typingText.implicitHeight + Theme.spacing_sm : 0
    
    Text {
        id: typingText
        visible: root.typingUsers && root.typingUsers.length > 0
        color: Theme.textSecondary
        font.pixelSize: Theme.scaleFont(12)
        font.italic: true
        
        text: {
            if (!root.typingUsers || root.typingUsers.length === 0) {
                return ""
            }
            
            var names = root.typingUsers
            if (names.length === 1) {
                return names[0] + " is typing..."
            } else if (names.length === 2) {
                return names[0] + " and " + names[1] + " are typing..."
            } else {
                return names.slice(0, 2).join(", ") + " and " + (names.length - 2) + " more are typing..."
            }
        }
        
        // Animated ellipsis
        SequentialAnimation on text {
            running: root.typingUsers && root.typingUsers.length > 0
            loops: Animation.Infinite
            
            PropertyAnimation {
                target: typingText
                property: "text"
                to: typingText.text.replace(/\.{0,3}$/, ".")
                duration: 500
            }
            PropertyAnimation {
                target: typingText
                property: "text"
                to: typingText.text.replace(/\.{0,3}$/, "..")
                duration: 500
            }
            PropertyAnimation {
                target: typingText
                property: "text"
                to: typingText.text.replace(/\.{0,3}$/, "...")
                duration: 500
            }
        }
    }
}
