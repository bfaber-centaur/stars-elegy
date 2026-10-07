package main

import (
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

func writeTree(t *testing.T, files map[string]string) string {
	t.Helper()
	root := t.TempDir()
	for p, body := range files {
		full := filepath.Join(root, filepath.FromSlash(p))
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func TestLint(t *testing.T) {
	root := writeTree(t, map[string]string{
		"docs/PARITY.md": `# Parity

## Movement

Round 1 (FM-001 to FM-004), round 2 FM-101..105, MF-1..MF-12, UG01–UG21.
`,
		"docs/KERNEL.md": `# Kernel

## Status of each rule

| Rule | Status |
|---|---|
| Habitability | CONFIRMED (FM-001) |

## Conventions

CONFIRMED means an oracle run agreed.

## Habitability

Text without a tag of its own; the status table covers it.

## Distance (CONFIRMED, FM-002)

Vectors (CONFIRMED): 25.5 ly at warp 5 is 1 year.

## Fuel

Fuel is priced per year (CONFIRMED).

See ` + "`OBJECTS.md`" + ` "Decay" and
` + "`OBJECTS.md`" + ` "Hits" and [decay](OBJECTS.md#decay-confirmed-mf-4) and
[gone](OBJECTS.md#nothing). Measured in FM-103 and FM-106 (CONFIRMED).
Earlier work is in #47; fleet #12 is a fleet. ` + "`experiments/fm001`" + ` and
` + "`experiments/nothere`" + `; private stars-decomp ` + "`docs/x.md`" + `.

## Mining

Mining text with no tag.

## Open experiments

- **MF-13.** The 512th field (BINARY-ONLY).
`,
		"docs/OBJECTS.md": `# Objects

## Decay (CONFIRMED, MF-4)

Fields decay. MF-13 is a prediction, BINARY-ONLY.

## Sweeping

- **MF-2** sweeping rule (BINARY-ONLY).
- **MF-2** again (BINARY-ONLY).

See RACES.md for races.
`,
		"experiments/fm001/predictions.tsv": "case\tscreen\titem\tprediction\nA\tx\tfuel\t1\nA\tx\tfuel\t2\nB\tx\tfuel\t1\n",
	})
	fs, err := lint(root)
	if err != nil {
		t.Fatal(err)
	}
	var got []string
	for _, f := range fs {
		got = append(got, f.Check+" "+f.File+": "+f.Msg)
	}
	sort.Strings(got)
	want := []string{
		"broken-anchor docs/KERNEL.md: docs/OBJECTS.md has no anchor #nothing",
		"duplicate-id docs/OBJECTS.md: MF-2 defined twice in one section (first at line 9)",
		"duplicate-id experiments/fm001/predictions.tsv: A / fuel repeated (first at line 2)",
		"missing-file docs/OBJECTS.md: RACES.md does not exist",
		"missing-path docs/KERNEL.md: `experiments/nothere` does not exist",
		"missing-section docs/KERNEL.md: docs/OBJECTS.md has no section \"Hits\"",
		"pr-ref docs/KERNEL.md: cites PR #47: Earlier work is in #47; fleet #12 is a fleet. `experiments/fm001` and",
		"uncited docs/KERNEL.md: CONFIRMED without a case ID: Fuel is priced per year (CONFIRMED).",
		"unknown-case docs/KERNEL.md: FM-106 is not in PARITY.md or vectors/",
		"untagged docs/KERNEL.md: section \"Mining\" has no status tag",
	}
	if strings.Join(got, "\n") != strings.Join(want, "\n") {
		t.Errorf("findings:\n%s\n\nwant:\n%s", strings.Join(got, "\n"), strings.Join(want, "\n"))
	}
}

func TestFindCases(t *testing.T) {
	for _, c := range []struct {
		in   string
		want string
	}{
		{"FM-001..003", "FM-1 FM-2 FM-3"},
		{"CB-009 to CB-011", "CB-9 CB-10 CB-11"},
		{"MF-1..MF-3, OB-010-S", "MF-1 MF-2 MF-3 OB-10"},
		{"UG01–UG03 and SC-001F", "UG-1 UG-2 UG-3 SC-1"},
		{"RD-P11, SHA-256, KX-005 R3", "RD-P11 KX-5"},
		{"PG001 run", "PG-1"},
	} {
		var ids []string
		for _, r := range findCases(c.in) {
			ids = append(ids, r.expand()...)
		}
		if got := strings.Join(ids, " "); got != c.want {
			t.Errorf("findCases(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestSlug(t *testing.T) {
	for in, want := range map[string]string{
		"Decay (CONFIRMED, MF-4)":            "decay-confirmed-mf-4",
		"`KERNEL.md` \"Turn order\"":         "kernelmd-turn-order",
		"Fuel cost (CONFIRMED, FM-001..004)": "fuel-cost-confirmed-fm-001004",
	} {
		if got := slug(in); got != want {
			t.Errorf("slug(%q) = %q, want %q", in, got, want)
		}
	}
}
