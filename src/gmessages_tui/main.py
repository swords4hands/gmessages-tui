from .app import GMessagesApp
from .browser import BrowserBridge


def main() -> None:
    bridge = BrowserBridge()
    bridge.start()
    try:
        app = GMessagesApp(bridge)
        app.run()
    finally:
        bridge.stop()


if __name__ == "__main__":
    main()
