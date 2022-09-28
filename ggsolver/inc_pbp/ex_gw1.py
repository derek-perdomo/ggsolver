import itertools

from ggsolver.inc_pbp.models import PrefModel, ImprovementMDP
from ggsolver.inc_pbp.reachability import SASIReach
from ggsolver.models import register_property
from ggsolver.mdp.models import QualitativeMDP
from ggsolver.gridworld import util


class MDPGridworld(QualitativeMDP):
    GRAPH_PROPERTY = QualitativeMDP.GRAPH_PROPERTY.copy()

    def __init__(self, dim, batt, obstacles, goals, accessibility_trans):
        """
        dim: (ROWS, COLS) of gridworld
        batt: maximum charge of robot battery
            E.g., batt=4 means battery can take values between 0 and 4, inclusive.)
        obstacles: [cell]
        goals: [cell]
        accessibility_trans: {goal: [goal]}

        """
        super(MDPGridworld, self).__init__()

        # Class variables
        self._dim = dim
        self._batt = batt
        self._obs = obstacles
        self._goals = goals
        self._accessibility_trans = accessibility_trans

        # Helper variable (stochasticity of actions)
        self._stochasticity = {
            "N": ["N", "NE", "NW", "STAY"],
            "E": ["E", "NE", "SE", "STAY"],
            "S": ["S", "SE", "SW", "STAY"],
            "W": ["W", "NW", "SW", "STAY"],
        }

    def states(self):
        """
        state = (p1.row: int, p1.col: int, p1.batt: int, accessible:List[Bool])
        """
        return list(itertools.product(
            range(self.dim()[0]),
            range(self.dim()[1]),
            range(self.batt()),
            list(itertools.product([True, False], repeat=len(self.roi())))
        ))

    def actions(self):
        return [
            util.GW_ACT_N,
            util.GW_ACT_E,
            util.GW_ACT_S,
            util.GW_ACT_W
        ]

    def delta(self, state, act):
        row, col, batt, accessibility = state

        # Manage battery constraint
        if batt == 0:
            return [state]
        else:
            n_batt = batt - 1

        # Cell transition
        next_cells = self._apply_non_det_actions((row, col), act)
        next_cells = util.bouncy_wall((row, col), next_cells, self.dim())
        next_cells = util.bouncy_obstacle((row, col), next_cells, self.obs())

        # Apply accessibility modification rules and construct next state
        next_states = set()
        for cell in next_cells:
            n_accessibility = self._update_accessibility(accessibility, cell)
            next_states.add((cell[0], cell[1], n_batt, tuple(n_accessibility)))

        # Return next states
        return list(next_states)

    @register_property(GRAPH_PROPERTY)
    def dim(self):
        return self._dim

    @register_property(GRAPH_PROPERTY)
    def batt(self):
        return self._batt

    @register_property(GRAPH_PROPERTY)
    def obs(self):
        return self._obs

    @register_property(GRAPH_PROPERTY)
    def roi(self):
        return self._goals

    def _apply_non_det_actions(self, cell, act):
        actions = self._stochasticity[act]
        next_cells = set()
        for a in actions:
            next_cells.add(util.move(cell, a))
        return list(next_cells)

    def _update_accessibility(self, accessibility, cell):
        n_accessibility = [False] * len(accessibility)
        if cell in self._accessibility_trans:
            for goal in self._accessibility_trans[cell]:
                n_accessibility[self._goals.index(goal)] = True
        return [accessibility[i] or n_accessibility[i] for i in range(len(accessibility))]


if __name__ == '__main__':
    from pprint import pprint
    # gw = MDPGridworld(dim=(3, 3), batt=3, goals=[(0, 0), (1, 1)])
    gw = MDPGridworld(
        dim=(3, 3),
        batt=3,
        obstacles=[],
        goals=[(0, 0), (1, 1)],
        accessibility_trans={(0, 0): [(1, 1)]}
    )

    pprint(len(gw.states()))
    pprint(gw.actions())
    pprint(gw.delta((0, 1, 1, (True, False)), util.GW_ACT_W))
    pprint(gw.delta((0, 0, 0, (False, False)), util.GW_ACT_W))

    outcome_1 = [st for st in gw.states() if tuple(st[0:2]) == (0, 0)]
    outcome_2 = [st for st in gw.states() if tuple(st[0:2]) == (0, 0)]

    pref = PrefModel(
        outcomes={1: outcome_1, 2: outcome_2},
        pref=[(2, 1)]
    )

    imdp = ImprovementMDP(gw, pref)
    imdp_graph = imdp.graphify()
    final_nodes = {node for node in imdp_graph.nodes() if imdp_graph["state"][node][1] == 1}
    sasi = SASIReach(imdp_graph, final=final_nodes)
    sasi.solve()
