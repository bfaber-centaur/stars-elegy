// engine/turn.go
package engine

type Game struct {
	Year int
}

// todo: move to planet.go or similar
type Planet struct {
	Habitability int // -100 - 100, will be derived from environment + faction
}

// stubs
type Faction struct{}
type PlayerOrders struct{}
type Ruleset interface{}

type TurnResult struct {
	Game Game
}

func GenerateTurn(
	game Game,
	orders []PlayerOrders,
	rules Ruleset,
) (TurnResult, error) {
	game.Year++

	return TurnResult{
		Game: game,
	}, nil
}

// todo: move to planet.go or similar
func PopulationCapacity(
	planet Planet,
	faction Faction,
	rules Ruleset,
) int64 {
	hab := planet.Habitability

	if hab <= 0 {
		return 0
	}

	if hab < 5 {
		hab = 5
	}

	return 1_000_000 * int64(hab) / 100
}
