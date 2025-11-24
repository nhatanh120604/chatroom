import sys
import os
import logging
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from client.core.client import ChatClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Application entry point."""
    logger.info("Starting chat client application")
    
    # Set default Qt style
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    
    # Create application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Create and expose chat client to QML
    chat = ChatClient()
    engine.rootContext().setContextProperty("chatClient", chat)
    
    # Load QML
    base = os.path.dirname(__file__)
    qml_path = os.path.join(base, "qml", "Main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))
    
    # Graceful shutdown
    app.aboutToQuit.connect(chat.disconnect)
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        return -1
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())