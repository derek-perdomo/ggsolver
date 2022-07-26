# TODO. Try implementing zlk package.
# TODO. Add logging statements.
# TODO. Make note that user will not be warned of any private attributes that are unserialized.
# TODO. Make note that user must update RESERVED_PROPERTIES and _graphify_unpointed appropriately.
# TODO. Instead of registering property function, register just name and then use getattr to
#  find the appropriate function during serialization. This will allow rebinding functions.
import inspect
from ggsolver import util
from ggsolver.graph import NodePropertyMap, EdgePropertyMap, Graph


# ==========================================================================
# RESERVED_PROPERTIES
# ==========================================================================
KEYWORDS = [
    "turn",                 # node property: turn [0 (concurrent), 1 (P1), 2 (P2), 3 (Nature)
    "state",                # node property: state
    "label",                # node property: label of state (depends on graph property: atoms)
    "prob",                 # edge property: probability associated with the edge
    "act",                  # edge property: action associated with the edge (depends on edge property: actions)
    "atoms",                # graph property: atoms (set of atomic propositions)
    "actions",              # graph property: actions (set of all actions)
    "delta",                # reserved.
    "is_stochastic"         # reserved.
    "is_turn_based"         # reserved.
    "is_quantitative"       # reserved.
]


# ==========================================================================
# DECORATOR FUNCTIONS.
# ==========================================================================
def register_property(property_dict):
    def register_function(func):
        if func.__name__ in KEYWORDS:
            raise NameError(f"Cannot register {func.__name} as a property. The name is reserved.")
        property_dict[func.__name__] = func
        return func
    return register_function


class GraphicalModel:
    NODE_PROPERTY = dict()
    EDGE_PROPERTY = dict()
    GRAPH_PROPERTY = dict()

    def __init__(self, **kwargs):
        super(GraphicalModel, self).__init__()

        # # Node, edge and graph property generators
        # self._node_property_generators = dict()
        # self._edge_property_generators = dict()
        # self._graph_property_generators = dict()

        # Pointed model
        self._init_state = None

    def __str__(self):
        return f"<{self.__class__.__name__} object at {id(self)}>"

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _add_states_to_graph(self, graph):
        """
        Mutates the input graph.
        """
        assert isinstance(self.states(), (tuple, list)), f"{self.__class__.__name__}.states() must return a list/tuple."
        states = self.states()
        node_ids = list(graph.add_nodes(len(states)))
        p_map = NodePropertyMap(graph=graph)
        for i in range(len(node_ids)):
            p_map[node_ids[i]] = states[i]
        graph["states"] = p_map
        print(util.BColors.OKCYAN, f"[INFO] Processing node property: states.", util.BColors.ENDC)

    def _add_edges_to_graph(self, graph):
        """
        Mutates the input graph.
        """
        pass

    def _add_node_prop_to_graph(self, graph, p_name, default=None):
        """
        Assumes nodes are already added to graph.
        """
        try:
            p_map = NodePropertyMap(graph=graph, default=default)
            p_func = self.NODE_PROPERTY[p_name]
            for node in graph.nodes():
                state = graph["states"][node]
                p_map[node] = p_func(state)
            graph[p_name] = p_map
        except NotImplementedError:
            print(util.BColors.WARNING, f"[WARN] Ignoring node property: {p_name}. NotImplemented", util.BColors.ENDC)

    def _add_edge_prop_to_graph(self, graph, p_name, default=None):
        """
        Mutates the input graph.
        """
        try:
            p_map = EdgePropertyMap(graph=graph, default=default)
            p_func = self.EDGE_PROPERTY[p_name]
            for uid, vid, key in graph.edges():
                p_map[(uid, vid, key)] = p_func(uid, vid, key)
            graph[p_name] = p_map
        except NotImplementedError:
            print(util.BColors.WARNING, f"[WARN] Ignoring node property: {p_name}. NotImplemented", util.BColors.ENDC)

    def _add_graph_prop_to_graph(self, graph, p_name):
        """
        Mutates the input graph.
        """
        try:
            if inspect.isfunction(self.GRAPH_PROPERTY[p_name]):
                p_func = self.GRAPH_PROPERTY[p_name]
                graph[p_name] = p_func(self)
            elif inspect.ismethod(self.GRAPH_PROPERTY[p_name]):
                p_func = self.GRAPH_PROPERTY[p_name]
                graph[p_name] = p_func()
            else:
                graph[p_name] = self.GRAPH_PROPERTY[p_name]
        except NotImplementedError:
            print(util.BColors.WARNING, f"[WARN] Ignoring node property: {p_name}. NotImplemented", util.BColors.ENDC)

    def _define_special_properties(self):
        pass

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def states(self):
        raise NotImplementedError(f"{self.__class__.__name__}.states() is not implemented.")

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def initialize(self, state):
        if state in self.states():
            self._init_state = state

    def graphify(self, pointed=False):
        if pointed is True and self._init_state is None:
            raise ValueError(f"{self.__class__.__name__} is not initialized. "
                             f"Did you forget to call {self.__class__.__name__}.initialize() function?")
        elif pointed is True and self._init_state is not None:
            graph = self.graphify_pointed()
        else:
            graph = self.graphify_unpointed()

        print(util.BColors.OKGREEN, f"[SUCCESS] {graph} generated.", util.BColors.ENDC)
        return graph

    def graphify_pointed(self):
        raise NotImplementedError(f"{self.__class__.__name__}._graphify_pointed() is not implemented.")

    def graphify_unpointed(self):
        # raise NotImplementedError(f"{self.__class__.__name__}._graphify_unpointed() is not implemented.")
        graph = Graph()
        self._add_states_to_graph(graph)
        return graph

    def serialize(self):
        # 1. Graphify
        # 2. Serialize the graph
        # 3. Return a dict
        pass

    def save(self, fpath, pointed=False, overwrite=False):
        # 1. Graphify
        # 2. Save the graph
        pass

    @classmethod
    def deserialize(cls, obj_dict):
        # 1. Construct a graph from obj_dict.
        # 2. Define functions from graph
        # 3. Create cls() instance.
        # 4. Update __dir__ with new methods
        # 5. Return instance
        pass

    @classmethod
    def load(cls, fpath):
        # 1. Load obj_dict
        # 2. deserialize
        pass

    @register_property(GRAPH_PROPERTY)
    def init_state(self):
        return self._init_state


class TSys(GraphicalModel):
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(TSys, self).__init__(**kwargs)

        # TSys properties
        self._is_turn_based = is_tb
        self._is_stochastic = is_stoch
        self._is_quantitative = is_quant

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _add_edges_to_graph(self, graph):
        """
        Mutates the input graph.
        """
        # Get list/tuple of states and actions
        actions = self.actions()
        try:
            atoms = self.atoms()
        except NotImplementedError:
            atoms = None

        # Assert conditions on user implemented functions
        assert isinstance(actions, (tuple, list))
        assert isinstance(atoms, (tuple, list)) or atoms is None

        # Add edges
        property_act = EdgePropertyMap(graph=self)
        property_prob = EdgePropertyMap(graph=self, default=0.0)
        states = self.states()
        for nid in graph.nodes():
            st = states[nid]
            for act in actions:
                next_states = self.delta(st, act)

                # Deterministic TSys
                if not self._is_stochastic and next_states is not None:
                    uid = states.index(st)
                    vid = states.index(next_states)
                    key = graph.add_edge(uid, vid)
                    property_act[(uid, vid, key)] = act

                # Stochastic, qualitative
                elif self._is_stochastic and not self._is_quantitative and next_states is not None:
                    for n_state in next_states:
                        uid = states.index(st)
                        vid = states.index(n_state)
                        key = graph.add_edge(uid, vid)
                        property_act[(uid, vid, key)] = actions.index(act)

                # Stochastic, quantitative
                elif self._is_stochastic and self._is_stochastic and next_states is not None:
                    for n_state in next_states.support():
                        uid = states.index(st)
                        vid = states.index(n_state)
                        key = graph.add_edge(uid, vid)
                        property_act[(uid, vid, key)] = actions.index(act)
                        property_prob[(uid, vid, key)] = next_states.pmf(n_state)

                else:
                    print(util.BColors.WARNING, f"[WARN] {self.__class__.__name__}._graphify_unpointed(): "
                                                f"No edge(s) added to graph for state={st}, action={act}.",
                          util.BColors.ENDC)

        graph["act"] = property_act
        print(util.BColors.OKCYAN, f"[INFO] Processing edge property: act.", util.BColors.ENDC)

        graph["prob"] = property_prob
        print(util.BColors.OKCYAN, f"[INFO] Processing edge property: prob.", util.BColors.ENDC)

        return graph

    def _define_special_properties(self):
        self.NODE_PROPERTY.update({
            "turn": self.turn,
            "label": self.label,
        })
        self.GRAPH_PROPERTY.update({
            "actions": self.actions,
            "atoms": self.atoms,
        })

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def graphify_unpointed(self):
        graph = super(TSys, self).graphify_unpointed()
        self._add_edges_to_graph(graph)

        # Define special properties
        self._define_special_properties()

        # Graphify properties.
        for p_name in self.NODE_PROPERTY:
            print(util.BColors.OKCYAN, f"[INFO] Processing node property: {p_name}.", util.BColors.ENDC)
            self._add_node_prop_to_graph(graph, p_name)
        for p_name in self.EDGE_PROPERTY:
            print(util.BColors.OKCYAN + f"[INFO] Processing edge property: {p_name}.", util.BColors.ENDC)
            self._add_edge_prop_to_graph(graph, p_name)
        for p_name in self.GRAPH_PROPERTY:
            print(util.BColors.OKCYAN + f"[INFO] Processing graph property: {p_name}.", util.BColors.ENDC)
            self._add_graph_prop_to_graph(graph, p_name)
        return graph

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def actions(self):
        raise NotImplementedError(f"{self.__class__.__name__}.actions() is not implemented.")

    def delta(self, state, act):
        raise NotImplementedError(f"{self.__class__.__name__}.delta() is not implemented.")

    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    def label(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")

    def turn(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def is_turn_based(self):
        return self._is_turn_based

    @register_property(GRAPH_PROPERTY)
    def is_stochastic(self):
        return self._is_stochastic

    @register_property(GRAPH_PROPERTY)
    def is_quantitative(self):
        return self._is_quantitative


class Automaton(GraphicalModel):
    """
    Alphabet is powerset(atoms).
    """
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    REACHABILITY = "Reach"
    BUCHI = "Buchi"

    def __init__(self, **kwargs):
        super(Automaton, self).__init__(**kwargs)

        # Default properties (will be treated as graph properties during serialization)
        self.is_sbacc = None
        self.is_complete = None
        self.is_stutter_invariant = None
        self.is_deterministic = None
        self.is_unambiguous = None
        self.is_terminal = None

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _add_edges_to_graph(self, graph):
        """
        No merging of parallel edges performed right now.
        # TODO. Merge parallel edges to compress DFA.
        """
        edge_label = EdgePropertyMap(graph)
        states = self.states()
        for st in states:
            for inp in util.powerset(self.atoms()):
                next_state = self.delta(st, inp)
                if next_state is None:
                    print(util.BColors.WARNING + f"[WARN] Automaton transition undefined on state:{st}, inp:{inp}")
                    continue
                uid = states.index(st)
                vid = states.index(next_state)
                key = graph.add_edge(uid, vid)
                edge_label[(uid, vid, key)] = inp

        graph["edge_label"] = edge_label
        print(util.BColors.OKCYAN, f"[INFO] Processing edge property: edge_label.", util.BColors.ENDC)

        return graph

    def _define_special_properties(self):
        super(Automaton, self)._define_special_properties()

        self.NODE_PROPERTY.update({
            "final": self.final,
        })
        self.GRAPH_PROPERTY.update({
            "atoms": self.atoms,
            "acc_cond": self.acc_cond,
        })

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def delta(self, state, inp):
        raise NotImplementedError(f"{self.__class__.__name__}.delta() is not implemented.")

    def acc_cond(self):
        raise NotImplementedError(f"{self.__class__.__name__}.acc_cond() is not implemented.")

    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    def final(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")

    def num_acc_sets(self):
        raise NotImplementedError(f"{self.__class__.__name__}.num_acc_sets() is not implemented.")

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def is_supported_acc_cond(self):
        """
        Checks if acceptance condition is supported.
        """
        pass

    def graphify_unpointed(self):
        graph = super(Automaton, self).graphify_unpointed()
        self._add_edges_to_graph(graph)

        # Define special properties
        self._define_special_properties()

        # Graphify properties.
        for p_name in self.NODE_PROPERTY:
            print(util.BColors.OKCYAN, f"[INFO] Processing node property: {p_name}.", util.BColors.ENDC)
            self._add_node_prop_to_graph(graph, p_name)
        for p_name in self.EDGE_PROPERTY:
            print(util.BColors.OKCYAN + f"[INFO] Processing edge property: {p_name}.", util.BColors.ENDC)
            self._add_edge_prop_to_graph(graph, p_name)
        for p_name in self.GRAPH_PROPERTY:
            print(util.BColors.OKCYAN + f"[INFO] Processing graph property: {p_name}.", util.BColors.ENDC)
            self._add_graph_prop_to_graph(graph, p_name)
        return graph


class Game(TSys):
    NODE_PROPERTY = TSys.NODE_PROPERTY.copy()
    EDGE_PROPERTY = TSys.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = TSys.GRAPH_PROPERTY.copy()

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(Game, self).__init__(is_tb=is_tb, is_stoch=is_stoch, is_quant=is_quant, **kwargs)

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _define_special_properties(self):
        super(Game, self)._define_special_properties()

        self.NODE_PROPERTY.update({
            "final": self.final,
        })

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def final(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")


class Solver(Game):
    NODE_PROPERTY = TSys.NODE_PROPERTY.copy()
    EDGE_PROPERTY = TSys.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = TSys.GRAPH_PROPERTY.copy()

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(Solver, self).__init__(is_tb=is_tb, is_stoch=is_stoch, is_quant=is_quant, **kwargs)
        self._game = None

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _define_special_properties(self):
        super(Game, self)._define_special_properties()

        self.NODE_PROPERTY.update({
            "p1_win": self.p1_win,
            "p2_win": self.p2_win,
            "p3_win": self.p3_win,
            "pi1": self.pi1,
            "pi2": self.pi2,
            "pi3": self.pi3
        })
        self.EDGE_PROPERTY.update({

        })

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def solve(self):
        raise NotImplementedError(f"{self.__class__.__name__}.solve() is not implemented.")

    def load_game(self, game):
        assert isinstance(game, Game)
        self._game = game

    def load_game_from_file(self, fpath):
        raise NotImplementedError(f"{self.__class__.__name__}.load_game_from_file() is not implemented.")

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def p1_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p1_win() is not implemented.")

    def p2_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p2_win() is not implemented.")

    def p3_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p3_win() is not implemented.")

    def pi1(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi1() is not implemented.")

    def pi2(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi2() is not implemented.")

    def pi3(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi3() is not implemented.")