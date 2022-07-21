from ggsolver.graph import Graph
from functools import reduce


class SureWinReach:
    def __init__(self, graph: Graph, player=1):
        """
        Game graph that represents a deterministic two-player turn-based game.
        """
        assert player in [1, 2]
        assert graph["is_turn_based"] and not graph["is_stochastic"]
        self._player = player
        self._graph = graph
        self._turn = self._graph["turn"]    # Get the "turn" property map
        self._final = set()
        self._attr = list()                 # list of sets

    def set_final(self, final=None):
        self._final = set()
        if final is None:
            final = self._graph["final"]

            for node in self._graph.nodes():
                is_final = final[node]
                if is_final is None:
                    raise ValueError(f'Node property `final` is not defined for node '
                                     f'{node}:{self._graph["state"][node]}.')

                if is_final:
                    self._final.add(node)

        else:
            self._final = set(final)

    def solve(self):
        if len(self._final) == 0:
            raise ValueError("The set of final states is empty. Did you forget to call set_final()?")

        self._attr = [self._final]
        iter_count = 0
        while True:
            print(f"[INFO] solve():: iter_count:{iter_count}")
            iter_count += 1
            print(f"[INFO] pre_exists():: win:{set(reduce(set.union, self._attr))}")

            pre1 = self._pre_exists()
            pre2 = self._pre_forall()
            next_level = set.union(pre1, pre2)
            if next_level == self._attr[-1]:
                break
            self._attr.append(next_level)

        print(f"[INFO] -------------------------------------------------")
        print(f"[INFO] solve():: win:{set(reduce(set.union, self._attr))}")

    def _pre_exists(self):
        win = set(reduce(set.union, self._attr))
        pred = set()
        for vid in win:
            pred_vid = self._graph.predecessors(vid)
            for uid in pred_vid:
                if self._turn[uid] == self._player:
                    pred.add(uid)
        print(f"[INFO] pre_exists():: pred:{pred - win}")
        return pred - win

    def _pre_forall(self):
        win = set(reduce(set.union, self._attr))
        pred = set()
        for vid in win:
            pred_vid = self._graph.predecessors(vid)
            for uid in pred_vid:
                if set(self._graph.successors(uid)).issubset(win) and self._turn[uid] != self._player:
                    pred.add(uid)
        print(f"[INFO] pre_forall():: pred:{pred - win}")
        return pred - win

    def p1_win(self, state=None):
        """
        If state is None, the complete winning region of P1 is returned.
        """
        if state is None and self._player == 1:
            return [self._graph["states"][node] for node in reduce(set.union, self._attr)]
        elif state is None and self._player == 2:
            return [
                self._graph["states"][node]
                for node in self._graph.nodes()
                if node not in reduce(set.union, self._attr)
            ]

        if self._player == 1:
            return any(state in (self._graph["states"][node] for node in level) for level in self._attr)
        else:
            return all(state not in (self._graph["states"][node] for node in level) for level in self._attr)

    def p2_win(self, state=None):
        if state is None:
            return [self._graph["states"][node] for node in reduce(set.union, self._attr)]

        if self._player == 2:
            return any(state in (self._graph["states"][node] for node in level) for level in self._attr)
        else:
            return all(state not in (self._graph["states"][node] for node in level) for level in self._attr)

    def pi1(self, state):
        # TODO. Make state2node property default in graphical models.
        pass

    def pi2(self, state):
        pass
