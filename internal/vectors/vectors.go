// Package vectors reads and checks the public parity vectors in vectors/.
//
// A vector is one oracle run: the initial state in behavior terms, the
// number of years the original game generated, and the cases observed at
// the end. vectors/README.md describes the format for implementers; the
// types here are its machine-checked form. Decoding is strict, so a field
// a builder adds without updating these types fails the tests.
package vectors

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

const Schema = "stars-elegy-vector/1"

type Vector struct {
	Schema       string `json:"schema"`
	ID           string `json:"id"`
	Title        string `json:"title"`
	Source       Source `json:"source"`
	Years        int    `json:"years"`
	Random       string `json:"random"`
	Streams      int    `json:"streams"`
	InitialState State  `json:"initial_state"`
	Cases        []Case `json:"cases"`
}

type Source struct {
	Experiment  string `json:"experiment"`
	SpecRules   string `json:"spec_rules"`
	Parity      string `json:"parity"`
	RawEvidence string `json:"raw_evidence"`
}

type State struct {
	Year             int               `json:"year"`
	Game             Game              `json:"game"`
	Players          []Player          `json:"players"`
	Planets          []Planet          `json:"planets"`
	Designs          []Design          `json:"designs"`
	StarbaseDesigns  []Design          `json:"starbase_designs"`
	BattlePlans      []BattlePlan      `json:"battle_plans"`
	Fleets           []Fleet           `json:"fleets"`
	Objects          []Object          `json:"objects"`
	ProductionQueues []ProductionQueue `json:"production_queues"`
}

type Game struct {
	Name         string `json:"name"`
	Size         string `json:"size"`
	Bounds       [4]int `json:"bounds"`
	Density      string `json:"density,omitempty"`
	RandomEvents bool   `json:"random_events"`
	Players      int    `json:"players"`
}

type Player struct {
	ID                  int               `json:"id"`
	Tech                map[string]int    `json:"tech"`
	ResearchAccumulated map[string]int    `json:"research_accumulated"`
	ResearchPercent     int               `json:"research_percent"`
	ResearchField       string            `json:"research_field"`
	Relations           map[string]string `json:"relations"`
	MysteryTraderItems  []string          `json:"mystery_trader_items"`
	Race                Race              `json:"race"`
	Counts              struct {
		ShipDesigns     int `json:"ship_designs"`
		StarbaseDesigns int `json:"starbase_designs"`
	} `json:"counts"`
}

type Race struct {
	PRT           string   `json:"prt"`
	LRT           []string `json:"lrt"`
	GrowthPercent int      `json:"growth_percent"`
	Habitability  struct {
		Gravity     [3]int `json:"gravity"`
		Temperature [3]int `json:"temperature"`
		Radiation   [3]int `json:"radiation"`
		Order       string `json:"order"`
	} `json:"habitability"`
	ColonistsPerResource int               `json:"colonists_per_resource"`
	Factory              Economy           `json:"factory"`
	Mine                 Economy           `json:"mine"`
	ResearchCost         map[string]string `json:"research_cost"`
	TechsStartHigh       bool              `json:"techs_start_high"`
	FactoriesCostLess    bool              `json:"factories_cost_less"`
}

type Economy struct {
	Output int `json:"output"`
	Cost   int `json:"cost"`
	Per10k int `json:"per_10k"`
}

type Planet struct {
	ID                  int       `json:"id"`
	X                   int       `json:"x"`
	Y                   int       `json:"y"`
	Owner               int       `json:"owner"`
	Concentrations      []int     `json:"concentrations"`
	Environment         []int     `json:"environment"`
	OriginalEnvironment []int     `json:"original_environment,omitempty"`
	SurfaceMinerals     []int     `json:"surface_minerals,omitempty"`
	Population          *int      `json:"population,omitempty"`
	Excess              *int      `json:"excess,omitempty"`
	Mines               *int      `json:"mines,omitempty"`
	Factories           *int      `json:"factories,omitempty"`
	Defenses            *int      `json:"defenses,omitempty"`
	PlanetaryScanner    *int      `json:"planetary_scanner,omitempty"`
	LeftoverToResearch  *bool     `json:"leftover_to_research,omitempty"`
	Starbase            *Starbase `json:"starbase,omitempty"`
}

type Starbase struct {
	Design *int `json:"design"`
	Damage int  `json:"damage"`
}

type Design struct {
	Owner int     `json:"owner"`
	Slot  int     `json:"slot"`
	Hull  string  `json:"hull"`
	Slots []*Part `json:"slots"`
	Mass  int     `json:"mass"`
}

type Part struct {
	Count int    `json:"count"`
	Part  string `json:"part"`
}

type BattlePlan struct {
	Owner     int    `json:"owner"`
	Slot      int    `json:"slot"`
	Tactic    int    `json:"tactic"`
	Primary   int    `json:"primary"`
	Secondary int    `json:"secondary"`
	AttackWho int    `json:"attack_who"`
	DumpCargo bool   `json:"dump_cargo"`
	Name      string `json:"name"`
}

type Fleet struct {
	Owner      int            `json:"owner"`
	ID         int            `json:"id"`
	X          int            `json:"x"`
	Y          int            `json:"y"`
	Orbiting   *int           `json:"orbiting"`
	Ships      []Ships        `json:"ships"`
	Cargo      map[string]int `json:"cargo"`
	Fuel       int            `json:"fuel"`
	BattlePlan int            `json:"battle_plan"`
	Waypoints  []Waypoint     `json:"waypoints"`
}

type Ships struct {
	Design int     `json:"design"`
	Count  int     `json:"count"`
	Damage *Damage `json:"damage,omitempty"`
}

type Damage struct {
	Units          int `json:"units"`
	PercentOfShips int `json:"percent_of_ships"`
}

type Waypoint struct {
	X      int    `json:"x"`
	Y      int    `json:"y"`
	Warp   int    `json:"warp"`
	Target Target `json:"target"`
	Task   Task   `json:"task"`
}

type Target struct {
	Kind  string `json:"kind"`
	ID    *int   `json:"id,omitempty"`
	Owner *int   `json:"owner,omitempty"`
}

type Task struct {
	Kind     string                `json:"kind"`
	Orders   map[string]CargoOrder `json:"orders,omitempty"`
	Years    any                   `json:"years,omitempty"`
	ToPlayer *int                  `json:"to_player,omitempty"`
}

type CargoOrder struct {
	Action string `json:"action"`
	Value  int    `json:"value"`
}

// Object is a wormhole end, Mystery Trader, mineral packet or minefield;
// Kind says which fields apply.
type Object struct {
	Kind               string `json:"kind"`
	ID                 int    `json:"id"`
	Owner              *int   `json:"owner,omitempty"`
	X                  int    `json:"x"`
	Y                  int    `json:"y"`
	Partner            *int   `json:"partner,omitempty"`
	StabilityClass     *int   `json:"stability_class,omitempty"`
	YearsSinceJump     *int   `json:"years_since_jump,omitempty"`
	KnownTo            []int  `json:"known_to,omitempty"`
	DestinationKnownTo []int  `json:"destination_known_to,omitempty"`
	Destination        []int  `json:"destination,omitempty"`
	DestinationPlanet  *int   `json:"destination_planet,omitempty"`
	Warp               *int   `json:"warp,omitempty"`
	Met                []int  `json:"met,omitempty"`
	Offer              string `json:"offer,omitempty"`
	Minerals           []int  `json:"minerals,omitempty"`
	DecayClass         *int   `json:"decay_class,omitempty"`
	Mines              *int   `json:"mines,omitempty"`
	Type               string `json:"type,omitempty"`
	Detonating         *bool  `json:"detonating,omitempty"`
}

type ProductionQueue struct {
	Planet int `json:"planet"`
	Items  []struct {
		ID    int  `json:"id"`
		Count int  `json:"count"`
		Kind  *int `json:"kind"`
	} `json:"items"`
}

type Case struct {
	ID             string        `json:"id"`
	Rule           string        `json:"rule"`
	Setup          string        `json:"setup"`
	Tag            string        `json:"tag"`
	PredictionHeld bool          `json:"prediction_held"`
	VariesByStream bool          `json:"varies_by_stream"`
	Prediction     string        `json:"prediction,omitempty"`
	VoidStreams    *VoidStreams  `json:"void_streams,omitempty"`
	Expect         []Expectation `json:"expect"`
}

type VoidStreams struct {
	Streams []string `json:"streams"`
	Reason  string   `json:"reason"`
}

// Expectation is one observed outcome. Kind selects the subject and the
// fields that apply (vectors/README.md); Equals holds the observed values
// of the subject's fields that the case checked.
type Expectation struct {
	Year        int             `json:"year"`
	Kind        string          `json:"kind"`
	Stream      string          `json:"stream,omitempty"`
	Owner       *int            `json:"owner,omitempty"`
	ID          *int            `json:"id,omitempty"`
	Planet      *int            `json:"planet,omitempty"`
	Player      *int            `json:"player,omitempty"`
	Slot        *int            `json:"slot,omitempty"`
	X           *int            `json:"x,omitempty"`
	Y           *int            `json:"y,omitempty"`
	Equals      json.RawMessage `json:"equals,omitempty"`
	Tolerance   int             `json:"tolerance,omitempty"`
	MessageID   *int            `json:"message_id,omitempty"`
	Present     *bool           `json:"present,omitempty"`
	ObservedNew []int           `json:"observed_new,omitempty"`
	Check       string          `json:"check,omitempty"`
	Target      json.RawMessage `json:"target,omitempty"`
	Observed    json.RawMessage `json:"observed,omitempty"`
	Constraint  json.RawMessage `json:"constraint,omitempty"`
}

var (
	Tags  = map[string]bool{"CONFIRMED": true, "MEASURED": true, "LEGACY BUG": true}
	Kinds = map[string]bool{"fleet": true, "fleet_gone": true, "fleet_at": true, "no_fleet_at": true,
		"no_new_fleets": true, "planet": true, "production_queue": true, "design": true, "player": true,
		"wormhole": true, "trader": true, "packet": true, "packet_gone": true, "salvage_at": true,
		"message": true, "sample": true}
)

// Load decodes one vector strictly.
func Load(path string) (*Vector, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	d := json.NewDecoder(bytes.NewReader(b))
	d.DisallowUnknownFields()
	var v Vector
	if err := d.Decode(&v); err != nil {
		return nil, fmt.Errorf("%s: %w", path, err)
	}
	return &v, nil
}

// LoadAll loads every vectors/<corpus>/*.json under dir, sorted by path.
func LoadAll(dir string) ([]*Vector, error) {
	paths, err := filepath.Glob(filepath.Join(dir, "*", "*.json"))
	if err != nil {
		return nil, err
	}
	sort.Strings(paths)
	var out []*Vector
	for _, p := range paths {
		v, err := Load(p)
		if err != nil {
			return nil, err
		}
		out = append(out, v)
	}
	return out, nil
}

// Check reports format errors: the schema version, tags and kinds, unique
// case ids, and that every expectation names a player, fleet owner or
// planet that exists in the initial state.
func (v *Vector) Check() []error {
	var errs []error
	bad := func(f string, a ...any) { errs = append(errs, fmt.Errorf(v.ID+": "+f, a...)) }
	if v.Schema != Schema {
		bad("schema %q", v.Schema)
	}
	if v.Years < 1 || v.Streams < 1 || len(v.Cases) == 0 {
		bad("years %d, streams %d, %d cases", v.Years, v.Streams, len(v.Cases))
	}
	players := map[int]bool{}
	for _, p := range v.InitialState.Players {
		players[p.ID] = true
	}
	if len(players) != v.InitialState.Game.Players {
		bad("%d players, game says %d", len(players), v.InitialState.Game.Players)
	}
	planets := map[int]bool{}
	for _, p := range v.InitialState.Planets {
		planets[p.ID] = true
	}
	seen := map[string]bool{}
	for _, c := range v.Cases {
		if seen[c.ID] {
			bad("duplicate case %s", c.ID)
		}
		seen[c.ID] = true
		if !Tags[c.Tag] {
			bad("%s: tag %q", c.ID, c.Tag)
		}
		if c.Tag == "CONFIRMED" && (!c.PredictionHeld || c.VariesByStream) {
			bad("%s: CONFIRMED but prediction_held=%v varies_by_stream=%v", c.ID, c.PredictionHeld, c.VariesByStream)
		}
		if len(c.Expect) == 0 {
			bad("%s: no expectations", c.ID)
		}
		for _, e := range c.Expect {
			if !Kinds[e.Kind] {
				bad("%s: kind %q", c.ID, e.Kind)
				continue
			}
			if e.Year < 1 || e.Year > v.Years {
				bad("%s: year %d outside 1..%d", c.ID, e.Year, v.Years)
			}
			if e.Kind == "sample" && (e.Check == "" || e.Observed == nil) {
				bad("%s: sample without check or observed", c.ID)
			}
			if e.Kind == "sample" && c.Tag == "CONFIRMED" {
				bad("%s: CONFIRMED case with a sampled expectation", c.ID)
			}
			for _, o := range []*int{e.Owner, e.Player} {
				if o != nil && !players[*o] {
					bad("%s: player %d not in the initial state", c.ID, *o)
				}
			}
			if e.Kind == "player" && (e.ID == nil || !players[*e.ID]) {
				bad("%s: player expectation without a known player id", c.ID)
			}
			if (e.Kind == "planet" && (e.ID == nil || !planets[*e.ID])) ||
				(e.Kind == "production_queue" && (e.Planet == nil || !planets[*e.Planet])) {
				bad("%s: planet not in the initial state", c.ID)
			}
			if e.Equals == nil && (e.Kind == "fleet" || e.Kind == "planet" || e.Kind == "player" ||
				e.Kind == "design" || e.Kind == "wormhole" || e.Kind == "trader" || e.Kind == "production_queue") {
				bad("%s: %s expectation without equals", c.ID, e.Kind)
			}
		}
	}
	return errs
}
