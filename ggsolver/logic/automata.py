import copy
import itertools
import json
import logging
import networkx as nx
import os
from abc import ABC, abstractmethod
from parsers.utils import powerset


logger = logging.getLogger(__name__)


# GLOBALS. Acceptance conditions
ACC_REACHABILITY = "Reachability"
ACC_BUCHI = "Buchi"
ACC = [ACC_BUCHI, ACC_REACHABILITY]


class BaseAutomaton(ABC):
    EXPLICIT = "explicit"
    SYMBOLIC = "symbolic"

    def __init__(self, name):
        self._name = name
        self._graph = None
        self._alphabet = set()
        self._delta = None
        self._pred = None
        self._succ = None
        self._init_st = None
        self._final = None
        self._acc = None
        self._mode = None
        self._is_constructed = False
        self.properties = dict()

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self._name}">'

    def __str__(self):
        return pretty_print_automaton(self)

    def validate_graph(self, *args, **kwargs):
        err_msg = f"{repr(self)}.validate_graph method is not implemented by user."
        logger.warning(err_msg)

    def construct_explicit(self, graph, init_st, final, acc, *args, **kwargs):
        err_msg = f"{repr(self)}.construct_explicit method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def construct_symbolic(self, states, alphabet, delta, pred, succ, init_st, final, acc, *args, **kwargs):
        err_msg = f"{repr(self)}.construct_symbolic method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def load_from_file(self, metadata_file):
        """
        Loads and constructs automaton from file.
        :param metadata_file: Absolute path to metadata (json) file, including extension.
        """

        with open(metadata_file, "r") as json_file:
            properties_dict = json.load(json_file)

        graph_file = properties_dict["graph_file"]
        graph_format = properties_dict["graph_format"]

        # Save graph in given graph_format
        graph = nx.MultiDiGraph()
        if graph_format == "graphml":
            graph = nx.read_graphml(graph_file)

        elif graph_format == "pkl":
            graph = nx.read_gpickle(graph_file)

        elif graph_format == "cyjs":
            with open(graph_file, "wb") as cyjs_file:
                cyjs_json = json.load(cyjs_file)
            graph = nx.cytoscape_graph(cyjs_json)

        else:
            err_msg = f"Extension '.{graph_format}' is not supported to save {repr(self)} object to file."
            logger.error(err_msg)
            ValueError(err_msg)

        # Construct automaton object explicitly
        self._is_constructed = False
        self.construct_explicit(graph=graph,
                                init_st=properties_dict["init_st"],
                                final=set(properties_dict["final"]),
                                acc=properties_dict["acc"]
                                )
        self.properties.update(properties_dict["properties"])

    def make_explicit(self, *args, **kwargs):
        err_msg = f"{repr(self)}.make_explicit method is not implemented by user."
        logger.error(err_msg)
        raise NotImplementedError(err_msg)

    def states(self, data=False):
        if self._is_constructed:
            return self._graph.nodes(data=data)

        err_msg = f"Cannot access {repr(self)}.states(). Automaton is not constructed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    def save_to_file(self, file_name, path=None, graph_format="pkl"):
        """
        Saves the automaton to file. Generates two files:
            - `<file_name>.<graph_format>` - with graph encoding.
            - `<file_name>.json` - with automaton properties and filepath of saved graph file.

        :param file_name: File name without path and extension.
        :param path: Absolute path to directory where files must be saved. [Default: <current directory>]
        :param graph_format: Type of encoding to save graph. Currently, ggsolver supports {'pkl'}.
            [Default: "pkl"]

        :todo: Add save-load support for 'cyjs', 'graphml'.
        """
        # Cannot save automaton if it is not constructed.
        if not self.is_constructed:
            err_msg = f"Cannot save {repr(self)} to file. Automaton is not constructed."
            logger.error(err_msg)
            ValueError(err_msg)

        # If automaton is defined symbolically, make it explicit.
        if not self.mode == self.EXPLICIT:
            self.make_explicit()

        # If path is not given, use current directory.
        if path is None:
            path = os.getcwd()

        # Construct complete paths to save files.
        graph_file = os.path.join(path, f"{file_name}.{graph_format}")
        metadata_file = os.path.join(path, f"{file_name}.json")

        # Save graph in given graph_format
        if graph_format == "pkl":
            nx.write_gpickle(self._graph, graph_file)

        # elif graph_format == "graphml":
        #     nx.write_graphml(self._graph, graph_file)
        #
        # elif graph_format == "cyjs":
        #     cytoscape_json = nx.cytoscape_data(self._graph)
        #     with open(graph_file, "w") as cyjs_file:
        #         json.dump(cytoscape_json, cyjs_file)

        else:
            err_msg = f"Extension '.{graph_format}' is not supported to save {repr(self)} object to file."
            logger.error(err_msg)
            ValueError(err_msg)

        # Serialize automaton
        properties_dict = {
            "graph_format": graph_format,
            "graph_file": graph_file,
            "alphabet": list(self.alphabet),
            "init_st": self.init_st,
            "final": list(self.final),
            "acc": self.acc,
            "properties": self.properties,
        }

        # Save metadata
        with open(metadata_file, "w") as json_file:
            json.dump(properties_dict, json_file)

    @abstractmethod
    def delta(self, u, f):
        err_msg = f"{repr(self)}.delta method is not defined."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def pred(self, v):
        err_msg = f"{repr(self)}.pred method is not defined."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def succ(self, u):
        err_msg = f"{repr(self)}.succ method is not defined."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @property
    def acc(self):
        if self._is_constructed:
            return self._acc

        err_msg = f"Cannot access {repr(self)}.acc. Automaton is not constructed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    @property
    def alphabet(self):
        if self._is_constructed:
            return self._alphabet

        err_msg = f"Cannot access {repr(self)}.alphabet. Automaton is not constructed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    @property
    def final(self):
        if self._is_constructed:
            return self._final

        err_msg = f"Cannot access {repr(self)}.final. Automaton is not constructed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    @property
    def graph(self):
        if self._is_constructed and self._mode == self.EXPLICIT:
            return self._graph

        err_msg = f"Cannot access {repr(self)}.graph. Constraints: is_constructed={self._is_constructed} which " \
                  f"expected is True, mode={self._mode} expected is {self.EXPLICIT}"
        logger.error(err_msg)
        raise ValueError(err_msg)

    @property
    def init_st(self):
        if self._is_constructed:
            return self._init_st

        err_msg = f"Cannot access {repr(self)}.init_st. Automaton is not constructed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    @property
    def is_constructed(self):
        return self._is_constructed

    @property
    def mode(self):
        return self._mode


class Dfa(BaseAutomaton):
    def __init__(self, name):
        super(Dfa, self).__init__(name)
        self._final = set()
        self._acc = ACC_REACHABILITY

    def __str__(self):
        return pretty_print_automaton(self)

    def validate_graph(self, graph, final, init_st, *args, **kwargs):
        """
        Validates if the Dfa structure is well-defined.

        Checks whether
        (1) all edges, if exist, must have `symbol` attribute associated with them.
        (1) the accepting-state set is a subset of the state set.
        (2) the start-state is a member of the state set.

        :raises AssertionError: if either of the above conditions is not satisfied.
        """
        assert all("symbol" in data for _, _, data in graph.edges(data=True)), \
            "Dfa edges must have a `symbol` attribute associated with them."
        assert set.issubset(set(final), set(graph.nodes())), "Dfa final states must be a subset of Dfa states."
        assert init_st in graph.nodes(), "Dfa initial state states must be a member of Dfa states."

    def construct_symbolic(self, states, alphabet, delta, init_st, final, pred=None, succ=None, *args, **kwargs):
        if "skip_validation" not in kwargs:
            kwargs["skip_validation"] = False

        if self._is_constructed:
            raise RuntimeError("Cannot initialize an already initialized game.")

        assert isinstance(final, set), f"Final states must be a set."

        def _pred(v):
            pred_states = set()
            for u in states:
                for true_atoms in powerset(alphabet):
                    if v == delta(u, true_atoms):
                        pred_states.add((u, frozenset(true_atoms)))
            return pred_states

        def _succ(u):
            succ_states = set()
            for true_atoms in powerset(alphabet):
                v = delta(u, true_atoms)
                succ_states.add((v, frozenset(true_atoms)))
            return succ_states

        self._graph = nx.MultiDiGraph()
        self._graph.add_nodes_from(states)
        self._alphabet = alphabet
        self._delta = delta
        self._pred = pred if pred is not None else _pred
        self._succ = succ if succ is not None else _succ
        self._init_st = init_st
        self._final = final
        self._mode = self.SYMBOLIC
        self._is_constructed = True
        if kwargs["skip_validation"]:
            logger.warning(f"Skipping validation for {repr(self)} during construct_explicit.")
        else:
            self.validate_graph(graph=self._graph, final=self._final, init_st=self._init_st)

    def construct_explicit(self, graph, init_st, final, *args, **kwargs):
        if "skip_validation" not in kwargs:
            kwargs["skip_validation"] = False

        if self._is_constructed:
            raise RuntimeError("Cannot initialize an already initialized game.")

        def _delta(state, true_atoms):
            next_states = set()
            for _, q, data_q in graph.out_edges(state, data=True):
                if set(data_q["symbol"]) == set(true_atoms):
                    next_states.add(q)

            if len(next_states) > 1:
                err_msg = f"Dfa transition function is ill-formed or corrupted. Function call" \
                          f"{repr(self)}.delta({state}, {true_atoms}) resulted in {next_states}."
                logger.critical(err_msg)
                ValueError(err_msg)

            elif len(next_states) == 1:
                return next_states.pop()

            else:
                err_msg = f"Dfa transition function is incomplete. Function call" \
                          f"{repr(self)}.delta({state}, {true_atoms}) resulted in {next_states}."
                logger.warning(err_msg)
                return None

        def _pred(state):
            return {(e[0], frozenset(e[2]["symbol"])) for e in graph.in_edges(state, data=True)}

        def _succ(state):
            return {(e[1], frozenset(e[2]["symbol"])) for e in graph.out_edges(state, data=True)}

        assert isinstance(final, set), f"Dfa final states must be a set. Input type(final): {type(final)}"
        if kwargs["skip_validation"]:
            logger.warning(f"Skipping validation for {repr(self)} during construct_explicit.")
        else:
            self.validate_graph(graph, final, init_st)

        alphabet = set()
        for _, _, data in graph.edges(data=True):
            alphabet.update(set(data["symbol"]))

        self._graph = graph
        self._alphabet = alphabet
        self._delta = _delta
        self._pred = _pred
        self._succ = _succ
        self._init_st = init_st
        self._final = final
        self._mode = self.EXPLICIT
        self._is_constructed = True

    def make_explicit(self):
        """
        When Dfa is symbolically constructed, this function constructs all edges of Dfa to make it explicit.
        Internally, the function changes the mode of Dfa from `symbolic` to `explicit`.
        """
        if not self.is_constructed:
            err_msg = f"Cannot make {repr(self)} explicit. Dfa is not yet constructed."
            logger.error(err_msg)
            raise ValueError(err_msg)

        if self.mode == self.EXPLICIT:
            return

        # Create an empty copy of graph: keep all nodes and delete all edges.
        graph = nx.create_empty_copy(self._graph, with_data=True)
        for src in self.states():
            for sigma in powerset(self.alphabet):
                dst = self.delta(src, sigma)
                if dst is not None:
                    graph.add_edge(src, dst, symbol=sigma)

        # Reconstruct graph explicitly
        init_st = self.init_st
        final = self.final
        self._is_constructed = False
        self.construct_explicit(graph, init_st, final, skip_validation=True)

    def delta(self, u, true_atoms):
        # Check if delta is well-defined
        if not self._is_constructed:
            err_msg = f"{repr(self)}.delta method cannot be accessed. Dfa is not constructed."
            logger.critical(err_msg)
            raise ValueError(err_msg)
        assert set(true_atoms).issubset(self.alphabet), f"true_atoms must be subset of alphabet."
        assert u in self.states(), f"Input state {u} is not in {repr(self)}."

        # Call delta function
        v = self._delta(u, true_atoms)

        # Validate output of delta function
        err_msg = f"Output: {repr(self)}.delta({u}, {true_atoms}) -> {v} is not in Dfa states."
        if v not in self.states():
            logger.warning(err_msg)
            assert v is None, err_msg

        # Return output
        return v

    def pred(self, v):
        # Check if pred is well-defined
        if not self._is_constructed:
            err_msg = f"{repr(self)}.pred method cannot be accessed. Dfa is not constructed."
            logger.critical(err_msg)
            raise ValueError(err_msg)
        assert v in self.states(), f"Input state {v} is not in {repr(self)}."

        # Call pred function
        pred = self._pred(v)
        assert isinstance(pred, set), f"{repr(self)}.pred({v}) is expected to return a set. It returned {type(pred)}."
        return pred

    def succ(self, u):
        # Check if succ is well-defined
        if not self._is_constructed:
            err_msg = f"{repr(self)}.succ method cannot be accessed. Dfa is not constructed."
            logger.critical(err_msg)
            raise ValueError(err_msg)
        assert u in self.states(), f"Input state {u} is not in {repr(self)}."

        # Call succ function
        succ = self._succ(u)
        assert isinstance(succ, set), f"{repr(self)}.pred({u}) is expected to return a set. It returned {type(succ)}."
        return succ


def pretty_print_automaton(aut):
    if not aut.is_constructed:
        output = f"This {aut.__class__.__name__} object is not constructed."
        return output

    output = f"""
    This {aut.__class__.__name__} has {len(aut.states())} states.
    Alphabet: {aut.alphabet}
    Starting state: {aut.init_st}
    Accepting states: {aut.final}
    States: {aut.states()}
    Transition function:"""
    for src in aut.states():
        for sigma in powerset(aut.alphabet):
            try:
                dst = aut.delta(src, sigma)
                output += "\n\t\t" + f"{src} -- {set(sigma)} --> {dst}" if len(sigma) > 0 else \
                    "\n\t\t" + f"{src} -- {{}} --> {dst}"
            except AssertionError as err:
                logger.exception(str(err), exc_info=True)
                raise
    return output


def cross_product(aut1, aut2):
    if isinstance(aut1, Dfa) and isinstance(aut2, Dfa):
        return cross_product_dfa_dfa(aut1, aut2)
    else:
        raise ValueError(f"Cross product of type aut1: {type(aut1)} and aut2: {type(aut2)} is not implemented.")


def cross_product_dfa_dfa(dfa1, dfa2):
    if dfa1.alphabet != dfa2.alphabet:
        raise ValueError("Cross product of DFA's with different alphabet is not implemented.")

    states = itertools.product(dfa1.states(), dfa2.states())
    final = set(itertools.product(dfa1.final, dfa2.final))
    init_st = (dfa1.init_st, dfa2.init_st)
    alphabet = copy.deepcopy(dfa1.alphabet)

    def delta(state, true_atoms):
        nstate1 = dfa1.delta(state[0], true_atoms)
        nstate2 = dfa2.delta(state[1], true_atoms)
        return nstate1, nstate2

    def succ(state):
        succ_states = set()
        succ1 = list(dfa1.succ(state[0]))
        succ2 = list(dfa2.succ(state[1]))

        for (p1, sigma1), (p2, sigma2) in itertools.product(succ1, succ2):
            if sigma1 == sigma2:
                succ_states.add(((p1, p2), sigma1))

        return succ_states

    def pred(state):
        pre_states = set()
        pre1 = list(dfa1.pred(state[0]))
        pre2 = list(dfa2.pred(state[1]))

        for (p1, sigma1), (p2, sigma2) in itertools.product(pre1, pre2):
            if sigma1 == sigma2:
                pre_states.add(((p1, p2), sigma1))

        return pre_states

    prod_dfa = Dfa(name=f"cross_product({repr(dfa1)}, {repr(dfa2)})")
    prod_dfa.construct_symbolic(states=states, alphabet=alphabet,
                                delta=delta, pred=pred, succ=succ,
                                init_st=init_st, final=final)

    return prod_dfa
