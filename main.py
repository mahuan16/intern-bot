"""Checks for new internship listings and sends them to Discord."""

import json
import os
import sys
import time
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

# Discord allows max 10 embeds per message
EMBEDS_PER_MESSAGE = 10
MAX_PER_CATEGORY = 50  # avoid spamming you if 300 listings appear at once

COLORS = {
    "Software Engineering": 0x5865F2,   # blurple
    "Data Science / AI / ML": 0x57F287,  # green
}


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


def make_embed(item: dict) -> dict:
    """Turn one listing into a Discord embed (a styled card)."""
    return {
        "title": f"{item['company']} - {item['role']}"[:256],
        "url": item["url"],  # makes the title a clickable apply link
        "color": COLORS.get(item["category"], 0x99AAB5),
        "fields": [
            {"name": "Location", "value": item["location"][:1024] or "Not listed", "inline": True},
            {"name": "Category", "value": item["category"], "inline": True},
        ],
    }


def send_discord(content: str = "", embeds: list[dict] | None = None) -> None:
    if not WEBHOOK_URL:
        print(f"[dry run - no DISCORD_WEBHOOK_URL set] {content}")
        for e in embeds or []:
            print(f"  card: {e['title']} | {e['fields'][0]['value']} | {e['url']}")
        return

    payload = {"content": content, "embeds": embeds or []}
    while True:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        if resp.status_code == 429:  # rate limited: wait as long as Discord says, retry
            time.sleep(resp.json().get("retry_after", 2))
            continue
        resp.raise_for_status()
        break
    time.sleep(1)  # be polite between messages


def send_category(category: str, group: list[dict]) -> None:
    shown = group[:MAX_PER_CATEGORY]
    extra = len(group) - len(shown)

    header = f"**{len(group)} new {category} internships**"
    if extra:
        header += f" (showing first {len(shown)}, +{extra} more in the repo list)"

    embeds = [make_embed(i) for i in shown]
    # Send in batches of 10 cards; only the first message carries the header.
    for n in range(0, len(embeds), EMBEDS_PER_MESSAGE):
        send_discord(header if n == 0 else "", embeds[n : n + EMBEDS_PER_MESSAGE])


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
        if group:
            send_category(category, group)


if __name__ == "__main__":
    main()