# HST recorder

`stars-record` preserves distinct Stars! host-file states while J-RC3 is being
used as an oracle.

It watches one directory (non-recursively) for `*.HST` files. Every 100 ms by
default it reads each host file and hashes its contents. A candidate is accepted
only after the same contents are observed on two consecutive polls, which avoids
archiving a file while Stars! is still rewriting it.

## Usage

```sh
go run ./cmd/stars-record \
  -watch ~/Documents/stars_games \
  -out ./testdata/jrc3/recordings
```

Stop the recorder with `Ctrl-C`.

The polling interval can be overridden when useful:

```sh
go run ./cmd/stars-record -watch DIR -out DIR -interval 250ms
```

## Output

The recorder reads the plaintext Stars! file header to identify the game and
turn. Raw files remain the primary evidence and are grouped by game ID:

```text
recordings/
└── 92584875/
    ├── observations.jsonl
    └── raw/
        ├── 2400-PG001-b9086c3c.HST
        ├── 2401-PG001-72deebde.HST
        └── ...
```

Each accepted state appends one line to `observations.jsonl` containing the game
ID, turn, year, full SHA-256 hash, original source filename, and archived path.
On restart, existing observation logs are loaded so already-recorded contents
are not duplicated.

The hash suffix prevents silent replacement. If the same game and turn appears
with a different hash, both files are retained and a warning is emitted.

## Polling limitation

The recorder is observational, not transactional. If Stars! produces and
overwrites multiple complete HST states between polls, an intermediate state
can be missed. At the default 100 ms cadence this is unlikely during manual turn
generation, and a forward gap in observed turn numbers is reported as a warning.

Requiring two identical reads also means a candidate must remain unchanged for
roughly one poll interval before it is archived.

## Scope

The current `internal/starsfile` package decodes only the plaintext file header
needed by the recorder. Decryption and full block decoding are intentionally out
of scope for this MVP. The package can grow later if legacy Stars! file
interoperability becomes a project goal.
