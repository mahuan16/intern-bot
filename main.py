"""Checks for new internship listings and sends them to Discord."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from scraper import get_listings

SEEN_FILE = Path(__file__).parent / "seen.json"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- Schedule settings ------------------------------------------------------
TIMEZONE = "America/Los_Angeles"
RUN_HOURS = {12, 22}  # 12pm and 10pm local time
# ----------------------------------------------------------------------------

DISCORD_LIMIT = 1900  # Discord rejects messages over 2000 characters


def is_scheduled_hour() -> bool:
    """GitHub's cron runs in UTC and ignores daylight saving, so the workflow
    triggers at both possible UTC times and we check the local hour here."""
    if os.environ.get("FORCE_RUN") == "1":
        return True
    return datetime.now(ZoneInfo(TIMEZONE)).hour in RUN_HOURS


def load_seen() -> set[str] | None:
    if not SEEN_FILE.exists():
        return None  # None = first run ever
    return set(json.loads(SEEN_FILE.read_text()))


def save_seen(ids: set[str]) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(ids)))


def format_listing(item: dict) -> str:
    # <url> wrapping stops Discord from creating a giant preview embed per link
    return f"**{item['company']}** - {item['role']} ({item['location']})\n<{item['url']}>"


def chunk_messages(header: str, lines: list[str]) -> list[str]:
    """Pack lines into as few messages as possible, each under the limit."""
    messages, current = [], header
    for line in lines:
        if len(current) + len(line) + 2 > DISCORD_LIMIT:
            messages.append(current)
            current = ""
        current += "\n\n" + line if current else line
    if current:
        messages.append(current)
    return messages


def send_discord(text: str) -> None:
    if not WEBHOOK_URL:
        print("[dry run - no DISCORD_WEBHOOK_URL set]\n" + text + "\n")
        return
    resp = requests.post(WEBHOOK_URL, json={"content": text}, timeout=15)
    resp.raise_for_status()


def main() -> None:
    if not is_scheduled_hour():
        print("Not a scheduled hour, skipping.")
        return

    listings = get_listings()
    if not listings:
        # Parsing probably broke (README format changed). Don't wipe our memory.
        send_discord("Internship bot: found 0 listings, the scraper may need fixing.")
        sys.exit(1)

    seen = load_seen()
    current_ids = {item["id"] for item in listings}

    if seen is None:
        save_seen(current_ids)
        send_discord(
            f"Internship bot is live. Tracking {len(current_ids)} current listings. "
            "From now on I'll only message you about new ones."
        )
        return

    new_items = [item for item in listings if item["id"] not in seen]
    # Keep old IDs too, so a listing that briefly disappears doesn't re-alert later.
    save_seen(seen | current_ids)

    if not new_items:
        send_discord("No new internships since the last check.")
        return

    for category in ("Software Engineering", "Data Science / AI / ML"):
        group = [i for i in new_items if i["category"] == category]
        if not group:
            continue
        header = f"**{len(group)} new {category} internships**"
        for message in chunk_messages(header, [format_listing(i) for i in group]):
            send_discord(message)


if __name__ == "__main__":
    main()
