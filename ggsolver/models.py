# TODO. Try implementing dtptb package.
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
from ggsolver.logic import pl
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

    def __init__(self, is_deterministic=True, is_probabilistic=False, **kwargs):
        # Types of Graphical Models. Acceptable values:
        self._is_deterministic = is_deterministic
        self._is_probabilistic = is_probabilistic

        # Input domain (Expected value: A function that returns an Iterable object.)
        self._inp_domain = kwargs["input_domain"] if "input_domain" in kwargs else None
        self._inp_name = kwargs["input_name"] if "input_name" in kwargs else None

        # Pointed model
        self._init_state = kwargs["init_state"] if "init_state" in kwargs else None

        # Caching variables during serializing and deserializing the model.
        self.__graph = None
        self.__is_graphified = False
        self.__states = list()
        self.__state2node = dict()

    def __str__(self):
        return f"<{self.__class__.__name__} object at {id(self)}>"

    def __setattr__(self, key, value):
        # If key is any non "__xxx" variable, set `is_graphified` to False.
        if key != "__is_graphified" and hasattr(self, "__is_graphified"):
            if key[0:2] != "__":
                self.__is_graphified = False
        super(GraphicalModel, self).__setattr__(key, value)

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
                    try:
                        uid = self.__states.index(state)
                        vid = self.__states.index(next_states)
                        key = graph.add_edge(uid, vid)
                        property_inp[(uid, vid, key)] = inp
                    except ValueError:
                        logging.warning(
                            util.ColoredMsg.warn(f"[WARN] {self.__class__.__name__}._graphify_unpointed(): "
                                                 f"No edge(s) added to graph for state={state}, input={inp}, "
                                                 f"next_state={next_states}.")
                        )

                # If model is non-deterministic, next states is an Iterable of states.
                elif not self.is_deterministic and not self.is_probabilistic:
                    for next_state in next_states:
                        try:
                            uid = self.__states.index(state)
                            vid = self.__states.index(next_state)
                            key = graph.add_edge(uid, vid)
                            property_inp[(uid, vid, key)] = inp
                        except ValueError:
                            logging.warning(
                                util.ColoredMsg.warn(f"[WARN] {self.__class__.__name__}._graphify_unpointed(): "
                                                     f"No edge(s) added to graph for state={state}, input={inp}, "
                                                     f"next_state={next_state}.")
                            )

                # If model is stochastic, next states is a Distribution of states.
                elif not self.is_deterministic and self.is_probabilistic:
                    for next_state in next_states.support():
                        try:
                            uid = self.__states.index(state)
                            vid = self.__states.index(next_state)
                            key = graph.add_edge(uid, vid)
                            property_inp[(uid, vid, key)] = inp
                            property_prob[(uid, vid, key)] = next_states.pmf(next_state)
                        except ValueError:
                            logging.warning(
                                util.ColoredMsg.warn(f"[WARN] {self.__class__.__name__}._graphify_unpointed(): "
                                                     f"No edge(s) added to graph for state={state}, input={inp}, "
                                                     f"next_state={next_state}.")
                            )

                else:
                    raise TypeError("Graphical Model is neither deterministic, nor non-deterministic, nor stochastic! "
                                    f"Check the values: is_deterministic: {self.is_deterministic}, "
                                    f"self.is_quantitative:{self.is_probabilistic}.")

        # Update the properties with graph
        graph["inp_domain"] = inputs
        graph["prob"] = property_prob
        graph["input"] = property_inp
        if self._inp_name is not None:
            graph[self._inp_name] = property_inp

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
    def states(self):
        """
        Defines the states component of the graphical model.

        :return: (list/tuple of JSONifiable object). List or tuple of states.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.states() is not implemented.")

    def delta(self, state, inp) -> typing.Union[util.Distribution, typing.Iterable, object]:
        pass

    # ==========================================================================
    # PUBLIC FUNCTIONS.
    # ==========================================================================
    def initialize(self, state):
        """
        Sets the initial state of the graphical model.

        .. note:: The function does NOT check if the given state is valid.
        """
        self._init_state = state

    def graphify(self, pointed=False):
        """
        Constructs the underlying graph of the graphical model.

        :param pointed: (bool) If pointed is `True`, the :py:meth:`TSys.graphify_pointed()` is called, which constructs
            a pointed graphical model containing only the states reachable from the initial state.  Otherwise,
            :py:meth:`TSys.graphify_unpointed()` is called, which constructs the complete transition system.
        :return: (:class:`ggsolver.graph.Graph` object) An equivalent graph representation of the graphical model.
        """
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
        """
        Constructs the underlying graph of the graphical model. The constructed graph contains only the states that are
        reachable from the initial state.

        :return: (:class:`ggsolver.graph.Graph` object) An equivalent graph representation of the graphical model.
        """
        raise NotImplementedError(f"{self.__class__.__name__}._graphify_pointed() is not implemented.")

    def graphify_unpointed(self):
        """
        Constructs the underlying graph of the graphical model. The constructed graph contains all possible states in
        the model.

        :return: (:class:`ggsolver.graph.Graph` object) An equivalent graph representation of the graphical model.
        """
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
        """
        Serializes the underlying graph of the graphical model into a dictionary with the following format.
        The state properties are saved as node properties, transition properties are stored are edge properties
        and model properties are stored as graph properties in the underlying graph::

            {
                "graph": {
                    "nodes": <number of nodes>,
                    "edges": {
                        uid: {vid: key},
                        ...
                    }
                    "node_properties": {
                        "property_name": {
                            "default": <value>,
                            "dict": {
                                "uid": <property value>,
                                ...
                            }
                        },
                        ...
                    },
                    "edge_properties": {
                        "property_name": {
                            "default": <value>,
                            "dict": [{"edge": [uid, vid, key], "pvalue": <property value>} ...]
                        },
                        ...
                    },
                    "graph_properties": {
                        "property_name": <value>,
                        ...
                    }
                }
            }

        :return: (dict) Serialized graphical model.
        """
        # 1. Graphify
        # 2. Serialize the graph
        # 3. Return a dict
        raise NotImplementedError

    def save(self, fpath, pointed=False, overwrite=False, protocol="json"):
        """
        Saves the graphical model to file.

        :param fpath: (str) Path to which the file should be saved. Must include an extension.
        :param pointed: (bool) If pointed is `True`, the :py:meth:`TSys.graphify_pointed()` is called, which constructs
            a pointed graphical model containing only the states reachable from the initial state.  Otherwise,
            :py:meth:`TSys.graphify_unpointed()` is called, which constructs the complete transition system.
        :param overwrite: (bool) Specifies whether to overwrite the file, if it exists. [Default: False]
        :param protocol: (str) The protocol to use to save the file. Options: {"json" [Default], "pickle"}.

        .. note:: Pickle protocol is not tested.
        """
        # 1. Graphify
        graph = self.graphify(pointed=pointed)

        # 2. Save the graph
        graph.save(fpath, overwrite=overwrite, protocol=protocol)

    @classmethod
    def deserialize(cls, obj_dict):
        """
        Constructs a graphical model from a serialized graph object. The node properties are deserialized as state
        properties, the edge properties are deserialized as transition properties, and the graph properties are
        deserialized as model properties. All the deserialized properties are represented as a function in the
        GraphicalModel class. See example #todo.

        The format is described in :py:meth:`GraphicalModel.serialize`.

        :return: (Sub-class of GraphicalModel) An instance of the `cls` class. `cls` must be a sub-class of
            `GraphicalModel`.
        """
        # 1. Construct a graph from obj_dict.
        # 2. Define functions from graph
        # 3. Create cls() instance.
        # 4. Update __dir__ with new methods
        # 5. Return instance
        raise NotImplementedError

    @classmethod
    def load(cls, fpath, protocol="json"):
        """
        Loads the graphical model from file.

        :param fpath: (str) Path to which the file should be saved. Must include an extension.
        :param protocol: (str) The protocol to use to save the file. Options: {"json" [Default], "pickle"}.

        .. note:: Pickle protocol is not tested.
        """
        # Load game graph
        graph = Graph.load(fpath, protocol=protocol)

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

    @classmethod
    def from_graph(cls, graph):
        # Create object
        obj = cls()

        # Save graph
        # TODO. This is inefficent because we are storing `__states` and `__graph`. Remove redundancy.
        obj.__graph = graph
        obj.__is_graphified = True

        # Add graph properties
        for gprop, gprop_value in graph.graph_properties.items():
            # func_code = f"""def {gprop}():\n\treturn {gprop_value}"""
            func = lambda: obj.__graph.graph_properties[gprop]
            # exec(func_code)
            # func = locals()[gprop]
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

    def is_nondeterministic(self):
        """ Returns `True` if the graphical model is non-deterministic. Else, returns `False`. """
        return not self._is_deterministic and not self._is_probabilistic

    @register_property(GRAPH_PROPERTY)
    def init_state(self):
        """
        Returns the initial state of the graphical model.
        """
        return self._init_state

    @register_property(GRAPH_PROPERTY)
    def is_deterministic(self):
        """
        Returns `True` if the graphical model is deterministic. Else, returns `False`.
        """
        return self._is_deterministic

    @register_property(GRAPH_PROPERTY)
    def is_probabilistic(self):
        """ Returns `True` if the graphical model is probabilistic. Else, returns `False`. """
        return self._is_probabilistic


# ==========================================================================
# USER MODELS.
# ==========================================================================
class TSys(GraphicalModel):
    """
    Represents a transition system [Principles of Model Checking, Def. 2.1].

    .. math::
        TSys = (S, A, T, AP, L)


    In the `TSys` class, each component is represented as a function.

    - The set of states :math:`S` is represented by `TSys.states` function,
    - The set of actions :math:`A` is represented by `TSys.actions` function,
    - The transition function :math:`T` is represented by `TSys.delta` function,
    - The set of atomic propositions is represented by `TSys.atoms` function,
    - The labeling function :math:`L` is represented by `TSys.label` function.

    All of the above functions are marked abstract.
    The recommended way to use `TSys` class is by subclassing it and implementing its component functions.

    A transition system can be either deterministic or non-deterministic or probabilistic.
    To define a **deterministic** transition system, provide a keyword argument `is_deterministic=True`
    to the constructor. To define a **nondeterministic** transition system, provide a keyword argument
    `is_deterministic=False` to the constructor. To define a **probabilistic** transition system, provide
    a keyword arguments `is_deterministic=False, is_probabilistic=True` to the constructor.

    The design of `TSys` class closely follows its mathematical definition.
    Hence, the signatures of `delta` function for deterministic, nondeterministic, probabilistic
    transition systems are different.

    - **deterministic:**  `delta(state, act) -> single state`
    - **non-deterministic:**  `delta(state, act) -> a list of states`
    - **probabilistic:**  `delta(state, act) -> a distribution over states`

    An important feature of `TSys` class is the `graphify()` function. It constructs a `Graph` object that is equivalent to the transition system. The nodes of the `Graph` represent the states of `TSys`, the edges of the `Graph` are defined by the set of `actions` and the `delta` function. The atomic propositions, labeling function are stored as `node, edge` and `graph` properties. By default, every `Graph` returned a `TSys.graphify()` function have the following (node/edge/graph) properties:

    - `state`: (node property) A Map from every node to the state of transition system it represents.
    - `actions`: (graph property) List of valid actions.
    - `input`: (edge property) A map from every edge `(uid, vid, key)` to its associated action label.
    - `prob`: (edge property) The probability associated with the edge `(uid, vid, key)`.
    - `atoms`: (graph property) List of valid atomic propositions.
    - `label`: (node property) A map every node to the list of atomic propositions true in the state represented by that node.
    - `init_state`: (graph property) Initial state of transition system.
    - `is_deterministic`: (graph property) Is the transition system deterministic?
    - `is_probabilistic`: (graph property) Is the transition system probabilistic?

    **Note:** Some features of probabilistic transition system are not tested. If you are trying to implement a probabilistic transition system, reach out to Abhishek Kulkarni (a.kulkarni2@ufl.edu).


    Next, we demonstrate how to use `TSys` class to define a deterministic, non-deterministic and probabilistic transition system.

    """
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    def __init__(self, is_deterministic=True, is_probabilistic=False, **kwargs):
        """
        Constructs a transition system.

        :param is_deterministic: (bool). If `True` then the transition system is deterministic. Otherwise,
            it is either non-deterministic or probabilistic.
        :param is_probabilistic: (bool). If `is_deterministic` is `False`, then if `is_probabilistic` is `True`
            then the transition system is probabilistic. Otherwise, it is non-deterministic.
        :param input_domain: (optional, function). A member function of TSys class that defines the inputs to the
            transition system. [Default: TSys.actions]
        :param input_name: (optional, str). The name of input property during graphify().
        :param init_state: (optional, JSON-serializable object). The initial state of the transition system.
        """
        super(TSys, self).__init__(input_domain=self.actions,
                                   is_deterministic=is_deterministic,
                                   is_probabilistic=is_probabilistic,
                                   **kwargs)

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(GRAPH_PROPERTY)
    def actions(self):
        """
        Defines the actions component of the transition system.

        :return: (list/tuple of str). List or tuple of action labels.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.actions() is not implemented.")

    def delta(self, state, act):
        """
        Defines the transition function of the transition system.

        :param state: (object) A valid state.
        :param act: (str) An action.
        :return: (object/list(object)/util.Distribution object). Depending on the type of transition system, the return
            type is different.
            - Deterministic: returns a single state.
            - Non-deterministic: returns a list/tuple of states.
            - Probabilistic: returns a distribution over all state.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.delta() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def atoms(self):
        """
        Defines the atomic propositions component of the transition system.

        :return: (list/tuple of str). List or tuple of atomic proposition labels.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    @register_property(NODE_PROPERTY)
    def label(self, state):
        """
        Defines the labeling function of the transition system.

        :param state: (object) A valid state.
        :return: (list/tuple of str). A list/tuple of atomic propositions that are true in the given state.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.label() is not implemented.")


class Game(TSys):
    """
    Represents a game transition system, hereafter referred simply as a game.
    A `Game` can represent two mathematical structures commonly used in literature, namely

    .. math::
        G = (S, A, T, AP, L, formula)

    .. math::
        G = (S, A, T, F, WinCond)

    In the `Game` class, each component is represented as a function. By defining the relevant functions, a `Game`
    class may represent either of the two mathematical structures.

    - The set of states :math:`S` is represented by `Game.states` function,
    - The set of actions :math:`A` is represented by `Game.actions` function,
    - The transition function :math:`T` is represented by `Game.delta` function,
    - The set of atomic propositions :math:`AP` is represented by `Game.atoms` function,
    - The labeling function :math:`L` is represented by `Game.label` function.
    - When the winning condition is represented by a logic formula :math:`formula`, we define `Game.formula` function.
    - When the winning condition is represented by a final states :math:`F`, we define `Game.final` function.
      In this case, we must also specify the acceptance condition.
    - The winning condition :math:`WinCond` is represented by `Game.win_cond` function.

    All of the above functions are marked abstract.
    The recommended way to use `Game` class is by subclassing it and implementing the relevant component functions.

    **Categorization of a Game:** A game is categorized by three types:

    -   A game can be either deterministic or non-deterministic or probabilistic.
        To define a **deterministic** transition system, provide a keyword argument `is_deterministic=True` to the
        constructor. To define a **nondeterministic** transition system, provide a keyword argument `is_deterministic=False`
        to the constructor. To define a **probabilistic** transition system, provide a keyword arguments
        `is_deterministic=False, is_probabilistic=True` to the constructor.

        The design of `Game` class closely follows its mathematical definition.
        Hence, the signatures of `delta` function for deterministic, nondeterministic, probabilistic games are different.

        - **deterministic:**  `delta(state, act) -> single state`
        - **non-deterministic:**  `delta(state, act) -> a list of states`
        - **probabilistic:**  `delta(state, act) -> a distribution over states`

    -   A game can be turn-based or concurrent. To define a **concurrent** game, provide a keyword argument
        `is_turn_based=False`. The game is `turn_based` by default.

    -   A game can be a 1/1.5/2/2.5-player game. A one-player game models a deterministic motion planning-type problem in
        a static environment. A 1.5-player game is an MDP. A two-player game models a deterministic interaction between
        two strategic players. And, a 2.5-player game models a stochastic interaction between two strategic players.

        If a game is one or two player, then the :py:meth:`Game.delta` is `deterministic`.
        If a game is 1.5 or 2.5 player, then the :py:meth:`Game.delta` is either `non-deterministic` (when
        transition probabilities are unknown), and `probabilistic` (when transition probabilities are known).

    Every state in a turn-based game is controlled by a player. To define which player controls which state, define
    a game component :py:meth:`Game.turn` which takes in a state and returns a value between 0 and 3 to indicate
    which player controls the state.

    An important feature of `Game` class is the `graphify()` function. It constructs a `Graph` object that is
    equivalent to the game. The nodes of the `Graph` represent the states of `Game`,
    the edges of the `Graph` are defined by the set of `actions` and the `delta` function.
    The atomic propositions, labeling function are stored as `node, edge` and `graph` properties.
    By default, every `Graph` returned a `Game.graphify()` function have the following (node/edge/graph) properties:

    - `state`: (node property) A Map from every node to the state of transition system it represents.
    - `actions`: (graph property) List of valid actions.
    - `input`: (edge property) A map from every edge `(uid, vid, key)` to its associated action label.
    - `prob`: (edge property) The probability associated with the edge `(uid, vid, key)`.
    - `atoms`: (graph property) List of valid atomic propositions.
    - `label`: (node property) A map every node to the list of atomic propositions true in the state represented by that node.
    - `init_state`: (graph property) Initial state of transition system.
    - `is_deterministic`: (graph property) Is the transition system deterministic?
    - `is_probabilistic`: (graph property) Is the transition system probabilistic?
    - `is_turn_based`: (graph property) Is the transition system turn-based?
    - `final`: (node property) Returns an integer denoting the acceptance set the state belongs to.
    - `win_cond`: (graph property) The winning condition of the game.
    - `formula`: (graph property) A logic formula representing the winning condition of the game.
    - `turn`: (node property) A map from every node to an integer (0/1/2) that denotes which player controls the node.
    - `p1_acts`: (graph property) A subset of actions accessible to P1.
    - `p2_acts`: (graph property) A subset of actions accessible to P2.

    **Note:** Some features of probabilistic transition system are not tested.
    If you are trying to implement a probabilistic transition system, reach out to Abhishek Kulkarni
    (a.kulkarni2@ufl.edu).
    """
    NODE_PROPERTY = TSys.NODE_PROPERTY.copy()
    EDGE_PROPERTY = TSys.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = TSys.GRAPH_PROPERTY.copy()

    def __init__(self, is_turn_based=True, is_deterministic=True, is_probabilistic=False, **kwargs):
        super(Game, self).__init__(is_deterministic=is_deterministic,
                                   is_probabilistic=is_probabilistic,
                                   **kwargs)
        self._is_turn_based = is_turn_based

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(NODE_PROPERTY)
    def final(self, state):
        """
        Defines whether the given state is a final state.
        The structure of final state is based on the winning condition
        [See Automata, Logics and Infinite Games (Ch. 2)].

        :param state: (object) A valid state.
        :return: (int or a list of ints). The integer denotes the acceptance set the state belongs to.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def is_turn_based(self):
        """ Is the game turn based? """
        return self._is_turn_based

    @register_property(NODE_PROPERTY)
    def turn(self, state):
        """
        Defines the player who controls the given state.

        :param state: (object) A valid state.
        :return: (int). In turn-based game, turn can be 1 for player 1 or 2 for player 2.
            In concurrent games, the turn must be 0.

        .. note:: For concurrent games, the turn function can be left unimplemented.
        """
        raise NotImplementedError

    @register_property(GRAPH_PROPERTY)
    def p1_acts(self):
        """ A subset of actions accessible to P1. """
        raise NotImplementedError

    @register_property(GRAPH_PROPERTY)
    def p2_acts(self):
        """ A subset of actions accessible to P2. """
        raise NotImplementedError

    @register_property(GRAPH_PROPERTY)
    def win_cond(self):
        """ Winning condition of the game. """
        raise NotImplementedError

    @register_property(GRAPH_PROPERTY)
    def formula(self):
        """ A logic formula representing the winning condition of the game. """
        raise NotImplementedError


class Automaton(GraphicalModel):
    """
    Alphabet is powerset(atoms).
    """
    NODE_PROPERTY = GraphicalModel.NODE_PROPERTY.copy()
    EDGE_PROPERTY = GraphicalModel.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = GraphicalModel.GRAPH_PROPERTY.copy()

    ACC_REACH = "Reach"
    ACC_SAFETY = "Safety"
    ACC_BUCHI = "Buchi"
    ACC_COBUCHI = "co-Buchi"
    ACC_PARITY = "Parity Min Even"
    ACC_PREF_LAST = "Preference Last"
    ACC_PREF_MP = "Preference MostPreferred"
    ACC_UNDEFINED = "undefined"

    def __init__(self, **kwargs):
        """
        Supported keyword arguments:

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (Iterable[states]) The set of final states, a subset of states iterable.
        :param acc_cond: (tuple) A tuple of automaton acceptance type and an acceptance set.
            For example, DFA has an acceptance condition of `(Automaton.ACC_REACH, 0)`.
        :param is_deterministic: (bool) Whether the Automaton is deterministic.
        """
        super(Automaton, self).__init__(**kwargs)

        # Process keyword arguments
        if "states" in kwargs:
            def states_():
                return list(kwargs["states"])
            self.states = states_

        if "atoms" in kwargs:
            def atoms_():
                return list(kwargs["atoms"])
            self.atoms = atoms_

        if "trans_dict" in kwargs:
            def delta_(state, inp):
                next_states = set()
                for formula, n_state in kwargs["trans_dict"][state].items():
                    if pl.evaluate(formula, inp):
                        next_states.add(n_state)

                if self.is_deterministic():
                    if len(next_states) > 1:
                        raise ValueError("Non-determinism detected in a deterministic automaton. " +
                                         f"delta({state}, {inp}) -> {next_states}.")
                    return next(iter(next_states), None) if len(next_states) == 1 else None

                return next_states

            self.delta = delta_

        if "init_state" in kwargs:
            self.initialize(kwargs["init_state"])

        if "final" in kwargs:
            def final_(state):
                return 0 if state in kwargs["final"] else -1
            self.final = final_

        if "acc_cond" in kwargs:
            def acc_cond_():
                return kwargs["acc_cond"]
            self.acc_cond = acc_cond_

        if "is_deterministic" in kwargs:
            def is_deterministic_():
                return kwargs["is_deterministic"]
            self.is_deterministic = is_deterministic_

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    @register_property(GRAPH_PROPERTY)
    def atoms(self):
        raise NotImplementedError(f"{self.__class__.__name__}.atoms() is not implemented.")

    @register_property(NODE_PROPERTY)
    def final(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.final() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def acc_type(self):
        return self.acc_cond()[0]

    @register_property(GRAPH_PROPERTY)
    def acc_cond(self):
        return self.ACC_UNDEFINED, None

    @register_property(GRAPH_PROPERTY)
    def num_acc_sets(self):
        raise NotImplementedError(f"{self.__class__.__name__}.num_acc_sets() is not implemented.")

    @register_property(GRAPH_PROPERTY)
    def is_complete(self):
        raise NotImplementedError

    # ==========================================================================
    # FUNCTIONS TO BE IMPLEMENTED BY USER.
    # ==========================================================================
    def sigma(self):
        """
        Returns the set of alphabet of automaton. It is the powerset of atoms().
        """
        return list(util.powerset(self.atoms()))


class Solver:
    """
    Represents a game solver that computes the winning regions and strategies for the players
    under a fixed solution concept.

    It is recommended to implement a solver using the underlying graph of the game.
    This helps speeding up the algorithms. Hence, a typical workflow would look like

    .. code::
        def __init__(self, game, ...):
            super(Solver, self).__init__(game, ...)
            self._graph = self.game.graphify()

        def solver(self):
            ... uses only self._graph.

    """
    DETERMINISTIC = "deterministic"
    RANDOMIZED = "randomized"

    def __init__(self, graph, strategy_type=DETERMINISTIC, **kwargs):
        # Load and validate graph
        self._graph = graph
        self.validate()

        # Type of strategy
        self._strategy_type = strategy_type

        # Winning regions of the players
        self._win1 = None
        self._win2 = None

        # Cache variables
        self.__state2node = dict()

    def validate(self):
        """
        Validates the input game.
        Typically, this would involve checking if all necessary properties are well-defined.
        """
        pass

    def reset(self):
        """ Resets the internal variables to default values. """
        # Winning regions of the players
        self.win1 = None
        self.win2 = None

    def solve(self):
        """
        Solves the game to compute winning regions as per the solution concept.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.solve() is not implemented.")

    def pi1(self, node):
        """
        Player 1's strategy at the given state.

        :param node: A valid state in the game.
        :return: A valid action.
        """
        raise NotImplementedError

    def pi2(self, node):
        """
        Player 2's strategy at the given state.

        :param node: A valid state in the game.
        :return: A valid action.
        """
        raise NotImplementedError

    def win1(self):
        return self._win1

    def win2(self):
        return self._win1

    def enabled_acts(self, node):
        pass

    def serialize(self):
        pass

    @classmethod
    def deserialize(cls, graph_dict):
        raise NotImplementedError

    def save(self, fpath, overwrite=False, protocol="json"):
        # Add win1, win2, win3 as graph properties
        # Add pi1, pi2, pi3 as node properties
        pass

    def load(self, fpath, protocol="json"):
        pass

    def strategy_type(self):
        return self._strategy_type
