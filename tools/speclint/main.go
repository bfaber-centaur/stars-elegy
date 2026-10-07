// Command speclint checks the public specs for consistency:
//
//   - every rule section in a spec file carries a status tag;
//   - every CONFIRMED or MEASURED tag names a corpus case;
//   - cited case IDs exist in docs/PARITY.md or vectors/;
//   - Markdown links, anchors, `FILE.md` "Section" references and
//     backticked repository paths resolve;
//   - rule and prediction IDs are defined once;
//   - prose cites cases, not pull request numbers.
//
// Usage, from the repository root:
//
//	go run ./tools/speclint                  # fail on findings not in the baseline
//	go run ./tools/speclint -all             # list every finding
//	go run ./tools/speclint -write-baseline  # accept the current findings
//
// The baseline (tools/speclint/baseline.txt) lists accepted findings by
// file, check and message, without line numbers. A finding fixed in the
// specs should also leave the baseline; -write-baseline rewrites it.
package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

func main() {
	root := flag.String("root", ".", "repository root")
	baseline := flag.String("baseline", "tools/speclint/baseline.txt", "accepted findings, relative to -root")
	all := flag.Bool("all", false, "print every finding, baselined or not")
	write := flag.Bool("write-baseline", false, "write the current findings to the baseline")
	flag.Parse()

	findings, err := lint(*root)
	if err != nil {
		fmt.Fprintln(os.Stderr, "speclint:", err)
		os.Exit(2)
	}
	bpath := filepath.Join(*root, *baseline)
	if *write {
		if err := writeBaseline(bpath, findings); err != nil {
			fmt.Fprintln(os.Stderr, "speclint:", err)
			os.Exit(2)
		}
		fmt.Printf("speclint: %d findings written to %s\n", len(findings), *baseline)
		return
	}
	accepted, err := readBaseline(bpath)
	if err != nil && !os.IsNotExist(err) {
		fmt.Fprintln(os.Stderr, "speclint:", err)
		os.Exit(2)
	}
	fresh, known := 0, 0
	used := map[string]int{}
	for _, f := range findings {
		if accepted[f.Key()] > used[f.Key()] {
			used[f.Key()]++
			known++
			if *all {
				fmt.Println(f.String() + " (baseline)")
			}
			continue
		}
		fresh++
		fmt.Println(f.String())
	}
	stale := 0
	for k, n := range accepted {
		stale += max(0, n-used[k])
	}
	fmt.Printf("speclint: %d new, %d in baseline, %d baseline entries no longer found\n", fresh, known, stale)
	if fresh > 0 {
		os.Exit(1)
	}
}

func lint(root string) ([]Finding, error) {
	docs, err := loadDocs(root)
	if err != nil {
		return nil, err
	}
	reg, err := buildRegistry(root, docs)
	if err != nil {
		return nil, err
	}
	l := &linter{root: root, docs: docs, reg: reg}
	if err := l.run(); err != nil {
		return nil, err
	}
	sort.SliceStable(l.findings, func(i, j int) bool {
		a, b := l.findings[i], l.findings[j]
		if a.File != b.File {
			return a.File < b.File
		}
		return a.Line < b.Line
	})
	return l.findings, nil
}

func readBaseline(p string) (map[string]int, error) {
	f, err := os.Open(p)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	out := map[string]int{}
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		t := sc.Text()
		if t == "" || strings.HasPrefix(t, "#") {
			continue
		}
		out[t]++
	}
	return out, sc.Err()
}

func writeBaseline(p string, fs []Finding) error {
	var b strings.Builder
	b.WriteString("# speclint baseline: accepted findings (file, check, message), one per line.\n")
	b.WriteString("# Regenerate with: go run ./tools/speclint -write-baseline\n")
	keys := make([]string, 0, len(fs))
	for _, f := range fs {
		keys = append(keys, f.Key())
	}
	sort.Strings(keys)
	for _, k := range keys {
		b.WriteString(k + "\n")
	}
	return os.WriteFile(p, []byte(b.String()), 0o644)
}
