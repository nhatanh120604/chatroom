// styles/Theme.qml
pragma Singleton
import QtQuick 2.15

QtObject {
    id: theme
    
    // ========== COLORS ==========
    readonly property color window: "#090C12"
    readonly property color gradientTop: "#111927"
    readonly property color gradientBottom: "#07090D"
    readonly property color panel: "#121A26"
    readonly property color surface: "#152033"
    readonly property color card: "#1A2738"
    readonly property color canvas: "#1F2D40"
    readonly property color accent: "#E0C184"
    readonly property color accentSoft: "#26E0C184"
    readonly property color accentBold: "#F3DCA3"
    readonly property color textPrimary: "#F4F7FB"
    readonly property color textSecondary: "#A5AEC1"
    readonly property color outline: "#222E42"
    readonly property color success: "#35A57C"
    readonly property color warning: "#CE6C6C"
    
    // Avatar default gradient
    readonly property var avatarDefault: ({
        top: "#6DE5AE",
        bottom: "#2C9C6D"
    })
    
    // ========== TYPOGRAPHY ==========
    readonly property real fontScale: 1.12
    
    function scaleFont(size) {
        return Math.round(size * fontScale)
    }
    
    readonly property string emojiFont: {
        if (Qt.platform.os === "windows") return "Segoe UI Emoji"
        if (Qt.platform.os === "osx") return "Apple Color Emoji"
        return "Noto Color Emoji, Noto Emoji, Symbola, DejaVu Sans"
    }
    
    // ========== SPACING ==========
    readonly property int spacing_xs: 4
    readonly property int spacing_sm: 8
    readonly property int spacing_md: 12
    readonly property int spacing_lg: 16
    readonly property int spacing_xl: 20
    readonly property int spacing_xxl: 24
    readonly property int spacing_xxxl: 32
    
    // ========== BORDER RADIUS ==========
    readonly property int radius_sm: 8
    readonly property int radius_md: 16
    readonly property int radius_lg: 20
    readonly property int radius_xl: 24
    readonly property int radius_xxl: 28
    
    // ========== ANIMATION DURATIONS ==========
    readonly property int duration_fast: 150
    readonly property int duration_normal: 220
    readonly property int duration_slow: 320
    
    // ========== SHADOWS ==========
    readonly property var shadow_sm: ({
        horizontalOffset: 0,
        verticalOffset: 4,
        blur: 12,
        color: "#18000000"
    })
    
    readonly property var shadow_md: ({
        horizontalOffset: 0,
        verticalOffset: 8,
        blur: 24,
        color: "#22000000"
    })
    
    readonly property var shadow_lg: ({
        horizontalOffset: 0,
        verticalOffset: 18,
        blur: 36,
        color: "#28000000"
    })
}