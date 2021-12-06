import logging
import random
from ggsolver.oneplayer.model import OnePlayerGame
from functools import reduce


class SWinReach:
    """
    Sure winning region and strategy for one-player game. This is simple path planning on directed graph.

    Notes.
        * Each solver instance is defined as a triple of game object, set of final states and the player who
        has the reachability objective.
        * Solver constructs two data structures:
            1. `attractor`: which represents the level-set of winning states for the player with reachability task.
            2. `win_edges`: winning edges for the player with reachability task. These edges are used to define
                    P1's and P2's winning strategies.
    """

    def __init__(self, game, final):
        assert isinstance(game, OnePlayerGame), f"Input `game` must be a OnePlayerGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = 1
        self.attractor = list()         # attractor_p is level set of winning states for reachability player
        self.strategy = dict()          # winning strategy of reachability player
        self._is_solved = False

    def reset(self):
        self.attractor = list()         # attractor is for the player with reachability objective: self.player
        self.strategy = set()           # win_edges is for the player with reachability objective: self.player
        self._is_solved = False

    def solve(self):
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve SWinReach({self.game}, {self.final}, {self.player}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Fixed point computation
        self.attractor = [set(self.final)]
        while True:
            # Evaluate one-step reachability
            win_states, strategy = self._pre(self.attractor)

            # Loop termination condition
            if len(win_states) == 0:
                break

            # Update data structures
            self.attractor.append(win_states)
            self.strategy.update(strategy)

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        try:
            return list(self.strategy[v].keys())[0]
        except KeyError:
            return None

    def p2_strategy(self, v):
        raise ValueError("P2 strategy is undefined in one-player game.")

    def _pre(self, attractor):
        # Initialize data structure to store newly identified winning states and strategy
        p_new_win_states = set()
        p_new_win_strategy = dict()

        # Collect all winning states
        p_win_states = set(reduce(set.union, attractor))

        for v in p_win_states:
            pred_v = self.game.pred(v)
            for u, a in pred_v:
                p_win_states.add(u)
                p_new_win_strategy[u].update({a, v})

        return p_new_win_states, p_new_win_strategy

    @property
    def p1_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.strategy

    @property
    def p2_strategy_map(self):
        raise ValueError("P2 strategy is undefined in one-player game.")

    @property
    def p1_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return set(reduce(set.union, self.attractor))

    @property
    def p2_winning_region(self):
        raise ValueError("P2 strategy is undefined in one-player game.")


class ASWinReach(SWinReach):
    def p1_strategy(self, v):
        try:
            return random.choice(list(self.strategy[v].keys()))
        except KeyError:
            return None

    def p2_strategy(self, v):
        raise ValueError("P2 strategy is undefined in one-player game.")