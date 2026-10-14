from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from .browser import BrowserBridge
from .state import BrowserSnapshot


class GMessagesApp(App[None]):
    CSS = """
    Screen {
        layout: vertical;
    }

    #status {
        padding: 1;
        height: 5;
        border: solid $accent;
    }

    #threads {
        border: round $panel;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("o", "open_messages", "Open Messages"),
    ]

    def __init__(self, bridge: BrowserBridge) -> None:
        super().__init__()
        self.bridge = bridge

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield Static("Starting browser bridge...", id="status")
            yield ListView(id="threads")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_snapshot()

    def action_open_messages(self) -> None:
        self.bridge.ensure_messages_page()
        self.refresh_snapshot()

    def action_refresh(self) -> None:
        self.refresh_snapshot()

    def refresh_snapshot(self) -> None:
        snapshot = self.bridge.snapshot()
        self._render_snapshot(snapshot)

    def _render_snapshot(self, snapshot: BrowserSnapshot) -> None:
        status = self.query_one("#status", Static)
        threads = self.query_one("#threads", ListView)

        auth_text = "connected" if snapshot.authenticated else "waiting for login"
        status.update(
            "\n".join(
                [
                    f"Page: {snapshot.title}",
                    f"URL: {snapshot.url}",
                    f"Session: {auth_text}",
                    f"Threads parsed: {len(snapshot.conversations)}",
                ]
            )
        )

        threads.clear()
        if not snapshot.conversations:
            threads.append(ListItem(Label("No conversations parsed yet.")))
            return

        for conversation in snapshot.conversations:
            unread_prefix = "* " if conversation.unread else ""
            text = f"{unread_prefix}{conversation.title}"
            if conversation.snippet:
                text = f"{text} | {conversation.snippet}"
            threads.append(ListItem(Label(text)))
