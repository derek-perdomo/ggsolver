from ggsolver.graph import Graph
from ggsolver.models import Solver
from functools import reduce


class SWinReach(Solver):
    # TODO (MC). See the documentation for Graph class to understand the input.

    def __init__(self, graph, final=None, player=1, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param player: (int) Either 1 or 2.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(SWinReach, self).__init__(graph, **kwargs)
        self._player = player
        self._turn = self._graph["turn"]
        self._final = set(final) if final is not None else {n for n in graph.nodes() if self._graph["final"][n]}
        self._attr = list()         # list of sets

    def solve(self):
        # TODO (MC). Implement the sure winning algorithm. Feel free to define helper functions, if necessary.
        #   Use `self._attr` which is a list of sets to construct the attractor level sets.
        #   Use `self._attr` to construct the set of winning nodes of P1. Update value of self._win1.
        #   Use `self._attr` to construct the set of winning nodes of P2. Update value of self._win2.
        self._win1 = set()
        self._win2 = set()

    def pi1(self, node):
        # TODO (MC). Use self._attr to construct strategy of P1.
        #   If self.type_strategy() is "deterministic" then return the function should return the same action
        #       when called with the same input.
        #   Otherwise, you must choose a random winning action of P1 from self.win1_act.
        pass

    def pi2(self, node):
        pass

    def win1_act(self, node):
        # TODO (MC). Use self._attr to return a list of all winning actions at given node.
        pass

    def win2_act(self, node):
        # TODO (MC). Use self._attr to return a list of all winning actions at given node.
        pass


ASWinReach = SWinReach


