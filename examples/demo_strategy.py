"""
In this example, two robots interact over a gridworld. The robot 1 is P1 and robot 2 is P2.

State: (p1.row, p1.col, p2.row, p2.col, turn)
Actions (P1): N, E, S, W.
Actions (P2): N, E, S, W.
Objective: Do not collide with each other while staying within the gridworld. That is, any action leading the robot
outside gridworld (e.g., actions S, W at (0, 0)) are disabled.
Termination Condition: If a robot is cornered (i.e. it does not have a safe action to play), the robot quits.

The robots execute a random strategy except when the robots are adjacent. When adjacent, the robots will choose
action to move away from the other robot. For example, if P1 is in (1, 0) and P2 is at (0, 0). Then, P1 will execute
"N" because P2 is 1-step south of P1, and P2 will execute "S" because P1 is 1-step north of P2.
"""
import itertools
from ggsolver.graph import Graph
from ggsolver.models import Game, Solver
from ggsolver.gw_util import *
from pprint import pprint


class GWGame(Game):
    SINK_STATE = "sink-state"

    def __init__(self, dim):
        super(GWGame, self).__init__(is_tb=True, is_stoch=False)
        self.dim = dim

    def states(self):
        rows = self.dim[0]
        cols = self.dim[1]
        states = list(itertools.product(range(rows), range(cols), range(rows), range(cols), range(1, 3)))
        states = states + [GWGame.SINK_STATE]
        return states

    def actions(self):
        return list(GW_ACT_4.keys())

    def delta(self, state, act):
        # If state is sink, next state is sink
        if state == GWGame.SINK_STATE:
            return GWGame.SINK_STATE

        # Decouple state
        p1_row, p1_col, p2_row, p2_col, turn = state

        # Get action function (standard functions are implemented in gridworld2.py)
        act_func = GW_ACT_4[act]

        if turn == 1:
            # Apply action to state
            n_p1_row, n_p1_col = act_func(p1_row, p1_col)

            # Validate new state is within boundary
            if is_cell_in_gridworld(n_p1_row, n_p1_col, self.dim):
                return n_p1_row, n_p1_col, p2_row, p2_col, 2
            else:
                return GWGame.SINK_STATE

        elif turn == 2:
            # Apply action to state
            n_p2_row, n_p2_col = act_func(p2_row, p2_col)

            # Validate new state is within boundary
            if is_cell_in_gridworld(n_p2_row, n_p2_col, self.dim):
                return p1_row, p1_col, n_p2_row, n_p2_col, 1
            else:
                return GWGame.SINK_STATE

    def turn(self, state):
        if state == GWGame.SINK_STATE:
            return -1
        return state[4]


class GWStrategy(Solver):
    def pi1(self, state):
        if state == GWGame.SINK_STATE:
            return []

        _, _, _, _, turn = state
        if turn != 1:
            return []

        strategy = []
        for act in self.game.actions():
            # Apply action to see what's the next state.
            n_state = self.game.delta(state, act)

            # If no collision and the action does not lead robot outside the gridworld, then add it to strategy.
            if n_state == GWGame.SINK_STATE:
                continue

            # Decouple next state
            n_p1_row, n_p1_col, n_p2_row, n_p2_col, _ = n_state

            # If the next state results in collision, then strategy is to select the opposite action.
            #   The opposite action should be valid (i.e. must not lead the robot outside the gridworld).
            if n_p1_row == n_p2_row and n_p1_col == n_p2_col:
                if act == "N" and self.game.delta(state, "S") != GWGame.SINK_STATE:
                    return ["S"]
                elif act == "E" and self.game.delta(state, "W") != GWGame.SINK_STATE:
                    return ["W"]
                elif act == "S" and self.game.delta(state, "N") != GWGame.SINK_STATE:
                    return ["N"]
                elif act == "W" and self.game.delta(state, "E") != GWGame.SINK_STATE:
                    return ["E"]
                else:
                    return []

            # If no collision and the action does not lead robot outside the gridworld, then add it to strategy.
            strategy.append(act)

        return strategy

    def pi2(self, state):
        if state == GWGame.SINK_STATE:
            return []

        _, _, _, _, turn = state
        if turn != 2:
            return []

        strategy = []
        for act in self.game.actions():
            # Apply action to see what's the next state.
            n_state = self.game.delta(state, act)

            # If no collision and the action does not lead robot outside the gridworld, then add it to strategy.
            if n_state == GWGame.SINK_STATE:
                continue

            # Decouple next state
            n_p1_row, n_p1_col, n_p2_row, n_p2_col, _ = n_state

            # If the next state results in collision, then strategy is to select the opposite action.
            #   The opposite action should be valid (i.e. must not lead the robot outside the gridworld).
            if n_p1_row == n_p2_row and n_p1_col == n_p2_col:
                if act == "N" and self.game.delta(state, "S") != GWGame.SINK_STATE:
                    return ["S"]
                elif act == "E" and self.game.delta(state, "W") != GWGame.SINK_STATE:
                    return ["W"]
                elif act == "S" and self.game.delta(state, "N") != GWGame.SINK_STATE:
                    return ["N"]
                elif act == "W" and self.game.delta(state, "E") != GWGame.SINK_STATE:
                    return ["E"]
                else:
                    return []

            # If no collision and the action does not lead robot outside the gridworld, then add it to strategy.
            strategy.append(act)

        return strategy


if __name__ == '__main__':
    game = GWGame(dim=(4, 4))
    print(game.delta(state=(0, 0, 1, 1, 1), act="S"))
    print(game.delta(state=(0, 0, 1, 1, 1), act="N"))

    strategy = GWStrategy()
    strategy.load_game(game)
    print(strategy.pi1(state=(0, 1, 1, 1, 1)))
    print(strategy.pi2(state=(0, 1, 1, 1, 2)))

    # graph = game.graphify()
    # pprint(graph.serialize())
    game.save("gwgame1.game", overwrite=True)
    game_graph = Graph.load("gwgame1.game")
    pprint(game_graph.serialize())

    strategy.save("gwgame1.strategy", overwrite=True)
    solver_object = Solver.load("gwgame1.strategy")
    print(solver_object._state2node[(0, 0, 0, 0, 1)])
    print(solver_object._state2node["sink-state"])
    print(solver_object.actions())
    print(solver_object.is_turn_based())
    print("turn: ", solver_object.turn((0, 0, 0, 0, 1)))
    print("turn: ", solver_object.turn((0, 0, 1, 0, 2)))
    print("pi1: ", solver_object.pi1((0, 0, 2, 0, 1)))
    print("pi2: ", solver_object.pi2((0, 0, 1, 0, 2)))
    print("delta: ", solver_object.delta((0, 0, 1, 0, 2), "N"))
