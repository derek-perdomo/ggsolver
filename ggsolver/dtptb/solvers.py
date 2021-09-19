import logging
import random
from ggsolver.dtptb.model import DtptbGame
from functools import reduce


class SWinReach:
    """
    Sure winning region and strategy for deterministic two-player turn-based game.

    References:
        * R. McNaughton (1993), "Infinite games played on finite graphs," Annals of Pure and Applied Logic 65(2).
        * W. Zielonka (1998), "Infinite games on finitely coloured graphs with applications to automata on infinite
            trees," Theoretical Computer Science 200(1-2).
        * E. Gradel, and T. Wolfgang, "Automata, logics, and infinite games: a guide to current research." (2002).


    Notes.
        * Each solver instance is defined by the triple of game object, set of final states and the player who
        has the reachability objective.
        * Solver constructs two data structures:
            1. `attractor`: which represents the level-set of winning states for the player with reachability task.
            2. `win_edges`: winning edges for the player with reachability task. These edges are used to define
                    P1's and P2's winning strategies.
    """

    def __init__(self, game, final, player=1):
        assert isinstance(game, DtptbGame), f"Input `game` must be a DtptbGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = int(player)
        self.attractor_p = list()         # attractor_p is level set of winning states for reachability player
        self.attractor_np = list()        # attractor_np is level set of winning states for safety player
        self.strategy_p = dict()           # winning strategy of reachability player
        self.strategy_np = dict()          # winning strategy of safety player
        self._is_solved = False

    def reset(self):
        self.attractor_p = list()  # attractor is for the player with reachability objective: self.player
        self.strategy_p = set()  # win_edges is for the player with reachability objective: self.player
        self._is_solved = False

    def solve(self):
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve SWinReach({self.game}, {self.final}, {self.player}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Fixed point computation
        self.attractor_p = [set(self.final)]
        while True:
            # Evaluate one-step reachability
            if self.player == 1:
                win_states, strategy = self._pre(self.attractor_p, 1)
            else:   # self.player == 2
                win_states, strategy = self._pre(self.attractor_p, 1)

            # Loop termination condition
            if len(win_states) == 0:
                break

            # Update data structures
            self.attractor_p.append(win_states)
            self.strategy_p.update(strategy)

        # Construct opponent's winning region and strategy
        self.attractor_np = [set(self.game.states()) - set(reduce(set.union, self.attractor_p))]
        for v in self.game.states():
            if v not in self.strategy_p:
                self.strategy_np[v] = dict()
                for t, a in self.game.succ(v):
                    self.strategy_np[v] = {a: t}
            else:
                for t, a in self.game.succ(v):
                    if a not in self.strategy_p[v]:
                        self.strategy_np[v] = {a: t}

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            try:
                return list(self.strategy_p[v].keys())[0]
            except KeyError:
                return None
        else:
            try:
                return list(self.strategy_np[v].keys())[0]
            except KeyError:
                return None

    def p2_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            try:
                return list(self.strategy_p[v].keys())[0]
            except KeyError:
                return None
        else:
            try:
                return list(self.strategy_np[v].keys())[0]
            except KeyError:
                return None

    def _pre(self, attractor, player):
        # Initialize data structure to store newly identified winning states and strategy
        p_new_win_states = set()
        p_new_win_strategy = dict()

        # Collect all winning states
        p_win_states = set(reduce(set.union, attractor))

        for v in p_win_states:
            pred_v = self.game.pred(v)
            for u, _ in pred_v:
                if u in p_win_states:
                    continue
                succ_u = self.game.succ(u)
                progress_states = set.intersection(p_win_states, {t for t, _ in succ_u})
                turn = self.game.get_state_property(u, "turn")
                if turn == player and len(progress_states) > 0:
                    p_new_win_states.add(u)
                    for t, a in succ_u:
                        if t not in progress_states:
                            continue
                        if u not in p_new_win_strategy:
                            p_new_win_strategy[u] = dict()
                        p_new_win_strategy[u].update({a: t})
                elif turn != player and len(progress_states) == len(succ_u):
                    p_new_win_states.add(u)
                    for t, a in succ_u:
                        if u not in p_new_win_strategy:
                            p_new_win_strategy[u] = dict()
                        p_new_win_strategy[u].update({a: t})

        return p_new_win_states, p_new_win_strategy

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
            err_msg = f"Cannot access P2's strategy before solving the game."
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
            return set(reduce(set.union, self.attractor_p))
        else:
            return set(reduce(set.union, self.attractor_np))

    @property
    def p2_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P2's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            return set(reduce(set.union, self.attractor_p))
        else:
            return set(reduce(set.union, self.attractor_np))


class ASWinReach(SWinReach):
    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 1:
            try:
                return random.choice(list(self.strategy_p[v].keys()))
            except KeyError:
                return None
        else:
            try:
                return random.choice(list(self.strategy_np[v].keys()))
            except KeyError:
                return None

    def p2_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        if self.player == 2:
            try:
                return random.choice(list(self.strategy_p[v].keys()))
            except KeyError:
                return None
        else:
            try:
                return random.choice(list(self.strategy_np[v].keys()))
            except KeyError:
                return None
