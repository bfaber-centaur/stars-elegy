package main

import (
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"unicode"
)

// Doc is one Markdown file, split into lines, with fenced code marked and
// its headings listed.
type Doc struct {
	Path     string // slash-separated, relative to the repository root
	Lines    []string
	Code     []bool // line is inside a fenced code block (or is a fence)
	Headings []Heading
	Anchors  map[string]bool
}

// Heading is an ATX heading.
type Heading struct {
	Level int
	Line  int // 0-based
	Text  string
}

var atxRe = regexp.MustCompile(`^(#{1,6})\s+(.*?)\s*#*\s*$`)

func parseDoc(path string, data []byte) *Doc {
	text := strings.ReplaceAll(string(data), "\r\n", "\n")
	d := &Doc{Path: path, Lines: strings.Split(text, "\n"), Anchors: map[string]bool{}}
	d.Code = make([]bool, len(d.Lines))
	fence := ""
	seen := map[string]int{}
	for i, l := range d.Lines {
		t := strings.TrimLeft(l, " ")
		if fence != "" {
			d.Code[i] = true
			if strings.HasPrefix(t, fence) {
				fence = ""
			}
			continue
		}
		if strings.HasPrefix(t, "```") || strings.HasPrefix(t, "~~~") {
			fence = t[:3]
			d.Code[i] = true
			continue
		}
		if m := atxRe.FindStringSubmatch(l); m != nil {
			h := Heading{Level: len(m[1]), Line: i, Text: m[2]}
			d.Headings = append(d.Headings, h)
			s := slug(h.Text)
			if n, ok := seen[s]; ok {
				seen[s] = n + 1
				s = s + "-" + itoa(n+1)
			} else {
				seen[s] = 0
			}
			d.Anchors[s] = true
		}
	}
	return d
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	var b []byte
	for n > 0 {
		b = append([]byte{byte('0' + n%10)}, b...)
		n /= 10
	}
	return string(b)
}

// slug is GitHub's heading anchor: inline markup dropped, lower case,
// punctuation removed, spaces to hyphens.
func slug(s string) string {
	s = stripInline(s)
	var b strings.Builder
	for _, r := range strings.ToLower(s) {
		switch {
		case unicode.IsLetter(r) || unicode.IsDigit(r) || r == '_' || r == '-':
			b.WriteRune(r)
		case r == ' ':
			b.WriteByte('-')
		}
	}
	return b.String()
}

var linkTextRe = regexp.MustCompile(`\[([^\]]*)\]\([^)]*\)`)

// stripInline removes links (keeping their text), backticks and emphasis.
func stripInline(s string) string {
	s = linkTextRe.ReplaceAllString(s, "$1")
	s = strings.NewReplacer("`", "", "**", "", "__", "").Replace(s)
	return s
}

// section returns the line range [start, end) of the body under heading k.
func (d *Doc) section(k int) (int, int) {
	start := d.Headings[k].Line + 1
	end := len(d.Lines)
	if k+1 < len(d.Headings) {
		end = d.Headings[k+1].Line
	}
	return start, end
}

// ancestors returns the headings that contain heading k.
func (d *Doc) ancestors(k int) []Heading {
	var out []Heading
	lvl := d.Headings[k].Level
	for j := k - 1; j >= 0 && lvl > 1; j-- {
		if d.Headings[j].Level < lvl {
			out = append(out, d.Headings[j])
			lvl = d.Headings[j].Level
		}
	}
	return out
}

// headingAt returns the index of the heading whose section holds line i,
// or -1 before the first heading.
func (d *Doc) headingAt(i int) int {
	k := sort.Search(len(d.Headings), func(j int) bool { return d.Headings[j].Line > i })
	return k - 1
}

// block returns the bounds [s, e) of the paragraph, list item or table row
// holding line i.
func (d *Doc) block(i int) (int, int) {
	if isTableRow(d.Lines[i]) || isHeading(d.Lines[i]) {
		return i, i + 1
	}
	s := i
	for s > 0 && !d.Code[s-1] && !isBreak(d.Lines[s]) && !isBreak(d.Lines[s-1]) && !isItemStart(d.Lines[s]) {
		s--
	}
	e := i + 1
	for e < len(d.Lines) && !d.Code[e] && !isBreak(d.Lines[e]) && !isItemStart(d.Lines[e]) {
		e++
	}
	return s, e
}

func isHeading(l string) bool  { return atxRe.MatchString(l) }
func isTableRow(l string) bool { return strings.HasPrefix(strings.TrimSpace(l), "|") }
func isBreak(l string) bool {
	return strings.TrimSpace(l) == "" || isHeading(l) || isTableRow(l)
}

var itemRe = regexp.MustCompile(`^\s*([-*+]|\d+[.)])\s`)

func isItemStart(l string) bool { return itemRe.MatchString(l) }

// loadDocs reads every Markdown file under root (skipping .git and
// dependency directories).
func loadDocs(root string) (map[string]*Doc, error) {
	docs := map[string]*Doc{}
	err := filepath.WalkDir(root, func(p string, e os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		name := e.Name()
		if e.IsDir() {
			if p != root && (strings.HasPrefix(name, ".") || name == "node_modules" || name == "__pycache__") {
				return filepath.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(name, ".md") {
			return nil
		}
		data, err := os.ReadFile(p)
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(root, p)
		rel = filepath.ToSlash(rel)
		docs[rel] = parseDoc(rel, data)
		return nil
	})
	return docs, err
}
