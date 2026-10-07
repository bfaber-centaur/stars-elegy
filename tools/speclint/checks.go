package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

// Finding is one problem. Its key leaves out the line number so that a
// baseline survives edits elsewhere in the file.
type Finding struct {
	File  string
	Line  int // 1-based
	Check string
	Msg   string
}

func (f Finding) Key() string { return f.File + "\t" + f.Check + "\t" + f.Msg }
func (f Finding) String() string {
	return fmt.Sprintf("%s:%d: [%s] %s", f.File, f.Line, f.Check, f.Msg)
}

// Spec files carry tagged rules. The others are records (PARITY.md),
// procedures (ORACLE.md, HST_RECORDER.md) or the gap list (COVERAGE.md).
var notSpec = map[string]bool{
	"docs/PARITY.md": true, "docs/ORACLE.md": true, "docs/HST_RECORDER.md": true, "docs/COVERAGE.md": true,
}

func isSpec(p string) bool {
	return strings.HasPrefix(p, "docs/") && strings.Count(p, "/") == 1 && strings.HasSuffix(p, ".md") && !notSpec[p]
}

var (
	tagRe       = regexp.MustCompile(`\b(CONFIRMED|MEASURED|DOCUMENTED|UNKNOWN|LEGACY BUG|INTENTIONALLY DIFFERENT|BINARY-ONLY)\b`)
	evidenceTag = regexp.MustCompile(`\b(CONFIRMED|MEASURED)\b`)
	// Sections that hold no rules of their own.
	exemptSection = regexp.MustCompile(`(?i)^(status|conventions|open experiments|sources|implementing|columns|scope|notes|category values|contents|overview|how to read|vocabulary|glossary|not covered|elegy|oracle plan|predictions|related|open questions)\b`)
)

type linter struct {
	root     string
	docs     map[string]*Doc
	reg      *Registry
	findings []Finding
}

func (l *linter) add(d *Doc, line int, check, format string, args ...any) {
	l.findings = append(l.findings, Finding{File: d.Path, Line: line + 1, Check: check, Msg: fmt.Sprintf(format, args...)})
}

func (l *linter) sortedDocs() []*Doc {
	var out []*Doc
	for _, d := range l.docs {
		out = append(out, d)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Path < out[j].Path })
	return out
}

// statusNames lists the first column of a spec's status table.
func statusNames(d *Doc) []string {
	var names []string
	for k, h := range d.Headings {
		if !strings.HasPrefix(strings.ToLower(h.Text), "status") {
			continue
		}
		s, e := d.section(k)
		for i := s; i < e; i++ {
			if !isTableRow(d.Lines[i]) {
				continue
			}
			cells := strings.Split(strings.Trim(strings.TrimSpace(d.Lines[i]), "|"), "|")
			if len(cells) > 1 && tagRe.MatchString(d.Lines[i]) {
				names = append(names, norm(cells[0]))
			}
		}
	}
	return names
}

func norm(s string) string {
	s = strings.ToLower(stripInline(s))
	s = strings.NewReplacer("“", "\"", "”", "\"", "’", "'").Replace(s)
	return strings.Join(strings.Fields(s), " ")
}

// headName is a heading's text without its parenthetical tag.
func headName(t string) string {
	t = norm(t)
	if i := strings.Index(t, " ("); i > 0 {
		t = t[:i]
	}
	return strings.TrimSuffix(t, ":")
}

func hasProse(d *Doc, s, e int) bool {
	for i := s; i < e; i++ {
		if !d.Code[i] && strings.TrimSpace(d.Lines[i]) != "" {
			return true
		}
	}
	return false
}

// checkTags: every rule section in a spec file has a tag in its heading,
// an enclosing heading, its own text, or its row of the status table.
func (l *linter) checkTags(d *Doc) {
	status := statusNames(d)
	for k, h := range d.Headings {
		if h.Level < 2 || exemptSection.MatchString(stripInline(h.Text)) {
			continue
		}
		s, e := d.section(k)
		if !hasProse(d, s, e) || (k+1 < len(d.Headings) && d.Headings[k+1].Level > h.Level) {
			continue // no text, or an introduction to tagged subsections
		}
		ok := tagRe.MatchString(h.Text)
		for _, a := range d.ancestors(k) {
			ok = ok || tagRe.MatchString(a.Text) || exemptSection.MatchString(stripInline(a.Text))
		}
		for i := s; i < e && !ok; i++ {
			ok = !d.Code[i] && tagRe.MatchString(d.Lines[i])
		}
		name := headName(h.Text)
		for _, n := range status {
			ok = ok || strings.HasPrefix(name, n) || strings.HasPrefix(n, name)
		}
		if !ok {
			l.add(d, h.Line, "untagged", "section %q has no status tag", stripInline(h.Text))
		}
	}
}

// checkCitations: every CONFIRMED or MEASURED tag in a spec file names a
// corpus case in the same heading, table row, paragraph or list item; a
// heading's tag may be backed by a case in the section's text.
func (l *linter) checkCitations(d *Doc) {
	for i, line := range d.Lines {
		if d.Code[i] || !evidenceTag.MatchString(line) || tagDefRe.MatchString(line) {
			continue
		}
		k := d.headingAt(i)
		if k >= 0 && exemptSection.MatchString(stripInline(d.Headings[k].Text)) && !isTableRow(line) {
			continue
		}
		s, e := d.block(i)
		if isHeading(line) {
			_, e = d.section(k)
		}
		cited := false
		for j := s; j < e && !cited; j++ {
			cited = l.cites(d.Lines[j])
		}
		if k >= 0 && !cited {
			cited = l.cites(d.Headings[k].Text)
			for _, a := range d.ancestors(k) {
				cited = cited || l.cites(a.Text)
			}
		}
		if !cited {
			for _, m := range evidenceTag.FindAllString(line, -1) {
				l.add(d, i, "uncited", "%s without a case ID: %s", m, clip(line))
			}
		}
	}
}

// tagDefRe: a line defining what a tag means ("**CONFIRMED** means ...").
var tagDefRe = regexp.MustCompile(`\*\*(CONFIRMED|MEASURED)[^*]*\*\*\s*(means|:|—|-)`)

// roundRe: a corpus round named by prefix ("FM round 2").
var roundRe = regexp.MustCompile(`\b[A-Z]{2,4} round \d+\b`)

// runRe: an oracle run named by corpus and run directory ("tk/tk002").
var runRe = regexp.MustCompile(`\b[a-z]{2,4}\d?/[a-z]{2,4}[-_]?\d{2,4}`)

// labelRe: a corpus prefix and a case label inside it ("PQ C13").
var labelRe = regexp.MustCompile(`\b([A-Z]{2,4})\s+[A-Z]\d{1,3}\b`)

func (l *linter) cites(s string) bool {
	if len(findCases(s)) > 0 || roundRe.MatchString(s) || runRe.MatchString(s) {
		return true
	}
	for _, m := range labelRe.FindAllStringSubmatch(s, -1) {
		if l.reg.Prefixes[m[1]] {
			return true
		}
	}
	return false
}

func clip(s string) string {
	s = strings.TrimSpace(s)
	if len(s) > 90 {
		s = s[:87] + "..."
	}
	return s
}

// checkCaseIDs: case IDs cited in spec files exist in PARITY.md or the
// vectors. An ID cited only with BINARY-ONLY text may instead be a
// prediction named in some spec's open experiments.
func (l *linter) checkCaseIDs(d *Doc, predictions map[string]bool) {
	for i, line := range d.Lines {
		if d.Code[i] {
			continue
		}
		for _, r := range findCases(line) {
			if !l.reg.Prefixes[prefixOf(r.ID)] && !predictions[r.ID] {
				continue // not a corpus prefix PARITY.md knows: a label, not a case
			}
			for _, id := range []string{r.ID, r.RangeTo} {
				if id == "" || l.reg.IDs[id] {
					continue
				}
				s, e := d.block(i)
				claim := false
				for j := s; j < e; j++ {
					claim = claim || evidenceTag.MatchString(d.Lines[j])
				}
				if predictions[id] && !claim {
					continue
				}
				l.add(d, i, "unknown-case", "%s is not in PARITY.md or vectors/", id)
			}
		}
	}
}

// predictionIDs collects the case IDs named in every spec's open
// experiments: predictions, not yet results.
func (l *linter) predictionIDs() map[string]bool {
	out := map[string]bool{}
	for _, d := range l.sortedDocs() {
		if !isSpec(d.Path) {
			continue
		}
		for k, h := range d.Headings {
			t := strings.ToLower(stripInline(h.Text))
			if !strings.HasPrefix(t, "open experiments") && !strings.HasPrefix(t, "open questions") {
				continue
			}
			s, _ := d.section(k)
			e := len(d.Lines)
			for j := k + 1; j < len(d.Headings); j++ {
				if d.Headings[j].Level <= h.Level {
					e = d.Headings[j].Line
					break
				}
			}
			for i := s; i < e; i++ {
				for _, r := range findCases(d.Lines[i]) {
					for _, id := range r.expand() {
						out[id] = true
					}
				}
			}
		}
	}
	return out
}

var (
	mdLinkRe = regexp.MustCompile(`\]\(([^)\s]+)\)`)
	// FILE.md "Section" or PARITY "Section", optionally → "Subsection".
	secRefRe    = regexp.MustCompile("`?\\b([A-Z][A-Z_-]+)(\\.md)?`?(?:,|:)?\\s+(?:section\\s+|sections\\s+)?[\"“]([^\"”]+)[\"”]((?:\\s*(?:→|->|>)\\s*[\"“][^\"”]+[\"”])*)")
	chainRe     = regexp.MustCompile(`[\"“]([^\"”]+)[\"”]`)
	placeholder = regexp.MustCompile(`[0-9]*N{1,3}\b|NNN|XXX`)
	specFileRe  = regexp.MustCompile(`(?:^|[^/\w-])([A-Z][A-Z0-9_-]+\.md)\b`)
	pathRe      = regexp.MustCompile("`((?:experiments|tools|scripts|docs|internal|cmd|vectors|data)/[^`\\s]*)`")
	privateRe   = regexp.MustCompile("(?i)(decomp|apparatus|private|(^|[^-\\w])elegy\\b)[^;]*$")
)

// checkLinks: Markdown links, `FILE.md` "Section" references and
// backticked repository paths resolve.
func (l *linter) checkLinks(d *Doc) {
	for i, line := range d.Lines {
		if d.Code[i] {
			continue
		}
		prev := ""
		if i > 0 {
			prev = d.Lines[i-1]
		}
		for _, m := range mdLinkRe.FindAllStringSubmatch(line, -1) {
			l.checkLink(d, i, m[1])
		}
		for _, m := range secRefRe.FindAllStringSubmatchIndex(line, -1) {
			stem := line[m[2]:m[3]]
			target := l.specByStem(stem)
			if target == nil {
				continue
			}
			names := []string{line[m[6]:m[7]]}
			for _, c := range chainRe.FindAllStringSubmatch(line[m[8]:m[9]], -1) {
				names = append(names, c[1])
			}
			for _, n := range names {
				if !hasHeading(target, n) {
					l.add(d, i, "missing-section", "%s has no section %q", target.Path, n)
				}
			}
		}
		for _, m := range specFileRe.FindAllStringSubmatchIndex(line, -1) {
			name := line[m[2]:m[3]]
			if l.docs["docs/"+name] == nil && l.docs[name] == nil && l.docs[path.Join(path.Dir(d.Path), name)] == nil &&
				!privateContext(prev, line, m[0]) {
				l.add(d, i, "missing-file", "%s does not exist", name)
			}
		}
		for _, m := range pathRe.FindAllStringSubmatchIndex(line, -1) {
			p := strings.TrimRight(line[m[2]:m[3]], ".,:;")
			if strings.ContainsAny(p, "*<>{}…$") || placeholder.MatchString(p) || strings.Contains(p, "...") || privateContext(prev, line, m[0]) {
				continue
			}
			p = strings.SplitN(p, "#", 2)[0]
			p = strings.SplitN(p, ":", 2)[0]
			if _, err := os.Stat(filepath.Join(l.root, filepath.FromSlash(p))); err != nil {
				l.add(d, i, "missing-path", "`%s` does not exist", p)
			}
		}
	}
}

// privateContext: the reference just before off names a private repository
// (stars-decomp, apparatus) or the elegy repository.
func privateContext(prev, line string, off int) bool {
	before := prev + " " + line[:off]
	if len(before) > 100 {
		before = before[len(before)-100:]
	}
	return privateRe.MatchString(before)
}

func (l *linter) specByStem(stem string) *Doc {
	return l.docs["docs/"+stem+".md"]
}

func hasHeading(d *Doc, q string) bool {
	q = norm(q)
	q = strings.TrimSuffix(q, ".")
	for _, h := range d.Headings {
		t := norm(h.Text)
		if t == q || strings.HasPrefix(t, q) || headName(h.Text) == q {
			return true
		}
	}
	return false
}

func (l *linter) checkLink(d *Doc, i int, target string) {
	if strings.Contains(target, "://") || strings.HasPrefix(target, "mailto:") {
		return
	}
	file, anchor, _ := strings.Cut(target, "#")
	td := d
	if file != "" {
		p := path.Clean(path.Join(path.Dir(d.Path), file))
		if _, err := os.Stat(filepath.Join(l.root, filepath.FromSlash(p))); err != nil {
			l.add(d, i, "broken-link", "link target %s does not exist", file)
			return
		}
		td = l.docs[p]
	}
	if anchor != "" && td != nil && !td.Anchors[anchor] {
		l.add(d, i, "broken-anchor", "%s has no anchor #%s", td.Path, anchor)
	}
}

// PR numbers in prose: "#47", "(#55)", "stars-elegy #49", "PR 12".
var (
	prRe     = regexp.MustCompile(`(^|[\s(\[,;/])#(\d{1,4})\b`)
	prWordRe = regexp.MustCompile(`\b(?:PR|pull request)\s+(\d{1,4})\b`)
	gameNum  = regexp.MustCompile(`(?i)(fleet|planet|player|ship|design|slot|item|row|no\.|number|gater|scout|hauler|heavy|token|stack|"[^"]*)\s*$`)
)

// checkPRRefs: prose cites cases, not pull requests, whose numbers change
// when work is restarted.
func (l *linter) checkPRRefs(d *Doc) {
	for i, line := range d.Lines {
		if d.Code[i] {
			continue
		}
		bare := codeSpanRe.ReplaceAllString(line, "")
		bs, be := d.block(i)
		ctx := strings.ToLower(strings.Join(d.Lines[bs:be], " "))
		numbering := strings.Contains(ctx, "fleet number") || strings.Contains(ctx, "numbered")
		for _, m := range prRe.FindAllStringSubmatchIndex(bare, -1) {
			before := bare[:m[4]-1]
			if gameNum.MatchString(before) || (numbering && !repoRe.MatchString(before)) {
				continue
			}
			l.add(d, i, "pr-ref", "cites PR #%s: %s", bare[m[4]:m[5]], clip(line))
		}
		for _, m := range prWordRe.FindAllStringSubmatch(bare, -1) {
			l.add(d, i, "pr-ref", "cites PR #%s: %s", m[1], clip(line))
		}
	}
}

var repoRe = regexp.MustCompile(`(stars-elegy|stars-decomp|apparatus|elegy|PR)\s*$`)

var codeSpanRe = regexp.MustCompile("`[^`]*`")

// checkDefinitions: an ID defined (bold list label or heading start) is defined once per file and once across spec files.
var defRe = regexp.MustCompile(`^(?:\s*(?:[-*+]|\d+[.)])\s+\*\*|#{2,6}\s+)([A-Z]{1,4}-[A-Z]?\d{1,4}(?:-[A-Z0-9]+)?[a-z]?)\b`)

func (l *linter) checkDefinitions() {
	type def struct {
		d    *Doc
		line int
	}
	across := map[string][]def{}
	for _, d := range l.sortedDocs() {
		if !isSpec(d.Path) {
			continue
		}
		local := map[string]int{}
		for i, line := range d.Lines {
			if d.Code[i] {
				continue
			}
			m := defRe.FindStringSubmatch(line)
			if m == nil {
				continue
			}
			id := m[1]
			if j, ok := local[id]; ok && d.headingAt(j) == d.headingAt(i) {
				l.add(d, i, "duplicate-id", "%s defined twice in one section (first at line %d)", id, j+1)
				continue
			}
			if _, ok := local[id]; !ok {
				local[id] = i
				across[id] = append(across[id], def{d, i})
			}
		}
	}
	ids := make([]string, 0, len(across))
	for id := range across {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	for _, id := range ids {
		ds := across[id]
		for _, x := range ds[1:] {
			l.add(x.d, x.line, "duplicate-id", "%s also defined in %s:%d", id, ds[0].d.Path, ds[0].line+1)
		}
	}
}

// checkPredictionFiles: case IDs in experiments' prediction, expectation
// and result tables are unique per file.
func (l *linter) checkPredictionFiles() error {
	return filepath.WalkDir(filepath.Join(l.root, "experiments"), func(p string, e os.DirEntry, err error) error {
		if err != nil || e.IsDir() || !strings.HasSuffix(p, ".tsv") {
			return err
		}
		base := strings.ToLower(e.Name())
		if !strings.Contains(base, "predict") && !strings.Contains(base, "expect") {
			return nil
		}
		f, err := os.Open(p)
		if err != nil {
			return err
		}
		defer f.Close()
		rel, _ := filepath.Rel(l.root, p)
		rel = filepath.ToSlash(rel)
		sc := bufio.NewScanner(f)
		sc.Buffer(make([]byte, 1<<20), 1<<20)
		seen := map[string]int{}
		n := 0
		header := ""
		for sc.Scan() {
			n++
			cols := strings.Split(sc.Text(), "\t")
			if n == 1 {
				header = strings.ToLower(cols[0])
				continue
			}
			if header != "case" && header != "id" || len(cols) < 2 {
				return nil
			}
			// Several rows per case are normal (one per item); the
			// case plus its item column is the identity.
			key := cols[0] + "\t" + cols[1]
			if len(cols) > 3 {
				key = cols[0] + "\t" + cols[2]
			}
			if j, ok := seen[key]; ok {
				l.findings = append(l.findings, Finding{File: rel, Line: n, Check: "duplicate-id",
					Msg: fmt.Sprintf("%s repeated (first at line %d)", strings.ReplaceAll(key, "\t", " / "), j)})
				continue
			}
			seen[key] = n
		}
		return sc.Err()
	})
}

// checkVectors: vector case IDs are unique across vectors/.
func (l *linter) checkVectors() error {
	files, _ := filepath.Glob(filepath.Join(l.root, "vectors", "*", "*.json"))
	sort.Strings(files)
	first := map[string]string{}
	for _, f := range files {
		data, err := os.ReadFile(f)
		if err != nil {
			return err
		}
		var v struct {
			Cases []struct {
				ID string `json:"id"`
			} `json:"cases"`
		}
		if json.Unmarshal(data, &v) != nil {
			continue
		}
		rel, _ := filepath.Rel(l.root, f)
		rel = filepath.ToSlash(rel)
		for _, c := range v.Cases {
			if p, ok := first[c.ID]; ok {
				l.findings = append(l.findings, Finding{File: rel, Line: 1, Check: "duplicate-id",
					Msg: fmt.Sprintf("vector case %s also in %s", c.ID, p)})
				continue
			}
			first[c.ID] = rel
		}
	}
	return nil
}

func (l *linter) run() error {
	preds := l.predictionIDs()
	for _, d := range l.sortedDocs() {
		if isSpec(d.Path) {
			l.checkTags(d)
			l.checkCitations(d)
			l.checkCaseIDs(d, preds)
		}
		if strings.HasPrefix(d.Path, "docs/") || d.Path == "README.md" || strings.HasPrefix(d.Path, "vectors/") {
			l.checkLinks(d)
		}
		if strings.HasPrefix(d.Path, "docs/") && strings.Count(d.Path, "/") == 1 {
			l.checkPRRefs(d)
		}
	}
	l.checkDefinitions()
	if err := l.checkVectors(); err != nil {
		return err
	}
	return l.checkPredictionFiles()
}
