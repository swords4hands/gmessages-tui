from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

from .selectors import (
    SNIPPET_CANDIDATES,
    THREAD_CANDIDATES,
    TITLE_CANDIDATES,
    UNREAD_CANDIDATES,
)
from .state import BrowserSnapshot, ConversationSummary


MESSAGES_URL = os.environ.get("GMESSAGES_URL", "https://messages.google.com/web")
PROFILE_DIR = Path(os.environ.get("PLAYWRIGHT_PROFILE_DIR", "./playwright-data"))
HEADLESS = os.environ.get("GMESSAGES_HEADLESS", "false").lower() == "true"


class BrowserBridge:
    def __init__(self) -> None:
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> None:
        if self._context is not None:
            return

        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=HEADLESS,
            viewport={"width": 1440, "height": 1024},
        )
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
        self._page.goto(MESSAGES_URL, wait_until="domcontentloaded")

    def stop(self) -> None:
        if self._context is not None:
            self._context.close()
            self._context = None
            self._page = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def ensure_messages_page(self) -> None:
        page = self.page
        if not page.url.startswith(MESSAGES_URL):
            page.goto(MESSAGES_URL, wait_until="domcontentloaded")

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("BrowserBridge.start() must be called before using the page")
        return self._page

    def snapshot(self) -> BrowserSnapshot:
        self.ensure_messages_page()
        page = self.page
        title = page.title()
        url = page.url
        body = page.locator("body").inner_text(timeout=5_000)
        login_markers = ("Messages for web", "QR code", "Scan the QR code")
        authenticated = not any(marker in body for marker in login_markers)

        conversations = self._read_conversations(page) if authenticated else []
        return BrowserSnapshot(
            title=title,
            url=url,
            authenticated=authenticated,
            conversations=conversations,
        )

    def _read_conversations(self, page: Page) -> list[ConversationSummary]:
        js = """
        ({ threadCandidates, titleCandidates, snippetCandidates, unreadCandidates }) => {
          const pickText = (root, selectors) => {
            for (const selector of selectors) {
              const node = root.querySelector(selector);
              const text = node?.textContent?.trim();
              if (text) return text;
            }
            return "";
          };

          const hasMatch = (root, selectors) => {
            return selectors.some((selector) => root.querySelector(selector));
          };

          const seen = new Set();
          const results = [];

          for (const selector of threadCandidates) {
            for (const node of document.querySelectorAll(selector)) {
              const key = node.outerHTML.slice(0, 160);
              if (seen.has(key)) continue;
              seen.add(key);

              const title = pickText(node, titleCandidates);
              const snippet = pickText(node, snippetCandidates);
              const unread = hasMatch(node, unreadCandidates);

              if (title || snippet) {
                results.push({ title: title || "(untitled)", snippet, unread });
              }
            }
          }

          return results.slice(0, 50);
        }
        """
        raw = page.evaluate(
            js,
            {
                "threadCandidates": list(THREAD_CANDIDATES),
                "titleCandidates": list(TITLE_CANDIDATES),
                "snippetCandidates": list(SNIPPET_CANDIDATES),
                "unreadCandidates": list(UNREAD_CANDIDATES),
            },
        )
        return [ConversationSummary(**item) for item in raw]
