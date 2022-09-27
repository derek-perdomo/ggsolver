"""
Solver for SPI and SASI strategies.
"""
from ggsolver.mdp.reachability import ASWinReach
from ggsolver.models import Solver


class SASIReach(Solver):
    """
    Alg. 1 from ACC 2023 paper.
    """
    def __init__(self, graph, final, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(SASIReach, self).__init__(graph, **kwargs)
        self._final = final
        self._strategy_graph = None

    def solve(self):
        iter_count = 0
        set_r = set(self._final)
        set_cal_w = []
        while len(set_r) > 0:
            set_w = ASWinReach(self._graph, final=set_r)
            set_w.solve()
            set_w = set_w.win1()

            set_r = set()
            for uid in set_w:
                si, mi = self._graph["state"][uid]
                if mi == 0:
                    set_r.add((si, 1))

            if iter_count == 0:
                set_cal_w.insert(0, set(self._graph.nodes()) - set_w)

            set_cal_w.append(set_w)
            iter_count += 1

        self._win1 = set_cal_w


