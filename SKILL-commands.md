# D&D Skill — Command Procedures

Full step-by-step procedures for all `/dnd` slash commands. Load this file at `/dnd load` or before executing any slash command.

---

## `/dnd new <campaign-name> [theme]`
1. Ask: *"Start the cinematic display companion? [y/n]"*
   - **Yes** → ask *"LAN mode? [y/n]"*
     - LAN → `bash ~/.claude/skills/dnd/display/start-display.sh --lan`, print both URLs, set `_display_running = true`
     - Local → `bash ~/.claude/skills/dnd/display/start-display.sh`, print URL, set `_display_running = true`
     - Then: `python3 ~/.claude/skills/dnd/display/push_stats.py --clear`
   - **No** → continue without display
2. `mkdir -p ~/.claude/dnd/campaigns/<name>/characters`
3. Copy and populate templates from `~/.claude/skills/dnd/templates/` — state.md, world.md, npcs.md, session-log.md
4. Ask: **party size** and **starting level**
5. **Tone/Genre Wizard** — present all four in one message:
   - Tone: `grimdark / dark fantasy / heroic / horror / political / swashbuckling / cosmic`
   - Magic level: `none / low / medium / high`
   - Setting type: `medieval / renaissance / ancient / nautical / underground`
   - Danger level: `lethal / gritty / standard / heroic`
   *(If `[theme]` supplied, pre-fill Tone and ask remaining three. Randomise any blank via dice.py and log `"d6=N → [result]"` in world.md.)*
6. **World Foundations** — geography/biome/climate, magic system, pantheon (2–3 active deities), calendar. Write to `## World Foundations` in world.md. Seed `state.md → ## World State → In-world date`.
7. **Three Truths** — one settlement, one nearby threat, one mystery (with clue trail). Write to respective sections in world.md.
8. **Threat Escalation Arc** — fill the five-stage table in world.md immediately after threat generation. Set current stage to 1. Write `Threat arc stage: 1 — Now` to `state.md → ## World State`.
9. **2 Factions** — archetype, all fields including current activity. Write to `## Factions` in world.md. Write one-line faction states to `state.md → ## World State`.
10. **3 NPCs with relationship web** — full entries (role, stats, demeanor, motivation, secret, speech quirk, faction, current goal, schedule, personality axes). Generate all three first, then fill Relationships (every NPC needs ≥2 links to others). Update index table.
11. **3–5 Quest Seeds** from threat, factions, mystery, NPC motivations. Write to `## Quest Seed Bank` in world.md.
12. **Dynamic Campaign Arc** — auto-generate the arc from all world data just created. Use Opus for this step. Ask: *"Generate a committed narrative arc? [y/n — recommended]"*

   **If yes:** Drawing from theme, threat arc stages, factions, Three Truths, NPC motivations, and quest seeds, derive:
   - **`theme`** — one sentence: what is this story ultimately about? Not the threat — its meaning.
   - **`resolution`** — the committed endpoint shape: if the party succeeds, what's the emotional truth? Keep specific events open; commit to the shape.
   - **Acts 1–3**, each with 2 beats. Each beat has:
     - `label` — a dramatic name
     - `what_changes` — before/after: what's fundamentally different once this lands?
     - `world_pressure` — the specific faction or NPC move (naming actual entities from this world) that makes the beat feel inevitable
   - **`steering_notes`** — how to reach the first beat without forcing it

   Beat layout:
   - Act 1: **1a Inciting Incident** (the threat becomes personal for the party), **1b Complication** (the problem is bigger or stranger than it first appeared)
   - Act 2: **2a Midpoint Shift** (what the party *thought* they were doing changes), **2b All Is Lost** (a genuine setback — something fails, is lost, or collapses)
   - Act 3: **3a Final Confrontation** (the decisive moment the campaign turns on), **3b Resolution** (what's different about the world and the characters after)

   Write to `state.md → ## Campaign Arc` with `type: dynamic`. Deliver a one-paragraph arc summary to the DM.

   **If no:** Write `type: sandbox` to `## Campaign Arc`. The story remains open-ended with no arc tracking.

13. Write state.md with session count 0, starting location.
14. Confirm creation, offer `/dnd character new`.

---

## `/dnd load <campaign-name>`
1. Ask: *"Start the cinematic display companion? [y/n]"*
   - Same display start/LAN flow as `/dnd new` step 1.
   - **Session tail replay:** before clearing the display, check if `~/.claude/skills/dnd/display/session_tail.json` exists. If it does, read it. After `--clear` and full stats push (step 4 below), replay the tail by sending each entry via the appropriate `send.py` flag. Entry type → flag mapping:
     - `player` key present → `send.py --player <name>` with text via stdin
     - `npc` key present → `send.py --npc <name>` with text via stdin
     - `dice` key present → `send.py --dice` with text via stdin
     - `xp_award` key present → `send.py --xp-award '<json of the xp_award sub-dict>'` (the sub-dict already has a `summary` field so no reconstruction needed)
     - `inspiration_award` key present → `send.py --inspiration-award '<name>'`
     - none of the above (plain DM narration) → `send.py` with text via stdin
     This restores the last scene to the display before the recap. The tail is written continuously by `app.py` — it always contains the last session's final exchanges regardless of how the session ended.
   - Clear previous transcript: `python3 ~/.claude/skills/dnd/display/push_stats.py --clear`
   - Register active campaign for DM Help: `python3 ~/.claude/skills/dnd/display/push_stats.py --set-campaign <campaign-name>`
   - Ask: *"Enable autorun mode for player input? [y/n]"*
     - **y** → write `autorun: true` to `state.md → ## Session Flags`; enter the autorun wait after the recap paragraph.
     - **n** → continue without autorun; DM drives turns manually.

2. Read SKILL-scripts.md (for script syntax this session)
3. Read state.md, world.md, npcs.md (index only), and all characters/*.md
   - **state.md contains `## DM Style Notes`** — read and internalize before narrating anything. These are table-specific calibration patterns that override default DM instincts.
   - **world.md:** Load in full — World Foundations and active Adventure Nodes both inform narration and faction moves. Do NOT read `world-seeds.md` at load (generation artifact, not live reference).
   - **npcs.md:** Index row only at load. **Before writing substantive dialogue or decisions for any named NPC, read their full entry in `npcs-full.md`.** Do not wait for an explicit `/dnd npc [name]` call — do it proactively when a scene centers on that character. Index rows carry surface traits only; personality axes, relationships, and hidden goals are in the full entry.
   - **Do NOT read session-log.md at load** — recent events are already in `state.md → ## Recent Events`. Only read session-log.md if the player explicitly requests a recap, or if DM Calibration from the last 1-2 sessions is needed and not already internalized.
4. Push full party stats to display sidebar. **CRITICAL:** use `--json` with a complete player object — **never** the `--player` shorthand here. `--player` only updates existing fields; it cannot populate the card or sheet tabs. The display shows "Full sheet not loaded" when `sheet` is absent.

   ```bash
   python3 ~/.claude/skills/dnd/display/push_stats.py --replace-players --json '{
     "players": [
       {
         "name": "CharName",
         "race": "Race",
         "class": "Class (Background)",
         "level": N,
         "hp": {"current": N, "max": N, "temp": 0},
         "ac": N,
         "speed": 30,
         "hit_dice": {"max": N, "remaining": N, "die": "d8"},
         "xp": {"current": N, "next": N},
         "conditions": [],
         "concentration": null,
         "inspiration": 0,
         "spell_slots": {},
         "sheet": {
           "attacks": [{"name":"...","bonus":"+N","damage":"...","type":"...","notes":"..."}],
           "features": [{"name":"Feature 1","text":"Description of what it does."},{"name":"Feature 2","text":"Description."}],
           "inventory": ["Item 1", "Item 2"]
         }
       }
     ]
   }'
   ```

   For casters, add `"spells": {"cantrips":["..."],"level1":["..."]}` inside `sheet`. Omit for non-casters.

   `--replace-players` clears stale characters from previous campaigns. Build the JSON from the character file — every field above is required for the card and sheet tabs to render correctly.

   Also push `--world-time`, `--factions`, and `--quests` in the **same** `push_stats.py` call as the player JSON to avoid race conditions where the display server receives a partial update. Combine all into one invocation:

   ```bash
   python3 ~/.claude/skills/dnd/display/push_stats.py --replace-players \
     --json '{...players...}' \
     --world-time '{...}' \
     --factions '[...]' \
     --quests '[...]'
   ```

   Faction JSON structure — **`standing` is required**:
   ```json
   [{"name":"Pale Court","standing":"Allied"},{"name":"The Kept","standing":"Hostile"}]
   ```
   `standing` values: `Allied`, `Friendly`, `Neutral`, `Suspicious`, `Hostile`. If the field is omitted, `app.py` defaults it to `"Neutral"` and logs a warning to stderr — but always include it explicitly. Map prose from `state.md` to exact values (e.g. "deep ally" → `"Allied"`, "active hostile" → `"Hostile"`). Use `[]` to clear.

   The faction panel only appears when at least one faction is present — do not skip this push.

   Quest JSON structure:
   ```json
   [{"name":"The Missing Shipment","status":"resolved"},{"name":"Keth the Collector","status":"threat"}]
   ```
   Quest `status` values: `active` (amber), `threat` (red), `resolved` (green), `failed` (muted). Use `[]` to clear all quests:
   ```bash
   python3 ~/.claude/skills/dnd/display/push_stats.py --quests '[...]'
   ```
   The quest panel only appears when at least one quest is present — do not skip this push.
5. Deliver one in-character paragraph recapping current situation — where the party is, what's at stake, what was last happening.
6. Enter active DM mode — no `/dnd` prefix needed from this point.

---

## `/dnd import <filepath> [campaign-name]`

Import a pre-written campaign from a source file (PDF, MD, TXT, Obsidian note, DOCX) and create a playable campaign from it.

**Supported file types:** `.pdf` `.md` `.txt` `.obsidian` `.markdown` `.docx`

### Step 1 — Extract source text
```bash
python3 ~/.claude/skills/dnd/scripts/import_campaign.py "<filepath>" --info
```
Print file info. If word count is over 4000, chunk the source:
```bash
python3 ~/.claude/skills/dnd/scripts/import_campaign.py "<filepath>" --chunks  # total chunks
python3 ~/.claude/skills/dnd/scripts/import_campaign.py "<filepath>" --chunk 0  # first chunk
```
For short sources (under 4000 words), read in full:
```bash
python3 ~/.claude/skills/dnd/scripts/import_campaign.py "<filepath>"
```

### Step 2 — Analyse structure
Read the extracted text and identify:
- **Campaign title and system**
- **Structure type:** `linear` (scene chain A→B→C) | `hub-and-spoke` (central hub + spoke locations, player-driven order) | `faction-web` (multi-faction city/complex, overlapping arcs)
- **Acts and chapters** — numbered sections, chapter headings, or named scenes
- **Key beats** — required story events the DM must deliver (boss reveals, faction turns, mandatory encounters)
- **Locations** — distinct named places with descriptions
- **NPCs** — names, roles, motivations, relationships, stat blocks if present
- **Factions** — groups with agendas, relationships to party
- **Quest hooks and seeds** — explicit adventure hooks, side quests, optional encounters
- **Starting conditions** — where does the party begin, what level, what's the inciting event

For large sources, read all chunks before proceeding.

### Step 3 — Confirm campaign name
If `[campaign-name]` not supplied, suggest one from the title and ask to confirm.

### Step 4 — Display summary and confirm
Show a structured summary before writing any files:

```
Title:    <source title>
Type:     structured / <structure type>
Acts:     N  |  Chapters: N  |  Key beats: N
NPCs:     N named  |  Factions: N
Locations: N distinct

Campaign name: <name>
Campaign dir:  ~/.claude/dnd/campaigns/<name>/

Proceed? [y/n]
```

### Step 5 — Create campaign files
On confirmation:

1. `mkdir -p ~/.claude/dnd/campaigns/<name>/characters`
2. Copy templates from `~/.claude/skills/dnd/templates/`
3. Write **world.md**:
   - `## World Foundations` — setting, geography, tone, magic level, calendar if present
   - `## Three Truths` — one settlement, one threat, one mystery (drawn from source)
   - `## Threat Escalation Arc` — map source acts to the 5-stage table; set stage 1
   - `## Factions` — all factions with archetype, current activity, relationship to party
   - `## Quest Seed Bank` — all explicit hooks + 2–3 implied side threads
   - `## Adventure Nodes` — named locations with one-line descriptions

4. Write **npcs.md** index table (one row per NPC: name, role, location, one-line demeanor)

5. Write **npcs-full.md** — full entry for each named NPC:
   - Role, motivation, secret, speech quirk, faction affiliation
   - Relationships to other NPCs (min 2 per NPC)
   - Stat block summary if present in source

6. Write **state.md** from template:
   - Populate `## Current Situation` — starting location and party placeholder
   - Populate `## World State` — in-world date if given, factions, threat arc stage 1
   - Populate `## Campaign Arc` — full act/chapter structure with key beats, telegraph scenes, and steering notes (see format in template)
   - Leave `## Active Quests`, `## Session Flags`, `## DM Style Notes` as template defaults

7. Write **session-log.md** with Session 0 import record:
   ```
   ## Session 0 — Import — <date>
   Source: <filepath>
   Imported: <N> acts, <N> chapters, <N> NPCs, <N> locations
   ```

### Step 6 — Gap-fill wizard
After writing files, identify anything the source left ambiguous:
- If starting level not specified → ask
- If party size not specified → ask
- If calendar/in-world date absent → offer to generate or leave blank
- If tone not clear from source → offer Tone/Genre Wizard

### Step 7 — Confirm and offer next step
Print summary of files written. Offer:
```
Campaign "<name>" created from <source title>.
→ /dnd character new      — create your character
→ /dnd load <name>        — start playing immediately
```

---

## `/dnd save`
Write session events to session-log.md, update state.md (location, active quests, party HP/resources, recent events), update any characters/*.md that changed. Mirror each updated character to global roster (`~/.claude/dnd/characters/<name>.md`).

**Update `## Live State Flags` in state.md on every save.** This section is the compaction-resistant anchor — it holds facts that prose summaries flatten. After each session, review and update:
- **Cover:** each PC's active cover, its status (INTACT / BLOWN / PARTIAL), and the one-line reason. Remove covers that are no longer active.
- **Faction stances:** each faction with non-neutral standing toward the party. Format: `[Faction]: [Allied/Friendly/Neutral/Suspicious/Hostile] — [one-line reason]`. Remove factions that have returned to neutral.
- **NPC dispositions:** each NPC with changed or notable standing. Format: `[Name]: [disposition] — [one-line reason]`. Remove NPCs who have returned to baseline.

If nothing changed in a category this session, leave it as-is. If a fact was wrong in the previous save, correct it.

Then update `## Faction Moves` in state.md: for each active faction, answer *"what did they do while the party was occupied?"* One line per faction — even if nothing visible yet. Confirm what was written.

**Session tail archive:** `app.py` continuously writes `~/.claude/skills/dnd/display/session_tail.json` — this is always current. At save time, also write the tail as a named session snapshot: `~/.claude/dnd/campaigns/<name>/session-tail.md` (SKILL-side human-readable, already done by the DM narration) **and** verify `session_tail.json` exists and is non-empty. If it is missing or empty (e.g. the display was not running), write it from the last narration block and player inputs available in context.

**Session log archival (run on every save after session count > 3):**
session-log.md keeps only the **2 most recent full session entries**. Older entries move to `session-log-archive.md` (append, never delete). Before archiving each entry, extract a 3–5 bullet continuity summary and write it to `## Continuity Archive` in state.md. Format:

```markdown
### Session N — [date] — [one-line location/event label]
- [Key fact that may resurface as a callback]
- [NPC revelation, exact wording of something important, decision that has consequences]
- [Roll outcome that changed the fiction]
- [Relationship shift, attitude change, item acquired with story significance]
```

The continuity summary is what stays hot in context. The full verbose log is in the archive, readable on `/dnd recap` or explicit request. When a past detail surfaces mid-scene, check `## Continuity Archive` first, then read session-log-archive.md if more depth is needed.

---

## `/dnd end`
1. Run `/dnd save`, then:
   a. Append **Session Recap** block to session-log.md with key events and open threads.
   b. Ask: *"Quick calibration — what worked this session, and what would you adjust next time?"* Write answers to `### DM Calibration`. If skipped, leave blank.
   c. Update `## World State` in state.md: check whether events advanced the threat arc stage, shifted faction states, or changed the in-world date. Update all three.
   d. If the calibration response reveals a new pattern (or confirms/contradicts an existing one), update `## DM Style Notes` in state.md. Add new bullets; refine existing ones if the pattern has sharpened. Do not log every session — only update when something genuinely new or changed is observed.
   e. **Arc check** (dynamic arcs only — skip for sandbox/structured): If `## Campaign Arc` has `type: dynamic`, review this session's key events against `outstanding_beats`. Ask: *"Did any arc beats land this session? [beat id(s) like '1b 2a', or 'none']"*
      - If beats landed: run `/dnd arc advance <beat-id>` for each. Update `steering_notes` for the next outstanding beat.
      - If none: check whether `world_pressure` for the next outstanding beat should appear in this session's Faction Moves entry. If yes, note it there — it should land next session.
2. If `_display_running = true`, stop the display:
   ```bash
   kill $(cat ~/.claude/skills/dnd/display/app.pid 2>/dev/null) 2>/dev/null
   rm -f ~/.claude/skills/dnd/display/app.pid
   ```

---

## `/dnd abandon`

Exit the current session **without saving any state changes**. Use this when an error occurred and you want to discard everything since the last `/dnd save` (or since load, if the session was never saved).

1. Confirm: *"Abandon session? All unsaved state changes will be lost. Type 'yes' to confirm."* — do not proceed until confirmed.
2. Do **NOT** write to state.md, world.md, npcs.md, session-log.md, or any character files.
3. Clear the autorun flag in memory (`autorun: false`) so the wait loop does not restart.
4. If `_display_running = true`, stop the display:
   ```bash
   kill $(cat ~/.claude/skills/dnd/display/app.pid 2>/dev/null) 2>/dev/null
   rm -f ~/.claude/skills/dnd/display/app.pid
   ```
5. Confirm: *"Session abandoned. No files were written. Run `/dnd load <campaign>` to reload from the last saved state."*

---

## `/dnd data [sync|status]`
- `sync` → `python3 ~/.claude/skills/dnd/scripts/sync_srd.py` — checks upstream SHAs (5e-bits + FoundryVTT) and rebuilds `dnd5e_srd.json` only if either source has new commits
- `sync --force` → `python3 ~/.claude/skills/dnd/scripts/sync_srd.py --force` — rebuild regardless
- `sync --check` → check upstream without rebuilding
- `status` → `python3 ~/.claude/skills/dnd/scripts/build_srd.py --status` — show current dataset metadata

Dataset is bundled at `~/.claude/skills/dnd/data/dnd5e_srd.json` (1453 records: spells, equipment, magic items, conditions, monsters, class features). No download required at runtime. Run `sync` only when you want to pull new upstream content.

---

## `/dnd display [start|stop|status]`
- `start` → ask LAN mode [y/n]; run `bash ~/.claude/skills/dnd/display/start-display.sh [--lan]`; print URL(s)
- `stop` → `kill $(cat ~/.claude/skills/dnd/display/app.pid) 2>/dev/null && rm -f ~/.claude/skills/dnd/display/app.pid`
- `status` → `curl -sk $(cat ~/.claude/skills/dnd/display/.scheme 2>/dev/null || echo http)://localhost:5001/ping` — reachable or unreachable
- No argument → print quick-start instructions

---

## `/dnd list`
Read `~/.claude/dnd/campaigns/*/state.md`, print summary table: campaign name | last session date | session count.

---

## `/dnd character new [campaign-name]`
1. Ask: name, race, class, background
2. Ask: *"In a sentence, what should the DM know about [Name]?"*
   - If answered: derive ONE pillar — **Bond**, **Flaw**, **Ideal**, or **Goal** (whichever fits best). Store both the raw sentence and derived pillar in `## Character Pillar`.
   - If skipped: leave `## Character Pillar` blank. Do not invent one. Do not re-prompt.
3. Ask: roll or point buy
   - Roll → `ability-scores.py roll`, present 3 arrays, player assigns
   - Point buy → `ability-scores.py pointbuy --check <scores>` to validate
4. Apply racial bonuses. Run `character.py calc` to derive all secondary stats.
5. Ask: Fighting Style (Fighter/Paladin/Ranger), spells (if caster)
6. Assign starting equipment per class + background
7. Write to `characters/<name>.md` using `templates/character-sheet.md`; set `## Campaign History → Origin campaign`
8. Add to `state.md` party line
9. Mirror to global roster: `cp characters/<name>.md ~/.claude/dnd/characters/<name>.md`
10. Run supplemental builder to fetch any non-SRD spells/features the character uses:
    ```bash
    python3 ~/.claude/skills/dnd/scripts/build_supplemental.py --character ~/.claude/dnd/campaigns/<name>/characters/<charname>.md
    ```
    This scans the character file for spells and features not in the SRD and fetches descriptions from dnd5e.wikidot.com into `dnd5e_supplemental.json`. Skips any entries already present. Safe to re-run.

---

## `/dnd character sheet [name]`
Read `characters/<name>.md`, display cleanly. If name omitted and one character exists, show that one.

---

## `/dnd character import <name> [from:<campaign>]`
1. Find character sheet: `from:<campaign>` specified → that campaign's characters/; otherwise check global roster `~/.claude/dnd/characters/<name>.md`; if neither → search all campaigns, list matches, ask.
2. Show summary (level, XP, HP, key inventory) and ask: *"Import at current level [X], or level up before starting?"*
   - As-is → copy directly; Level up first → run `/dnd level up` on source sheet
3. Copy to current campaign's `characters/<name>.md`. Update: Campaign, Last Updated, Previous campaigns, Death Saves (reset).
4. Optionally ask about equipment adjustment for new setting.
5. Add to `state.md` party line. Update global roster.
6. Run supplemental builder for any non-SRD entries:
    ```bash
    python3 ~/.claude/skills/dnd/scripts/build_supplemental.py --character ~/.claude/dnd/campaigns/<name>/characters/<charname>.md
    ```
7. Deliver one-paragraph in-character aside — how does it feel to step into a new world?

---

## `/dnd level up [name]`
1. **XP gate — check first:**

   | Level | XP required | Level | XP required |
   |-------|-------------|-------|-------------|
   | 2 | 300 | 11 | 85,000 |
   | 3 | 900 | 12 | 100,000 |
   | 4 | 2,700 | 13 | 120,000 |
   | 5 | 6,500 | 14 | 140,000 |
   | 6 | 14,000 | 15 | 165,000 |
   | 7 | 23,000 | 16 | 195,000 |
   | 8 | 34,000 | 17 | 225,000 |
   | 9 | 48,000 | 18 | 265,000 |
   | 10 | 64,000 | 19 | 305,000 |
   |    |         | 20 | 355,000 |

   Insufficient XP → report deficit and stop. Only continue on explicit DM override.
2. Read sheet. Run `character.py levelup`. Apply class features. Ask for HP roll or average. Update sheet + global roster. Narrate the growth.

---

## `/dnd npc [name]`
- Existing → read full entry from npcs-full.md (search by name), portray in character with voice/quirk
- New → generate full entry: role, CR-appropriate stats, demeanor, motivation, secret, speech quirk, faction (or "independent"), current goal, schedule, all four personality axes, ≥2 relationships to existing NPCs. Default attitude neutral. Append full entry to npcs-full.md; add one-line summary row to npcs.md index.

## `/dnd npc attitude <name> <shift>`
Find NPC in npcs.md, shift attitude one step (hostile → unfriendly → neutral → friendly → allied), log reason and date.

---

## `/dnd characters`
List all characters in global roster (`~/.claude/dnd/characters/`). Display: name, race/class/level, origin campaign, previous campaigns, last updated.

---

## `/dnd roll <notation>`
Run `scripts/dice.py <notation>`. Display output verbatim. Examples: `d20`, `2d6+3`, `d20 adv`, `4d6kh3`.

---

## `/dnd combat start`
1. Identify combatants; collect name, DEX mod, HP, AC, type (pc/npc) for each.
2. Run `combat.py init '<JSON>'` — auto-roll initiative for every combatant including PCs. Display tracker and per-combatant roll breakdown.
3. Send initiative to display:
   ```bash
   python3 ~/.claude/skills/dnd/display/send.py << 'DNDEND'
   ⚔️ Initiative — Round 1
   [Name]: d20(N) + DEX = total
   Turn order: [Name] → [Name] → ...
   DNDEND
   ```
4. Push turn order to stats sidebar:
   ```bash
   python3 ~/.claude/skills/dnd/display/push_stats.py --turn-order '{"order":[...],"current":"FirstName","round":1}'
   ```
5. Save STATE_JSON to `state.md` under `## Active Combat`.
6. Step through turns using the per-turn sequence (in SKILL.md Active DM Mode).
7. On combat end: update HP in character sheets, clear `## Active Combat`, `push_stats.py --turn-clear`, narrate aftermath, send XP summary, run `tracker.py -c <campaign> clear`.

**XP awards** go in the final display send:
```bash
python3 ~/.claude/skills/dnd/display/send.py << 'DNDEND'
[combat aftermath narration]

⭐ XP Awarded
- [Enemy] defeated: N XP
- [Objective] completed: N XP
- Total: N XP ÷ [players] = N XP each
- [Name]: N / 300 XP | [Name]: N / 300 XP
DNDEND
```

---

## `/dnd rest <short|long>`
**Short (1 hour):**
1. Ask how many Hit Dice the player spends. Roll `d[hit-die] + CON mod` per die via `dice.py`. Update HP, push `push_stats.py --player NAME --hp`.
2. Note class features that recharge (e.g. Second Wind → `push_stats.py --player NAME --second-wind true`).
3. Advance time: `calendar.py -c <campaign> rest short`
4. Clear encounter conditions: `tracker.py -c <campaign> clear` (concentration may persist — ask)

**Long (8 hours):**
1. Restore all HP, half max Hit Dice (round up), all spell slots, most class features. Update sheet.
2. Push: `push_stats.py --player NAME --hp <max> <max>` and `--second-wind true`.
3. Advance time: `calendar.py -c <campaign> rest long`
4. Clear all tracker state: `tracker.py -c <campaign> clear --all`
5. Update `state.md` in-world date to match calendar output.

---

## `/dnd recap`
Read session-log.md. Deliver 3–5 sentence in-character narrator recap of the most recent session entry.

## `/dnd world`
Read and display world.md.

## `/dnd quests`
Read `state.md` → display Active Quests and Open Threads sections.

---

## `/dnd arc [status|advance|revise|view]`

Manage the dynamic campaign arc. Active only when `state.md → ## Campaign Arc` has `type: dynamic` — no-op for sandbox and structured campaigns.

- **`/dnd arc`** or **`/dnd arc status`** — print current act, current beat label, `what_changes` for the current beat, and `steering_notes`. Quick reference, one screen.
- **`/dnd arc advance [beat-id]`** — mark the named beat complete (current beat if omitted). Remove from `outstanding_beats`. Advance `current_beat` to the next pending beat. If all beats in an act are complete, advance `current_act`. Update `steering_notes` to describe how to reach the newly current beat without forcing it.

  **When the final beat (3b) is marked complete — arc continuation:**
  `outstanding_beats` is now empty. Ask: *"The arc is complete. Continue the campaign with a new arc? [y/n]"*
  - **Yes** → run `/dnd arc new` (see below).
  - **No** → set `type: sandbox` and clear `outstanding_beats`. The campaign continues open-ended from the resolution state.

- **`/dnd arc new`** — generate a new arc for a campaign that has completed its previous arc. Use Opus for this step.

  The new arc must be **intentionally distinct** — not a continuation of the same conflict, but a new chapter that grows from the changed world. The resolution of arc N is the status quo of arc N+1.

  Procedure:
  1. Read the completed arc's `resolution` field — this is now the world's baseline.
  2. Read `## DM Notes`, `## World State`, `## Faction Moves`, and any `## Continuity Archive` entries to understand what the world looks like post-resolution.
  3. Derive the new arc from **the consequences** of what just resolved. Ask: *what problem did solving the last arc create? What power vacuum formed? What did the party's victory cost that now has to be reckoned with? What was ignored because the last arc demanded all attention?*
  4. Generate a new full arc (theme, resolution, acts 1–3, 6 beats) using the same format as the initial arc. The new theme must be meaningfully different from the previous one — same world, new lens.
  5. Archive the completed arc: move the current `acts` block, `theme`, and `resolution` into a new `## Arc History` section in state.md under `arc_N` (numbered), with a one-line summary of how it resolved.
  6. Write the new arc to `## Campaign Arc`, incrementing `arc_number`. Set `current_act: 1`, `current_beat: "1a"`, `outstanding_beats` to all 6 beat ids.
  7. Append to `revision_log`: `"<date>: Arc N complete. New arc N+1 generated. [one-line premise of the new arc]"`
  8. Deliver a one-paragraph summary of the new arc's premise and how it differs from the previous one.

- **`/dnd arc view`** — show full arc: theme, resolution, all acts and beats with completion status (current / complete / pending). If `## Arc History` exists, show a one-line summary of each completed arc above the current one.
- **`/dnd arc revise`** — open revision flow for when the story has taken a major unexpected turn:
  1. Show all outstanding beats.
  2. Ask: *"What's changed in the story that the arc doesn't reflect?"*
  3. Rewrite `what_changes` and/or `world_pressure` for affected outstanding beats to fit the new direction. Do not modify completed beats.
  4. Append to `revision_log`: `"<date>: <what changed and why — one sentence>"`
  5. Update `steering_notes`.
  6. Confirm what was revised.

---

## `/dnd tutor on` / `/dnd tutor off`
Toggle tutor/learning mode. Write `tutor_mode: true/false` to `state.md` under `## Session Flags`. Session-scoped — does not persist to next `/dnd load` unless explicitly set again. (Full tutor mode behavior is in SKILL.md.)

---

## `/dnd autorun on` / `/dnd autorun off`

Toggle autorun (taxi) mode — Claude drives the turn loop automatically when players submit via the display companion. No PTY wrapper required.

**On:**
1. Write `autorun: true` to `state.md → ## Session Flags`.
2. **Check Bash permissions** — read `~/.claude/settings.json`. If `permissions.allow` does not include `"Bash"` (or `"Bash(*)"` or similar), add it automatically:
   - Read the file, merge `"Bash"` into `permissions.allow`, write it back.
   - Tell the DM: *"Added Bash to permissions.allow in ~/.claude/settings.json — autorun won't prompt for each wait. Restart this session for it to take effect if it doesn't immediately."*
   - If it was already present, skip silently.
3. Confirm to the DM: *"Autorun enabled. Players submit via the display; I'll pick up each action automatically. Send me a message at any time to take control of a turn."*
4. If the user specified an interval (e.g. `/dnd autorun on 45`), write `autorun_interval: 45` to `state.md → ## Session Flags`. Default is 60 if omitted.
5. Immediately enter the autorun wait (see SKILL.md for the Bash block). If there's already something in `.input_queue`, pick it up as the current turn's player action.

The display shows a pie-clock countdown draining from full to empty over the interval. Green pulse = actively waiting. Configurable via `autorun_interval: N` in state.md (default 60 seconds).

**Off:**
1. Write `autorun: false` (or remove the line) to `state.md → ## Session Flags`.
2. Confirm: *"Autorun disabled. Back to manual mode — press Enter or tell me to submit when players are ready."*
3. Do NOT start the autorun wait after this response.

**Check on `/dnd load`:** If `autorun: true` is present in state.md, tell the DM autorun is active and begin the wait loop after the recap paragraph.

**When NOT to run the autorun wait (even if flag is set):**
- Mid-combat, resolving a specific combatant's turn
- Waiting on a player dice roll result
- The DM just sent a message (they're driving this turn)
- During `/dnd save`, `/dnd end`, or any command response
