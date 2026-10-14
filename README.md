# GMessages TUI

This project provides a Dockerized starting point for a terminal UI backed by
Google Messages for Web. The browser session is managed with Playwright and the
UI is built with Textual.

## What this scaffold does

- Opens a persistent Chromium profile against `https://messages.google.com/web`
- Preserves login state in `./playwright-data`
- Exposes a minimal Textual interface for:
  - refreshing a page snapshot
  - listing whatever conversation rows can currently be parsed
  - opening Google Messages Web in the managed browser

## What it does not do yet

- robust message parsing for every Google Messages UI variant
- live sync via browser events
- compose/send workflow from the TUI
- contact resolution

Google Messages does not provide a stable public API for this use case, so the
main engineering work is DOM inspection and keeping selectors resilient.

## Run

```bash
docker compose build
docker compose run --rm gmessages-tui
```

On first launch:

1. Scan the QR code or complete the sign-in flow in the Chromium window.
2. Press `r` in the TUI to refresh the snapshot.
3. If the conversation list stays empty, inspect the live DOM and update
   `src/gmessages_tui/selectors.py`.

## Next steps

- Add richer selector sets after inspecting the current production DOM.
- Cache parsed conversations/messages in SQLite.
- Split the browser bridge into polling and action endpoints.
- Add message send support once the composer selectors are stable.
