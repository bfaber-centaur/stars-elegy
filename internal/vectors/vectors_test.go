package vectors

import (
	"encoding/json"
	"fmt"
	"strings"
	"testing"
)

func TestVectors(t *testing.T) {
	vs, err := LoadAll("../../vectors")
	if err != nil {
		t.Fatal(err)
	}
	if len(vs) == 0 {
		t.Fatal("no vectors found")
	}
	ids := map[string]bool{}
	cases := 0
	for _, v := range vs {
		if ids[v.ID] {
			t.Errorf("duplicate vector id %s", v.ID)
		}
		ids[v.ID] = true
		for _, e := range v.Check() {
			t.Error(e)
		}
		cases += len(v.Cases)
	}
	t.Logf("%d vectors, %d cases", len(vs), cases)
}

func TestOrderFields(t *testing.T) {
	one, three := 1, 3
	v := &Vector{Schema: Schema, ID: "T", Years: 1, Streams: 1,
		InitialState: &State{Game: Game{Players: 1}, Players: []Player{{ID: 0}}},
		Orders: []OrderSet{{Year: 1, Player: 0, Orders: []Order{
			{Kind: "fleet_battle_plan", Fleet: &one, Plan: &three},
			{Kind: "fleet_battle_plan", Fleet: &one},
			{Kind: "teleport"},
		}}},
		Cases: []Case{{ID: "T-1", Tag: "MEASURED", Expect: []Expectation{{Year: 1, Kind: "no_battle"}}}}}
	errs := v.Check()
	if len(errs) != 2 {
		t.Fatalf("want 2 errors (missing plan, unknown kind), got %v", errs)
	}
	for k := range OrderFields {
		if (&Order{}).has(OrderFields[k][0]) {
			t.Errorf("%s: an empty order has %s", k, OrderFields[k][0])
		}
	}
}

func TestConcentrationFractions(t *testing.T) {
	for _, c := range []struct {
		f    []int
		errs int
	}{
		{nil, 0},
		{[]int{0, 128, 255}, 0},
		{[]int{1, 2}, 1},
		{[]int{1, 2, 3, 4}, 1},
		{[]int{-1, 0, 0}, 1},
		{[]int{0, -1, 0}, 1},
		{[]int{0, 0, -1}, 1},
		{[]int{256, 0, 0}, 1},
		{[]int{0, 256, 0}, 1},
		{[]int{0, 0, 256}, 1},
	} {
		v := &Vector{Schema: Schema, ID: "T", Years: 1, Streams: 1,
			InitialState: &State{Game: Game{Players: 1}, Players: []Player{{ID: 0}},
				Planets: []Planet{{ID: 0, ConcFractions: c.f}}},
			Cases: []Case{{ID: "T-1", Tag: "MEASURED", Expect: []Expectation{{Year: 1, Kind: "no_battle"}}}}}
		if errs := v.Check(); len(errs) != c.errs {
			t.Errorf("%v: want %d errors, got %v", c.f, c.errs, errs)
		}
	}
}

func TestPlayerHomeworld(t *testing.T) {
	zero, one, two := 0, 1, 2
	for _, c := range []struct {
		hw   *int
		errs int
	}{
		{nil, 0},
		{&zero, 0},
		{&one, 0},
		{&two, 1},
	} {
		v := &Vector{Schema: Schema, ID: "T", Years: 1, Streams: 1,
			InitialState: &State{Game: Game{Players: 1}, Players: []Player{{ID: 0, Homeworld: c.hw}},
				Planets: []Planet{{ID: 0}, {ID: 1}}},
			Cases: []Case{{ID: "T-1", Tag: "MEASURED", Expect: []Expectation{{Year: 1, Kind: "no_battle"}}}}}
		if errs := v.Check(); len(errs) != c.errs {
			t.Errorf("homeworld %v: want %d errors, got %v", c.hw, c.errs, errs)
		}
	}
}

// RG-001's 2430 start: player 1 colonized planets 32, 77 and 81 that year,
// and only 81 held an ancient artifact (the 0x05e research gift).
// KX-004 S11: a comet moves the current and original environment by the
// same amount, each clamped on its own; an untouched planet keeps no
// separate original (null: equal to the current value).
func TestKX004S11CometOriginal(t *testing.T) {
	v, err := Load("../../vectors/kx004/s11.json")
	if err != nil {
		t.Fatal(err)
	}
	want := map[string]string{
		"cycles 1985/2":   `[1,99,60] [43,58,99]`,
		"cycles 930/15":   `[54,50,50] [99,20,20]`,
		"cycles 2190/11":  `[99,52,50] [63,44,30]`,
		"cycles 6000/22":  `[19,1,81] [22,6,94]`,
		"cycles 3700/17":  `[55,47,54] null`,
		"cycles 10500/19": `[48,78,29] null`,
	}
	got := map[string]string{}
	for _, e := range v.Cases[0].Expect {
		if e.Kind != "planet" {
			continue
		}
		var eq struct {
			Env  json.RawMessage `json:"environment"`
			Orig json.RawMessage `json:"original_environment"`
		}
		if err := json.Unmarshal(e.Equals, &eq); err != nil || eq.Env == nil {
			continue
		}
		got[fmt.Sprintf("%s/%d", e.Stream, *e.ID)] = string(eq.Env) + " " + string(eq.Orig)
	}
	for k, w := range want {
		if got[k] != w {
			t.Errorf("%s: environment, original = %q, want %q", k, got[k], w)
		}
	}
}

// Salvage carries its stored skip-decay mark: RG-001's 2434 battle salvage
// at (1324, 1257) starts year 6 marked fresh; MF-13b's mine-hit salvage at
// (1400, 1400) is not.
func TestSalvageFresh(t *testing.T) {
	for file, want := range map[string]bool{"rg/rg001-y6.json": true, "mf/mf13b.json": false} {
		v, err := Load("../../vectors/" + file)
		if err != nil {
			t.Fatal(err)
		}
		n := 0
		for _, o := range v.InitialState.Objects {
			if o.Kind != "salvage" {
				continue
			}
			n++
			if o.Fresh == nil || *o.Fresh != want {
				t.Errorf("%s salvage %d at (%d, %d): fresh %v, want %v", file, o.ID, o.X, o.Y, o.Fresh, want)
			}
		}
		if n != 1 {
			t.Errorf("%s: %d salvage records, want 1", file, n)
		}
	}
	bad := Vector{ID: "x", InitialState: &State{Objects: []Object{{Kind: "salvage"}}}}
	found := false
	for _, e := range bad.Check() {
		found = found || strings.Contains(e.Error(), "fresh")
	}
	if !found {
		t.Error("Check accepts salvage without fresh")
	}
}

// The client injects its default-queue record (block 46) into player 0's
// first-year orders; RG-002 carries it as a default_queue order there only.
func TestDefaultQueueOrder(t *testing.T) {
	for y := 1; y <= 6; y++ {
		file := fmt.Sprintf("../../vectors/rg/rg002-y%d.json", y)
		v, err := Load(file)
		if err != nil {
			t.Fatal(err)
		}
		n := 0
		for _, s := range v.Orders {
			for _, o := range s.Orders {
				if o.Kind != "default_queue" {
					continue
				}
				n++
				if s.Player != 0 || s.Year != 1 || o.Items == nil || len(o.Items) != 0 ||
					o.LeftoverToResearch == nil || *o.LeftoverToResearch {
					t.Errorf("%s: default_queue order %+v in year %d player %d", file, o, s.Year, s.Player)
				}
			}
		}
		if want := map[bool]int{true: 1, false: 0}[y == 1]; n != want {
			t.Errorf("%s: %d default_queue orders, want %d", file, n, want)
		}
	}
	bad := Vector{ID: "x", Years: 1, InitialState: &State{Players: []Player{{ID: 0}}}, Orders: []OrderSet{{Year: 1, Player: 0, Orders: []Order{{Kind: "default_queue", Items: []QueueItem{}}}}}}
	found := false
	for _, e := range bad.Check() {
		found = found || strings.Contains(e.Error(), "leftover_to_research")
	}
	if !found {
		t.Error("Check accepts a default_queue order without leftover_to_research")
	}
}

// RG-002 player 0's default queue is the edited one (experiments/rg002:
// Auto Factories 100, Auto Mines 100, Auto Defenses 20, Auto Min and Max
// Terraform 5) at year 1's start and empty from year 2 on (the host
// emptied it in year 1, PARITY "Representative game (RG-002)"); the
// computer players' is empty throughout.
func TestDefaultQueue(t *testing.T) {
	want := []QueueItem{{ID: 1, Count: 100}, {ID: 0, Count: 100}, {ID: 2, Count: 20}, {ID: 4, Count: 5}, {ID: 5, Count: 5}}
	for y := 1; y <= 6; y++ {
		file := fmt.Sprintf("../../vectors/rg/rg002-y%d.json", y)
		v, err := Load(file)
		if err != nil {
			t.Fatal(err)
		}
		for _, p := range v.InitialState.Players {
			if p.DefaultLeftover == nil || *p.DefaultLeftover {
				t.Errorf("%s player %d: default_leftover_to_research %v, want false", file, p.ID, p.DefaultLeftover)
			}
			w := want
			if p.ID != 0 || y > 1 {
				w = nil
			}
			if len(p.DefaultQueue) != len(w) {
				t.Errorf("%s player %d: default_queue %+v, want %+v", file, p.ID, p.DefaultQueue, w)
				continue
			}
			for i, it := range p.DefaultQueue {
				if it.ID != w[i].ID || it.Count != w[i].Count || it.Kind == nil || *it.Kind != 1 {
					t.Errorf("%s player %d: default_queue[%d] = %+v, want %+v kind 1", file, p.ID, i, it, w[i])
				}
			}
		}
	}
	one, two := 1, 2
	for _, p := range []Player{
		{ID: 0, DefaultQueue: []QueueItem{}},
		{ID: 0, DefaultQueue: []QueueItem{{ID: 0, Count: 5, Kind: &one, Percent: 3}}, DefaultLeftover: new(bool)},
		{ID: 0, DefaultQueue: []QueueItem{{ID: 0, Count: 5, Kind: &two}}, DefaultLeftover: new(bool)},
	} {
		bad := Vector{ID: "x", InitialState: &State{Players: []Player{p}}}
		found := false
		for _, e := range bad.Check() {
			found = found || strings.Contains(e.Error(), "default_")
		}
		if !found {
			t.Errorf("Check accepts player %+v", p)
		}
	}
}

func TestRG001Artifact(t *testing.T) {
	v, err := Load("../../vectors/rg/rg001-y1.json")
	if err != nil {
		t.Fatal(err)
	}
	art := map[int]bool{}
	for _, p := range v.InitialState.Planets {
		if p.Artifact {
			art[p.ID] = true
		}
	}
	if !art[81] || art[32] || art[77] {
		t.Errorf("artifacts on %v: want 81, not 32 or 77", art)
	}
}

// TestStartSample checks that every RG battle record says whether its start
// tokens were drawn, and the RG-003 count (vectors/README "start_sample").
func TestStartSample(t *testing.T) {
	for _, f := range []string{"rg001", "rg002", "rg003"} {
		v, err := Load("../../vectors/rg/" + f + ".json")
		if err != nil {
			t.Fatal(err)
		}
		n, fixed := 0, 0
		for _, c := range v.Cases {
			for _, e := range c.Expect {
				if e.Kind != "battle" {
					continue
				}
				n++
				if e.StartSample == nil {
					t.Errorf("%s: battle at (%d,%d) without start_sample", c.ID, *e.X, *e.Y)
				} else if !*e.StartSample {
					fixed++
				}
			}
		}
		if f == "rg003" && (n != 102 || fixed != 100) {
			t.Errorf("rg003: %d battles, %d with fixed start tokens; want 102, 100", n, fixed)
		}
	}
	f := false
	bad := Vector{ID: "x", Years: 1, InitialState: &State{Players: []Player{{ID: 0}}},
		Cases: []Case{{ID: "x", Tag: "MEASURED", Expect: []Expectation{{Year: 1, Kind: "battle_actions",
			Actions: json.RawMessage(`[]`), StartSample: &f}}}}}
	found := false
	for _, err := range bad.Check() {
		found = found || strings.Contains(err.Error(), "start_sample")
	}
	if !found {
		t.Error("Check accepts start_sample on battle_actions")
	}
}

// TestMessageSequence checks that each player's message sequence holds the
// same ids as its `message` expectations, in a corpus of each builder, and
// that Check refuses a malformed entry.
func TestMessageSequence(t *testing.T) {
	type key struct {
		stream       string
		year, player int
	}
	for _, file := range []string{"../../vectors/rg/rg002.json", "../../vectors/kx005/t0.json", "../../vectors/pq/c01.json"} {
		v, err := Load(file)
		if err != nil {
			t.Fatal(err)
		}
		ids, seqs := map[key]map[int]bool{}, map[key]map[int]bool{}
		summaries, drawn := 0, 0
		for _, c := range v.Cases {
			for _, e := range c.Expect {
				if e.Player == nil {
					continue
				}
				k := key{e.Stream, e.Year, *e.Player}
				switch {
				case e.Kind == "message" && e.Present != nil && *e.Present:
					if ids[k] == nil {
						ids[k] = map[int]bool{}
					}
					ids[k][*e.MessageID] = true
				case e.Kind == "message_sequence":
					if seqs[k] != nil {
						t.Errorf("%s: two sequences for %+v", file, k)
					}
					seqs[k] = map[int]bool{}
					for _, m := range e.Messages {
						seqs[k][m.ID] = true
						// battle summaries (MESSAGES.md 0x091-0x0a8, 0x113-0x116) follow the draws
						summary := m.ID >= 0x091 && m.ID <= 0x0a8 || m.ID >= 0x113 && m.ID <= 0x116
						if summary && !m.Sample {
							t.Errorf("%s %+v: battle summary %#x not a sample", file, k, m.ID)
						}
						if summary {
							summaries++
						}
						// a build at planet 95 that another stream did not repeat (no battle there)
						if c.ID == "RG-002-2464" && *e.Player == 0 && m.ID == 0x036 && m.Focus == 95 && m.Sample {
							drawn++
						}
					}
				}
			}
		}
		if len(seqs) == 0 {
			t.Errorf("%s: no message_sequence", file)
		}
		if strings.Contains(file, "rg002") && (summaries == 0 || drawn != 1) {
			t.Errorf("%s: %d battle summaries, %d drawn builds at planet 95 in 2464; want some and 1", file, summaries, drawn)
		}
		for k, s := range seqs {
			want := map[int]bool{}
			for _, st := range []string{"", k.stream} { // ids every stream got are listed once, without a stream
				for id := range ids[key{st, k.year, k.player}] {
					want[id] = true
				}
			}
			if fmt.Sprint(s) != fmt.Sprint(want) {
				t.Errorf("%s %+v: sequence ids %v, message ids %v", file, k, s, want)
			}
		}
	}
	p := 0
	for _, e := range []Expectation{
		{Year: 1, Kind: "message_sequence", Player: &p},
		{Year: 1, Kind: "message_sequence", Player: &p, Messages: []Message{{ID: 0x183}}},
		{Year: 1, Kind: "message_sequence", Player: &p, Messages: []Message{{ID: 1, Params: make([]int, 8)}}},
		{Year: 1, Kind: "message_sequence", Player: &p, Messages: []Message{{ID: 1, Focus: 0x10000}}},
		{Year: 1, Kind: "message_sequence", Player: &p, Messages: []Message{{ID: 1, Focus: -1}}},
		{Year: 1, Kind: "message_sequence", Messages: []Message{{ID: 1}}},
	} {
		bad := Vector{ID: "x", Years: 1, InitialState: &State{Players: []Player{{ID: 0}}},
			Cases: []Case{{ID: "x", Tag: "MEASURED", Expect: []Expectation{e}}}}
		found := false
		for _, err := range bad.Check() {
			found = found || strings.Contains(err.Error(), "message_sequence")
		}
		if !found {
			t.Errorf("Check accepts %+v", e)
		}
	}
}

func TestAltBattleFields(t *testing.T) {
	x, y := 10, 20
	for _, c := range []struct {
		e    Expectation
		errs int
	}{
		{Expectation{X: &x, Y: &y, Players: []int{0}, Sample: true}, 0},
		{Expectation{X: &x, Y: &y, Players: []int{0}}, 1},
		{Expectation{X: &x, Players: []int{0}, Sample: true}, 1},
		{Expectation{X: &x, Y: &y, Sample: true}, 1},
	} {
		c.e.Year, c.e.Kind = 1, "alt_battle"
		v := &Vector{Schema: Schema, ID: "T", Years: 1, Streams: 1,
			InitialState: &State{Game: Game{Players: 1}, Players: []Player{{ID: 0}}},
			Cases:        []Case{{ID: "T-1", Tag: "MEASURED", Expect: []Expectation{c.e}}}}
		if errs := v.Check(); len(errs) != c.errs {
			t.Errorf("%+v: want %d errors, got %v", c.e, c.errs, errs)
		}
	}
}
