# DnD DM Display — Cinematic Spectator Screen

Renders your DM session as a cinematic full-screen display on a browser tab,
which you Chromecast to your TV. You continue typing in the terminal as normal.

```
Terminal (you type here)
    ↓ stdout captured by wrapper.py
 Flask on localhost:5001
    ↓ SSE stream
 Browser tab → Chromecast → TV
```

---

## Setup

### 1. Install dependencies

```bash
cd ~/.claude/skills/dnd/display
pip3 install -r requirements.txt
```

### 2. Start the Flask server

Open a dedicated terminal window and run:

```bash
python3 ~/.claude/skills/dnd/display/app.py
```

You should see:
```
DnD DM Display — Flask server starting on http://localhost:5001
```

Leave this running. It does nothing until the wrapper connects.

### 3. Open the browser tab

Navigate to: **http://localhost:5001**

You'll see the dark cinematic background with ambient particles.
Now Chromecast this tab to your TV:
- Chrome: click the three-dot menu → Cast → select your Chromecast device → Cast tab
- The tab stays open and connected on your laptop

### 4. Start your Claude session via the wrapper

**Instead of running `claude` directly, run:**

```bash
python3 ~/.claude/skills/dnd/display/wrapper.py
```

This spawns `claude` inside a PTY — your terminal experience is completely
identical. All output is simultaneously forwarded to the Flask server.

You can pass arguments through:

```bash
python3 ~/.claude/skills/dnd/display/wrapper.py --resume
python3 ~/.claude/skills/dnd/display/wrapper.py --continue
```

Once the `/dnd load test-campaign` skill activates and the DM starts narrating,
text will appear on the TV with a typewriter effect, and the background will
shift to match the scene (inn, forest, dungeon, etc.).

---

## How it works

| Component | Role |
|---|---|
| `wrapper.py` | Spawns `claude` in a PTY, tees its stdout to the Flask server |
| `app.py` | Receives text, strips ANSI/TUI chrome, detects scene from keywords, pushes via SSE |
| `index.html` | Typewriter rendering, canvas particle system, CSS gradient crossfades |

### Scene detection

The Flask server scans each text chunk for keywords and derives a scene:

| Scene | Keywords (sample) | Particles |
|---|---|---|
| Tavern / Inn | tavern, inn, hearth, ale, candle | Embers |
| Mine | mine, seam, shaft, ore | Dust |
| Forest | forest, wood, tree, hollow wood | Fireflies |
| Dungeon | dungeon, corridor, torch | Dust |
| Temple | temple, shrine, altar, lantern | Smoke |
| Crypt | crypt, tomb, bones, undead | Smoke |
| Night | night, midnight, moon, star | Stars |
| Arcane | arcane, spell, rune, sigil | Sparks |
| Mountain | mountain, snow, blizzard | Snow |
| Ocean | ocean, sea, ship, wave | Bubbles |
| Desert | desert, sand, dune | Sand |
| City / Town | city, street, market, ashenveil | Rain |

The background gradient and particle type transition smoothly over ~2.5 seconds
when the scene changes.

### Text rendering

- DM output streams in as chunks from the Claude CLI
- ANSI escape codes and TUI chrome (borders, cost bars) are stripped server-side
- Characters render one at a time at ~18ms/char (typewriter effect)
- Gaps of >1.8 seconds between chunks start a new text block
- All previous responses remain visible and scroll naturally

---

## Troubleshooting

**Nothing appears on screen**
- Confirm Flask is running: `curl http://localhost:5001/ping` should return `ok`
- Confirm wrapper is running (not bare `claude`)
- Check the browser console for SSE connection errors

**Text looks garbled / shows control characters**
- The ANSI stripper may need tuning for your Claude CLI version
- Open an issue at the project repo with a sample of the raw output

**Scene never changes**
- Scene detection requires keywords in the DM narration
- The buffer window is 20 chunks — it may take a few paragraphs to trigger
- You can view the current detected scene name in the browser's scene indicator

**Particles are slow / choppy**
- Reduce particle count in `index.html` → `PARTICLE_COUNT` object
- Disable the glow effect on embers/fireflies by removing the `createRadialGradient` block

---

## Quick reference

```bash
DISPLAY=~/.claude/skills/dnd/display

# Terminal 1 — Flask server
python3 $DISPLAY/app.py

# Browser — open and Chromecast BEFORE starting your session
open http://localhost:5001

# Terminal 2 — Claude session via wrapper
python3 $DISPLAY/wrapper.py
python3 $DISPLAY/wrapper.py --resume   # resume existing session
```
