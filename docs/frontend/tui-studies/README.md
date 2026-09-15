# Stars! Elegy · TUI design studies

Thirteen visual studies, three rounds, no winner. Read the battle studies in order for deliberate divergence; the hybrids recombine pieces without resolving the disagreement. Every study contains a complete monochrome text mock and four or five short annotations. No frontend or architecture is implemented.

## Round 1 · Battle divergence

| Study | One-line premise |
| --- | --- |
| [B1 · Sounding table](battle/01-sounding-table.md) | A sparse plotting table makes position the main event and lets a single shot briefly annotate the field. |
| [B2 · Open record](battle/02-open-record.md) | A descending event history opens into a debugger-like before/after record. |
| [B3 · Touchline](battle/03-touchline.md) | A sports-replay score rail frames identical before/after views and a repeatable four-event passage. |
| [B4 · Track score](battle/04-track-score.md) | Horizontal stack lanes turn the battle into an interaction score, with position in a small inset. |
| [B5 · Action desk](battle/05-action-desk.md) | An operations console joins a stack register, event ledger, and pinned watch. |
| [B6 · Witness slip](battle/06-witness-slip.md) | An 80 × 24 event receipt keeps consequences and neighboring records readable in a drawer. |

## Round 2 · Adjacent surfaces

| Study | One-line premise |
| --- | --- |
| [S1 · Turn folio](surfaces/01-turn-folio.md) | A turn digest embeds a replay bookmark while keeping unread state separate from playback progress. |
| [S2 · Foundry book](surfaces/02-foundry-book.md) | A production ledger makes budgets and an unapplied reorder comparison visible together. |
| [S3 · Route card](surfaces/03-route-card.md) | A descending flight plan carries fuel and cargo through estimated future waypoints. |
| [S4 · Observation margin](surfaces/04-observation-margin.md) | A narrow companion to a modern galaxy map dates old observations and leaves current unknowns explicit. |

These four test changes already recorded, choices under revision, planned future events, and knowledge that may have expired.

## Round 3 · Hybridization

| Study | One-line premise |
| --- | --- |
| [H1 · Plot and score](hybrids/01-plot-and-score.md) | B1's stable plot meets B4's event lanes and B2's numerical receipt. |
| [H2 · Replay window](hybrids/02-replay-window.md) | B3's replay passage and B6's text inset live inside a modern desktop window, returning to S1's report. |
| [H3 · Contact notebook](hybrids/03-contact-notebook.md) | B2/B3's chronological spatial excerpts meet B5's watch and S4's careful treatment of knowledge. |

## Major axes

| Battle | Primary surface | Chronology | Default density | Character |
| --- | --- | --- | --- | --- |
| B1 | Whole battlefield | Horizontal, subordinate | Sparse | Tactical plot / glyphs |
| B2 | Event history | Vertical | Medium | Debugger / text and diffs |
| B3 | Paired battlefield views | Horizontal replay window | Sparse | Sports replay / spatial comparison |
| B4 | Stack interaction lanes | Horizontal, dominant | Dense | Instrument score / glyphs |
| B5 | Register and ledger | Vertical rows | Dense | Operations console / numbers |
| B6 | Event consequence | Vertical, three records | Sparse | Embedded receipt / prose |

Other tensions: whole battle versus selected contact; stable selection versus event focus; recorded fact versus preview versus stale knowledge; full terminal surface versus TUI inset. Most canvases are 120 × 40; B6 is 80 × 24, S4 is 72 × 38, and H3 is 96 × 40.

## Shared fixture and boundaries

The four supplied context files were read before drawing. The shared fictional encounter is **Deneb IV, 2443: Homeward versus Sable**. At E017, A03 (Mako ×14) fires on B07 (Needle); B07 goes from 12 to 10 ships and its illustrative shield readout goes from 46 to 12. Homeward has 26 ships; Sable has 26 remaining from 28. E016 moves B07 from f4 to f5; E018 moves A12 from e2 to e3.

Event ordinals, plot cells, shield units, future-event visibility, and planning estimates are presentation fixtures, not settled combat rules. No range, hit probability, target-choice explanation, or partial-construction behavior is asserted. Enemy fields require player-visible records. Similar contact names do not establish identity. Layouts deliberately vary spoiler preferences to expose that design question.

## Things that kept working

- A small before/after receipt explains a change without swallowing the screen.
- Fixed spatial framing makes stepping and comparison easier to trust.
- Ordinals, dates, and plain words distinguish selected events, planned orders, and stale observations.
- Stable IDs link glyphs to names; explicit unknowns avoid false numerical precision.
- Compact text panels survive next to surfaces that are not terminal-like.

## Open design questions

- How much tactical understanding survives without the whole plot visible?
- When the cursor moves, should selection follow the actor, the receiver, or a pinned stack?
- Which future events and battle outcomes should be concealed during a first replay?
- Can interaction lanes stay legible with dozens of stacks and overlapping events?
- Which fields will the actual battle record disclose, and which tempting explanations must remain absent?
- At ordinary desktop font sizes, which of these densities remain comfortable for an hour?

The corpus stops here: three attractors to react to, no implementation recommendation.
