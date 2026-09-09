// engine/turn.go
package engine

type Game struct {
	Year int
}

// todo: move to planet.go or similar
type Planet struct {
	Habitability int // -100 - 100, will be derived from environment + faction
	Population   int64
}

type Faction struct {
	GrowthRate int // percent per year
}

// stubs
type PlayerOrders struct{}
type Ruleset interface{}
type JRC3Rules struct{}

func Jrc3() Ruleset {
	return JRC3Rules{}
}

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

func PopulationGrowth(
	planet Planet,
	faction Faction,
	rules Ruleset,
) int64 {
	if planet.Habitability <= 0 {
		return 0 // hostile-world deaths come next
	}

	return planet.Population *
		int64(faction.GrowthRate) *
		int64(planet.Habitability) /
		10_000
}
