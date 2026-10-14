from dataclasses import dataclass, field


@dataclass(slots=True)
class ConversationSummary:
    title: str
    snippet: str = ""
    unread: bool = False


@dataclass(slots=True)
class BrowserSnapshot:
    title: str
    url: str
    authenticated: bool
    conversations: list[ConversationSummary] = field(default_factory=list)
