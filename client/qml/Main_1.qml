// Main.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia
import "./styles"
import "./components"
import "./pages"
import "./assets"

ApplicationWindow {
    id: window
    visible: true
    width: 920
    height: 600
    title: "Aurora Chat"
    color: Theme.window
    
    // ========== STATE ==========
    property var privateMessageModels: ({})
    property var conversationPages: ({})
    property var privateDrafts: ({})
    property var privatePendingFiles: ({})
    property var privateTypingStates: ({})
    property var messageIndexById: ({})
    property var userAvatars: ({})
    
    property string publicDraft: ""
    property var publicPendingFile: null
    property var publicTypingUsers: []
    property int totalUserCount: 0
    
    property bool soundsEnabled: true
    property var lastSoundTime: new Date(0)
    property int soundDebounceMs: 500
    property var activeDownloads: ({})  // transfer_id -> {progress, filename}
    
    // ========== MODELS ==========
    ListModel {
        id: conversationTabsModel
        ListElement { 
            key: "public"
            title: "Salon feed"
            isPrivate: false
            hasUnread: false
            unreadCount: 0
        }
    }
    
    ListModel { id: messagesModel }
    ListModel { id: usersModel }
    
    // ========== SOUND EFFECTS ==========
    SoundEffect {
        id: publicMessageSound
        source: Qt.resolvedUrl("./assets/notification_message.wav")
        volume: 0.5
    }
    
    SoundEffect {
        id: privateMessageSound
        source: Qt.resolvedUrl("./assets/notification_private.wav")
        volume: 0.6
    }
    
    // ========== HELPER FUNCTIONS ==========
    function playSoundIfAllowed(soundEffect) {
        if (!soundsEnabled) return
        
        var now = new Date()
        if (now - lastSoundTime > soundDebounceMs) {
            soundEffect.play()
            lastSoundTime = now
        }
    }
    
    function showToast(message, isError) {
        console.log("[QML] showToast called:", message, "error:", isError)
        if (toast) {
            toast.show(message, isError || false)
        } else {
            console.error("[QML] toast not found!")
        }
    }
    
    function updateDownloadProgress(transferId, current, total) {
        var snapshot = Object.assign({}, activeDownloads)
        if (current >= total && total > 0) {
            if (snapshot[transferId]) {
                snapshot[transferId].progress = 1.0
            }
        } else if (total > 0) {
            if (!snapshot[transferId]) {
                snapshot[transferId] = {
                    progress: 0,
                    filename: "",
                    current: current,
                    total: total
                }
            }
            snapshot[transferId].progress = current / total
            snapshot[transferId].current = current
            snapshot[transferId].total = total
        }
        activeDownloads = snapshot
        logFileTransfer(transferId, snapshot[transferId].filename, "IN_PROGRESS", snapshot[transferId].progress)
    }
    
    function clearDownload(transferId) {
        var snapshot = Object.assign({}, activeDownloads)
        delete snapshot[transferId]
        activeDownloads = snapshot
        logFileTransfer(transferId, "", "CANCELLED")
    }
    
    // ========== LOGGING FUNCTIONS ==========
    function logDebug(tag, message) {
        console.log("[DEBUG] [" + tag + "] " + message)
    }
    
    function logInfo(tag, message) {
        console.log("[INFO] [" + tag + "] " + message)
    }
    
    function logWarning(tag, message) {
        console.warn("[WARN] [" + tag + "] " + message)
    }
    
    function logError(tag, message) {
        console.error("[ERROR] [" + tag + "] " + message)
    }
    
    function logFileTransfer(transferId, fileName, status, progress) {
        var msg = "Transfer: " + transferId + " | File: " + fileName + " | Status: " + status
        if (progress !== undefined) {
            msg += " | Progress: " + (progress * 100).toFixed(1) + "%"
        }
        logDebug("FileTransfer", msg)
    }
    
    function logMessage(user, text, isPrivate, hasFile) {
        var type = isPrivate ? "PRIVATE" : "PUBLIC"
        var fileInfo = hasFile ? " [WITH FILE]" : ""
        logDebug("Message", type + ": " + user + " - " + text.substring(0, 50) + fileInfo)
    }
    
    function logConversation(action, peer) {
        logDebug("Conversation", action + ": " + peer)
    }
    
    function logState(property, value) {
        logDebug("State", property + " = " + JSON.stringify(value).substring(0, 100))
    }
    
    function formatTimestamp(ts) {
        try {
            if (ts && ts.length > 0) {
                var d = new Date(ts)
                if (!isNaN(d.getTime()))
                    return Qt.formatDateTime(d, "hh:mm ap")
            }
        } catch(e) {}
        return Qt.formatDateTime(new Date(), "hh:mm ap")
    }
    
    function avatarSourceFor(name) {
        if (!name || !userAvatars || !userAvatars[name] || !userAvatars[name].data) {
            return ""
        }
        var info = userAvatars[name]
        var mime = info.mime && info.mime.length > 0 ? info.mime : "image/png"
        return "data:" + mime + ";base64," + info.data
    }
    
    function ensurePrivateModel(peer) {
        if (!peer) return null
        if (!privateMessageModels[peer]) {
            privateMessageModels[peer] = Qt.createQmlObject(
                'import QtQuick 2.15; ListModel {}', 
                window
            )
        }
        return privateMessageModels[peer]
    }
    
    function conversationIndex(key) {
        for (var i = 0; i < conversationTabsModel.count; ++i) {
            if (conversationTabsModel.get(i).key === key) {
                return i
            }
        }
        return -1
    }
    
    function openPrivateConversation(peer) {
        if (!peer || peer === chatClient.username) return
        
        logConversation("OPEN", peer)
        ensurePrivateModel(peer)
        if (conversationIndex(peer) === -1) {
            conversationTabsModel.append({
                "key": peer,
                "title": peer,
                "isPrivate": true,
                "hasUnread": false,
                "unreadCount": 0
            })
            logInfo("Conversation", "Created new conversation with " + peer)
        }
        
        var idx = conversationIndex(peer)
        if (idx >= 0) {
            conversationTabBar.currentIndex = idx
            logDebug("Conversation", "Switched to conversation index " + idx)
        }
    }
    
    function closePrivateConversation(peer) {
        var idx = conversationIndex(peer)
        if (idx > 0) {
            conversationTabsModel.remove(idx)
            delete conversationPages[peer]
            delete privateDrafts[peer]
            delete privatePendingFiles[peer]
        }
    }
    
    function clearConversationUnread(key) {
        var idx = conversationIndex(key)
        if (idx >= 0) {
            conversationTabsModel.setProperty(idx, "hasUnread", false)
            conversationTabsModel.setProperty(idx, "unreadCount", 0)
        }
    }
    
    function incrementConversationUnread(key) {
        var idx = conversationIndex(key)
        if (idx >= 0) {
            var current = conversationTabsModel.get(idx).unreadCount || 0
            conversationTabsModel.setProperty(idx, "unreadCount", current + 1)
            conversationTabsModel.setProperty(idx, "hasUnread", true)
        }
    }
    
    function appendPrivateMessage(peer, author, text, isOutgoing, messageId, status, filePayload, timestamp) {
        if (!peer || peer.length === 0) return
        
        var model = ensurePrivateModel(peer)
        if (!model) return
        
        if (conversationIndex(peer) === -1) {
            conversationTabsModel.append({
                "key": peer,
                "title": peer,
                "isPrivate": true,
                "hasUnread": false,
                "unreadCount": 0
            })
        }
        
        var hasFile = filePayload && (filePayload.data || filePayload.transfer_id)
        logMessage(author || peer, text, true, hasFile)
        
        model.append({
            "user": author || peer,
            "text": text || "",
            "timestamp": timestamp || formatTimestamp(""),
            "isPrivate": true,
            "isOutgoing": isOutgoing === true,
            "displayContext": isOutgoing === true ? "You" : author,
            "status": status || "sent",
            "fileName": filePayload && filePayload.filename ? filePayload.filename : (filePayload && filePayload.name ? filePayload.name : ""),
            "fileMime": filePayload && filePayload.mime ? filePayload.mime : "",
            "fileData": filePayload && filePayload.data ? filePayload.data : "",
            "fileSize": filePayload && filePayload.size ? Number(filePayload.size) : 0,
            "transferId": filePayload && filePayload.transfer_id ? String(filePayload.transfer_id) : ""
        })
        
        var idx = conversationIndex(peer)
        var isActive = idx === conversationTabBar.currentIndex
        
        if (!isActive && isOutgoing !== true) {
            incrementConversationUnread(peer)
            logDebug("Unread", "Incremented unread count for " + peer)
        }
        
        if (isOutgoing !== true) {
            playSoundIfAllowed(privateMessageSound)
        }
    }
    
    function resetState() {
        messagesModel.clear()
        usersModel.clear()
        totalUserCount = 0
        publicTypingUsers = []
        privateTypingStates = ({})
        userAvatars = ({})
        
        // Clear private conversations
        while (conversationTabsModel.count > 1) {
            conversationTabsModel.remove(1)
        }
        
        var keys = Object.keys(privateMessageModels)
        for (var i = 0; i < keys.length; ++i) {
            var key = keys[i]
            if (privateMessageModels[key]) {
                privateMessageModels[key].destroy()
            }
        }
        privateMessageModels = ({})
        conversationPages = ({})
        privateDrafts = ({})
        privatePendingFiles = ({})
        messageIndexById = ({})
    }
    
    // ========== BACKGROUND ==========
    Rectangle {
        anchors.fill: parent
        
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.gradientTop }
            GradientStop { position: 1.0; color: Theme.gradientBottom }
        }
        
        // Animated aurora glows
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
                        to: parent.width - 160
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
                        to: parent.height - 140
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
    }
    
    // ========== MAIN CONTENT ==========
    Item {
        id: contentRoot
        anchors.fill: parent
        opacity: 0
        y: 16
        
        ParallelAnimation {
            running: true
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
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 26
            
            // Header
            Header {
                Layout.fillWidth: true
                Layout.preferredHeight: 132
                
                username: chatClient.username
                connectionState: chatClient.connectionState
                soundsEnabled: window.soundsEnabled
                
                onRegisterClicked: function(username) {
                    chatClient.register(username)
                }
                
                onDisconnectClicked: chatClient.disconnect()
                
                onAvatarClicked: {
                    // Open file dialog for avatar
                    console.log("Avatar selection not yet implemented")
                }
                
                onSoundToggled: {
                    window.soundsEnabled = !window.soundsEnabled
                }
            }
            
            // Main content row
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 22
                
                // Chat panel
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    Rectangle {
                        anchors.fill: parent
                        radius: Theme.radius_xxl
                        border.color: Theme.outline
                        border.width: 1
                        
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: Theme.panel }
                            GradientStop { position: 1.0; color: Theme.surface }
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 28
                            spacing: Theme.spacing_lg
                            
                            ConversationTabs {
                                id: conversationTabBar
                                Layout.fillWidth: true
                                model: conversationTabsModel
                                
                                onTabCloseRequested: function(key) {
                                    closePrivateConversation(key)
                                }
                                
                                onCurrentIndexChanged: {
                                    if (currentIndex >= 0 && currentIndex < conversationTabsModel.count) {
                                        var tab = conversationTabsModel.get(currentIndex)
                                        clearConversationUnread(tab.key)
                                    }
                                }
                            }
                            
                            StackLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                currentIndex: conversationTabBar.currentIndex
                                
                                Repeater {
                                    model: conversationTabsModel
                                    
                                    delegate: Loader {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        
                                        required property string key
                                        required property string title
                                        required property bool isPrivate
                                        
                                        sourceComponent: isPrivate 
                                            ? privateChatComponent 
                                            : publicChatComponent
                                        
                                        onLoaded: {
                                            if (isPrivate) {
                                                item.setup(key, title)
                                                item.messagesModel = ensurePrivateModel(key)
                                            } else {
                                                item.setup()
                                                item.messagesModel = messagesModel
                                            }
                                            conversationPages[key] = item
                                        }
                                    }
                                }
                            }
                        }
                    }
                
                // User list panel
                UserList {
                    Layout.preferredWidth: 260
                    Layout.fillHeight: true
                    
                    model: usersModel
                    userCount: window.totalUserCount
                    
                    onUserClicked: function(username) {
                        openPrivateConversation(username)
                    }
                    
                    function getAvatarSource(username) {
                        return avatarSourceFor(username)
                    }
                }
            }
        }
    }
    
    // ========== TOAST NOTIFICATION ==========
    Toast {
        id: toast
    }
    
    // ========== PAGE COMPONENTS ==========
    Component {
        id: publicChatComponent
        
        PublicChatPage {
            userCount: window.totalUserCount
            typingUsers: window.publicTypingUsers
            pendingFile: window.publicPendingFile
            draft: window.publicDraft
            
            onSendMessage: function(text, filePath) {
                chatClient.sendMessageWithAttachment(text, filePath)
                window.publicDraft = ""
                window.publicPendingFile = null
            }
            
            onFileSelected: function(filePath) {
                var meta = chatClient.inspectFile(filePath)
                if (meta && meta.path) {
                    window.publicPendingFile = meta
                }
            }
            
            onTypingStateChanged: function(isTyping) {
                chatClient.indicatePublicTyping(isTyping)
            }
            
            onCopyRequested: function(text) {
                chatClient.copyToClipboard(text)
            }
        }
    }
    
    Component {
        id: privateChatComponent
        
        PrivateChatPage {
            onSendMessage: function(text, filePath) {
                if (peerKey.length > 0) {
                    chatClient.sendPrivateMessageWithAttachment(peerKey, text, filePath)
                    privateDrafts[peerKey] = ""
                    privatePendingFiles[peerKey] = null
                }
            }
            
            onFileSelected: function(filePath) {
                var meta = chatClient.inspectFile(filePath)
                if (meta && meta.path && peerKey.length > 0) {
                    privatePendingFiles[peerKey] = meta
                    pendingFile = meta
                }
            }
            
            onTypingStateChanged: function(isTyping) {
                if (peerKey.length > 0) {
                    chatClient.indicatePrivateTyping(peerKey, isTyping)
                }
            }
            
            onCopyRequested: function(text) {
                chatClient.copyToClipboard(text)
            }
        }
    }
    
    // ========== BACKEND CONNECTIONS ==========
    Connections {
        target: chatClient
        
        function onMessageReceivedEx(username, message, file, timestamp) {
            messagesModel.append({
                "user": username,
                "text": message,
                "timestamp": formatTimestamp(timestamp),
                "isPrivate": false,
                "isOutgoing": false,
                "displayContext": username,
                "status": "",
                "fileName": file && file.filename ? file.filename : (file && file.name ? file.name : ""),
                "fileMime": file && file.mime ? file.mime : "",
                "fileData": file && file.data ? file.data : "",
                "fileSize": file && file.size ? Number(file.size) : 0,
                "transferId": file && file.transfer_id ? String(file.transfer_id) : ""
            })
            
            if (username !== chatClient.username) {
                playSoundIfAllowed(publicMessageSound)
            }
        }
        
        function onPrivateMessageReceivedEx(sender, recipient, message, messageId, status, file, timestamp) {
            var peer = sender
            appendPrivateMessage(peer, sender, message, false, messageId, status, file, formatTimestamp(timestamp))
        }
        
        function onPrivateMessageSentEx(sender, recipient, message, messageId, status, file, timestamp) {
            var peer = recipient
            appendPrivateMessage(peer, sender, message, true, messageId, status, file, formatTimestamp(timestamp))
        }
        
        function onUsersUpdated(users) {
            usersModel.clear()
            window.totalUserCount = users.length
            
            for (var i = 0; i < users.length; i++) {
                if (users[i] !== chatClient.username) {
                    usersModel.append({"name": users[i]})
                }
            }
        }
        
        function onAvatarsUpdated(avatars) {
            window.userAvatars = avatars || ({})
        }
        
        function onDisconnected(userRequested) {
            resetState()
            
            if (userRequested) {
                messagesModel.append({
                    "user": "System",
                    "text": "Disconnected from server",
                    "timestamp": formatTimestamp(""),
                    "isPrivate": false,
                    "isOutgoing": false,
                    "displayContext": "System",
                    "status": "",
                    "fileName": "",
                    "fileMime": "",
                    "fileData": "",
                    "fileSize": 0
                })
            } else {
                messagesModel.append({
                    "user": "System",
                    "text": "Connection lost. Attempting to reconnect...",
                    "timestamp": formatTimestamp(""),
                    "isPrivate": false,
                    "isOutgoing": false,
                    "displayContext": "System",
                    "status": "",
                    "fileName": "",
                    "fileMime": "",
                    "fileData": "",
                    "fileSize": 0
                })
            }
        }
        
        function onReconnected() {
            messagesModel.append({
                "user": "System",
                "text": "✓ Reconnected successfully!",
                "timestamp": formatTimestamp(""),
                "isPrivate": false,
                "isOutgoing": false,
                "displayContext": "System",
                "status": "",
                "fileName": "",
                "fileMime": "",
                "fileData": "",
                "fileSize": 0
            })
        }
        
        function onErrorReceived(message) {
            toast.show(message, true)
        }
        
        function onGeneralHistoryReceived(history) {
            messagesModel.clear()
            if (!history) return
            
            for (var i = 0; i < history.length; ++i) {
                var entry = history[i]
                if (!entry) continue
                
                messagesModel.append({
                    "user": entry.username || "Unknown",
                    "text": entry.message || "",
                    "timestamp": formatTimestamp(entry.timestamp || ""),
                    "isPrivate": false,
                    "isOutgoing": false,
                    "displayContext": entry.username || "Unknown",
                    "status": "",
                    "fileName": entry.file && entry.file.filename ? entry.file.filename : (entry.file && entry.file.name ? entry.file.name : ""),
                    "fileMime": entry.file && entry.file.mime ? entry.file.mime : "",
                    "fileData": entry.file && entry.file.data ? entry.file.data : "",
                    "fileSize": entry.file && entry.file.size ? Number(entry.file.size) : 0,
                    "transferId": entry.file && entry.file.transfer_id ? String(entry.file.transfer_id) : ""
                })
            }
        }
    }
    
    // ========== MODELS ==========
    ListModel {
        id: conversationTabsModel
        ListElement { key: "public"; title: "Salon feed"; isPrivate: false; hasUnread: false; unreadCount: 0 }
    }
    ListModel { id: messagesModel }
    ListModel { id: usersModel }
}