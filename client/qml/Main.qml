import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 6.6


ApplicationWindow {
    id: window
    visible: true
    width: 920
    height: 600
    title: "Aurora Chat"
    color: palette.window

    readonly property var palette: ({
        window: "#090C12",
        gradientTop: "#111927",
        gradientBottom: "#07090D",
        panel: "#121A26",
        surface: "#152033",
        card: "#1A2738",
        canvas: "#1F2D40",
        accent: "#E0C184",
        accentSoft: "#E0C18426",
        accentBold: "#F3DCA3",
        textPrimary: "#F4F7FB",
        textSecondary: "#A5AEC1",
        outline: "#222E42",
        success: "#35A57C",
        warning: "#CE6C6C"
    })

    readonly property var avatarDefaultColors: ({ top: "#6DE5AE", bottom: "#2C9C6D" })

    function avatarGradientFor(name) {
        return avatarDefaultColors
    }

    background: Rectangle {
        id: backgroundLayer
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: palette.gradientTop }
            GradientStop { position: 1.0; color: palette.gradientBottom }
        }

        property real shimmerOffset: -0.4

        Rectangle {
            anchors.fill: parent
            opacity: 0.12
            gradient: Gradient {
                GradientStop {
                    position: Math.max(0.0, Math.min(1.0, backgroundLayer.shimmerOffset - 0.25))
                    color: "#00000000"
                }
                GradientStop {
                    position: Math.max(0.0, Math.min(1.0, backgroundLayer.shimmerOffset))
                    color: "#22FFFFFF"
                }
                GradientStop {
                    position: Math.max(0.0, Math.min(1.0, backgroundLayer.shimmerOffset + 0.25))
                    color: "#00000000"
                }
            }
        }

        Item {
            anchors.fill: parent
            opacity: 0.35

            Rectangle {
                id: auroraGlowA
                width: 420
                height: 420
                radius: width / 2
                anchors.verticalCenter: parent.verticalCenter
                x: -260
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#40E0C184" }
                    GradientStop { position: 1.0; color: "#00000000" }
                }
                SequentialAnimation on x {
                    loops: Animation.Infinite
                    NumberAnimation {
                        to: backgroundLayer.width - 160
                        duration: 28000
                        easing.type: Easing.InOutSine
                    }
                    NumberAnimation {
                        to: -260
                        duration: 28000
                        easing.type: Easing.InOutSine
                    }
                }
            }

            Rectangle {
                id: auroraGlowB
                width: 360
                height: 360
                radius: width / 2
                anchors.horizontalCenter: parent.horizontalCenter
                y: -180
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#3035A57C" }
                    GradientStop { position: 1.0; color: "#00000000" }
                }
                SequentialAnimation on y {
                    loops: Animation.Infinite
                    NumberAnimation {
                        to: backgroundLayer.height - 140
                        duration: 24000
                        easing.type: Easing.InOutSine
                    }
                    NumberAnimation {
                        to: -180
                        duration: 24000
                        easing.type: Easing.InOutSine
                    }
                }
            }
        }

        NumberAnimation on shimmerOffset {
            loops: Animation.Infinite
            from: -0.4
            to: 1.4
            duration: 22000
            easing.type: Easing.InOutSine
        }
    }

    Rectangle {
        anchors.fill: parent
        radius: 0
        color: "#14FFFFFF" // Subtle overlay
    }

    Item {
        id: contentRoot
        anchors.fill: parent
        opacity: 0
        y: 16

        ParallelAnimation {
            id: introAnimation
            running: false
            PropertyAnimation {
                target: contentRoot
                property: "opacity"
                to: 1
                duration: 320
                easing.type: Easing.OutCubic
            }
            PropertyAnimation {
                target: contentRoot
                property: "y"
                to: 0
                duration: 360
                easing.type: Easing.OutCubic
            }
        }

        Component.onCompleted: introAnimation.start()

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 26

        // --- HEADER CARD ---
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 132

            MultiEffect {
                anchors.fill: headerCard
                source: headerCard
                shadowEnabled: true
                shadowHorizontalOffset: 0
                shadowVerticalOffset: 18
                shadowBlur: 32
                shadowColor: "#28000000"
                autoPaddingEnabled: true
            }

            Rectangle {
                id: headerCard
                anchors.fill: parent
                radius: 28
                transformOrigin: Item.Center
                border.color: palette.outline
                border.width: 1
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#1C283B" } // Using custom gradient
                    GradientStop { position: 1.0; color: palette.panel }
                }

                Item {
                    anchors.fill: parent
                    anchors.margins: 28

                    RowLayout {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width
                        spacing: 28

                        // --- Header Welcome Text ---
                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignVCenter
                            spacing: 10

                            Text {
                                text: chatClient.username.length > 0 ? "Welcome back, " + chatClient.username : "Aurora Lounge"
                                color: palette.textPrimary
                                font.pixelSize: 26
                                font.bold: true
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Text {
                                text: chatClient.username.length > 0 ? "Share a thought with the lounge—your voice sets tonight's tone." : "Reserve a signature name to slip past the velvet rope."
                                color: palette.textSecondary
                                font.pixelSize: 14
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }

                            RowLayout {
                                spacing: 12

                                Rectangle {
                                    Layout.preferredWidth: 160
                                    Layout.preferredHeight: 32
                                    radius: 16
                                    border.width: 0
                                    color: chatClient.username.length > 0 ? palette.success : palette.accentSoft

                                    Text {
                                        anchors.centerIn: parent
                                        text: chatClient.username.length > 0 ? "Enrolled guest" : "Guest access"
                                        color: chatClient.username.length > 0 ? palette.textPrimary : palette.textSecondary
                                        font.pixelSize: 12
                                        font.bold: true
                                    }
                                }

                                Rectangle {
                                    Layout.preferredWidth: 160
                                    Layout.preferredHeight: 32
                                    radius: 16
                                    color: "transparent"
                                    border.color: palette.outline
                                    border.width: 1

                                    Timer {
                                        id: clockTimer
                                        interval: 1000 // Updates once per second
                                        running: true
                                        repeat: true
                                    }

                                    Text {
                                        anchors.centerIn: parent
                                        text: {
                                            clockTimer.triggered() // Depend on the timer
                                            return Qt.formatDateTime(new Date(), "ddd, MMM d • hh:mm ap")
                                        }
                                        color: palette.textSecondary
                                        font.pixelSize: 12
                                    }
                                }
                            }
                        }

                        // --- Header User Input ---
                        ColumnLayout {
                            spacing: 12
                            Layout.preferredWidth: 320
                            Layout.alignment: Qt.AlignVCenter

                            Rectangle {
                                // *** BUG FIX: Added Layout.fillWidth ***
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                radius: 18
                                color: window.palette.canvas
                                border.color: usernameField.activeFocus ? window.palette.accent : window.palette.outline
                                border.width: 1

                                TextField {
                                    id: usernameField
                                    anchors.fill: parent
                                    leftPadding: 18
                                    rightPadding: 18
                                    topPadding: 10
                                    bottomPadding: 10
                                    placeholderText: "Choose your lounge signature"
                                    placeholderTextColor: window.palette.textSecondary
                                    color: window.palette.textPrimary
                                    selectionColor: window.palette.accent
                                    selectedTextColor: window.palette.textPrimary
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 14
                                    enabled: chatClient.username.length === 0
                                    cursorDelegate: Rectangle {
                                        width: 2
                                        color: window.palette.accent
                                    }
                                    background: null
                                    selectByMouse: true
                                    onAccepted: registerButton.clicked()
                                }
                            }

                            RowLayout {
                                spacing: 12

                                Button {
                                    id: registerButton
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 44
                                    enabled: chatClient.username.length === 0
                                    padding: 0
                                    topPadding: 0
                                    bottomPadding: 0
                                    leftPadding: 0
                                    rightPadding: 0
                                    transformOrigin: Item.Center
                                    scale: down ? 0.95 : (hovered ? 1.04 : 1.0)
                                    Behavior on scale {
                                        NumberAnimation {
                                            duration: 160
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                    background: Rectangle {
                                        id: registerBackground
                                        radius: 20
                                        border.width: 0
                                        readonly property color enabledTop: palette.accentBold
                                        readonly property color enabledBottom: palette.accent
                                        readonly property color disabledTop: "#3A465D"
                                        readonly property color disabledBottom: "#2A354A"
                                        color: registerButton.enabled ? enabledBottom : disabledBottom
                                        readonly property color topColor: registerButton.enabled ? enabledTop : disabledTop
                                        readonly property color bottomColor: registerButton.enabled ? enabledBottom : disabledBottom
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: registerBackground.topColor }
                                            GradientStop { position: 1.0; color: registerBackground.bottomColor }
                                        }

                                        Rectangle {
                                            anchors.fill: parent
                                            radius: parent.radius
                                            gradient: Gradient {
                                                GradientStop { position: 0.0; color: "#40FFFFFF" }
                                                GradientStop { position: 1.0; color: "#00FFFFFF" }
                                            }
                                            opacity: registerButton.down ? 0.5 : ((registerButton.hovered && registerButton.enabled) ? 0.25 : 0.0)
                                            Behavior on opacity {
                                                NumberAnimation {
                                                    duration: 160
                                                    easing.type: Easing.OutQuad
                                                }
                                            }
                                        }
                                    }
                                    contentItem: Text {
                                        anchors.centerIn: parent
                                        text: chatClient.username.length > 0 ? "Registered" : "Enter the lounge"
                                        color: palette.panel
                                        font.pixelSize: 14
                                        font.bold: true
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        var name = usernameField.text.trim()
                                        if (name.length > 0) {
                                            chatClient.register(name)
                                        }
                                    }
                                }

                                ToolButton {
                                    Layout.preferredWidth: 44
                                    Layout.preferredHeight: 44
                                    onClicked: chatClient.disconnect()
                                    padding: 0
                                    topPadding: 0
                                    bottomPadding: 0
                                    leftPadding: 0
                                    rightPadding: 0
                                    background: Rectangle {
                                        radius: 20
                                        color: palette.surface
                                        border.color: palette.outline
                                    }
                                    contentItem: Text {
                                        anchors.fill: parent
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                        text: "\u2715"
                                        color: palette.textSecondary
                                        font.pixelSize: 20
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- MAIN CONTENT (CHAT + USER LIST) ---
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 22

            // --- CHAT PANEL ---
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                MultiEffect {
                    anchors.fill: chatCard
                    source: chatCard
                    shadowEnabled: true
                    shadowHorizontalOffset: 0
                    shadowVerticalOffset: 18
                    shadowBlur: 36
                    shadowColor: "#22000000"
                    autoPaddingEnabled: true
                }

                Rectangle {
                    id: chatCard
                    anchors.fill: parent
                    radius: 26
                    transformOrigin: Item.Center
                    border.color: palette.outline
                    border.width: 1
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: palette.panel }
                        GradientStop { position: 1.0; color: palette.surface }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 28
                        spacing: 20

                        // --- Chat Header ---
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            Text {
                                text: "Salon feed"
                                color: palette.textPrimary
                                font.pixelSize: 18
                                font.bold: true
                            }

                            Rectangle {
                                Layout.preferredWidth: 6
                                Layout.preferredHeight: 6
                                radius: 3
                                color: palette.accent
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Text {
                                text: usersModel.count > 0 ? usersModel.count + " guests mingling" : "Awaiting first arrival"
                                color: palette.textSecondary
                                font.pixelSize: 12
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }

                        // --- Chat Message Area ---
                        Flickable {
                            id: scrollArea
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            property bool autoStickToBottom: true
                            contentWidth: chatColumn.width
                            contentHeight: chatColumn.height
                            boundsBehavior: Flickable.DragAndOvershootBounds

                            Component.onCompleted: scrollToEnd(false)

                            Column {
                                id: chatColumn
                                width: scrollArea.width
                                spacing: 20

                                Repeater {
                                    model: messagesModel
                                    delegate: messageDelegateComponent
                                }

                                Item {
                                    width: parent.width
                                    height: 12
                                }
                            }

                            ScrollIndicator.vertical: ScrollIndicator {
                                anchors.right: parent.right
                                anchors.rightMargin: 0
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                contentItem: Rectangle {
                                    radius: 2
                                    color: palette.accent
                                }
                            }

                            onContentHeightChanged: scrollToEnd(autoStickToBottom)
                            onContentYChanged: {
                                if ((moving || dragging) && !atYEnd) {
                                    autoStickToBottom = false
                                } else if (!moving && !dragging && atYEnd) {
                                    autoStickToBottom = true
                                }
                            }
                            onMovementStarted: {
                                if (!atYEnd) {
                                    autoStickToBottom = false
                                }
                            }
                            onMovementEnded: {
                                if (atYEnd) {
                                    autoStickToBottom = true
                                }
                            }
                            onDraggingChanged: {
                                if (dragging && !atYEnd) {
                                    autoStickToBottom = false
                                } else if (!dragging && atYEnd) {
                                    autoStickToBottom = true
                                }
                            }

                            NumberAnimation {
                                id: scrollAnimation
                                target: scrollArea
                                property: "contentY"
                                duration: 220
                                easing.type: Easing.InOutQuad
                            }

                            function scrollToEnd(animated) {
                                var target = Math.max(0, contentHeight - height)
                                if (Math.abs(contentY - target) < 0.5) {
                                    return
                                }
                                if (animated) {
                                    scrollAnimation.stop()
                                    scrollAnimation.from = contentY
                                    scrollAnimation.to = target
                                    scrollAnimation.restart()
                                } else {
                                    scrollAnimation.stop()
                                    contentY = target
                                }
                            }
                        }

                        // --- Chat Input Bar ---
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 84
                            radius: 22
                            color: window.palette.surface
                            border.color: window.palette.outline
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 16

                                Rectangle {
                                    id: messageFieldFrame
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 48
                                    radius: 16
                                    color: window.palette.canvas
                                    border.color: messageField.activeFocus ? window.palette.accent : window.palette.outline
                                    border.width: 1
                                    property real rippleProgress: 0
                                    Behavior on border.color {
                                        ColorAnimation {
                                            duration: 180
                                            easing.type: Easing.OutQuad
                                        }
                                    }

                                    Rectangle {
                                        id: rippleOverlay
                                        anchors.fill: parent
                                        radius: parent.radius
                                        color: "transparent"
                                        border.width: 0
                                        opacity: messageField.activeFocus ? 0.35 : 0.0
                                        visible: opacity > 0
                                        gradient: Gradient {
                                            GradientStop {
                                                position: Math.max(0.0, messageFieldFrame.rippleProgress - 0.2)
                                                color: "#00FFFFFF"
                                            }
                                            GradientStop {
                                                position: Math.max(0.0, Math.min(1.0, messageFieldFrame.rippleProgress))
                                                color: window.palette.accent
                                            }
                                            GradientStop {
                                                position: Math.min(1.0, messageFieldFrame.rippleProgress + 0.2)
                                                color: "#00FFFFFF"
                                            }
                                        }
                                        Behavior on opacity {
                                            NumberAnimation {
                                                duration: 220
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
                                        leftPadding: 18
                                        rightPadding: 18
                                        topPadding: 12
                                        bottomPadding: 12
                                        placeholderText: "Contribute to the salon or /msg <guest> <message>"
                                        placeholderTextColor: window.palette.textSecondary
                                        color: window.palette.textPrimary
                                        selectionColor: window.palette.accent
                                        selectedTextColor: window.palette.textPrimary
                                        verticalAlignment: Text.AlignVCenter
                                        font.pixelSize: 14
                                        wrapMode: Text.WordWrap
                                        cursorDelegate: Rectangle {
                                            width: 2
                                            color: window.palette.accent
                                        }
                                        background: null
                                        selectByMouse: true
                                        onAccepted: sendButton.clicked()
                                        onActiveFocusChanged: {
                                            if (activeFocus) {
                                                messageFieldFrame.rippleProgress = 0
                                                rippleAnimator.restart()
                                            } else {
                                                rippleAnimator.stop()
                                                messageFieldFrame.rippleProgress = 0
                                            }
                                        }
                                    }
                                }

                                Button {
                                    id: sendButton
                                    Layout.preferredWidth: 124
                                    Layout.preferredHeight: 48
                                    padding: 0
                                    topPadding: 0
                                    bottomPadding: 0
                                    leftPadding: 0
                                    rightPadding: 0
                                    transformOrigin: Item.Center
                                    scale: down ? 0.95 : (hovered ? 1.05 : 1.0)
                                    Behavior on scale {
                                        NumberAnimation {
                                            duration: 160
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                    background: Rectangle {
                                        id: sendBackground
                                        radius: 22
                                        border.width: 0
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: palette.accentBold }
                                            GradientStop { position: 1.0; color: palette.accent }
                                        }
                                        Rectangle {
                                            anchors.fill: parent
                                            radius: parent.radius
                                            gradient: Gradient {
                                                GradientStop { position: 0.0; color: "#40FFFFFF" }
                                                GradientStop { position: 1.0; color: "#00FFFFFF" }
                                            }
                                            opacity: sendButton.down ? 0.55 : (sendButton.hovered ? 0.28 : 0.0)
                                            Behavior on opacity {
                                                NumberAnimation {
                                                    duration: 160
                                                    easing.type: Easing.OutQuad
                                                }
                                            }
                                        }
                                    }
                                    contentItem: Text {
                                        anchors.centerIn: parent
                                        text: "Send"
                                        color: palette.panel
                                        font.pixelSize: 15
                                        font.bold: true
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        var text = messageField.text
                                        if (text.length > 0) {
                                            if (text.startsWith("/msg ")) {
                                                var parts = text.substring(5).split(" ")
                                                var recipient = parts.shift()
                                                var message = parts.join(" ")
                                                if (recipient && message) {
                                                    chatClient.sendPrivateMessage(recipient, message)
                                                    messagesModel.append({
                                                        "user": "To " + recipient,
                                                        "text": message,
                                                        "isPrivate": true
                                                    })
                                                }
                                            } else {
                                                chatClient.sendMessage(text)
                                            }
                                            messageField.text = ""
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // --- CONCIERGE (USER LIST) PANEL ---
            Item {
                Layout.preferredWidth: 260
                Layout.fillHeight: true

                MultiEffect {
                    anchors.fill: conciergeCard
                    source: conciergeCard
                    shadowEnabled: true
                    shadowHorizontalOffset: 0
                    shadowVerticalOffset: 18
                    shadowBlur: 32
                    shadowColor: "#22000000"
                    autoPaddingEnabled: true
                }

                Rectangle {
                    id: conciergeCard
                    anchors.fill: parent
                    radius: 26
                    transformOrigin: Item.Center
                    border.color: palette.outline
                    border.width: 1
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: palette.surface }
                        GradientStop { position: 1.0; color: palette.panel }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 18

                        Text {
                            text: "Concierge"
                            color: palette.textPrimary
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            text: "Spot a guest, tap to begin a private exchange."
                            color: palette.textSecondary
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 1
                            color: palette.outline
                            opacity: 0.18
                        }

                        ListView {
                            id: usersView
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            spacing: 12
                            model: usersModel
                            delegate: userDelegateComponent
                        }
                    }
                }
            }
        }
    }

    // --- MODELS ---
    ListModel { id: messagesModel }
    ListModel { id: usersModel }

    // --- FEEDBACK ANIMATIONS ---
    ParallelAnimation {
        id: disconnectAnimation
        running: false

        SequentialAnimation {
            PropertyAnimation {
                target: headerCard
                property: "scale"
                to: 0.96
                duration: 130
                easing.type: Easing.InOutQuad
            }
            PropertyAnimation {
                target: headerCard
                property: "scale"
                to: 1
                duration: 220
                easing.type: Easing.OutBack
            }
        }

        SequentialAnimation {
            PropertyAnimation {
                target: chatCard
                property: "scale"
                to: 0.95
                duration: 130
                easing.type: Easing.InOutQuad
            }
            PropertyAnimation {
                target: chatCard
                property: "scale"
                to: 1
                duration: 240
                easing.type: Easing.OutBack
            }
        }

        SequentialAnimation {
            PropertyAnimation {
                target: conciergeCard
                property: "scale"
                to: 0.95
                duration: 130
                easing.type: Easing.InOutQuad
            }
            PropertyAnimation {
                target: conciergeCard
                property: "scale"
                to: 1
                duration: 220
                easing.type: Easing.OutBack
            }
        }
    }

    // --- COMPONENT DEFINITIONS ---
    Component {
        id: messageDelegateComponent

        Column {
            id: messageContainer
            width: parent.width
            spacing: 6
            property bool isFirst: index === 0
            property bool isSystem: model.user === "System"
            opacity: 0
            scale: 0.97
            transformOrigin: Item.TopLeft

            Component.onCompleted: entryAnimation.start()

            ParallelAnimation {
                id: entryAnimation
                running: false
                PropertyAnimation {
                    target: messageContainer
                    property: "opacity"
                    to: 1
                    duration: 220
                    easing.type: Easing.OutQuad
                }
                PropertyAnimation {
                    target: messageContainer
                    property: "scale"
                    to: 1
                    duration: 220
                    easing.type: Easing.OutBack
                }
            }

            Rectangle {
                width: parent.width
                height: isFirst ? 0 : 1
                color: palette.outline
                opacity: 0.18
            }

            Text {
                text: model.isPrivate ? model.user + " • private channel" : model.user
                color: model.isPrivate ? palette.accent : palette.textSecondary
                font.pixelSize: 12
                font.bold: true
                Layout.alignment: Qt.AlignLeft
                topPadding: isFirst ? 2 : 0
            }

            Rectangle {
                id: messageBubble
                width: parent.width
                radius: 18
                color: messageContainer.isSystem ? palette.accentSoft : (model.isPrivate ? palette.accentSoft : palette.card)
                border.width: 1
                property color baseBorder: messageContainer.isSystem ? palette.accent : (model.isPrivate ? palette.accent : palette.canvas)
                border.color: baseBorder
                Behavior on border.color {
                    ColorAnimation {
                        duration: 260
                        easing.type: Easing.OutQuad
                    }
                }

                SequentialAnimation {
                    id: systemGlow
                    running: false
                    ColorAnimation {
                        target: messageBubble
                        property: "border.color"
                        to: palette.accentBold
                        duration: 120
                        easing.type: Easing.OutQuad
                    }
                    ColorAnimation {
                        target: messageBubble
                        property: "border.color"
                        to: messageBubble.baseBorder
                        duration: 420
                        easing.type: Easing.OutCubic
                    }
                }

                Component.onCompleted: {
                    if (messageContainer.isSystem) {
                        systemGlow.restart()
                    }
                }

                Text {
                    text: model.text
                    color: palette.textPrimary
                    wrapMode: Text.Wrap
                    anchors.fill: parent
                    anchors.margins: 20
                    font.pixelSize: 15
                    lineHeight: 1.35
                }
            }
        }
    }

    Component {
        id: userDelegateComponent

        Rectangle {
            id: userCard
            width: usersView.width
            height: 56
            radius: 20
            color: hovered ? palette.accentSoft : palette.card
            border.color: hovered ? palette.accent : palette.outline
            border.width: hovered ? 1 : 0
            transformOrigin: Item.Center
            scale: hovered ? 1.04 : 1.0

            Behavior on scale {
                NumberAnimation {
                    duration: 140
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on color {
                ColorAnimation {
                    duration: 140
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on border.color {
                ColorAnimation {
                    duration: 140
                    easing.type: Easing.OutQuad
                }
            }

            property bool hovered: mouseArea.containsMouse

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    messageField.text = "/msg " + name + " "
                    messageField.forceActiveFocus()
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 12

                Rectangle {
                    id: avatarBadge
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 30
                    radius: 15
                    property var avatarColors: window.avatarGradientFor(name)
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: avatarBadge.avatarColors.top }
                        GradientStop { position: 1.0; color: avatarBadge.avatarColors.bottom }
                    }
                    border.color: "#60FFFFFF"
                    border.width: 1
                    scale: 1
                    transformOrigin: Item.Center
                    property real sheenOffset: -0.6

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: "transparent"
                        border.width: 0
                        gradient: Gradient {
                            GradientStop {
                                position: Math.max(0.0, Math.min(1.0, avatarBadge.sheenOffset - 0.2))
                                color: "#00FFFFFF"
                            }
                            GradientStop {
                                position: Math.max(0.0, Math.min(1.0, avatarBadge.sheenOffset))
                                color: "#55FFFFFF"
                            }
                            GradientStop {
                                position: Math.max(0.0, Math.min(1.0, avatarBadge.sheenOffset + 0.2))
                                color: "#00FFFFFF"
                            }
                        }
                        opacity: 0.7
                    }

                    SequentialAnimation {
                        id: avatarPulse
                        loops: Animation.Infinite
                        running: true
                        NumberAnimation {
                            target: avatarBadge
                            property: "scale"
                            to: 1.08
                            duration: 1100
                            easing.type: Easing.InOutSine
                        }
                        NumberAnimation {
                            target: avatarBadge
                            property: "scale"
                            to: 1.0
                            duration: 1100
                            easing.type: Easing.InOutSine
                        }
                    }

                    NumberAnimation on sheenOffset {
                        loops: Animation.Infinite
                        from: -0.6
                        to: 1.6
                        duration: 4200
                        easing.type: Easing.InOutSine
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: name
                        color: palette.textPrimary
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Text {
                        text: "Invite to private line"
                        color: palette.textSecondary
                        font.pixelSize: 11
                    }
                }
            }
        }
    }

    // --- BACKEND CONNECTIONS ---
    Connections {
        target: chatClient

        function onMessageReceived(username, message) {
            messagesModel.append({
                "user": username,
                "text": message,
                "isPrivate": false
            })
        }

        function onPrivateMessageReceived(sender, recipient, message) {
            messagesModel.append({
                "user": "From " + sender,
                "text": message,
                "isPrivate": true
            })
        }

        function onUsersUpdated(users) {
            usersModel.clear()
            for (var i = 0; i < users.length; i++) {
                usersModel.append({"name": users[i]})
            }
        }

        function onDisconnected() {
            messagesModel.clear()
            usersModel.clear()
            messagesModel.append({
                "user": "System",
                "text": "You have been disconnected.",
                "isPrivate": false
            })
            disconnectAnimation.restart()
        }

        function onErrorReceived(message) {
            messagesModel.append({
                "user": "System",
                "text": message,
                "isPrivate": false
            })
        }

        function onUsernameChanged(name) {
            usernameField.text = name
            if (name.length > 0) {
                messageField.forceActiveFocus()
            }
        }
    }
}
}
