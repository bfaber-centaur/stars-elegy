# TUI Design Language — v0

These are starting constraints, not commandments. Break one only when the mock demonstrates why.

## 1. TUI is a visual grammar, not the product architecture

A terminal-style surface may live inside a modern window.

Do not make the rest of the application terminal-like merely for consistency.

The battle replay is allowed to be the strongest expression of this language.

## 2. Information before nostalgia

The screen should earn its density.

Prefer:
- aligned numeric columns;
- compact labels;
- meaningful whitespace;
- stable spatial regions;
- tiny sparklines / bars / glyphs where they carry information;
- text labels over ambiguous icons;
- state conveyed redundantly when useful.

Avoid fake scanlines, faux phosphor glow, visual noise, and decorative borders that consume space without adding structure.

## 3. Quiet base, sharp state changes

Most of the UI should be visually quiet.

Reserve emphasis for:
- selection;
- warnings;
- damage;
- changed state;
- new intel;
- blocked orders;
- battle events;
- temporal focus in a replay.

A mock should still make sense in monochrome. Color, if imagined, is an enhancement rather than the only carrier of meaning.

## 4. Monospace can feel elegant

Do not equate monospace with crude.

Use:
- box drawing when it clarifies hierarchy;
- Unicode symbols cautiously;
- short rules and dividers;
- typographic rhythm;
- consistent column widths;
- restrained capitalization.

ASCII-only variants are welcome where they are stronger.

## 5. Dense does not mean cramped

Stars! is a spreadsheet-adjacent strategy game. Density is welcome.

But divide the screen into a few stable regions with obvious jobs.

A useful default for design studies:
- 120×40 characters for a full surface;
- 80×24 only when testing compression;
- narrower embedded panels when explicitly exploring a Wails subview.

## 6. Keyboard language may survive even in Wails

Mocks may show key hints such as:

`←/→ step   Space play/pause   G goto event   I inspect   Esc close`

Treat these as interaction shorthand, not a commitment that the final product is keyboard-only.

Mouse affordances do not need to be drawn unless the concept depends on them.

## 7. Stars!-specific feeling

Aim for an interface that supports:
- many small facts;
- comparison;
- planning;
- uncertainty / stale intel;
- deterministic replay;
- long-horizon decisions.

Avoid modern “one giant card per thing” dashboard styling.

This should feel made for a strategy game where the player wants six facts visible at once.

## 8. No false canon

Use canonical terms when known: planet, fleet, resources, factories, mines, research, battle plan, scanner/intel, turn/year.

When uncertain about exact mechanics, label the concept as a presentation experiment.

Mock values and invented names are encouraged.

## 9. A tiny amount of personality is good

The project is an elegy, not a corporate dashboard.

Subtle human touches are welcome:
- fleet names;
- terse battle prose;
- understated separators;
- compact little status phrases;
- a sense of “one more turn.”

Do not turn the UI into lore or comedy writing.
