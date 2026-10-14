"""Selector candidates for Google Messages Web.

These are intentionally conservative. Google Messages is a moving SPA, so the
right long-term approach is to inspect the production DOM and evolve these lists
as breakages are found.
"""

THREAD_CANDIDATES = (
    "[data-e2e-conversation-id]",
    "[data-conversation-id]",
    "mws-conversation-list-item",
    '[role="listitem"]',
)

TITLE_CANDIDATES = (
    "[data-e2e-conversation-title]",
    ".title",
    "h3",
    '[data-e2e-username]',
)

SNIPPET_CANDIDATES = (
    "[data-e2e-last-message-text]",
    ".snippet",
    ".text-content",
)

UNREAD_CANDIDATES = (
    "[aria-label*='unread']",
    "[data-e2e-unread-count]",
    ".unread",
)
