import random

import networkx as nx

from ggsolver.graph import Graph, SubGraph
from ggsolver.models import Solver
from functools import reduce


# TODO. Adopt to SubGraph based solver.
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
        self._final = set(final) if final is not None else {n for n in graph.nodes() if self._graph["final"][n] == 0}
        self._strategy_graph = None

    def solve(self):
        """
        Alg. 45 from Principles of Model Checking.
        Using the same variable names as Alg. 45.
        """
        # Initialize algorithm variables
        graph = SubGraph(self._graph)
        b = self._final

        # Make B absorbing
        for uid in b:
            for _, vid, key in graph.out_edges(uid):
                graph.hide_edge(uid, vid, key)

        # Compute the set of nodes disconnected from B
        disconnected = self.disconnected(graph, b)
        set_u = {s for s in graph.nodes() if s in disconnected}
        # print(f"Initializing set_u: {set_u}")

        while True:
            set_r = set_u.copy()
            # print(f"--------------------------")
            # print(f"set_r: {set_u}")
            while len(set_r) > 0:
                u = set_r.pop()
                # print(f"Popped: {u}, Pre: {self.pre(graph, u)}")

                for t, a in self.pre(graph, u):
                    # print(f"\tProcessing {t}, {a}")
                    # print(f"\tt in set_u: {t in set_u}")
                    if t in set_u:
                        continue
                    self.remove_act(graph, t, a)
                    # print(f"\tlen(graph.successors(t)) == 0: {len(graph.successors(t)) == 0}")
                    if len(graph.successors(t)) == 0:
                        # print(f"\tAdding node: {t} to set_t, set_u")
                        set_r.add(t)
                        set_u.add(t)
                # print(f"\tHiding node: {u}")
                graph.hide_node(u)
            disconnected = self.disconnected(graph, b)
            set_u = {s for s in set(graph.nodes()) - set_u if s in disconnected}
            # print(f"New set_u: {set_u}")
            if len(set_u) == 0:
                break

        self._win1 = set(graph.visible_nodes())
        self._strategy_graph = graph
        # print(self._win1)

    def pi1(self, node):
        return random.choice(self.win1_act(node))

    def win1_act(self, node):
        if self._strategy_graph.has_node(node):
            acts = set()
            for uid, vid, key in self._strategy_graph.out_edges(node):
                acts.add(self._graph["input"][uid, vid, key])
            return list(acts)
        return []

    @staticmethod
    def disconnected(graph, sources):
        reachable_nodes = graph.reverse_bfs(sources)
        return set(graph.visible_nodes()) - reachable_nodes

    def pre(self, graph, vid):
        if graph.has_node(vid):
            return {(uid, graph["input"][uid, vid, key]) for uid, _, key in graph.in_edges(vid)}
        return set()

    def remove_act(self, graph, uid, act):
        for _, vid, key in graph.out_edges(uid):
            if graph["input"][uid, vid, key] == act:
                # print(f"\tHiding {uid}, {act}, edge:{uid, vid, key}")
                graph.hide_edge(uid, vid, key)


class PWinReach(Solver):
    def __init__(self, graph, final=None, player=1, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param player: (int) Either 1 or 2.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(PWinReach, self).__init__(graph, **kwargs)
        self._player = player
        self._final = set(final) if final is not None else {n for n in graph.nodes() if self._graph["final"][n] == 0}
        self._strategy_graph = None

    def solve(self):
        """
        Alg. 45 from Principles of Model Checking.
        Using the same variable names as Alg. 45.
        """
        self.reset()
        final = self._final
        reachable_nodes = self._solution.reverse_bfs(final)
        for uid in self._solution.nodes():
            if uid not in reachable_nodes:
                self._solution.hide_node(uid)
        self._is_solved = True

    def pi1(self, node):
        return random.choice(self.win1_act(node))

    def win1_act(self, node):
        if self._strategy_graph.has_node(node):
            acts = set()
            for uid, vid, key in self._strategy_graph.out_edges(node):
                acts.add(self._graph["input"][uid, vid, key])
            return list(acts)
        return []

