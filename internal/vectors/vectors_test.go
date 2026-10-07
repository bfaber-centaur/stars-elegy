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
