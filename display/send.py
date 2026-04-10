#!/usr/bin/env python3
"""
send.py — send text to the DnD DM display server.

Usage:
    # DM narration (default)
    python3 send.py << 'DNDEND'
    The tavern reeks of old ale and burnt tallow.
    DNDEND

    # Player action — prepends character name on display
    python3 send.py --player Flerb << 'DNDEND'
    Flerb draws her greatsword and steps forward.
    DNDEND

    # Dice result — pipe from dice.py for open rolls
    python3 ~/.claude/skills/dnd/scripts/dice.py d20+4 | python3 send.py --dice

    # Short inline string
    echo "Short message" | python3 send.py
"""

import sys
import json
import argparse
import urllib.request

FLASK_URL = "http://localhost:5001/chunk"
TIMEOUT = 2.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Send text to the DnD display server.")
    parser.add_argument(
        "--player", metavar="NAME",
        help="Send as a player action, prepending the character name on display",
    )
    parser.add_argument(
        "--dice", action="store_true",
        help="Send as a dice result (inline gold styling)",
    )
    args = parser.parse_args()

    text = sys.stdin.read()
    if not text.strip():
        return

    payload: dict = {"text": text}
    if args.player:
        payload["player"] = args.player
    if args.dice:
        payload["dice"] = True

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        FLASK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=TIMEOUT)
    except Exception:
        pass  # Display not running — fail silently


if __name__ == "__main__":
    main()
