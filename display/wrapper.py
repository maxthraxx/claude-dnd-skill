#!/usr/bin/env python3
"""
wrapper.py — Claude CLI stdout interceptor for DnD DM display

Usage:
    python3 wrapper.py [claude args...]

Spawns the claude CLI inside a PTY so the terminal experience is identical
to running `claude` directly. Simultaneously forwards all output to the
Flask display server at localhost:5000/chunk.

If Flask is not running, the terminal experience is completely unaffected —
the forward fails silently and you lose nothing.
"""

import os
import pty
import sys
import queue
import threading
import time

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

FLASK_URL = "http://localhost:5001/chunk"
CONNECT_TIMEOUT = 0.3   # seconds — fast fail so terminal never lags
POST_TIMEOUT    = 1.0

# ─── Async Flask sender ───────────────────────────────────────────────────────
# All POSTs happen on a background thread so the PTY read callback never blocks.

_chunk_queue: queue.Queue = queue.Queue(maxsize=512)
_flask_available = True   # optimistic; flips false on repeated failures
_failure_count   = 0
_FAILURE_LIMIT   = 5      # give up forwarding after N consecutive failures


def _flask_sender() -> None:
    global _flask_available, _failure_count

    while True:
        try:
            chunk = _chunk_queue.get(timeout=5)
        except queue.Empty:
            continue

        if chunk is None:          # sentinel — shut down
            break

        if not REQUESTS_AVAILABLE or not _flask_available:
            continue

        try:
            requests.post(
                FLASK_URL,
                json={"text": chunk},
                timeout=(CONNECT_TIMEOUT, POST_TIMEOUT),
            )
            _failure_count = 0     # reset on success
        except Exception:
            _failure_count += 1
            if _failure_count >= _FAILURE_LIMIT:
                _flask_available = False   # stop trying until process restart


_sender = threading.Thread(target=_flask_sender, daemon=True, name="flask-sender")
_sender.start()


# ─── PTY read callback ────────────────────────────────────────────────────────

def _master_read(fd: int) -> bytes:
    """Called by pty.spawn when the child writes output.
    Returns the data — pty.spawn writes it to our stdout automatically.
    We enqueue it for async forwarding to Flask.
    """
    data = os.read(fd, 4096)
    if data:
        try:
            _chunk_queue.put_nowait(data.decode("utf-8", errors="replace"))
        except queue.Full:
            pass   # drop rather than block
    return data


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        argv = ["claude"]

    # If first arg isn't 'claude', prepend it so you can do:
    #   python3 wrapper.py --resume
    # and have it behave as:
    #   claude --resume
    if argv[0] != "claude":
        argv = ["claude"] + argv

    try:
        # pty.spawn gives the child a real PTY, preserving full interactive
        # behaviour (readline, colours, cursor movement). The user's stdin
        # flows to the child; the child's stdout flows back through
        # _master_read → our stdout.
        exit_code = pty.spawn(argv, _master_read)
    except FileNotFoundError:
        sys.stderr.write(
            f"wrapper.py: command not found: {argv[0]}\n"
            "Make sure `claude` is on your PATH.\n"
        )
        exit_code = 127
    finally:
        # Drain the queue briefly before exit so the last response reaches Flask
        _chunk_queue.put(None)      # sentinel
        _sender.join(timeout=2.0)

    sys.exit(exit_code if isinstance(exit_code, int) else 0)


if __name__ == "__main__":
    main()
