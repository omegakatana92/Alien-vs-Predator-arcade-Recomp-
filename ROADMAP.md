# Alien vs. Predator — features and roadmap

Where this port stands against a finished one, and what each missing piece needs. The reference is the
toolkit's own complete example, [vampire-savior-recomp](https://github.com/tmcleroy/vampire-savior-recomp)
(`games/vampire_savior/src/`), and the toolkit's documents `docs/FEATURES.md` and `docs/FIGHT.md`.

Everything below is an **optional feature**: with every feature off, the port must run exactly as the
board does. Nothing from the game (no ROM, no RAM dump, no ripped art/text) may ever be committed — each
thing found is recorded in `PROGRESS.md` as *how* it was found (a RAM diff, a write watch, a trace),
never as the data itself.

## What works today

From the toolkit, with no game work:

- The **launcher**: chooses the ROM set, checks every file by CRC-32, sets the controls, Play.
- The **in-game menu** (Esc, `F1`, a stick's click, or Start+Select): save states (9 slots), Reset,
  Insert coin, Player 2 joins, Quit game.
- **Stop, step, slow** (P, O, `-`/`=`).
- **Run-ahead** and the **Display** options (scaling, picture shape, window size, full screen).
- Every key and button **remappable**, for each player.

Nothing on the game's own memory yet: `games/avsp/src/` is empty, so this first release is the board
and the toolkit, nothing added.

## What a finished port adds (this is the work)

### 0. Foundation — know the game's memory

Find and name the values every feature below needs, in a header `games/avsp/src/avsp.h`. The toolkit's
tools do the finding (all documented in `docs/FEATURES.md`):

- `--dump-ram F:FILE` + `tools/ramfind.py DUMP=VALUE ...` — addresses that held a known value across
  several dumps (this is how credits and health are usually found).
- `--trace LOW-HIGH:FILE` with a run that does known things at known frames (a coin, a hit, the clock
  running down).
- `--watch LOW[-HIGH]` — every write to an address and the instruction that made it, read against
  `work/avsp/program.lst`.
- `--poke ADDR=BYTE,...` to try a guess; `--menu FRAME:KEYS` to press the menu's own rows;
  `--shot-every N:PFX` to see a run.

What a run-and-gun needs: the credit word, the score, the player's health, lives, ammo, the two
players' positions and facing, the enemy table, and the stage/timer words.

### 1. The Features page (the game's own switches)

| Feature | Kind | Needs |
| --- | --- | --- |
| Free play | on/off | the credit word held at its full value |
| No damage | Cheats | the player's health word |
| Infinite lives | Cheats | the lives counter |
| Infinite ammo / rapid fire | Cheats | the ammo/weapon words and the fire routine |
| Board/operator settings (difficulty, lives, free play) | choices | reading the EEPROM's operator settings |
| "The game's own test menu" | command | a routine address to jump to |

### 2. Training aids

| Piece | What it adds | Needs |
| --- | --- | --- |
| Input display | what each stick holds, and for how long | the two players' input words |
| Hit boxes | the players' and enemies' boxes, drawn on the picture | the box tables and the camera's place |
| Enemy/stage readout | what is on screen and where | the enemy table |

The toolkit's `fight/` parts (built for fighting games) cover some of this; the input display is the
first one and needs the least.

### 3. Alternative modes

| Mode | What it adds | Needs |
| --- | --- | --- |
| Attract watcher | the game's own show on a loop, no coin | the credit word and the attract state |
| Endless | a game that never ends | the stage/game-over state |
| Widescreen | more of the field in 16:9 | rewrites of the camera and the background scrollers |

### 4. Readable rewrites (correctness)

Rewrite the game's key routines by hand as named C++ (`docs/READABLE.md`): the players' movement,
shooting, collisions and the stage advance. Each is checked call by call with `make check-rewrites`.
This is what makes clean cheats and the training aids possible.

## Recommended order

1. **The foundation** — credits, health, lives and the players' positions, named in `avsp.h`.
2. **The quick cheats** — free play, no damage, infinite lives, on the Features page.
3. **Training aids** — the input display first, then hit boxes.
4. **Alternative modes** — attract watcher, endless.
5. **Widescreen.**
6. **Readable rewrites** — needed by the later training aids and widescreen; correctness.

## Before uploading: a checklist

- [x] `README.md` states the exact ROM set (`avsp`, Europe 940520) and that **only that revision**
      works, with the Capcom disclaimer.
- [x] `rom/`, `build/`, `work/` are ignored and **absent** from the repository; no game data, keys or
      dumps anywhere; no screenshots.
- [x] `make check`, `make check-toolkit`, `make check-common` pass.
- [x] `LICENSE` (GPL-3.0-only) and `THIRD_PARTY_NOTICES.md` (the cipher is MAME's, BSD-3-Clause); the
      release archives carry them and the licences of what they ship.
- [x] First commit made; the repository builds from a fresh clone with the player's own ROM set
      (`make`, `make explore`, `make launcher`). The first release, `v1.0.0`, is up.
