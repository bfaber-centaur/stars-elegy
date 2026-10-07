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
	Schema       string   `json:"schema"`
	ID           string   `json:"id"`
	Title        string   `json:"title"`
	Source       Source   `json:"source"`
	Years        int      `json:"years"`
	Random       string   `json:"random"`
	Streams      int      `json:"streams"`
	InitialState *State   `json:"initial_state,omitempty"`
	NewGame      *NewGame `json:"new_game,omitempty"`
	// Orders are the orders players submitted, per year and player, in
	// the order they were given. Without them, the orders are the fleets'
	// waypoints and the other standing orders in the initial state.
	Orders []OrderSet `json:"orders,omitempty"`
	Cases  []Case     `json:"cases"`
}

// OrderSet is what one player submitted for one generated year.
type OrderSet struct {
	Year   int     `json:"year"`
	Player int     `json:"player"`
	Orders []Order `json:"orders"`
}

// Order is one player order in behavior terms; Kind selects the fields
// that apply (vectors/README.md "Orders"). Fleets, planets, designs and
// plans are the submitting player's unless a field says otherwise.
type Order struct {
	Kind string `json:"kind"`

	Fleet  *int `json:"fleet,omitempty"`
	Planet *int `json:"planet,omitempty"`
	Slot   *int `json:"slot,omitempty"`
	Index  *int `json:"index,omitempty"`

	// cargo: With is the other side; Amounts are signed, positive into the fleet
	With    *Target        `json:"with,omitempty"`
	Amounts map[string]int `json:"amounts,omitempty"`
	// production_queue: the planet's whole new queue
	Items []QueueItem `json:"items,omitempty"`
	// research
	Percent   *int   `json:"percent,omitempty"`
	Field     string `json:"field,omitempty"`
	NextField any    `json:"next_field,omitempty"` // a field, "lowest", or the stored number
	// battle_plan
	Name      string `json:"name,omitempty"`
	Tactic    *int   `json:"tactic,omitempty"`
	Primary   *int   `json:"primary,omitempty"`
	Secondary *int   `json:"secondary,omitempty"`
	AttackWho *int   `json:"attack_who,omitempty"`
	DumpCargo *bool  `json:"dump_cargo,omitempty"`
	// fleet_battle_plan
	Plan *int `json:"plan,omitempty"`
	// design, design_delete
	Starbase *bool   `json:"starbase,omitempty"`
	Hull     string  `json:"hull,omitempty"`
	Slots    []*Part `json:"slots,omitempty"`
	// waypoint_add, waypoint_change
	Waypoint *Waypoint `json:"waypoint,omitempty"`
	// repeat_orders, detonate
	On *bool `json:"on,omitempty"`
	// split: the ships that leave; merge: the fleets joining Fleet
	Ships  []Ships `json:"ships,omitempty"`
	Fleets []int   `json:"fleets,omitempty"`
	// detonate
	Minefield *int `json:"minefield,omitempty"`
	// planet_settings
	LeftoverToResearch *bool `json:"leftover_to_research,omitempty"`
	RouteTo            *int  `json:"route_to,omitempty"`
	// relations
	Relations map[string]string `json:"relations,omitempty"`
}

// OrderFields lists each order kind and the fields it needs.
var OrderFields = map[string][]string{
	"production_queue":   {"planet", "items"},
	"planet_settings":    {"planet"},
	"research":           {"percent", "field"},
	"battle_plan":        {"slot", "tactic", "primary", "secondary", "attack_who"},
	"battle_plan_delete": {"slot"},
	"fleet_battle_plan":  {"fleet", "plan"},
	"design":             {"slot", "starbase", "hull"},
	"design_delete":      {"slot", "starbase"},
	"waypoint_add":       {"fleet", "index", "waypoint"},
	"waypoint_change":    {"fleet", "index", "waypoint"},
	"waypoint_delete":    {"fleet", "index"},
	"repeat_orders":      {"fleet", "on"},
	"cargo":              {"fleet", "with", "amounts"},
	"split":              {"fleet", "ships"},
	"merge":              {"fleet", "fleets"},
	"rename":             {"fleet", "name"},
	"detonate":           {"minefield", "on"},
	"relations":          {"relations"},
}

func (o *Order) has(f string) bool {
	switch f {
	case "fleet":
		return o.Fleet != nil
	case "planet":
		return o.Planet != nil
	case "slot":
		return o.Slot != nil
	case "index":
		return o.Index != nil
	case "items":
		return o.Items != nil
	case "percent":
		return o.Percent != nil
	case "field":
		return o.Field != ""
	case "tactic":
		return o.Tactic != nil
	case "primary":
		return o.Primary != nil
	case "secondary":
		return o.Secondary != nil
	case "attack_who":
		return o.AttackWho != nil
	case "plan":
		return o.Plan != nil
	case "starbase":
		return o.Starbase != nil
	case "hull":
		return o.Hull != ""
	case "waypoint":
		return o.Waypoint != nil
	case "on":
		return o.On != nil
	case "with":
		return o.With != nil
	case "amounts":
		return o.Amounts != nil
	case "ships":
		return o.Ships != nil
	case "fleets":
		return o.Fleets != nil
	case "name":
		return o.Name != ""
	case "minefield":
		return o.Minefield != nil
	case "relations":
		return o.Relations != nil
	}
	return false
}

// NewGame replaces InitialState in a universe-generation vector (years 0):
// the new-game settings and the players' races; the cases describe the
// generated turn-0 game.
type NewGame struct {
	Settings json.RawMessage `json:"settings"`
	Races    json.RawMessage `json:"races"`
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
	Name              string                      `json:"name"`
	Size              string                      `json:"size"`
	Bounds            []int                       `json:"bounds,omitempty"`
	Density           string                      `json:"density,omitempty"`
	Players           int                         `json:"players"`
	RandomEvents      *bool                       `json:"random_events,omitempty"`
	SlowerTech        *bool                       `json:"slower_tech,omitempty"`
	PublicScores      *bool                       `json:"public_scores,omitempty"`
	VictoryConditions map[string]VictoryCondition `json:"victory_conditions,omitempty"`
}

type VictoryCondition struct {
	Value   int   `json:"value"`
	Enabled *bool `json:"enabled,omitempty"`
}

type Player struct {
	ID                  int               `json:"id"`
	Tech                map[string]int    `json:"tech"`
	ResearchAccumulated map[string]int    `json:"research_accumulated"`
	ResearchPercent     int               `json:"research_percent"`
	ResearchField       string            `json:"research_field"`
	Relations           map[string]string `json:"relations"`
	MysteryTraderItems  []string          `json:"mystery_trader_items"`
	Computer            bool              `json:"computer,omitempty"` // a computer player: the host plans its orders
	Race                Race              `json:"race"`
	Counts              struct {
		ShipDesigns     int `json:"ship_designs"`
		StarbaseDesigns int `json:"starbase_designs"`
	} `json:"counts"`
}

type Race struct {
	PRT           any      `json:"prt"` // a name, or the stored number when out of range
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
	LeftoverSpend        any               `json:"leftover_spend"`
	Stat15               int               `json:"stat_15"`
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
	RouteTo             *int      `json:"route_to,omitempty"` // the planet's route destination
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
	Owner        int            `json:"owner"`
	ID           int            `json:"id"`
	X            int            `json:"x"`
	Y            int            `json:"y"`
	Orbiting     *int           `json:"orbiting"`
	Ships        []Ships        `json:"ships"`
	Cargo        map[string]int `json:"cargo"`
	Fuel         int            `json:"fuel"`
	BattlePlan   int            `json:"battle_plan"`
	Waypoints    []Waypoint     `json:"waypoints"`
	RepeatOrders bool           `json:"repeat_orders,omitempty"`
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
	Range    *int                  `json:"range,omitempty"` // patrol
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
	Planet int         `json:"planet"`
	Items  []QueueItem `json:"items"`
}

type QueueItem struct {
	ID      int  `json:"id"`
	Count   int  `json:"count"`
	Percent int  `json:"percent,omitempty"`
	Kind    *int `json:"kind"`
}

type Case struct {
	ID             string        `json:"id"`
	Rule           string        `json:"rule"`
	Setup          string        `json:"setup"`
	Tag            string        `json:"tag"`
	PredictionHeld bool          `json:"prediction_held"`
	VariesByStream bool          `json:"varies_by_stream"`
	Prediction     string        `json:"prediction,omitempty"`
	Verdict        string        `json:"verdict,omitempty"`
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
	SeenBy      *int            `json:"seen_by,omitempty"` // the player whose file showed it
	Slot        *int            `json:"slot,omitempty"`
	X           *int            `json:"x,omitempty"`
	Y           *int            `json:"y,omitempty"`
	Equals      json.RawMessage `json:"equals,omitempty"`
	Tolerance   any             `json:"tolerance,omitempty"` // ly for a packet, or {field: amount}
	MessageID   *int            `json:"message_id,omitempty"`
	Present     *bool           `json:"present,omitempty"`
	ObservedNew []int           `json:"observed_new,omitempty"`
	Check       string          `json:"check,omitempty"`
	Target      json.RawMessage `json:"target,omitempty"`
	Observed    json.RawMessage `json:"observed,omitempty"`
	Constraint  json.RawMessage `json:"constraint,omitempty"`

	// battle, battle_actions
	Players []int           `json:"players,omitempty"`
	Tokens  json.RawMessage `json:"tokens,omitempty"`
	Actions json.RawMessage `json:"actions,omitempty"`
	// view: what player Viewer knows of Subject; client_estimate: a value
	// the original client displays on Screen for Subject
	Viewer  *int            `json:"viewer,omitempty"`
	Subject json.RawMessage `json:"subject,omitempty"`
	Screen  string          `json:"screen,omitempty"`
	Field   string          `json:"field,omitempty"`
}

var (
	Tags  = map[string]bool{"CONFIRMED": true, "MEASURED": true, "LEGACY BUG": true}
	Kinds = map[string]bool{"fleet": true, "fleet_gone": true, "fleet_at": true, "no_fleet_at": true,
		"no_new_fleets": true, "planet": true, "production_queue": true, "design": true, "player": true,
		"wormhole": true, "trader": true, "packet": true, "packet_gone": true, "salvage_at": true,
		"message": true, "sample": true, "battle": true, "battle_actions": true, "no_battle": true,
		"object": true, "object_gone": true, "minefield": true, "view": true, "client_estimate": true,
		"battle_plan": true, "battle_plan_gone": true, "design_gone": true, "starbase_design": true,
		"starbase_design_gone": true}
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
	if (v.InitialState == nil) == (v.NewGame == nil) {
		bad("needs exactly one of initial_state and new_game")
		return errs
	}
	if v.NewGame != nil && v.Years != 0 || v.InitialState != nil && v.Years < 1 {
		bad("years %d (0 only for a new_game vector)", v.Years)
	}
	if v.Streams < 1 || len(v.Cases) == 0 {
		bad("streams %d, %d cases", v.Streams, len(v.Cases))
	}
	players, planets := map[int]bool{}, map[int]bool{}
	if st := v.InitialState; st != nil {
		for _, p := range st.Players {
			players[p.ID] = true
		}
		if len(players) != st.Game.Players {
			bad("%d players, game says %d", len(players), st.Game.Players)
		}
		for _, p := range st.Planets {
			planets[p.ID] = true
		}
	}
	known := func(m map[int]bool, id int) bool { return v.NewGame != nil || m[id] }
	for _, set := range v.Orders {
		if set.Year < 1 || set.Year > v.Years || !known(players, set.Player) {
			bad("orders for year %d, player %d", set.Year, set.Player)
		}
		for i, o := range set.Orders {
			need, ok := OrderFields[o.Kind]
			if !ok {
				bad("order %d: kind %q", i, o.Kind)
				continue
			}
			for _, f := range need {
				if !o.has(f) {
					bad("order %d (%s): no %s", i, o.Kind, f)
				}
			}
		}
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
		if c.Tag == "CONFIRMED" && !c.PredictionHeld {
			bad("%s: CONFIRMED but the prediction did not hold", c.ID)
		}
		if len(c.Expect) == 0 {
			bad("%s: no expectations", c.ID)
		}
		for _, e := range c.Expect {
			if !Kinds[e.Kind] {
				bad("%s: kind %q", c.ID, e.Kind)
				continue
			}
			if e.Year < 1 && v.NewGame == nil || e.Year > v.Years {
				bad("%s: year %d outside 1..%d", c.ID, e.Year, v.Years)
			}
			if e.Kind == "sample" && (e.Check == "" || e.Observed == nil) {
				bad("%s: sample without check or observed", c.ID)
			}
			if e.Kind == "sample" && c.Tag == "CONFIRMED" {
				bad("%s: CONFIRMED case with a sampled expectation", c.ID)
			}
			if (e.Kind == "battle" && e.Tokens == nil) || (e.Kind == "battle_actions" && e.Actions == nil) ||
				(e.Kind == "view" && (e.Viewer == nil || e.Subject == nil)) ||
				(e.Kind == "client_estimate" && (e.Screen == "" || e.Subject == nil || e.Field == "")) {
				bad("%s: %s expectation missing its fields", c.ID, e.Kind)
			}
			for _, o := range []*int{e.Owner, e.Player} {
				if o != nil && *o >= 0 && !known(players, *o) {
					bad("%s: player %d not in the initial state", c.ID, *o)
				}
			}
			if e.Kind == "player" && (e.ID == nil || !known(players, *e.ID)) {
				bad("%s: player expectation without a known player id", c.ID)
			}
			if (e.Kind == "planet" && (e.ID == nil || !known(planets, *e.ID))) ||
				(e.Kind == "production_queue" && (e.Planet == nil || !known(planets, *e.Planet))) {
				bad("%s: planet not in the initial state", c.ID)
			}
			if e.Equals == nil && (e.Kind == "fleet" || e.Kind == "planet" || e.Kind == "player" ||
				e.Kind == "design" || e.Kind == "wormhole" || e.Kind == "trader" || e.Kind == "production_queue" ||
				e.Kind == "minefield" || e.Kind == "view" || e.Kind == "client_estimate" || e.Kind == "object" ||
				e.Kind == "battle_plan" || e.Kind == "starbase_design") {
				bad("%s: %s expectation without equals", c.ID, e.Kind)
			}
		}
	}
	return errs
}
