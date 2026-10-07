# stars-elegy

Public research and parity workspace for **Stars! J-RC3**.

This repository contains the behavioral side of the project:

- controlled experiments against the original game;
- `docs/PARITY.md`, the canonical public record of measured/documented behavior;
- headless oracle tooling;
- Stars! file inspection/recording tools;
- sanitized research fixtures and experiment infrastructure.

The canonical game implementation now lives in **[bfaber-centaur/elegy](https://github.com/bfaber-centaur/elegy)**. Engine/product code should move there rather than growing in this repository.

Private original-game apparatus and raw registered-copy evidence live outside this public repository. Binary reverse-engineering work is also kept private and promoted here only as behavior-level findings when useful.

Oracle setup: [docs/ORACLE.md](docs/ORACLE.md).

Spec consistency: `go run ./tools/speclint` checks status tags, case citations, cross-file references, ID uniqueness and pull-request numbers in prose. CI runs it against `tools/speclint/baseline.txt`; see `tools/speclint/main.go`.
