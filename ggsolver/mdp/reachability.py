from ggsolver.graph import Graph, SubGraph
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
        """
        Alg. 45 from Principles of Model Checking.
        Using the same variable names as Alg. 45.
        """
        # Initialize algorithm variables
        graph = SubGraph(self._graph)
        b = self._final

        # Compute the set of nodes disconnected from B
        disconnected = self.disconnected(graph, b)
        u = {s for s in graph.nodes() if s in disconnected}

        while True:
            r = u
            while len(r) > 0:
                u = r.pop()
                for t, a in self.pre(graph, u):
                    if t in u:
                        continue
                    self.remove_act(graph, t, a)
                    if len(graph.successors(t)) == 0:
                        r.add(t)
                        u.add(t)
                graph.hide_node(u)
            disconnected = self.disconnected(graph, b)
            u = {s for s in set(graph.nodes()) - u if s in disconnected}
            if len(u) == 0:
                break

        self._win1 = set(graph.visible_nodes())


    def pi1(self, node):
        pass

    def win1_act(self, node):
        pass


