package vectors

import "testing"

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
