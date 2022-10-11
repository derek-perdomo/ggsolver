import logging
from ggsolver.graph import NodePropertyMap
from ggsolver.util import ColoredMsg
from ggsolver.models import Solver
from functools import reduce
from tqdm import tqdm
logger = logging.getLogger(__name__)


class SWinReach(Solver):
    def __init__(self, graph, final=None, player=1, **kwargs):
        if not graph["is_deterministic"]:
            logger.warning(ColoredMsg.warn(f"dtptb.SWinReach expects deterministic game graph. Input parameters: "
                                           f"is_deterministic={graph['is_deterministic']}, "
                                           f"is_probabilistic={graph['is_probabilistic']}."))

        if not graph["is_turn_based"]:
            logger.warning(ColoredMsg.warn(f"dtptb.SWinReach expects turn-based game graph. Input parameters: "
                                           f"is_turn_based={graph['is_turn_based']}."))

        super(SWinReach, self).__init__(graph, **kwargs)
        self._player = player
        self._final = final if final is not None else self.get_final_states()
        self._turn = self._solution["turn"]
        self._rank = NodePropertyMap(self._solution, default=float("inf"))
        self._solution["rank"] = self._rank

    def reset(self):
        super(SWinReach, self).reset()
        self._rank = NodePropertyMap(self._solution)
        self._is_solved = False

    def get_final_states(self):
        return {uid for uid in self.graph().nodes() if self.graph()["final"][uid]}

    def solve(self):
        # Reset solver
        self.reset()

        # Level sets (list of sets)
        rank = 0
        win_nodes = set(self._final)

        # Initialize rank, node/edge_winner for final states
        for uid in win_nodes:
            self._rank[uid] = rank
            self._node_winner[uid] = self._player
            for _, vid, key in self._solution.out_edges(uid):
                self._edge_winner[uid, vid, key] = self._player

        # Zielonka's recursive algorithm
        with tqdm(total=self._solution.number_of_visible_nodes(), desc="Pointed graphify adding edges") as progress_bar:
            while True:
                predecessors = set(reduce(set.union, map(set, map(self._solution.predecessors, win_nodes))))

                pre_p = {uid for uid in predecessors if self._turn[uid] == self._player}
                pre_np = predecessors - pre_p
                pre_np = {uid for uid in pre_np if set(self._solution.successors(uid)).issubset(win_nodes)}

                next_level = set.union(pre_p, pre_np) - win_nodes
                if len(next_level) == 0:
                    break

                rank += 1
                for uid in next_level:
                    # Associate winner with nodes
                    self._rank[uid] = rank
                    self._node_winner[uid] = self._player

                    # Update progress_bar
                    progress_bar.update(1)

                    for _, vid, key in self._solution.out_edges(uid):
                        self._edge_winner[uid, vid, key] = self._player if vid in win_nodes else \
                            (1 if self._player == 2 else 2)

                win_nodes |= next_level

            # States not in win_nodes are winning for np.
            for uid in set(self._solution.nodes()) - win_nodes:
                self._node_winner[uid] = (1 if self._player == 2 else 2)
                progress_bar.update(1)

        # Mark the game to be solved
        self._is_solved = True


class SWinSafe(SWinReach):
    def __init__(self, graph, final=None, player=1, **kwargs):
        super(SWinSafe, self).__init__(graph, **kwargs)
        self._final = final if final is not None else self.get_final_states()

    def get_final_states(self):
        return {uid for uid in self.graph().nodes() if self.graph()["final"][uid]}

    def solve(self):
        # Reset solver
        self.reset()

        # Formulate and solve dual reachability game
        final = set(self.graph().nodes()) - self._final
        dual_player = 1 if self._player == 1 else 2
        dual_solver = SWinReach(self.graph(), final, dual_player)
        dual_solver.solve()

        # Process the output back to safety game
        self._solution = dual_solver.solution()
        self._node_winner = self._solution["node_winner"]
        self._edge_winner = self._solution["edge_winner"]

        # Mark the game to be solved
        self._is_solved = True


ASWinReach = SWinReach
ASWinSafe = SWinSafe
