# TODO. Try implementing zlk package.
# TODO. Add logging statements.
# TODO. Make note that user will not be warned of any private attributes that are unserialized.
# TODO. Make note that user must update RESERVED_PROPERTIES and _graphify_unpointed appropriately.
# TODO. Instead of registering property function, register just name and then use getattr to
#  find the appropriate function during serialization. This will allow rebinding functions.
import inspect
import logging
import typing
from ggsolver import util
from ggsolver.graph import NodePropertyMap, EdgePropertyMap, Graph
from functools import partial


# ==========================================================================
# DECORATOR FUNCTIONS.
# ==========================================================================
def register_property(property_set: set):
    def register_function(func):
        if func.__name__ in property_set:
            print(util.BColors.WARNING, f"[WARN] Duplicate property: {func.__name__}.", util.BColors.ENDC)
        property_set.add(func.__name__)
        return func
    return register_function


# ==========================================================================
# BASE CLASS.
# ==========================================================================
class GraphicalModel:
    NODE_PROPERTY = set()
    EDGE_PROPERTY = set()
    GRAPH_PROPERTY = set()

    def __init__(self, is_deterministic=True, is_quantitative=False, **kwargs):
        """
        Types of Graphical Models. Acceptable values:
        - Deterministic: (det: True, quant: [don't care]),
        - Non-deterministic: (det: False, quant: False),
        - Stochastic: (det: False, quant: True).
        """
        # Types of Graphical Models. Acceptable values:
        self._is_deterministic = is_deterministic
        self._is_quantitative = is_quantitative

        # Input domain (Expected value: A function that returns an Iterable object.)
        self._inp_domain = kwargs["input_domain"] if "input_domain" in kwargs else None

        # Pointed model
        self._init_state = kwargs["init_state"] if "init_state" in kwargs else None

        # Caching variables during serializing and deserializing the model.
        self.__states = list()
        self.__state2node = dict()

    def __str__(self):
        return f"<{self.__class__.__name__} object at {id(self)}>"

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _add_nodes_to_graph(self, graph):
        """
        Adds nodes to the input graph and sets the "state" property.
        """
        assert isinstance(self.states(), (tuple, list)), f"{self.__class__.__name__}.states() must return a list/tuple."
        states = self.states()
        node_ids = list(graph.add_nodes(len(states)))
        p_map = NodePropertyMap(graph=graph)
        for i in range(len(node_ids)):
            p_map[node_ids[i]] = states[i]
        graph["state"] = p_map

        # Cache states
        self.__states = states

        # Logging and printing
        logging.info(util.ColoredMsg.ok(f"[INFO] Processed graph property: states. Added {len(node_ids)} states."))

    def _add_edges_to_graph(self, graph):
        """
        Adds edges to the input graph and sets the "input" property.
        Each edge is unique identified by a triple (state, input, next_state).

        Assumes: self._add_nodes_to_graph() is called before and self.__states is cached.
        """
        try:
            inputs = self._inp_domain()
            assert isinstance(inputs, (list, tuple)), f"{self.__class__.__name__}.inp_domain must be a list/tuple."
        except TypeError:
            logging.error(util.ColoredMsg.error(f"[ERROR] Input domain of {self} is not set. No edges were added."))
            return

        if len(inputs) == 0:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Input domain of {self} is empty. No edges were added."))

        # Create an edge property called input
        property_inp = EdgePropertyMap(graph=self)
        property_prob = EdgePropertyMap(graph=self, default=None)

        # Generate edges by applying each input to every state.
        for state in self.__states:
            for inp in inputs:
                next_states = self.delta(state, inp)

                # There are three types of graphical models. Handle each separately.
                # If model is deterministic, next states is a single state.
                if self.is_deterministic:
                    uid = self.__states.index(state)
                    vid = self.__states.index(next_states)
                    key = graph.add_edge(uid, vid)
                    property_inp[(uid, vid, key)] = inp

                # If model is non-deterministic, next states is an Iterable of states.
                elif not self.is_deterministic and not self.is_quantitative:
                    for next_state in next_states:
                        uid = self.__states.index(state)
                        vid = self.__states.index(next_state)
                        key = graph.add_edge(uid, vid)
                        property_inp[(uid, vid, key)] = inp

                # If model is stochastic, next states is a Distribution of states.
                elif not self.is_deterministic and self.is_quantitative:
                    for next_state in next_states.support():
                        uid = self.__states.index(state)
                        vid = self.__states.index(next_state)
                        key = graph.add_edge(uid, vid)
                        property_inp[(uid, vid, key)] = inp
                        property_prob[(uid, vid, key)] = next_states.pmf(next_state)

                else:
                    raise TypeError("Graphical Model is neither deterministic, nor non-deterministic, nor stochastic! "
                                    f"Check the values: is_deterministic: {self.is_deterministic}, "
                                    f"self.is_quantitative:{self.is_quantitative}.")

        # Update the properties with graph
        graph["inp_domain"] = inputs
        graph["input"] = property_inp
        graph["prob"] = property_prob

        # Logging and printing
        logging.info(util.ColoredMsg.ok(f"[INFO] Processed graph property: inp_domain. OK."))
        logging.info(util.ColoredMsg.ok(f"[INFO] Processed edge property: input. OK."))
        logging.info(util.ColoredMsg.ok(f"[INFO] Processed edge property: prob. OK."))

    def _add_node_prop_to_graph(self, graph, p_name, default=None):
        """
        Adds the node property called `p_name` to the graph.

        Requires: `p_name` should be a function in self that inputs a single parameter: state.

        Assumes: self._add_nodes_to_graph() is called before.
        """
        if graph.has_property(p_name):
            logging.warning(util.ColoredMsg.warn(f"[WARN] Duplicate property is ignored: {p_name}. IGNORED"))
            return

        try:
            p_map = NodePropertyMap(graph=graph, default=default)
            p_func = getattr(self, p_name)   # self.NODE_PROPERTY[p_name]
            if not (inspect.isfunction(p_func) or inspect.ismethod(p_func)):
                raise TypeError(f"Node property {p_func} is not a function.")
            for uid in range(len(self.__states)):
                p_map[uid] = p_func(self.__states[uid])
            graph[p_name] = p_map
            logging.info(util.ColoredMsg.ok(f"[INFO] Processed node property: {p_name}. OK"))
        except NotImplementedError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Node property function not implemented: {p_name}. IGNORED"))
        except AttributeError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Node property function is not defined: {p_name}. IGNORED"))

    def _add_edge_prop_to_graph(self, graph, p_name, default=None):
        """
        Adds an edge property called `p_name` to the graph.

        Requires: `p_name` should be a function in self that inputs three parameters: state, inp, next_state .

        Assumes: self._add_nodes_to_graph() is called.
        Assumes: self._add_edges_to_graph() is called.
        """
        if graph.has_property(p_name):
            logging.warning(util.ColoredMsg.warn(f"[WARN] Duplicate property: {p_name}. IGNORED"))
            return

        try:
            p_map = EdgePropertyMap(graph=graph, default=default)
            p_func = getattr(self, p_name)
            if not (inspect.isfunction(p_func) or inspect.ismethod(p_func)):
                raise TypeError(f"Edge property {p_func} is not a function.")
            for uid, vid, key in graph.edges():
                p_map[(uid, vid, key)] = p_func(self.__states[uid], graph["input"][(uid, vid, key)], self.__states[vid])
            graph[p_name] = p_map
            logging.info(util.ColoredMsg.ok(f"[INFO] Processed edge property: {p_name}. OK"))
        except NotImplementedError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Edge property not implemented: {p_name}. IGNORED"))
        except AttributeError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Node property function is not defined: {p_name}. IGNORED"))

    def _add_graph_prop_to_graph(self, graph, p_name):
        """
        Adds a graph property called `p_name` to the graph.

        Requires: `p_name` should be a function in self that inputs no parameters.

        Assumes: self._add_states_to_graph() is called before and self.__states is cached.
        """
        if graph.has_property(p_name):
            logging.warning(util.ColoredMsg.warn(f"[WARN] Duplicate property: {p_name}. IGNORED"))
            return

        try:
            p_func = getattr(self, p_name)
            if inspect.ismethod(p_func) or (inspect.isfunction(p_func) and p_func.__name__ == "<lambda>"):
                graph[p_name] = p_func()
                logging.info(util.ColoredMsg.ok(f"[INFO] Processed graph property: {p_name}. OK"))
            elif inspect.isfunction(p_func):
                graph[p_name] = p_func(self)
                logging.info(util.ColoredMsg.ok(f"[INFO] Processed graph property: {p_name}. OK"))
            # elif inspect.ismethod(p_func):
            #     graph[p_name] = p_func()
            #     logging.warning(util.ColoredMsg.ok(f"[INFO] Processed graph property: {p_name}. OK"))
            else:
                raise TypeError(f"Graph property {p_name} is neither a function nor a method.")
        except NotImplementedError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Graph property is not implemented: {p_name}. IGNORED"))
        except AttributeError:
            logging.warning(util.ColoredMsg.warn(f"[WARN] Node property function is not defined: {p_name}. IGNORED"))
    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    # @register_property(GRAPH_PROPERTY)
    def states(self):
        raise NotImplementedError(f"{self.__class__.__name__}.states() is not implemented.")

    def delta(self, state, inp) -> typing.Union[util.Distribution, typing.Iterable, object]:
        pass

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
        graph = Graph()

        # Glob node, edge and graph properties
        state_props = self.NODE_PROPERTY
        trans_props = self.EDGE_PROPERTY
        graph_props = self.GRAPH_PROPERTY

        # Warn about duplication
        logging.info(util.ColoredMsg.header(f"[INFO] Globbed state properties: {state_props}"))
        logging.info(util.ColoredMsg.header(f"[INFO] Globbed trans properties: {trans_props}"))
        logging.info(util.ColoredMsg.header(f"[INFO] Globbed graph properties: {graph_props}"))
        logging.info(util.ColoredMsg.header(f"[INFO] Duplicate state, trans properties: "
                                            f"{set.intersection(state_props, trans_props)}"))
        logging.info(util.ColoredMsg.header(f"[INFO] Duplicate trans, graph properties: "
                                            f"{set.intersection(trans_props, graph_props)}"))
        logging.info(util.ColoredMsg.header(f"[INFO] Duplicate graph, state properties: "
                                            f"{set.intersection(graph_props, state_props)}"))

        # Add nodes and edges to the graph
        self._add_nodes_to_graph(graph)
        self._add_edges_to_graph(graph)

        # Add node properties
        for p_name in state_props:
            self._add_node_prop_to_graph(graph, p_name)

        # Add edge properties
        for p_name in trans_props:
            self._add_edge_prop_to_graph(graph, p_name)

        # Add graph properties
        for p_name in graph_props:
            self._add_graph_prop_to_graph(graph, p_name)

        return graph

    def serialize(self):
        # 1. Graphify
        # 2. Serialize the graph
        # 3. Return a dict
        pass

    def save(self, fpath, pointed=False, overwrite=False, protocol="json"):
        # 1. Graphify
        graph = self.graphify(pointed=pointed)

        # 2. Save the graph
        graph.save(fpath, overwrite=overwrite, protocol=protocol)

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
        # Load game graph
        graph = Graph.load(fpath)

        # Create object
        obj = cls()

        # Add graph properties
        for gprop, gprop_value in graph.graph_properties.items():
            func_code = f"""def {gprop}():\n\treturn {gprop_value}"""
            exec(func_code)
            func = locals()[gprop]
            setattr(obj, gprop, func)

        # Construct inverse state mapping
        for node in graph.nodes():
            state = graph["state"][node]
            if isinstance(state, list):
                state = tuple(state)
            obj.__state2node[state] = node

        # Add node properties
        def get_node_property(state, name):
            return graph.node_properties[name][obj.__state2node[state]]

        for nprop, nprop_value in graph.node_properties.items():
            setattr(obj, nprop, partial(get_node_property, name=nprop))

        # TODO. Add edge properties (How to handle them is unclear).

        # Reconstruct delta function
        def delta(state, act):
            # Get node from state
            node = obj.__state2node[state]

            # Get out_edges from node in graph
            out_edges = graph.out_edges(node)

            # Iterate over each out edge to match action.
            successors = set()
            for uid, vid, key in out_edges:
                action_label = graph["act"][(uid, vid, key)]
                if action_label == act:
                    successors.add(vid)

            # If model is deterministic, then return single state.
            if not graph["is_stochastic"]:
                return graph["state"][successors.pop()]

            # If model is stochastic and NOT quantitative, then return list of states.
            elif graph["is_stochastic"] and not graph["is_quantitative"]:
                return [graph["state"][vid] for vid in successors]

            # If model is stochastic and quantitative, then return distribution.
            else:
                successors = [graph["state"][vid] for vid in successors]
                prob = [graph["prob"][uid] for uid in successors]
                return util.Distribution(successors, prob)

        obj.delta = delta

        # Return reconstructed object
        return obj

    @register_property(GRAPH_PROPERTY)
    def init_state(self):
        return self._init_state

    @register_property(GRAPH_PROPERTY)
    def is_deterministic(self):
        return self._is_deterministic

    @register_property(GRAPH_PROPERTY)
    def is_quantitative(self):
        return self._is_quantitative


# ==========================================================================
# USER MODELS.
# ==========================================================================
class TSys(GraphicalModel):
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    def __init__(self, is_turn_based=True, is_deterministic=True, is_quantitative=False, **kwargs):
        super(TSys, self).__init__(input_domain=self.actions,
                                   is_deterministic=is_deterministic,
                                   is_quantitative=is_quantitative,
                                   **kwargs)

        # TSys can be turn-based or concurrent.
        self._is_turn_based = is_turn_based

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(GRAPH_PROPERTY)
    def actions(self):
        raise NotImplementedError(f"{self.__class__.__name__}.actions() is not implemented.")

    def delta(self, state, act):
        raise NotImplementedError(f"{self.__class__.__name__}.delta() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    @register_property(NODE_PROPERTY)
    def label(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")

    @register_property(NODE_PROPERTY)
    def turn(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def is_turn_based(self):
        return self._is_turn_based


class Game(TSys):
    def __init__(self, is_turn_based=True, is_deterministic=True, is_quantitative=False, **kwargs):
        super(Game, self).__init__(is_turn_based=is_turn_based,
                                   is_deterministic=is_deterministic,
                                   is_quantitative=is_quantitative,
                                   **kwargs)

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(TSys.NODE_PROPERTY)
    def final(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")


class Automaton(GraphicalModel):
    """
    Alphabet is powerset(atoms).
    """
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    REACHABILITY = "Reach"
    BUCHI = "Buchi"

    def __init__(self, acc_cond, **kwargs):
        super(Automaton, self).__init__(**kwargs)

        # If user provides direct definition of automaton
        if "states" in kwargs:
            self.states = lambda: list(kwargs["states"])

        if "atoms" in kwargs:
            self.atoms = lambda: list(kwargs["atoms"])

        if "init_state" in kwargs:
            self._init_state = lambda: list(kwargs["init_state"])

        if "final" in kwargs:
            self.final = lambda st: st in kwargs["final"]

        # Default properties (will be treated as graph properties during serialization)
        self._acc_cond = acc_cond
        self._is_sbacc = kwargs["is_sbacc"] if "is_sbacc" in kwargs else None
        self._is_complete = kwargs["is_complete"] if "is_complete" in kwargs else None
        self._is_stutter_invariant = kwargs["is_stutter_invariant"] if "is_stutter_invariant" in kwargs else None
        self._is_unambiguous = kwargs["is_unambiguous"] if "is_unambiguous" in kwargs else None
        self._is_terminal = kwargs["is_terminal"] if "is_terminal" in kwargs else None

    # ==========================================================================
    # PRIVATE FUNCTIONS.
    # ==========================================================================
    def _add_edges_to_graph(self, graph):
        """
        TODO. post process edges to merge parallel edges.
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

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(GRAPH_PROPERTY)
    def acc_cond(self):
        return self._acc_cond

    @register_property(GRAPH_PROPERTY)
    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    @register_property(NODE_PROPERTY)
    def final(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def num_acc_sets(self):
        raise NotImplementedError(f"{self.__class__.__name__}.num_acc_sets() is not implemented.")

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    @register_property(GRAPH_PROPERTY)
    def is_sbacc(self):
        return self._is_sbacc

    @register_property(GRAPH_PROPERTY)
    def is_complete(self):
        return self._is_complete

    @register_property(GRAPH_PROPERTY)
    def is_stutter_invariant(self):
        return self._is_stutter_invariant

    @register_property(GRAPH_PROPERTY)
    def is_unambiguous(self):
        return self._is_unambiguous

    @register_property(GRAPH_PROPERTY)
    def is_terminal(self):
        return self._is_terminal


class Solver(Game):
    NODE_PROPERTY = TSys.NODE_PROPERTY.copy()
    EDGE_PROPERTY = TSys.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = TSys.GRAPH_PROPERTY.copy()

    def __init__(self, is_tb=True, is_stoch=False, is_quant=False, **kwargs):
        super(Solver, self).__init__(is_tb=is_tb, is_stoch=is_stoch, is_quant=is_quant, **kwargs)
        self._game = None

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def actions(self):
        return self.game.actions()

    def delta(self, state, act):
        return self.game.delta(state, act)

    def atoms(self):
        return self.game.atoms()

    def label(self, state):
        return self.game.label(state)

    def turn(self, state):
        return self.game.turn(state)

    def states(self):
        return self.game.states()

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
    @register_property(NODE_PROPERTY)
    def p1_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p1_win() is not implemented.")

    @register_property(NODE_PROPERTY)
    def p2_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p2_win() is not implemented.")

    @register_property(NODE_PROPERTY)
    def p3_win(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.p3_win() is not implemented.")

    @register_property(NODE_PROPERTY)
    def pi1(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi1() is not implemented.")

    @register_property(NODE_PROPERTY)
    def pi2(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi2() is not implemented.")

    @register_property(NODE_PROPERTY)
    def pi3(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.pi3() is not implemented.")

    @property
    def game(self):
        if self._game is None:
            raise ValueError("Solver is not initialized. Did you forget to call Solver.load_game() function?")
        return self._game