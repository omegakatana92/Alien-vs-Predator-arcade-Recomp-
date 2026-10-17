# Alien vs. Predator — progress

What has been found in the game's memory, and **how** each thing was found, so that anyone can repeat
it. The data itself is never recorded here (no RAM dumps, no ROM bytes): only addresses, the values
seen, and the steps.

## The base port

The port is the toolkit's machine with the board's program translated: the 68000 program of the set
`avsp` (Europe 940520) and its Z80 sound program, found by `make explore` and translated by `make`. The
final run's log line — `instructions had no translation` — is what says the code is complete; it is
recorded with the release.

No game-specific address has been found yet: `games/avsp/src/` is empty, so nothing on the Features
page is the game's own. [ROADMAP.md](../ROADMAP.md) lists what is next (the credit word, the player's
health and lives, the players' positions) and the tools each is found with:

- `--dump-ram F:FILE` + `cps2recomp/tools/ramfind.py DUMP=VALUE ...` — addresses that held a value in
  every dump.
- `--trace LOW-HIGH:FILE` — every read/write in a range, for a run that does a known thing at a known
  frame.
- `--watch LOW[-HIGH]` — every write to an address and the instruction that made it, beside
  `work/avsp/program.lst`.
- `--poke ADDR=BYTE,...` and `--menu FRAME:KEYS` to try a guess and to press the menu's own rows.

## How the set was told apart

`avsp` is MAME's parent set (Europe 940520): its program is the four files `avpe.03d`, `avpe.04d`,
`avp.05d` and `avp.06`, whose CRC-32s are in `games/avsp/game.cfg`. The clones (`avspa`, `avspj`,
`avspu`) build from the same parent ROMs with their own program; only `avsp` is accepted, and the
launcher refuses any other by checksum.
