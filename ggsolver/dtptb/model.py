import logging
import networkx as nx
from ggsolver.ds import BaseGame
from ggsolver.logic import Dfa
from ggsolver.utils import product_tsys_dfa


class DtptbGame(BaseGame):

    def delta(self, u, a):
        next_state = {v for _, v, d in self.graph.out_edges(u, data=True) if d["action"] == a}

        if len(next_state) == 1:
            return next_state.pop()
        elif len(next_state) == 0:
            logging.warning(f"Game graph is incomplete. {repr(self)}.delta({u}, {a}) -> {next_state}.")
            return None
        else:
            error_msg = f"Game graph is not deterministic. {repr(self)}.delta({u}, {a}) -> {next_state}."
            logging.error(error_msg)
            raise ValueError(error_msg)

    def pred(self, v):
        return {(e[0], e[2]["action"]) for e in self.graph.in_edges(v, data=True)}

    def succ(self, u):
        return {(e[1], e[2]["action"]) for e in self.graph.out_edges(u, data=True)}

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
        :param kwargs: Use keyword parameter `validate_graph=False` to bypass graph validation.
        """
        if self.is_constructed:
            err_msg = f"Cannot reconstruct an already constructed {repr(self)}."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        if "validate_graph" not in kwargs:
            kwargs["validate_graph"] = True

        if kwargs["validate_graph"]:
            self.validate_graph(graph)

        actions = set()
        for _, _, data in graph.edges(data=True):
            actions.add(data["action"])

        self._graph = graph
        self._actions = actions
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._mode = self.EXPLICIT
        self._is_constructed = True

    def construct_symbolic(self, states, actions, **kwargs):
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
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._mode = self.SYMBOLIC
        self._is_constructed = True


def prod_game_dfa(game: DtptbGame, dfa: Dfa, name=None):
    return product_tsys_dfa(game, dfa, name)
