// engine/turn.go
package engine

type Game struct {
	Year int
}

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
