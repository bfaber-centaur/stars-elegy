# fleetlab tools

Oracle-side tools for building, running and reading original-game files.
How to use them is in `docs/ORACLE.md`; each tool's header comment lists
its commands. Self-tests that need no game file run in CI:

- `combatlab selftest`: the `computer` key's player byte and the dump's
  `b7=` field.
- `racelab selftest`: the race-file checksum after a rename to a shorter
  name (once the fix below is merged).

## Known defects

- **racelab: wrong checksum after renaming to a shorter name.** Found
  while building RG-004 (2026-10-13). `racelab edit … name=S plural=S`
  with a name shorter than the old one, such as a four-letter name, wrote
  a footer checksum the original rejects. The cause: StarsAPI's decode
  reuses the race buffer without clearing it, so the old name's tail
  stays in the bytes the checksum covers. RG-004 avoided it by using
  longer names (Jackal, Swarm). The fix (clear the buffer before decoding,
  with `racelab selftest` in CI) is in its own PR. Until it merges,
  check `racelab dump` for `checksum=ok` after a rename.
