# TODO. Try implementing zlk package.
# TODO. Add logging statements.
# FIXME. _graphify_unpointed() needs to be modularized for reuse in _graphify_pointed().

import inspect
from ggsolver import util
from ggsolver import graph


class GraphicalModel(graph.Graph):
    RESERVED_PROPERTIES = [
        "state",                # node property
        "is_turn_based",        # graph property
        "is_stochastic",        # graph property
        "is_quantitative",      # graph property
    ]

    def __init__(self, **kwargs):
        super(GraphicalModel, self).__init__()

        # Node, edge and graph property generators
        self._node_property_generators = dict()
        self._edge_property_generators = dict()
        self._graph_property_generators = dict()

        # Pointed model
        self._init_state = None

    def __str__(self):
        return f"<{self.__class__.__name__} object at {id(self)}>"

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _graphify_pointed(self):
        raise NotImplementedError(f"{self.__class__.__name__}._graphify_pointed() is not implemented.")

    def _graphify_unpointed(self):
        raise NotImplementedError(f"{self.__class__.__name__}._graphify_unpointed() is not implemented.")

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def states(self):
        raise NotImplementedError(f"{self.__class__.__name__}.states() is not implemented.")

    def actions(self):
        raise NotImplementedError(f"{self.__class__.__name__}.actions() is not implemented.")

    def delta(self, state, act):
        raise NotImplementedError(f"{self.__class__.__name__}.delta() is not implemented.")

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def initialize(self, state):
        if state in self.states():
            self._init_state = state

    def graphify(self, pointed=False):
        if pointed is True and self._init_state is not None:
            self._graphify_pointed()
        elif pointed is True and self._init_state is None:
            raise ValueError("TSys is not initialized. Did you forget to call TSys.initialize() function?")
        else:
            self._graphify_unpointed()

        # Warn about any properties that were ignored.
        # TODO. Make note that user will not be warned of any private attributes that are unserialized.
        # TODO. Make note that user must update RESERVED_PROPERTIES and _graphify_unpointed appropriately.
        private_attr = {attr for attr in self.__dict__.keys() if attr[0] == "_"}
        unserialized_attr = set(self.__dict__.keys()) - set(self.RESERVED_PROPERTIES) - private_attr

        if len(unserialized_attr) > 0:
            print(util.BColors.WARNING,
                  f"[WARN] Attributes {unserialized_attr} were not serialized because they are not "
                  f"node/edge/graph properties.", util.BColors.ENDC)

        print(util.BColors.OKGREEN, f"[SUCCESS] {graph.Graph.__str__(self)} generated.", util.BColors.ENDC)

    def serialize(self):
        pass

    def save(self, fpath, pointed=False, overwrite=False):
        pass

    @classmethod
    def deserialize(cls, obj_dict):
        pass

    @classmethod
    def load(cls, fpath):
        pass

    # ==========================================================================
    # DECORATOR FUNCTIONS.
    # ==========================================================================
    # @staticmethod
    def node_property(self, func):
        if func.__name__ in self.RESERVED_PROPERTIES:
            raise NameError(f"{func.__name__} is a RESERVED_PROPERTY. Cannot mark it as a node property.")
        self._node_properties[func.__name__] = func
        return func

    def edge_property(self, func):
        if func.__name__ in self.RESERVED_PROPERTIES:
            raise NameError(f"{func.__name__} is a RESERVED_PROPERTY. Cannot mark it as a edge property.")
        self._edge_properties[func.__name__] = func
        return func

    def graph_property(self, func):
        if func.__name__ in self.RESERVED_PROPERTIES:
            raise NameError(f"{func.__name__} is a RESERVED_PROPERTY. Cannot mark it as a graph property.")
        self._graph_properties[func.__name__] = func
        return func


class TSys(GraphicalModel):
    RESERVED_PROPERTIES = GraphicalModel.RESERVED_PROPERTIES + [
        "turn",             # node property
        "label",            # node property
        "act",              # edge property
        "prob",             # edge property
        "actions",          # graph property
        "atoms",            # graph property
    ]

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(TSys, self).__init__(**kwargs)

        # TSys properties
        self._is_turn_based = is_tb
        self._is_stochastic = is_stoch
        self._is_quantitative = is_quant

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _graphify_unpointed(self):
        # Get list/tuple of states and actions
        #   Avoid recomputing any complex parts of states() and action() functions.
        states = self.states()
        actions = self.actions()
        try:
            atoms = self.atoms()
        except NotImplementedError:
            atoms = None

        # Assert conditions on user implemented functions
        assert isinstance(states, (tuple, list))
        assert isinstance(actions, (tuple, list))
        assert isinstance(atoms, (tuple, list)) or atoms is None

        # Reset the transition system graph
        self.clear()

        # Add nodes
        self.add_nodes(len(self.states()))

        # Add edges
        property_act = graph.EdgePropertyMap(graph=self)
        property_prob = graph.EdgePropertyMap(graph=self, default=0.0)
        for st in states:
            for act in actions:
                next_states = self.delta(st, act)

                # Deterministic TSys
                if not self._is_stochastic and next_states is not None:
                    uid = states.index(st)
                    vid = states.index(next_states)
                    key = self.add_edge(uid, vid)
                    property_act[(uid, vid, key)] = act

                # Stochastic, qualitative
                elif self._is_stochastic and not self._is_quantitative and next_states is not None:
                    for n_state in next_states:
                        uid = states.index(st)
                        vid = states.index(n_state)
                        key = self.add_edge(uid, vid)
                        property_act[(uid, vid, key)] = actions.index(act)

                # Stochastic, quantitative
                elif self._is_stochastic and self._is_stochastic and next_states is not None:
                    for n_state in next_states.support():
                        uid = states.index(st)
                        vid = states.index(n_state)
                        key = self.add_edge(uid, vid)
                        property_act[(uid, vid, key)] = actions.index(act)
                        property_prob[(uid, vid, key)] = next_states.pmf(n_state)

                else:
                    print(util.BColors.WARNING, f"[WARN] {self.__class__.__name__}._graphify_unpointed(): "
                                                f"No edge(s) added to graph for state={st}, action={act}.",
                          util.BColors.ENDC)

        # Generate standard node properties (state, turn, label)
        property_state = graph.NodePropertyMap(graph=self)
        for st in states:
            property_state[states.index(st)] = st

        property_turn = graph.NodePropertyMap(graph=self, default=0)
        try:
            for st in states:
                st_turn = self.turn(st)
                property_turn[states.index(st)] = st_turn if st_turn is not None else property_turn.default
        except NotImplementedError:
            pass

        property_label = graph.NodePropertyMap(graph=self, default=set())
        try:
            for st in states:
                st_label = self.label(st)
                property_label[states.index(st)] = st_label if st_label is not None else property_label.default
        except NotImplementedError:
            pass

        # TODO. Add globbed properties.

        # Add node, edge and graph properties to graph
        self._node_properties.update({
            "state": property_state,
            "turn": property_turn,
            "label": property_label
        })
        self._edge_properties.update({
            "act": property_act,
            "prob": property_prob
        })
        self._graph_properties.update({
            "is_turn_based": self._is_turn_based,
            "is_stochastic": self._is_stochastic,
            "is_quantitative": self._is_quantitative,
            "actions": actions,
            "atoms": atoms
        })

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    def label(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")

    def turn(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")


class Automaton(GraphicalModel):
    """
    Alphabet is powerset(atoms).
    """
    RESERVED_PROPERTIES = GraphicalModel.RESERVED_PROPERTIES + [
        "final",                    # node property
        "symbol",                   # edge property
        "atoms",                    # graph property
        "is_sbacc",                 # graph property
        "is_complete",              # graph property
        "is_stutter_invariant",     # graph property
        "is_deterministic",         # graph property
        "is_unambiguous",           # graph property
        "is_terminal",              # graph property
        "acc_cond",                 # graph property
        "num_acc_sets",             # graph property
    ]

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

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def acc_cond(self):
        raise NotImplementedError(f"{self.__class__.__name__}.acc_cond() is not implemented.")

    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    def final(self):
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


class Game(TSys):
    RESERVED_PROPERTIES = TSys.RESERVED_PROPERTIES + [
        "final"
    ]

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(Game, self).__init__(is_tb=is_tb, is_stoch=is_stoch, is_quant=is_quant, **kwargs)

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _graphify_unpointed(self):
        super(Game, self)._graphify_unpointed()
        self._graph_properties["final"] = self.final()

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def final(self):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")
