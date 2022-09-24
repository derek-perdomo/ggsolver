import random

from ggsolver.graph import Graph
from ggsolver.graph import NodePropertyMap
from ggsolver.models import Solver

from functools import reduce


class SWinReach(Solver):
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
        self._attr = list()
        # _ranks is indexed by rank and _node_ranks is indexed by node
        self._ranks = dict()
        self._node_ranks = dict()

    def solve(self):
        # Create initial attractor list with final states
        self._attr.append(self._final)
        while True:
            current_win = set(self._attr[-1])
            # Check predecessors
            pre_1 = set()
            pre_2 = set()
            for node in current_win:
                predecessors = self._graph.predecessors(node)
                # Check all predecessors of nodes in current winning region
                for pred in predecessors:
                    # Add all nodes where turn=1
                    if self._graph["turn"][pred] == 1:
                        pre_1.add(pred)
                    # Add all nodes where turn=2 and edges only point to winning region
                    if self._graph["turn"][pred] == 2:
                        successors = self._graph.successors(pred)
                        if len(set(successors) - current_win) == 0:
                            pre_2.add(pred)
            # Add a new attractor that is the union of these two sets and last attractor
            new_attr = current_win.union(pre_1).union(pre_2)
            # Break if this new attractor is the same as the last one
            if new_attr == self._attr[-1]:
                break
            else:
                self._attr.append(new_attr)
        self._win1 = set(self._attr[-1])
        self._win2 = set(self._graph.nodes()).difference(set(self._attr[-1]))
        self.determine_ranks()

    def pi1(self, node):
        return self.pick_action(self.win1_act, node)

    def pi2(self, node):
        return self.pick_action(self.win2_act, node)

    def win1_act(self, node):
        # If final state or non-winning state or not P1s turn at state return empty list
        if self.rank(node) == 0 or self.rank(node) == float("inf") or self._graph["turn"][node] == 2:
            return list()

        target_nodes = self.nodes_at_rank(self.rank(node)-1)
        out_edges = self._graph.out_edges(node)
        winning_actions = list()

        for edge in out_edges:
            # edge[1] is the node the edge points to
            if edge[1] in target_nodes:
                winning_actions.append(edge)
        return winning_actions

    def win2_act(self, node):
        if node in self._win2 and self._graph["turn"][node] == 2:
            out_edges = self._graph.out_edges(node)
            target_nodes = self._win2
            winning_actions = list()
            for edge in out_edges:
                # edge[1] is the node the edge points to
                if edge[1] in target_nodes:
                    winning_actions.append(edge)
            return winning_actions
        else:
            return list()

    def pick_action(self, winning_function, node):
        winning_actions = winning_function(node)
        allowable_actions = self._graph.out_edges(node)

        # If there are winning actions
        if len(winning_actions) > 0 and self.strategy_type() == "deterministic":
            return winning_actions[0]
        elif len(winning_actions) > 0 and self.strategy_type() != "deterministic":
            return random.choice(winning_actions)
        # If there are no winning actions
        elif len(winning_actions) == 0 and self.strategy_type() == "deterministic":
            return allowable_actions[0]
        elif len(winning_actions) == 0 and self.strategy_type() != "deterministic":
            return random.choice(allowable_actions)

    def rank(self, node):
        """ Returns the rank of a given node """
        return self._node_ranks[node]

    def nodes_at_rank(self, rank):
        """ Returns a list of all nodes at a given rank """
        return self._ranks[rank]
    def determine_ranks(self):
        """ Calculates the rank of each node and stores it in self._ranks self._ranks is a dictionary that stores a list
        of nodes at each rank. Also stores the rank of each node in self._node_ranks. We use two lists so that we can
        calculate ranks once and then access them in O(1) on average."""
        ranked_nodes = set()
        current_rank = 0
        for attractor in self._attr:
            for node in attractor:
                if node not in ranked_nodes:
                    # Construct _ranks
                    try:
                        self._ranks[current_rank].append(node)
                    except KeyError:
                        self._ranks[current_rank] = list([node])
                    # Construct _node_ranks
                    self._node_ranks[node] = current_rank
                    ranked_nodes.add(node)
            current_rank += 1
        # add nodes not in the attractor list (not winning for P1)
        for node in self._win2:
            # Construct _ranks
            try:
                self._ranks[float("inf")].append(node)
            except KeyError:
                self._ranks[float("inf")] = list([node])
            # Construct _node_ranks
            self._node_ranks[node] = float("inf")

ASWinReach = SWinReach

if __name__ == '__main__':
    # Create the graph from richmodels example
    graph_rich = Graph()
    s0, s1, s2, s3, s4, s5, s6, s7 = graph_rich.add_nodes(num_nodes=8)

    graph_rich["turn"] = NodePropertyMap(graph_rich, default=-1)
    graph_rich["turn"][s0] = 1
    graph_rich["turn"][s1] = 2
    graph_rich["turn"][s2] = 2
    graph_rich["turn"][s3] = 2
    graph_rich["turn"][s4] = 1
    graph_rich["turn"][s5] = 2
    graph_rich["turn"][s6] = 1
    graph_rich["turn"][s7] = 2

    graph_rich.add_edges([
                    (s0, s1), (s0, s3),
                    (s1, s0), (s1, s2), (s1, s4),
                    (s2, s2), (s2, s4),
                    (s3, s0), (s3, s4), (s3, s5),
                    (s4, s3), (s4, s1),
                    (s5, s3), (s5, s6),
                    (s6, s6), (s6, s7),
                    (s7, s0), (s7, s3)
                    ])
    final_states = (s3, s4)

    # Test solver
    solver = SWinReach(graph_rich, final=final_states)
    solver.solve()
    for n in graph_rich.nodes():
        print(n, " win1_acts: ", solver.win1_act(n))
        print(n, " win2_acts: ", solver.win2_act(n))
    print(solver.win1())
    print(solver.win2())
