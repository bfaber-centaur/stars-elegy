package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// Case IDs look like CB-011, KX-002, FM-001..003, MF-1..MF-9, OB-010-S,
// SC-001F, RD-P11, T-3, or the older UG04. The canonical form drops leading
// zeros and suffixes: CB-11, OB-10, SC-1, RD-P11, UG-4, PG-1.
var (
	caseRe = regexp.MustCompile(`\b([A-Z]{1,4})-([A-Z]?)(\d{1,4})([A-Za-z]{0,2})\b`)
	ugRe   = regexp.MustCompile(`\b([A-Z]{2})(\d{2,3})\b`)
	// The older unhyphenated form: UG04, PG001.
	legacyRange = regexp.MustCompile(`^\s*(?:\.\.|–|—|-|\s+to\s+)\s*([A-Z]{2})?(\d{2,3})\b`)
	// A range continues a case ID: "..003", "..MF-9", "–UG21", "-CB-021".
	rangeRe = regexp.MustCompile(`^\s*(?:\.\.|–|—|\s+to\s+)\s*(?:([A-Z]{1,4})-?([A-Z]?))?(\d{1,4})\b`)
)

// Prefixes that look like case IDs but are not.
var notCase = map[string]bool{"SHA": true, "UTF": true, "ISO": true, "PR": true, "CP": true, "IEEE": true, "X": true}

// CaseRef is one case ID (or one end of a range) found in text.
type CaseRef struct {
	ID        string // canonical
	Raw       string
	Off       int
	RangeTo   string // canonical end of a range, if any
	RangeFrom int    // numeric start, for expansion
	RangeEnd  int
	End       int // offset just past the reference (and its range)
}

func canon(prefix, letter, num string) string {
	n, _ := strconv.Atoi(num)
	return prefix + "-" + letter + strconv.Itoa(n)
}

// findCases returns the case IDs in s, ranges expanded to their ends.
func findCases(s string) []CaseRef {
	var out []CaseRef
	for _, m := range caseRe.FindAllStringSubmatchIndex(s, -1) {
		p, l, n := s[m[2]:m[3]], s[m[4]:m[5]], s[m[6]:m[7]]
		if notCase[p] {
			continue
		}
		r := CaseRef{ID: canon(p, l, n), Raw: s[m[0]:m[1]], Off: m[0], End: m[1]}
		if rm := rangeRe.FindStringSubmatch(s[m[1]:]); rm != nil {
			p2, l2 := rm[1], rm[2]
			if p2 == "" {
				p2, l2 = p, l
			}
			if p2 == p && l2 == l {
				a, _ := strconv.Atoi(n)
				b, _ := strconv.Atoi(rm[3])
				if b > a && b-a < 1000 {
					r.RangeTo = canon(p2, l2, rm[3])
					r.RangeFrom, r.RangeEnd = a, b
					r.End = m[1] + len(rm[0])
				}
			}
		}
		out = append(out, r)
	}
	for _, m := range ugRe.FindAllStringSubmatchIndex(s, -1) {
		p, n := s[m[2]:m[3]], s[m[4]:m[5]]
		r := CaseRef{ID: canon(p, "", n), Raw: s[m[0]:m[1]], Off: m[0], End: m[1]}
		if rm := legacyRange.FindStringSubmatch(s[m[1]:]); rm != nil && (rm[1] == "" || rm[1] == p) {
			a, _ := strconv.Atoi(n)
			b, _ := strconv.Atoi(rm[2])
			if b > a && b-a < 1000 {
				r.RangeTo = canon(p, "", rm[2])
				r.RangeFrom, r.RangeEnd = a, b
				r.End = m[1] + len(rm[0])
			}
		}
		out = append(out, r)
	}
	// In text order, without the ends of ranges already counted.
	sort.Slice(out, func(i, j int) bool { return out[i].Off < out[j].Off })
	kept := out[:0]
	end := 0
	for _, r := range out {
		if r.Off < end {
			continue
		}
		kept = append(kept, r)
		end = r.End
	}
	return kept
}

// expand lists every canonical ID a reference covers.
func (r CaseRef) expand() []string {
	if r.RangeTo == "" {
		return []string{r.ID}
	}
	pre := strings.TrimRight(r.ID, "0123456789")
	var out []string
	for n := r.RangeFrom; n <= r.RangeEnd; n++ {
		out = append(out, pre+strconv.Itoa(n))
	}
	return out
}

// Registry is the set of case IDs a citation may name: every ID that
// appears in PARITY.md (ranges expanded) and every vector file and case ID.
type Registry struct {
	IDs      map[string]bool
	Prefixes map[string]bool
}

func (g *Registry) add(id string) {
	g.IDs[id] = true
	g.Prefixes[prefixOf(id)] = true
}

func prefixOf(id string) string {
	i := strings.IndexByte(id, '-')
	if i < 0 {
		return id
	}
	return id[:i]
}

func buildRegistry(root string, docs map[string]*Doc) (*Registry, error) {
	g := &Registry{IDs: map[string]bool{}, Prefixes: map[string]bool{}}
	if d := docs["docs/PARITY.md"]; d != nil {
		for _, l := range d.Lines {
			for _, r := range findCases(l) {
				for _, id := range r.expand() {
					g.add(id)
				}
			}
		}
	}
	files, _ := filepath.Glob(filepath.Join(root, "vectors", "*", "*.json"))
	for _, f := range files {
		data, err := os.ReadFile(f)
		if err != nil {
			return nil, err
		}
		var v struct {
			ID    string `json:"id"`
			Cases []struct {
				ID string `json:"id"`
			} `json:"cases"`
		}
		if json.Unmarshal(data, &v) != nil {
			continue
		}
		for _, s := range append([]string{v.ID}, caseIDs(v.Cases)...) {
			for _, r := range findCases(s) {
				g.add(r.ID)
			}
		}
	}
	return g, nil
}

func caseIDs(cs []struct {
	ID string `json:"id"`
}) []string {
	var out []string
	for _, c := range cs {
		out = append(out, c.ID)
	}
	return out
}
