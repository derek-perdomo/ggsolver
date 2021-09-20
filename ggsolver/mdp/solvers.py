"""
Algorithms to compute almost-sure winning, losing and positive winning regions, strategies for a player in game on MDP.

References:
    * H. Gimbert, Y. Oualhadj, and S. Paul, “Computing Optimal Strategies for Markov Decision Processes with
        Parity and Positive-Average Conditions,” Jan. 2011. Accessed: Jun. 11, 2021. [Online].
        Available: https://hal.archives-ouvertes.fr/hal-00559173
    * C. Baier and J.-P. Katoen, Principles of Model Checking. MIT press, 2008.
"""

import logging
import random
from ggsolver.mdp.model import MdpGame


class ASWinReach:
    """
    Almost-sure winning region and strategy for MDP game.
    """

    def __init__(self, game, final):
        assert isinstance(game, MdpGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = 1
        self.attractor = set()         # attractor_p is level set of winning states for reachability player
        self.strategy = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()}
        self._is_solved = False

    def reset(self):
        self.attractor = set()  # attractor is for the player with reachability objective: self.player
        self.strategy = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()}
        self._is_solved = False

    def solve(self):
        """
        Alg. 45 in Principles of Model Checking.
        """
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve SWinReach({self.game}, {self.final}, {self.player}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Initialize loop variables
        losing_states = set()
        set_u = self._disconnected(self.final, self.strategy)

        # Fixed point computation
        while len(set_u) > 0:
            set_r = set_u.copy()
            while len(set_r) > 0:
                u = set_r.pop()
                for t, a, p in self.game.pred(u):
                    if t in set_u:
                        continue
                    self.strategy[t].discard(a)
                    if len(self.strategy[t]) == 0:
                        set_r.add(t)
                        set_u.add(t)
                losing_states.add(u)
                self.strategy[u] = set()
            set_u = set.intersection((set(self.game.states()) - set_u),
                                     self._disconnected(final=self.final, enabled_actions=self.strategy))

        # Any state that's not losing is winning state.
        self.attractor = set(self.game.states()) - losing_states

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)
        return random.choice(list(self.strategy[v]))

    def _disconnected(self, final, enabled_actions):
        """
        Idea.
            1. Find what is connected given enabled actions.
                a. To be connected, i.e. for (u, a, v) to be valid, `a` must be enabled action at `u`.
            2. Whatever is not, is disconnected.

        BFS traversal.
        """
        connected = set(final)
        queue = list(final)
        queue_set = set(queue)      # Needed for efficient containment check. May be replaced by ordered_set.

        while len(queue) > 0:
            v = queue.pop()
            queue_set.remove(v)
            connected.add(v)

            pre_v = self.game.pred(v)
            for u, a, p in pre_v:
                # Do not process `u` if `a` is not enabled action at `u`.
                if a not in enabled_actions[u]:
                    continue

                # Otherwise, add `u` to queue if it's not already labeled `connected` or added to queue.
                if u not in connected and u not in queue_set:
                    queue.append(u)
                    queue_set.add(u)

        return set(self.game.states()) - connected

    @property
    def p1_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.strategy

    @property
    def p1_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.attractor


class ASLoseReach:
    """
    Almost-sure losing region in MDP game.
    """

    def __init__(self, game, final):
        assert isinstance(game, MdpGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = 1
        self.losing_region = set()  # attractor_p is set of positive winning states for controllable player
        self.enabled_actions = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()}
        self._is_solved = False

    def reset(self):
        self.losing_region = list()
        self.enabled_actions = {u: {a for _, a, _ in self.game.succ(u)} for u in self.game.states()}
        self._is_solved = False

    def solve(self):
        """
        Alg. 46 in Principles of Model Checking
        """
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve PWinReach({self.game}, {self.final}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Initialize loop variables
        self.losing_region = self.final.copy()
        set_r = self.losing_region.copy()

        # Fixed point computation
        while len(set_r) > 0:
            t = set_r.pop()
            for s, a, p in self.game.pred(t):
                if s in self.losing_region:
                    continue
                self.enabled_actions[s].discard(a)
                if len(self.enabled_actions[s]) == 0:
                    set_r.add(s)
                    self.losing_region.add(s)

        # Update solved flag
        self._is_solved = True

    def p1_enabled_actions(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.enabled_actions[v]

    @property
    def p1_enabled_actions_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.enabled_actions

    @property
    def p1_losing_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.losing_region


class PWinReach:
    """
    Positive winning region and strategy for MDP game.
    """

    def __init__(self, game, final):
        assert isinstance(game, MdpGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = 1
        self.attractor = set()           # attractor_p is set of positive winning states for controllable player
        self.strategy = dict()           # winning strategy of reachability player
        self._is_solved = False

    def reset(self):
        self.attractor = list()
        self.strategy = dict()
        self._is_solved = False

    def solve(self):
        """
        Backward reachability.
        """
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve PWinReach({self.game}, {self.final}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Initialize loop data structures
        queue = list(self.final)
        queue_set = set(queue)

        # Fixed point computation
        while len(queue) > 0:
            v = queue.pop(0)
            queue_set.remove(v)
            self.attractor.add(v)
            for u, a, p in self.game.pred(v):
                if u not in self.attractor and u not in queue_set:
                    queue.append(u)
                    queue_set.add(u)

        # Construct strategy
        for u in self.attractor:
            succ_u = self.game.succ(u)
            for v, a, p in succ_u:
                if v in self.attractor:
                    if u not in self.strategy:
                        self.strategy[u] = dict()
                    if a not in self.strategy[u]:
                        self.strategy[u][a] = dict()
                    self.strategy[u][a].update({v: p})

        # Update solved flag
        self._is_solved = True

    def p1_strategy(self, v):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        try:
            return random.choice(list(self.strategy[v].keys()))
        except KeyError:
            return None

    @property
    def p1_strategy_map(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's strategy before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.strategy

    @property
    def p1_winning_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.attractor


class PLoseReach:
    """
    Almost-sure winning region and strategy for MDP game.
    """

    def __init__(self, game, final):
        assert isinstance(game, MdpGame), f"Input `game` must be a MdpGame object. It is {type(game)}."
        self.game = game
        self.final = set(final)
        self.player = 1
        self.losing_region = set()           # attractor_p is set of positive winning states for controllable player
        self._is_solved = False

    def reset(self):
        self.losing_region = list()
        self._is_solved = False

    def solve(self):
        """
        Idea. States which are not almost-sure winning are positively losing for player 1.
        """
        # Do not resolve the game, if solution was already computed.
        if self._is_solved:
            err_msg = f"Ignoring attempt to solve PWinReach({self.game}, {self.final}). " \
                      f"Reset the game to resolve the game."
            logging.warning(err_msg)
            return

        # Create almost-sure winning solver
        aswin = ASWinReach(self.game, self.final)
        aswin.solve()
        self.losing_region = set(self.game.states()) - aswin.p1_winning_region

    @property
    def p1_losing_region(self):
        if not self._is_solved:
            err_msg = f"Cannot access P1's winning region before solving the game."
            logging.error(err_msg)
            raise ValueError(err_msg)

        return self.losing_region
