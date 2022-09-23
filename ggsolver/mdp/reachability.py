from ggsolver.graph import Graph
from ggsolver.models import Solver
from functools import reduce


class ASWinReach(Solver):
    def __init__(self, graph, final=None, player=1, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param player: (int) Either 1 or 2.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(ASWinReach, self).__init__(graph, **kwargs)
        self._player = player
        self._final = set(final) if final is not None else {n for n in graph.nodes() if self._graph["final"][n]}
    
    def solve(self):
        pass

    def pi1(self, node):
        pass

    def win1_act(self, node):
        pass


