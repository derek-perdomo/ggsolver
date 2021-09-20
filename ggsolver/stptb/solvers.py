"""
Algorithms to compute almost-sure winning, losing and positive winning regions, strategies for a player in game on MDP.

References:
    * L. de Alfaro and T. A. Henzinger, "Concurrent omega-regular games," Proceedings Fifteenth Annual IEEE
        Symposium on Logic in Computer Science (Cat. No.99CB36332), 2000, pp. 141-154, doi: 10.1109/LICS.2000.855763.
    * De Alfaro, Luca, Thomas A. Henzinger, and Orna Kupferman. "Concurrent reachability games."
        Theoretical Computer Science 386.3 (2007): 188-217.
"""

import logging
import random
from functools import reduce
from ggsolver.stptb.model import StptbGame


class ASWinReach:
    """
    Almost-sure winning region and strategy for player 1 in stochastic two-player turn-based game.
    """

    def __init__(self, game, final, player=1):
        assert isinstance(game, StptbGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = player
        self.attractor_p = list()  # attractor_p is level set of winning states for reachability player
        self.attractor_np = list()  # attractor_np is level set of winning states for safety player
        self.strategy_p = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                           if self.game.get_state_property(u, "turn") == self.player}
        self.strategy_np = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                            if self.game.get_state_property(u, "turn") != self.player}
        self._is_solved = False

    def reset(self):
        self.attractor_p = list()   # attractor_p is level set of winning states for reachability player
        self.attractor_np = list()  # attractor_np is level set of winning states for safety player
        self.strategy_p = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                           if self.game.get_state_property(u, "turn") == self.player}
        self.strategy_np = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                            if self.game.get_state_property(u, "turn") != self.player}
        self._is_solved = False

    def solve(self):
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve SWinReach({self.game}, {self.final}, {self.player}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Initialize loop parameters
        self.attractor_p = [set(self.final)]
        set_c = []

        # Fixed point computation
        while True:
            if self.player == 1:
                set_y = self._safe_2(self.attractor_p[-1] - set(self.final), gamma2=self.strategy_np)
                set_z = self._safe_1(self.attractor_p[-1] - set_y, gamma1=self.strategy_p)
                self.strategy_p = self._stay_1(set_z, gamma1=self.strategy_p)
            else:   # self.player == 2
                set_y = self._safe_1(self.attractor_p[-1] - set(self.final), gamma1=self.strategy_p)
                set_z = self._safe_2(self.attractor_p[-1] - set_y, gamma2=self.strategy_np)
                self.strategy_p = self._stay_2(set_z, gamma2=self.strategy_p)

            set_c.append(set_y)
            self.attractor_p.append(set_z)

            if self.attractor_p[-1] == self.attractor_p[-2]:
                break

        # Compute safety player's permissive strategy
        self.attractor_np = [set(self.game.states() - set(reduce(set.union, self.attractor_p)))]
        for u in self.attractor_np[-1]:
            rem_actions = set()
            for a in self.strategy_np[u]:
                if not {v for v, _ in self.game.delta(u, a)}.issubset(self.attractor_np[-1]):
                    rem_actions.add(a)
            self.strategy_np[u] = self.strategy_np[u] - rem_actions

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return random.choice(list(self.strategy_p[v]))
        else:
            return random.choice(list(self.strategy_np[v]))

    def p2_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P2's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return random.choice(list(self.strategy_p[v]))
        else:
            return random.choice(list(self.strategy_np[v]))

    def _safe_1(self, set_u, gamma1):
        list_v = [set(set_u)]
        while True:
            set_y1 = set()
            set_y2 = set()
            for s, data_s in self.game.states(data=True):
                if data_s["turn"] == 1:
                    if any({s for s, _ in self.game.delta(s, a)}.issubset(list_v[-1]) for a in gamma1[s]):
                        set_y1.add(s)
                else:  # data_s["turn"] == 2
                    if {t for t, _ in self.game.succ(s)}.issubset(list_v[-1]):
                        set_y2.add(s)
            list_v.append(set.intersection(list_v[-1], set.union(set_y1, set_y2)))
            if list_v[-1] == list_v[-2]:
                break
        return list_v[-1]

    def _safe_2(self, set_u, gamma2):
        list_v = [set(set_u)]
        while True:
            set_y1 = set()
            set_y2 = set()
            for s, data_s in self.game.states(data=True):
                if data_s["turn"] == 2:
                    if any({s for s, _ in self.game.delta(s, a)}.issubset(list_v[-1]) for a in gamma2[s]):
                        set_y2.add(s)
                else:  # data_s["turn"] == 21
                    if {t for t, _ in self.game.succ(s)}.issubset(list_v[-1]):
                        set_y1.add(s)
            list_v.append(set.intersection(list_v[-1], set.union(set_y1, set_y2)))
            if list_v[-1] == list_v[-2]:
                break
        return list_v[-1]

    def _stay_1(self, set_u, gamma1):
        """ Prune P1 actions that escape set_u. """

        gamma1 = gamma1.copy()
        for u, data_u in self.game.states(data=True):
            if data_u["turn"] == 2:
                continue
            rem_actions = set()
            for a in gamma1[u]:
                if not {v for v, _ in self.game.delta(u, a)}.issubset(set_u):
                    rem_actions.add(a)
            gamma1[u] = gamma1[u] - rem_actions

        return gamma1

    def _stay_2(self, set_u, gamma2):
        """ Prune P1 actions that escape set_u. """

        gamma2 = gamma2.copy()
        for u, data_u in self.game.states(data=True):
            if data_u["turn"] == 1:
                continue
            rem_actions = set()
            for a in gamma2[u]:
                if not {v for v, _ in self.game.delta(u, a)}.issubset(set_u):
                    rem_actions.add(a)
            gamma2[u] = gamma2[u] - rem_actions

        return gamma2

    @property
    def p1_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return self.strategy_p
        else:
            return self.strategy_np

    @property
    def p2_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return self.strategy_p
        else:
            return self.strategy_np

    @property
    def p1_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return self.attractor_p
        else:
            return self.attractor_np

    @property
    def p2_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return self.attractor_p
        else:
            return self.attractor_np


class PWinReach:
    """
    Positive winning region and strategy in stochastic two-player turn-based game.
    """

    def __init__(self, game, final, player=1):
        assert isinstance(game, StptbGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = player
        self.attractor_p = list()  # attractor_p is level set of winning states for reachability player
        self.attractor_np = list()  # attractor_np is level set of winning states for safety player
        self.strategy_p = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                           if self.game.get_state_property(u, "turn") == self.player}
        self.strategy_np = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                            if self.game.get_state_property(u, "turn") != self.player}
        self._is_solved = False

    def reset(self):
        self.attractor_p = list()   # attractor_p is level set of winning states for reachability player
        self.attractor_np = list()  # attractor_np is level set of winning states for safety player
        self.strategy_p = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                           if self.game.get_state_property(u, "turn") == self.player}
        self.strategy_np = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()
                            if self.game.get_state_property(u, "turn") != self.player}
        self._is_solved = False

    def solve(self):
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve PWinReach({self.game}, {self.final}, {self.player}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Initialize loop parameters
        self.attractor_p = [set(self.final)]
        set_c = []

        # Fixed point computation
        while True:
            if self.player == 1:
                set_y = self._safe_2(self.attractor_p[-1] - set(self.final), gamma2=self.strategy_np)
                set_z = self._safe_1(self.attractor_p[-1] - set_y, gamma1=self.strategy_p)
                self.strategy_p = self._reach_1(set_z, gamma1=self.strategy_p)
            else:   # self.player == 2
                set_y = self._safe_1(self.attractor_p[-1] - set(self.final), gamma1=self.strategy_p)
                set_z = self._safe_2(self.attractor_p[-1] - set_y, gamma2=self.strategy_np)
                self.strategy_p = self._reach_2(set_z, gamma2=self.strategy_p)

            set_c.append(set_y)
            self.attractor_p.append(set_z)

            if self.attractor_p[-1] == self.attractor_p[-2]:
                break

        # Compute safety player's permissive strategy
        self.attractor_np = [set(self.game.states() - set(reduce(set.union, self.attractor_p)))]
        for u in self.attractor_np[-1]:
            rem_actions = set()
            for a in self.strategy_np[u]:
                if not {v for v, _ in self.game.delta(u, a)}.issubset(self.attractor_np[-1]):
                    rem_actions.add(a)
            self.strategy_np[u] = self.strategy_np[u] - rem_actions

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return random.choice(list(self.strategy_p[v]))
        else:
            return random.choice(list(self.strategy_np[v]))

    def p2_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P2's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return random.choice(list(self.strategy_p[v]))
        else:
            return random.choice(list(self.strategy_np[v]))

    def _safe_1(self, set_u, gamma1):
        list_v = [set(set_u)]
        while True:
            set_y1 = set()
            set_y2 = set()
            for s, data_s in self.game.states(data=True):
                if data_s["turn"] == 1:
                    if any({s for s, _ in self.game.delta(s, a)}.issubset(list_v[-1]) for a in gamma1[s]):
                        set_y1.add(s)
                else:  # data_s["turn"] == 2
                    if {t for t, _ in self.game.succ(s)}.issubset(list_v[-1]):
                        set_y2.add(s)
            list_v.append(set.intersection(list_v[-1], set.union(set_y1, set_y2)))
            if list_v[-1] == list_v[-2]:
                break
        return list_v[-1]

    def _safe_2(self, set_u, gamma2):
        list_v = [set(set_u)]
        while True:
            set_y1 = set()
            set_y2 = set()
            for s, data_s in self.game.states(data=True):
                if data_s["turn"] == 2:
                    if any({s for s, _ in self.game.delta(s, a)}.issubset(list_v[-1]) for a in gamma2[s]):
                        set_y2.add(s)
                else:  # data_s["turn"] == 21
                    if {t for t, _ in self.game.succ(s)}.issubset(list_v[-1]):
                        set_y1.add(s)
            list_v.append(set.intersection(list_v[-1], set.union(set_y1, set_y2)))
            if list_v[-1] == list_v[-2]:
                break
        return list_v[-1]

    def _reach_1(self, set_u, gamma1):
        """ Prune P1 actions that escape set_u. """

        gamma1 = gamma1.copy()
        for u, data_u in self.game.states(data=True):
            if data_u["turn"] == 2:
                continue
            rem_actions = set()
            for a in gamma1[u]:
                if len(set.intersection({v for v, _ in self.game.delta(u, a)}, set_u)) == 0:
                    rem_actions.add(a)
            gamma1[u] = gamma1[u] - rem_actions

        return gamma1

    def _reach_2(self, set_u, gamma2):
        """ Prune P1 actions that escape set_u. """

        gamma2 = gamma2.copy()
        for u, data_u in self.game.states(data=True):
            if data_u["turn"] == 1:
                continue
            rem_actions = set()
            for a in gamma2[u]:
                if len(set.intersection({v for v, _ in self.game.delta(u, a)}, set_u)) == 0:
                    rem_actions.add(a)
            gamma2[u] = gamma2[u] - rem_actions

        return gamma2

    @property
    def p1_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return self.strategy_p
        else:
            return self.strategy_np

    @property
    def p2_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return self.strategy_p
        else:
            return self.strategy_np

    @property
    def p1_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            return self.attractor_p
        else:
            return self.attractor_np

    @property
    def p2_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return self.attractor_p
        else:
            return self.attractor_np
