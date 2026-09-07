// engine/turn_test.go
package engine

import "testing"

func TestGenerateTurnAdvancesYear(t *testing.T) {
	game := Game{
		Year: 2400,
	}

	result, err := GenerateTurn(game, nil, nil)
	if err != nil {
		t.Fatalf("GenerateTurn() error = %v", err)
	}

	if got, want := result.Game.Year, 2401; got != want {
		t.Errorf("year = %d, want %d", got, want)
	}
}
