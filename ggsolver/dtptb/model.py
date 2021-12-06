import logging
import networkx as nx
from ggsolver.ds import BaseGame
from ggsolver.logic import Dfa
from ggsolver.utils import product_tsys_dfa


class DtptbGame(BaseGame):

    def delta(self, u, a):
        # Check if game is constructed.
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.delta. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        # Get next state
        v = self._delta(u, a)

        # Check validity of next state and that delta function is deterministic.
        assert v in self.states()

        # Return next state
        return v

    def pred(self, v):
        # Check if game is constructed.
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.pred. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        # Get predecessor state
        pred_states = self._pred(v)
        assert isinstance(pred_states, set), f"{repr(self)}.pred must return a set. It returned {type(pred_states)}."

        # Return predecessor states
        return pred_states

    def succ(self, u):
        # Check if game is constructed.
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.succ. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        # Get successor state
        succ_states = self._succ(u)
        assert isinstance(succ_states, set), f"{repr(self)}.succ must return a set. It returned {type(succ_states)}."

        # Return successor states
        return succ_states

    def validate_graph(self, graph, **kwargs):
        """
        Check the following conditions.
        1. Type: nx.DiGraph, nx.MultiDiGraph
        2. Nodes have "turn" attribute.
        3. Edges have "action" attribute.

        :param graph: networkx.MultiDiGraph
        :return: True, if validation passes. Else, False.
        """
        assert isinstance(graph, (nx.MultiDiGraph, nx.DiGraph)), \
            f"graph must be a nx.MultiDiGraph or nx.DiGraph object."
        assert all("turn" in data for _, data in graph.nodes(data=True)), f"Each graph node must have 'turn' attribute."
        assert all("action" in data for _, _, data in graph.edges(data=True)), \
            f"Each graph edge must have 'action' attribute."

    def construct_explicit(self, graph, **kwargs):
        """
        Constructs deterministic two-player turn-based game from given graph.

        :param graph: networkx.DiGraph or networkx.MultiDiGraph object.
        :param kwargs: User may override default definitions of delta, pred, and/or succ by passing keyword params
            `delta`, `pred`, `succ`. Also, pass keyword parameter `validate_graph=False` to bypass graph validation.
        """
        if self.is_constructed:
            err_msg = f"Cannot reconstruct an already constructed {repr(self)}."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        def _delta(state, act):
            next_state = {v for _, v, d in self.graph.out_edges(state, data=True) if d["action"] == act}

            if len(next_state) == 1:
                return next_state.pop()
            elif len(next_state) == 0:
                logging.warning(f"Game graph is incomplete. {repr(self)}.delta({state}, {act}) -> {next_state}.")
                return None
            else:
                error_msg = f"Game graph is not deterministic. {repr(self)}.delta({state}, {act}) -> {next_state}."
                logging.error(error_msg)
                raise ValueError(error_msg)

        def _pred(state):
            return {(e[0], e[2]["action"]) for e in self.graph.in_edges(state, data=True)}

        def _succ(state):
            return {(e[1], e[2]["action"]) for e in self.graph.out_edges(state, data=True)}

        if "validate_graph" not in kwargs:
            kwargs["validate_graph"] = True

        if kwargs["validate_graph"]:
            self.validate_graph(graph)

        if "delta" in kwargs:
            _delta = kwargs["delta"]

        if "pred" in kwargs:
            _pred = kwargs["pred"]

        if "succ" in kwargs:
            _succ = kwargs["succ"]

        actions = set()
        for _, _, data in graph.edges(data=True):
            actions.add(data["action"])

        self._graph = graph
        self._actions = actions
        self._delta = _delta
        self._pred = _pred
        self._succ = _succ
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._mode = self.EXPLICIT
        self._is_constructed = True

    def construct_symbolic(self, states, actions, delta, pred, succ, **kwargs):
        """
        Constructs deterministic two-player turn-based game symbolically.
        """
        if self.is_constructed:
            err_msg = f"Cannot reconstruct an already constructed {repr(self)}."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        self._graph = nx.MultiDiGraph()
        self._graph.add_nodes_from(states)
        self._actions = actions
        self._delta = delta
        self._pred = pred
        self._succ = succ
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._mode = self.SYMBOLIC
        self._is_constructed = True


def prod_game_dfa(game: DtptbGame, dfa: Dfa, name=None):
    return product_tsys_dfa(game, dfa, name)
