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

    def solve(self):
        # Create initial attractor list with final states
        self._attr.append(self._final)
        while True:
            current_win = set(self._attr[-1])
            # Check predecessors
            pre_1 = set()
            pre_2 = set()
            for node in current_win:
                # TODO (MC). You need to use self._graph here.
                predecessors = self._graph.predecessors(node)
                # Check all predecessors of nodes in current winning region
                for pred in predecessors:
                    # Add all nodes where turn=1
                    if self._graph["turn"][pred] == 1:
                        pre_1.add(pred)
                    # Add all nodes where turn=2 and edges only point to winning region
                    if self._graph["turn"][pred] == 2:
                        successors = self._graph.successors(pred)
                        if set(successors).union(current_win) == current_win:
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

    def pi1(self, node):
        return self.pick_action(self.win1_act, node)

    def pi2(self, node):
        return self.pick_action(self.win2_act, node)

    def win1_act(self, node):
        target_nodes = list()
        successors = set(self._graph.successors(node))
        # Check if we are in the winning region, if so use the attractors to find the best action
        if node in self._win1:
            for attractor in self._attr:
                if set(attractor).intersection(successors) != set():
                    target_nodes = list(set(attractor).intersection(successors))
                    break
        # If we are not in the winning region pick an action to enter it
        else:
            target_nodes = self._win1.intersection(successors)
        winning_actions = self.get_actions_from_nodes(node, target_nodes)
        return winning_actions

    def win2_act(self, node):
        successors = set(graph.successors(node))
        # Winning moves are going to any node that is in the winning region
        winning_nodes = self._win2.intersection(successors)

        winning_actions = self.get_actions_from_nodes(node, winning_nodes)
        return winning_actions

    def get_actions_from_nodes(self, origin_node, target_nodes):
        actions = list()
        for target in target_nodes:
            actions.append((origin_node, target))
        return actions

    def pick_action(self, winning_function, node):
        winning_actions = winning_function(node)
        allowable_nodes = graph.successors(node)
        allowable_actions = self.get_actions_from_nodes(node, allowable_nodes)

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


ASWinReach = SWinReach

if __name__ == '__main__':
    # Create the graph from richmodels example
    graph = Graph()
    s0, s1, s2, s3, s4, s5, s6, s7 = graph.add_nodes(num_nodes=8)

    graph["turn"] = NodePropertyMap(graph, default="3")
    graph["turn"][s0] = "1"
    graph["turn"][s1] = "2"
    graph["turn"][s2] = "2"
    graph["turn"][s3] = "2"
    graph["turn"][s4] = "1"
    graph["turn"][s5] = "2"
    graph["turn"][s6] = "1"
    graph["turn"][s7] = "2"

    graph.add_edges([
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
    solver = SWinReach(graph, final=final_states)
    solver.solve()
    print(solver.pi2(s0))
