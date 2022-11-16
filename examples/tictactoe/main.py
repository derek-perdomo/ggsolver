import itertools

from ggsolver.gridworld.models import *
from ggsolver.models import Game


class TicTacToe(Game):
    def __init__(self, init_player=1):
        super(TicTacToe, self).__init__(is_deterministic=True)
        self.init_player = init_player
        self.winning_cell_combinations = [
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

    def states(self):
        # player 0: cell is unmarked, 1 means marked by P1, 2 means marked by P2.
        mark = [0, 1, 2]
        return list(itertools.product(mark, repeat=9))

    def actions(self):
        # (cell, player) means mark 'cell' to be 'player's cell.
        return [(cell, player) for cell in range(9) for player in range(3)]

    def delta(self, state, act):
        cell, player = act
        turn = self.turn(state)
        if state[cell] == 0 and turn == player:
            n_state = list(state)
            n_state[cell] = player
            return tuple(n_state)
        return state

    def atoms(self):
        return ["win", "draw", "lose"]

    def label(self, state):
        for c1, c2, c3 in self.winning_cell_combinations:
            if state[c1] == state[c2] == state[c3] == 1:
                return ["win"]
            if state[c1] == state[c2] == state[c3] == 2:
                return ["lose"]
        if all(cell_marked_with in [1, 2] for cell_marked_with in state):
            return ["draw"]
        return []

    def turn(self, state):
        if state.count(1) % 2 == 0:
            return self.init_player
        else:
            return 2 if self.init_player == 1 else 1

    def init_state(self):
        return (0, ) * 9


if __name__ == '__main__':
    game = TicTacToe()
    game.initialize(game.init_state())
    graph = game.graphify(pointed=True)
    print(f"{graph.number_of_nodes()}")
    print(f"{graph.number_of_edges()}")
