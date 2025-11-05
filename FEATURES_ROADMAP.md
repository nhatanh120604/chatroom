# 🚀 Aurora Chat - Feature Implementation Roadmap

## Overview
This document outlines the implementation plan for **5 high-priority features** to enhance Aurora Chat's user experience. Each feature is designed to be production-ready and integrate seamlessly with the existing codebase.

**Target Features:**
1. Connection Status Indicator
2. Copy Message Text
3. Notification Sounds
4. Unread Message Counter
5. Message Search

**Estimated Timeline:** 2-3 weeks  
**Difficulty Level:** Easy to Medium  
**Impact:** High - Significantly improves usability

---

## 📋 Codebase Architecture Summary

### Current Structure
```
client/
├── client.py              # ChatClient class (QObject with Signals/Slots)
├── crypto_utils.py        # Encryption utilities
├── qml/
│   └── Main.qml          # UI (2892 lines, PySide6/Qt Quick)
└── assets/
    ├── emoji_icon.svg
    └── file_icon.svg

server/
└── server.py             # Flask-SocketIO server
```

### Key Components

**Client-Side (Python):**
- `ChatClient` class extends `QObject`
- Uses `Signal`/`Slot` for Qt communication
- Socket.IO client for real-time messaging
- Threading for reconnection logic

**UI (QML):**
- Main window: `ApplicationWindow` (920x600)
- Dark theme palette with accent colors
- Tab-based conversations (`conversationTabsModel`)
- Message list with delegates (`messageDelegateComponent`)
- Already has `hasUnread` boolean per conversation

**Server-Side (Python):**
- Flask + Socket.IO
- In-memory storage (clients, messages, avatars)
- Thread-safe with locks
- Events: `message`, `private_message`, `typing`, etc.

---

## Feature 1️⃣: Connection Status Indicator ✅ COMPLETED

### 🎯 Goal
Display a persistent, visual indicator showing the current connection state (Connected, Reconnecting, Offline) in the UI header.

### 📍 Current State Analysis
- Client already emits signals: `disconnected`, `reconnecting(int)`, `reconnected`
- Connection state tracked in `client.py`: `_connected`, `_connecting`, `_reconnect_attempts`
- QML already handles these signals in lines 2792-2847

### ✅ Implementation Completed

**Changes made:**

1. **client/client.py** - Added connection state tracking:
   - Added `connectionStateChanged` Signal (line 69)
   - Added `_connection_state` property initialization (line 117)
   - Added `connectionState` Property and `_set_connection_state()` method (lines 1276-1283)
   - Updated `connect()` handler to set state to "connected" (line 135)
   - Updated `disconnect()` handler to set state to "offline" (line 183)
   - Updated `_reconnection_loop()` to set state to "reconnecting" (line 470)

2. **client/qml/Main.qml** - Added visual indicator:
   - Added Connection Status Indicator component in header (lines 651-731)
   - Displays color-coded status (green/yellow/gray)
   - Pulsing animation during reconnection
   - Tooltip on hover with status details

### 🛠 Implementation Plan

#### **Step 1: Add Connection State Property to Client** (client.py)
**File:** `client/client.py`  
**Location:** After line 68 (after `avatarsUpdated` signal)

```python
# Add new signal
connectionStateChanged = Signal(str)  # "connected", "reconnecting", "offline"
```

**Location:** In `__init__` method (around line 90)
```python
self._connection_state = "offline"  # Track state
```

**Location:** Add property getter/setter (around line 1260, before `if __name__ == "__main__"`)
```python
@Property(str, notify=connectionStateChanged)
def connectionState(self):
    return self._connection_state

def _set_connection_state(self, state):
    if self._connection_state != state:
        self._connection_state = state
        self.connectionStateChanged.emit(state)
```

#### **Step 2: Update Connection State in Event Handlers**

**Location:** In `connect()` handler (line ~127)
```python
def connect():
    print("Connected")
    self._connected = True
    self._connecting = False
    self._set_connection_state("connected")  # ADD THIS
    # ... rest of code
```

**Location:** In `disconnect()` handler (line ~180)
```python
def disconnect():
    print("Disconnected from server")
    self._connected = False
    self._set_connection_state("offline")  # ADD THIS
    # ... rest of code
```

**Location:** In `_reconnection_loop()` (line ~456)
```python
self._set_connection_state("reconnecting")  # ADD at start of loop
self.reconnecting.emit(self._reconnect_attempts)
```

#### **Step 3: Create Status Indicator Component in QML**

**File:** `client/qml/Main.qml`  
**Location:** After line 650 (in the header section, before the tabbed interface)

Add this component:
```qml
// Connection Status Indicator
Rectangle {
    Layout.preferredWidth: 140
    Layout.preferredHeight: 32
    radius: 16
    border.width: 1
    border.color: {
        if (chatClient.connectionState === "connected") return palette.success
        if (chatClient.connectionState === "reconnecting") return palette.warning
        return palette.outline
    }
    color: "transparent"
    
    Row {
        anchors.centerIn: parent
        spacing: 8
        
        Rectangle {
            width: 8
            height: 8
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: {
                if (chatClient.connectionState === "connected") return palette.success
                if (chatClient.connectionState === "reconnecting") return palette.warning
                return palette.textSecondary
            }
            
            // Pulse animation for reconnecting
            SequentialAnimation on opacity {
                running: chatClient.connectionState === "reconnecting"
                loops: Animation.Infinite
                PropertyAnimation { to: 0.3; duration: 600 }
                PropertyAnimation { to: 1.0; duration: 600 }
            }
        }
        
        Text {
            text: {
                if (chatClient.connectionState === "connected") return "Connected"
                if (chatClient.connectionState === "reconnecting") return "Reconnecting"
                return "Offline"
            }
            color: palette.textPrimary
            font.pixelSize: window.scaleFont(12)
            font.bold: true
        }
    }
    
    MouseArea {
        id: statusTooltipArea
        anchors.fill: parent
        hoverEnabled: true
    }
    
    // Tooltip
    Rectangle {
        visible: statusTooltipArea.containsMouse
        color: palette.panel
        border.color: palette.outline
        border.width: 1
        radius: 6
        width: tooltipText.width + 16
        height: tooltipText.height + 12
        x: parent.width / 2 - width / 2
        y: parent.height + 8
        z: 1000
        
        Text {
            id: tooltipText
            anchors.centerIn: parent
            text: {
                if (chatClient.connectionState === "connected") 
                    return "Connected to server"
                if (chatClient.connectionState === "reconnecting") 
                    return "Attempting to reconnect..."
                return "Not connected to server"
            }
            color: palette.textSecondary
            font.pixelSize: window.scaleFont(11)
        }
    }
}
```

#### **Step 4: Testing Checklist**
- [ ] Status shows "Connected" when connected
- [ ] Status shows "Reconnecting" with pulsing dot during reconnection
- [ ] Status shows "Offline" when disconnected
- [ ] Tooltip appears on hover
- [ ] Color changes match state (green/yellow/gray)
- [ ] Animations work smoothly

#### **Estimated Time:** 2-3 hours
#### **Difficulty:** Easy ⭐

---

## Feature 2️⃣: Copy Message Text ✅ COMPLETED

### 🎯 Goal
Allow users to right-click (or long-press) any message and copy its text content to clipboard.

### 📍 Current State Analysis
- Messages rendered via `messageDelegateComponent` (line 2252)
- Each message has `model.text`, `model.user`, `model.fileName`
- QML supports `MouseArea` for context menus
- Qt provides `Clipboard` API via `Qt.application.clipboard`

### ✅ Implementation Completed

**Changes made:**

1. **client/qml/Main.qml** - Added copy functionality:
   - Added `copyToClipboard()` function (lines 168-173)
   - Added right-click MouseArea to message delegate (lines 2625-2641)
   - Added styled context menu component at end of file (lines 3002-3067)
   - Menu includes 3 options:
     - "Copy Message" - Copies message text only
     - "Copy with Username" - Copies "username: message"
     - "Copy Filename" - Copies filename (only shown for file messages)

### 🛠 Implementation Plan

#### **Step 1: Add Copy Function to Main Window**

**File:** `client/qml/Main.qml`  
**Location:** Add to window's functions section (around line 150)

```qml
function copyToClipboard(text) {
    if (!text || text.length === 0) {
        return
    }
    Qt.application.clipboard.text = text
    // Optional: Show brief notification
    console.log("Copied to clipboard:", text.substring(0, 50))
}
```

#### **Step 2: Add Context Menu to Message Delegate**

**File:** `client/qml/Main.qml`  
**Location:** In `messageDelegateComponent`, after the message bubble (around line 2400)

Add this at the end of the `Column` (messageContainer), before the closing brace:

```qml
// Context Menu for copying
MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    propagateComposedEvents: true
    z: -1  // Don't block file downloads or other interactions
    
    onClicked: {
        if (mouse.button === Qt.RightButton) {
            contextMenu.messageText = model.text || ""
            contextMenu.userName = model.user || ""
            contextMenu.hasText = (model.text && model.text.length > 0)
            contextMenu.hasFile = (model.fileName && model.fileName.length > 0)
            contextMenu.fileName = model.fileName || ""
            contextMenu.popup()
        }
    }
}
```

#### **Step 3: Create Context Menu Component**

**File:** `client/qml/Main.qml`  
**Location:** At the end of the file, before final closing braces (around line 2890)

```qml
// Add this import at the top if not present
// import QtQuick.Controls 2.15

Menu {
    id: contextMenu
    
    property string messageText: ""
    property string userName: ""
    property bool hasText: false
    property bool hasFile: false
    property string fileName: ""
    
    MenuItem {
        text: "Copy Message"
        enabled: contextMenu.hasText
        onTriggered: {
            window.copyToClipboard(contextMenu.messageText)
        }
    }
    
    MenuItem {
        text: "Copy with Username"
        enabled: contextMenu.hasText
        onTriggered: {
            var fullText = contextMenu.userName + ": " + contextMenu.messageText
            window.copyToClipboard(fullText)
        }
    }
    
    MenuSeparator {
        visible: contextMenu.hasFile
    }
    
    MenuItem {
        text: "Copy Filename"
        visible: contextMenu.hasFile
        enabled: contextMenu.hasFile
        onTriggered: {
            window.copyToClipboard(contextMenu.fileName)
        }
    }
}
```

#### **Step 4: Style the Context Menu (Optional but Recommended)**

Add custom styling to match Aurora theme:

```qml
Menu {
    id: contextMenu
    // ... properties from above ...
    
    background: Rectangle {
        color: window.palette.panel
        border.color: window.palette.outline
        border.width: 1
        radius: 8
    }
    
    delegate: MenuItem {
        id: menuItem
        
        contentItem: Text {
            text: menuItem.text
            color: menuItem.enabled ? window.palette.textPrimary : window.palette.textSecondary
            font.pixelSize: window.scaleFont(13)
            opacity: menuItem.enabled ? 1.0 : 0.5
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
        }
        
        background: Rectangle {
            color: menuItem.highlighted ? window.palette.surface : "transparent"
            radius: 4
        }
        
        height: 32
        padding: 8
    }
}
```

#### **Step 5: Testing Checklist**
- [ ] Right-click on text message shows menu
- [ ] "Copy Message" copies text to clipboard
- [ ] "Copy with Username" includes username
- [ ] "Copy Filename" appears only for file messages
- [ ] Menu styled correctly with dark theme
- [ ] Works on both public and private messages
- [ ] Clipboard actually contains the text (test with Ctrl+V)

#### **Estimated Time:** 2-3 hours
#### **Difficulty:** Easy ⭐

---

## Feature 3️⃣: Notification Sounds ✅ COMPLETED

### 🎯 Goal
Play sound notifications for new messages (public/private) with a toggle to enable/disable.

### 📍 Current State Analysis
- QML supports `SoundEffect` from `QtMultimedia`
- Client emits `messageReceived` and `privateMessageReceivedEx` signals
- No existing sound assets in `client/assets/`

### ✅ Implementation Completed

**Changes made:**

1. **client/qml/Main.qml** - Added QtMultimedia import:
   - Added `import QtMultimedia` at line 5

2. **client/qml/Main.qml** - Added sound properties (lines 69-72):
   - `soundsEnabled: true` - Toggle for enabling/disabling notifications
   - `lastSoundTime: new Date(0)` - For debouncing
   - `soundDebounceMs: 500` - Minimum 500ms between sounds

3. **client/qml/Main.qml** - Added debouncing function (lines 183-191):
   - `playSoundIfAllowed(soundEffect)` - Checks soundsEnabled and debounces
   - Prevents sound spam when receiving rapid messages
   - Updates lastSoundTime after playing

4. **client/qml/Main.qml** - Added SoundEffect components (lines 1233-1268):
   - `publicMessageSound`: source="../assets/notification_message.mp3", volume 0.5
   - `privateMessageSound`: source="../assets/notification_private.mp3", volume 0.6
   - Both with error handling (console.warn if status === SoundEffect.Error)
   - **Note:** Sound files are .mp3 format (not .wav)

5. **client/qml/Main.qml** - Added sound toggle button in header (lines 790-846):
   - ToolButton with 🔔 (enabled) / 🔕 (muted) emoji
   - Positioned right after Connection Status Indicator
   - Hover effect with background highlight
   - Tooltip showing "Mute notifications" / "Unmute notifications"
   - Toggles soundsEnabled property on click

6. **client/qml/Main.qml** - Updated message handlers to play sounds:
   - `onMessageReceived` (lines 2917-2920): Plays publicMessageSound if username !== chatClient.username
   - `appendPrivateMessage` (lines 397-400): Plays privateMessageSound if isOutgoing !== true
   - Ensures sounds only play for messages from others, not own messages

**Sound Files Required:**
- `client/assets/notification_message.mp3` (public messages)
- `client/assets/notification_private.mp3` (private messages)

**Features:**
- ✅ Distinct sounds for public and private messages
- ✅ Volume calibration (private 0.6, public 0.5)
- ✅ Toggle button with emoji indicator
- ✅ Sound debouncing (500ms minimum between plays)
- ✅ No sounds for own messages
- ✅ Graceful error handling for missing sound files
- ✅ Hover tooltips for user guidance

### 🛠 Implementation Plan

#### **Step 1: Add Sound Files**

**Download/Create Sound Files:**
- Download free notification sounds from [Freesound.org](https://freesound.org) or [Zapsplat](https://www.zapsplat.com)
- Recommended: Short (0.3-0.5s), pleasant "ding" or "pop" sounds
- Format: `.wav` or `.mp3` (WAV preferred for instant playback)

**File Structure:**
```
client/assets/
├── emoji_icon.svg
├── file_icon.svg
├── notification_message.wav      # ADD THIS (public message)
└── notification_private.wav      # ADD THIS (private message)
```

**Alternatively, use QML's system sound:**
```qml
// Can use built-in sounds without files
SoundEffect {
    source: "qrc:/qt-project.org/imports/QtQuick/Controls/sounds/notification.wav"
}
```

#### **Step 2: Add Sound Settings Property**

**File:** `client/qml/Main.qml`  
**Location:** In window properties (around line 70)

```qml
property bool soundsEnabled: true  // Can be persisted to settings later
property bool soundsForPrivateOnly: false  // Optional: only private messages
```

#### **Step 3: Create Sound Effect Components**

**File:** `client/qml/Main.qml`  
**Location:** Before the main UI components (around line 430, after functions)

Add these components:

```qml
// Sound Effects (requires: import QtMultimedia)
SoundEffect {
    id: publicMessageSound
    source: Qt.resolvedUrl("../assets/notification_message.wav")
    volume: 0.5
    
    // Fallback if file doesn't exist
    Component.onCompleted: {
        if (status === SoundEffect.Error) {
            console.warn("Public message sound not loaded")
        }
    }
}

SoundEffect {
    id: privateMessageSound
    source: Qt.resolvedUrl("../assets/notification_private.wav")
    volume: 0.6  // Slightly louder for private
    
    Component.onCompleted: {
        if (status === SoundEffect.Error) {
            console.warn("Private message sound not loaded")
        }
    }
}
```

#### **Step 4: Play Sounds on Message Receipt**

**File:** `client/qml/Main.qml`  
**Location:** In `Connections` block for `chatClient` (around line 2792)

**Find the existing handlers and modify them:**

```qml
function onMessageReceived(username, message, filePayload) {
    // ... existing code to append message ...
    
    // ADD THIS: Play sound if not your own message
    if (window.soundsEnabled && username !== chatClient.username) {
        if (!window.soundsForPrivateOnly) {
            publicMessageSound.play()
        }
    }
}

function onPrivateMessageReceivedEx(sender, recipient, message, messageId, status, filePayload, timestamp) {
    // ... existing code to append message ...
    
    // ADD THIS: Play sound for incoming private messages
    if (window.soundsEnabled && sender !== chatClient.username) {
        privateMessageSound.play()
    }
}
```

#### **Step 5: Add Sound Toggle Button**

**File:** `client/qml/Main.qml`  
**Location:** In header section, next to connection status (around line 650)

```qml
// Sound Toggle Button
ToolButton {
    Layout.preferredWidth: 40
    Layout.preferredHeight: 40
    
    contentItem: Text {
        text: window.soundsEnabled ? "🔔" : "🔕"
        font.pixelSize: window.scaleFont(18)
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    background: Rectangle {
        radius: 20
        color: parent.hovered ? window.palette.surface : "transparent"
        border.color: window.palette.outline
        border.width: 1
    }
    
    onClicked: {
        window.soundsEnabled = !window.soundsEnabled
    }
    
    MouseArea {
        id: soundTooltipArea
        anchors.fill: parent
        hoverEnabled: true
        propagateComposedEvents: true
        onPressed: mouse.accepted = false
    }
    
    // Tooltip
    Rectangle {
        visible: soundTooltipArea.containsMouse
        color: palette.panel
        border.color: palette.outline
        border.width: 1
        radius: 6
        width: soundTooltipText.width + 16
        height: soundTooltipText.height + 12
        x: parent.width / 2 - width / 2
        y: parent.height + 8
        z: 1000
        
        Text {
            id: soundTooltipText
            anchors.centerIn: parent
            text: window.soundsEnabled ? "Mute notifications" : "Unmute notifications"
            color: palette.textSecondary
            font.pixelSize: window.scaleFont(11)
        }
    }
}
```

#### **Step 6: Add Import Statement**

**File:** `client/qml/Main.qml`  
**Location:** At the very top (around line 1-5)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 6.6
import QtMultimedia          // ADD THIS LINE
import Qt.labs.platform 1.1 as Platform
```

#### **Step 7: Optional - Prevent Sound Spam**

Add debouncing to prevent multiple sounds at once:

**Location:** In window properties
```qml
property var lastSoundTime: new Date(0)
property int soundDebounceMs: 500  // Min 500ms between sounds

function playSoundIfAllowed(soundEffect) {
    var now = new Date()
    if (now - lastSoundTime > soundDebounceMs) {
        soundEffect.play()
        lastSoundTime = now
    }
}
```

Then use `window.playSoundIfAllowed(publicMessageSound)` instead of direct `.play()`

#### **Step 8: Testing Checklist**
- [ ] Import QtMultimedia doesn't cause errors
- [ ] Sound files load successfully (check console)
- [ ] Public messages play sound (only for others' messages)
- [ ] Private messages play sound (only for incoming)
- [ ] Toggle button mutes/unmutes correctly
- [ ] Sounds don't play when window is focused on active conversation (optional)
- [ ] Volume is appropriate (not too loud)
- [ ] No sound spam (debouncing works)

#### **Estimated Time:** 3-4 hours (including finding/creating sounds)
#### **Difficulty:** Easy-Medium ⭐⭐

---

## Feature 4️⃣: Unread Message Counter ✅ COMPLETED

### 🎯 Goal
Display numeric badges showing unread message count on conversation tabs, replacing the simple red dot indicator.

### 📍 Current State Analysis
- Already has `hasUnread` boolean per conversation (line 913)
- Function `setConversationUnread(key, unread)` exists (line 228)
- Conversation tabs use `conversationTabsModel` with properties: `key`, `title`, `isPrivate`, `hasUnread`

### ✅ Implementation Completed

**Changes made:**

1. **client/qml/Main.qml** - Updated conversation model:
   - Added `unreadCount: 0` property to `conversationTabsModel` (line 1210)
   - All new conversations initialize with `unreadCount: 0` (lines 347, 396)

2. **client/qml/Main.qml** - Added unread count management functions (lines 237-260):
   - Updated `setConversationUnread(key, unread)` to clear count when unread is false
   - Added `incrementConversationUnread(key)` - Increments count and sets hasUnread flag
   - Added `clearConversationUnread(key)` - Clears both hasUnread and count

3. **client/qml/Main.qml** - Updated tab delegate with numeric badge (lines 1028-1065):
   - Added `required property int unreadCount` to TabButton delegate
   - Replaced small red dot with numeric badge showing count
   - Badge displays: 1, 2, 3... up to 99+ (for counts over 99)
   - Styled with warning color background, white bold text
   - Auto-sizing based on text width: `Math.max(20, badgeText.width + 10)`

4. **client/qml/Main.qml** - Updated message handlers:
   - `onMessageReceived` (line 2818): Calls `incrementConversationUnread("public")` for inactive tabs
   - `appendPrivateMessage` (line 378): Calls `incrementConversationUnread(peer)` for incoming messages on inactive tabs

5. **client/qml/Main.qml** - Added auto-clear on tab selection (lines 1020-1026):
   - TabBar `onCurrentIndexChanged` handler
   - Automatically calls `clearConversationUnread(tab.key)` when tab is selected
   - Ensures active tabs never show unread count

### 🛠 Implementation Plan

#### **Step 1: Add Unread Count to Conversation Model**

**File:** `client/qml/Main.qml`  
**Location:** Modify `conversationTabsModel` initialization (line 1101)

**Change from:**
```qml
ListModel {
    id: conversationTabsModel
    ListElement {
        key: "public"
        title: "Public Lounge"
        isPrivate: false
        hasUnread: false
    }
}
```

**To:**
```qml
ListModel {
    id: conversationTabsModel
    ListElement {
        key: "public"
        title: "Public Lounge"
        isPrivate: false
        hasUnread: false
        unreadCount: 0  // ADD THIS
    }
}
```

#### **Step 2: Update Conversation Functions**

**File:** `client/qml/Main.qml`  
**Location:** Modify `setConversationUnread` function (around line 228)

**Change from:**
```qml
function setConversationUnread(key, unread) {
    var idx = conversationIndex(key)
    if (idx >= 0) {
        conversationTabsModel.setProperty(idx, "hasUnread", unread)
    }
}
```

**To:**
```qml
function setConversationUnread(key, unread, count) {
    var idx = conversationIndex(key)
    if (idx >= 0) {
        conversationTabsModel.setProperty(idx, "hasUnread", unread)
        conversationTabsModel.setProperty(idx, "unreadCount", count || 0)
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

function clearConversationUnread(key) {
    setConversationUnread(key, false, 0)
}
```

#### **Step 3: Update Message Received Handlers**

**File:** `client/qml/Main.qml`  
**Location:** In message handling functions (around line 2850)

**Find and modify these handlers:**

```qml
function onMessageReceived(username, message, filePayload) {
    messagesModel.append({
        "user": username,
        "text": message,
        // ... rest of properties
    })
    
    // ADD THIS: Increment unread if not on public tab
    var idx = window.conversationIndex("public")
    var isActive = idx === conversationTabBar.currentIndex
    if (!isActive && username !== chatClient.username) {
        window.incrementConversationUnread("public")
    }
    
    // ... rest of code
}

function onPrivateMessageReceivedEx(sender, recipient, message, messageId, status, filePayload, timestamp) {
    var peer = (sender === chatClient.username ? recipient : sender)
    // ... existing code to append message ...
    
    // ADD THIS: Increment unread if not active
    var idx = window.conversationIndex(peer)
    var isActive = idx === conversationTabBar.currentIndex
    if (!isActive && sender !== chatClient.username) {
        window.incrementConversationUnread(peer)
    }
}
```

#### **Step 4: Clear Unread When Tab Selected**

**File:** `client/qml/Main.qml`  
**Location:** In `TabBar` onCurrentIndexChanged (around line 907)

```qml
TabBar {
    id: conversationTabBar
    // ... existing properties ...
    
    onCurrentIndexChanged: {
        // ... existing code ...
        
        // ADD THIS: Clear unread count when tab selected
        if (currentIndex >= 0 && currentIndex < conversationTabsModel.count) {
            var tab = conversationTabsModel.get(currentIndex)
            window.clearConversationUnread(tab.key)
        }
    }
}
```

#### **Step 5: Update Tab Delegate to Show Badge**

**File:** `client/qml/Main.qml`  
**Location:** In `TabButton` delegate (around line 909)

**Find the existing delegate and modify it:**

```qml
delegate: TabButton {
    id: tabButton
    required property int index
    required property string title
    required property bool hasUnread
    required property int unreadCount  // ADD THIS
    
    // ... existing properties ...
    
    contentItem: Row {
        spacing: 8
        
        Text {
            text: tabButton.title
            color: tabButton.index === conversationTabBar.currentIndex 
                   ? window.palette.accentBold 
                   : window.palette.textSecondary
            font.pixelSize: window.scaleFont(13)
            font.bold: tabButton.index === conversationTabBar.currentIndex
            anchors.verticalCenter: parent.verticalCenter
        }
        
        // Unread Badge (REPLACE the old red dot)
        Rectangle {
            visible: tabButton.hasUnread && tabButton.unreadCount > 0
            width: Math.max(20, badgeText.width + 10)
            height: 20
            radius: 10
            color: window.palette.warning
            anchors.verticalCenter: parent.verticalCenter
            
            Text {
                id: badgeText
                anchors.centerIn: parent
                text: tabButton.unreadCount > 99 ? "99+" : tabButton.unreadCount.toString()
                color: window.palette.textPrimary
                font.pixelSize: window.scaleFont(10)
                font.bold: true
            }
        }
    }
    
    // ... rest of delegate code ...
}
```

#### **Step 6: Update New Conversation Creation**

**File:** `client/qml/Main.qml`  
**Location:** Where conversations are created (around line 319, 368)

**Update to include unreadCount:**

```qml
function addOrSelectPrivateConversation(peer) {
    // ... existing code ...
    if (idx === -1) {
        conversationTabsModel.append({
            "key": peer, 
            "title": peer, 
            "isPrivate": true, 
            "hasUnread": false,
            "unreadCount": 0  // ADD THIS
        })
    }
    // ... rest of code
}
```

#### **Step 7: Add Total Unread Counter (Optional)**

Add a total unread count in the window title or header:

```qml
// In window properties (around line 70)
property int totalUnreadCount: 0

function updateTotalUnread() {
    var total = 0
    for (var i = 0; i < conversationTabsModel.count; ++i) {
        total += conversationTabsModel.get(i).unreadCount || 0
    }
    totalUnreadCount = total
}

// Call this whenever unread counts change
// Update incrementConversationUnread:
function incrementConversationUnread(key) {
    var idx = conversationIndex(key)
    if (idx >= 0) {
        var current = conversationTabsModel.get(idx).unreadCount || 0
        conversationTabsModel.setProperty(idx, "unreadCount", current + 1)
        conversationTabsModel.setProperty(idx, "hasUnread", true)
        updateTotalUnread()  // ADD THIS
    }
}

// Update window title (in ApplicationWindow):
title: totalUnreadCount > 0 
       ? "Aurora Chat (" + totalUnreadCount + ")"
       : "Aurora Chat"
```

#### **Step 8: Testing Checklist**
- [ ] Badge shows correct count (1, 2, 3... 99+)
- [ ] Count increments when receiving messages on inactive tabs
- [ ] Count clears when switching to that tab
- [ ] Badge visible only when count > 0
- [ ] Works for both public and private conversations
- [ ] Total unread shows in window title (if implemented)
- [ ] Badge styled correctly (red background, white text)
- [ ] No count increase for own messages

#### **Estimated Time:** 3-4 hours
#### **Difficulty:** Medium ⭐⭐

---

## Feature 5️⃣: Message Search

### 🎯 Goal
Add a search bar to find messages by text content or sender, with highlighting of matches and quick navigation.

### 📍 Current State Analysis
- Messages stored in `messagesModel` (public) and `privateMessageModels[peer]` (private)
- Each message has: `user`, `text`, `fileName`, `timestamp`
- ListView for messages with delegate rendering
- No existing search functionality

### 🛠 Implementation Plan

#### **Step 1: Add Search State Properties**

**File:** `client/qml/Main.qml`  
**Location:** In window properties (around line 70)

```qml
property bool searchMode: false
property string searchQuery: ""
property var searchResults: []
property int currentSearchIndex: -1
```

#### **Step 2: Add Search Function**

**File:** `client/qml/Main.qml`  
**Location:** In window functions (around line 200)

```qml
function performSearch(query) {
    searchResults = []
    currentSearchIndex = -1
    
    if (!query || query.trim().length === 0) {
        return
    }
    
    var lowerQuery = query.toLowerCase()
    var current = conversationTabsModel.get(conversationTabBar.currentIndex)
    if (!current) return
    
    var model = current.isPrivate 
                ? privateMessageModels[current.key] 
                : messagesModel
    
    if (!model) return
    
    // Search through messages
    for (var i = 0; i < model.count; ++i) {
        var msg = model.get(i)
        var text = (msg.text || "").toLowerCase()
        var user = (msg.user || "").toLowerCase()
        var fileName = (msg.fileName || "").toLowerCase()
        
        if (text.includes(lowerQuery) || 
            user.includes(lowerQuery) || 
            fileName.includes(lowerQuery)) {
            searchResults.push({
                index: i,
                user: msg.user,
                text: msg.text,
                timestamp: msg.timestamp
            })
        }
    }
    
    // Auto-select first result
    if (searchResults.length > 0) {
        currentSearchIndex = 0
        scrollToSearchResult(0)
    }
}

function scrollToSearchResult(resultIndex) {
    if (resultIndex < 0 || resultIndex >= searchResults.length) {
        return
    }
    
    var result = searchResults[resultIndex]
    var current = conversationTabsModel.get(conversationTabBar.currentIndex)
    if (!current) return
    
    var page = conversationPages[current.key]
    if (page && page.scrollToIndex) {
        page.scrollToIndex(result.index)
    }
}

function nextSearchResult() {
    if (searchResults.length === 0) return
    currentSearchIndex = (currentSearchIndex + 1) % searchResults.length
    scrollToSearchResult(currentSearchIndex)
}

function previousSearchResult() {
    if (searchResults.length === 0) return
    currentSearchIndex = currentSearchIndex <= 0 
                         ? searchResults.length - 1 
                         : currentSearchIndex - 1
    scrollToSearchResult(currentSearchIndex)
}

function exitSearchMode() {
    searchMode = false
    searchQuery = ""
    searchResults = []
    currentSearchIndex = -1
}
```

#### **Step 3: Add scrollToIndex Method to Message ListView**

**File:** `client/qml/Main.qml`  
**Location:** In the ListView for messages (inside conversation pages, around line 1200)

**Find the ListView and add this method:**

```qml
ListView {
    id: messagesList
    // ... existing properties ...
    
    function scrollToIndex(index) {
        if (index >= 0 && index < count) {
            positionViewAtIndex(index, ListView.Center)
            currentIndex = index
        }
    }
    
    // ... rest of ListView
}

// Make sure to register this in conversationPages:
Component.onCompleted: {
    window.conversationPages[peerKey || "public"] = messagesList
}
```

#### **Step 4: Create Search Bar Component**

**File:** `client/qml/Main.qml`  
**Location:** Add at the top of conversation area (around line 1100, before TabBar)

```qml
// Search Bar
Rectangle {
    id: searchBar
    visible: window.searchMode
    height: visible ? 60 : 0
    Layout.fillWidth: true
    color: window.palette.surface
    border.color: window.palette.outline
    border.width: 1
    
    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // Search Icon
        Text {
            text: "🔍"
            font.pixelSize: window.scaleFont(18)
        }
        
        // Search Input
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            radius: 18
            color: window.palette.panel
            border.color: searchField.activeFocus 
                         ? window.palette.accent 
                         : window.palette.outline
            border.width: 1
            
            TextField {
                id: searchField
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                placeholderText: "Search messages..."
                placeholderTextColor: window.palette.textSecondary
                color: window.palette.textPrimary
                background: null
                selectByMouse: true
                
                onTextChanged: {
                    window.searchQuery = text
                    window.performSearch(text)
                }
                
                onAccepted: {
                    window.nextSearchResult()
                }
                
                Keys.onEscapePressed: {
                    window.exitSearchMode()
                }
            }
        }
        
        // Result Counter
        Text {
            visible: window.searchResults.length > 0
            text: (window.currentSearchIndex + 1) + " / " + window.searchResults.length
            color: window.palette.textSecondary
            font.pixelSize: window.scaleFont(12)
        }
        
        // Previous Button
        ToolButton {
            enabled: window.searchResults.length > 0
            text: "↑"
            font.pixelSize: window.scaleFont(16)
            onClicked: window.previousSearchResult()
            
            background: Rectangle {
                radius: 4
                color: parent.hovered ? window.palette.canvas : "transparent"
            }
        }
        
        // Next Button
        ToolButton {
            enabled: window.searchResults.length > 0
            text: "↓"
            font.pixelSize: window.scaleFont(16)
            onClicked: window.nextSearchResult()
            
            background: Rectangle {
                radius: 4
                color: parent.hovered ? window.palette.canvas : "transparent"
            }
        }
        
        // Close Button
        ToolButton {
            text: "✕"
            font.pixelSize: window.scaleFont(16)
            onClicked: window.exitSearchMode()
            
            background: Rectangle {
                radius: 4
                color: parent.hovered ? window.palette.warning : "transparent"
            }
        }
    }
}
```

#### **Step 5: Add Search Activation Button**

**File:** `client/qml/Main.qml`  
**Location:** In header toolbar (around line 830, near disconnect button)

```qml
ToolButton {
    text: "🔍"
    font.pixelSize: window.scaleFont(18)
    Layout.preferredWidth: 40
    Layout.preferredHeight: 40
    
    onClicked: {
        window.searchMode = !window.searchMode
        if (window.searchMode) {
            searchField.forceActiveFocus()
        }
    }
    
    background: Rectangle {
        radius: 20
        color: parent.hovered || window.searchMode 
               ? window.palette.surface 
               : "transparent"
        border.color: window.palette.outline
        border.width: 1
    }
    
    // Tooltip
    MouseArea {
        id: searchButtonTooltip
        anchors.fill: parent
        hoverEnabled: true
        propagateComposedEvents: true
        onPressed: mouse.accepted = false
    }
    
    Rectangle {
        visible: searchButtonTooltip.containsMouse
        color: palette.panel
        border.color: palette.outline
        border.width: 1
        radius: 6
        width: searchTooltipText.width + 16
        height: searchTooltipText.height + 12
        x: parent.width / 2 - width / 2
        y: parent.height + 8
        z: 1000
        
        Text {
            id: searchTooltipText
            anchors.centerIn: parent
            text: "Search messages (Ctrl+F)"
            color: palette.textSecondary
            font.pixelSize: window.scaleFont(11)
        }
    }
}
```

#### **Step 6: Add Keyboard Shortcut**

**File:** `client/qml/Main.qml`  
**Location:** In ApplicationWindow (around line 430)

```qml
ApplicationWindow {
    // ... existing properties ...
    
    // Keyboard shortcuts
    Shortcut {
        sequence: "Ctrl+F"
        onActivated: {
            window.searchMode = true
            searchField.forceActiveFocus()
        }
    }
    
    Shortcut {
        sequence: "Escape"
        enabled: window.searchMode
        onActivated: {
            window.exitSearchMode()
        }
    }
    
    Shortcut {
        sequence: "F3"
        enabled: window.searchMode
        onActivated: {
            window.nextSearchResult()
        }
    }
    
    Shortcut {
        sequence: "Shift+F3"
        enabled: window.searchMode
        onActivated: {
            window.previousSearchResult()
        }
    }
}
```

#### **Step 7: Highlight Search Results (Optional but Recommended)**

**File:** `client/qml/Main.qml`  
**Location:** In message delegate (around line 2340, where message text is displayed)

**Add highlight property to message text:**

```qml
Text {
    id: messageText
    text: model.text || ""
    // ... existing properties ...
    
    // ADD THIS: Highlight search matches
    property bool isSearchMatch: {
        if (!window.searchMode || !window.searchQuery) return false
        var lowerText = (text || "").toLowerCase()
        var lowerQuery = window.searchQuery.toLowerCase()
        return lowerText.includes(lowerQuery)
    }
    
    Rectangle {
        anchors.fill: parent
        color: window.palette.accent
        opacity: parent.isSearchMatch ? 0.2 : 0.0
        radius: 4
        z: -1
    }
}
```

#### **Step 8: Testing Checklist**
- [ ] Ctrl+F activates search mode
- [ ] Search field appears with animation
- [ ] Typing filters messages in real-time
- [ ] Result counter shows "X / Y"
- [ ] Navigation buttons scroll to matches
- [ ] Enter key goes to next result
- [ ] Escape closes search
- [ ] Matches are highlighted
- [ ] Search works in public and private chats
- [ ] F3 / Shift+F3 shortcuts work
- [ ] Search is case-insensitive
- [ ] Searches username and message text

#### **Estimated Time:** 5-6 hours
#### **Difficulty:** Medium ⭐⭐⭐

---

## 📅 Implementation Timeline

### Week 1: Foundation Features
- **Days 1-2:** Feature 1 - Connection Status Indicator (3 hours)
- **Days 2-3:** Feature 2 - Copy Message Text (3 hours)
- **Days 3-5:** Feature 3 - Notification Sounds (4 hours)

### Week 2: Advanced Features
- **Days 1-3:** Feature 4 - Unread Message Counter (4 hours)
- **Days 4-7:** Feature 5 - Message Search (6 hours)

### Week 3: Testing & Polish
- **Days 1-3:** Integration testing
- **Days 4-5:** Bug fixes and refinements
- **Days 6-7:** Documentation and final review

**Total Estimated Time:** 20-23 hours of active development

---

## 🧪 Testing Strategy

### Unit Testing
- Test each feature independently
- Verify signal/slot connections
- Check property bindings

### Integration Testing
- Test features working together
- Verify no performance degradation
- Check for race conditions

### User Testing
- Test with real usage patterns
- Verify intuitive behavior
- Check accessibility

### Edge Cases
- Empty messages
- Long messages (>1000 chars)
- Rapid message spam
- Network disconnections during search
- Special characters in search

---

## 📦 Deployment Checklist

### Before Merging
- [ ] All features implemented
- [ ] Code reviewed and tested
- [ ] No console errors or warnings
- [ ] Sound files optimized (<50KB each)
- [ ] Performance acceptable (no lag)
- [ ] Cross-platform tested (Windows/Linux/Mac if possible)

### Documentation Updates
- [ ] Update README.md with new features
- [ ] Add keyboard shortcuts section
- [ ] Update screenshots/demo GIF
- [ ] Document sound file requirements

### Version Control
- [ ] Create feature branch
- [ ] Commit with descriptive messages
- [ ] Tag release (v1.1.0)
- [ ] Update CHANGELOG.md

---

## 🚀 Future Enhancements

After completing these 5 features, consider:

1. **Persistent Settings** - Save sound/search preferences
2. **Advanced Search** - Filter by date, user, file type
3. **Message Reactions** - Quick emoji responses
4. **Desktop Notifications** - OS-level notifications when minimized
5. **Dark/Light Theme Toggle** - User preference

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue:** Sounds don't play  
**Solution:** Check QtMultimedia import, verify file paths, check file format (use WAV)

**Issue:** Search is slow with many messages  
**Solution:** Implement search debouncing (wait 300ms after typing stops)

**Issue:** Unread count incorrect  
**Solution:** Ensure all message handlers call `incrementConversationUnread()`

**Issue:** Connection status doesn't update  
**Solution:** Verify `_set_connection_state()` is called in all connection event handlers

---

## ✅ Success Criteria

Features are considered complete when:

1. ✅ All code compiles without errors
2. ✅ All testing checklists passed
3. ✅ Features work on all supported platforms
4. ✅ No performance regression
5. ✅ User feedback is positive
6. ✅ Documentation is updated

---

## 🎯 Summary

This roadmap provides a clear, step-by-step implementation plan for 5 essential features that will significantly enhance Aurora Chat's usability. Each feature is designed to integrate seamlessly with your existing architecture, maintaining code quality and user experience.

**Key Takeaways:**
- Start with easy features (Connection Status, Copy Text)
- Build confidence before tackling complex features (Search)
- Test thoroughly at each step
- Maintain your existing code style and architecture
- Document as you go

Good luck with implementation! 🚀
