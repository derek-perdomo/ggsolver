import logging
import networkx as nx
from ggsolver.ds import BaseGame
from ggsolver.logic import Dfa
from ggsolver.utils import product_tsys_dfa


class MdpGame(BaseGame):
    def __init__(self, name):
        super(MdpGame, self).__init__(name)
        self._is_qualitative = False

    def construct_explicit(self, graph, is_qualitative=False, **kwargs):
        """
        Constructs game on MDP represented as a graph.

        :param graph: networkx.DiGraph or networkx.MultiDiGraph object.
        :param is_qualitative: Denotes whether MDP game is qualitative (probability values will be ignored) or not.
        :param kwargs: Accepts following parameters.
            - `validate_graph`: Set to False to bypass graph validation.
        """
        # Avoid repeated construction of game structure
        if self.is_constructed:
            err_msg = f"Cannot reconstruct an already constructed {repr(self)}."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        # Process input parameters
        validate_graph = True if "validate_graph" not in kwargs else kwargs["validate_graph"]

        # Run validations on input graph structure
        if validate_graph:
            self.validate_graph(graph, is_qualitative=is_qualitative)

        # Construct action set
        actions = set()
        for _, _, data in graph.edges(data=True):
            actions.add(data["action"])

        # Construct game structure
        self._graph = graph
        self._actions = actions
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._mode = self.EXPLICIT
        self._is_constructed = True
        self._is_qualitative = is_qualitative

    def construct_symbolic(self, states, actions, is_qualitative=False, **kwargs):
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
        self._is_qualitative = is_qualitative

    def delta(self, u, a):
        if self._is_qualitative:
            next_states = {(v, None) for _, v, d in self.graph.out_edges(u, data=True) if d["action"] == a}
        else:
            next_states = {(v, d["prob"]) for _, v, d in self.graph.out_edges(u, data=True) if d["action"] == a}

        return next_states

    def pred(self, v):
        if self._is_qualitative:
            pred_states = {(u, d["action"], None) for u, _, d in self.graph.in_edges(v, data=True)}
        else:
            pred_states = {(u, d["action"], d["prob"]) for u, _, d in self.graph.in_edges(v, data=True)}
        return pred_states

    def succ(self, u):
        if self._is_qualitative:
            succ_states = {(v, d["action"], None) for _, v, d in self.graph.out_edges(u, data=True)}
        else:
            succ_states = {(v, d["action"], d["prob"]) for _, v, d in self.graph.out_edges(u, data=True)}
        return succ_states

    def get_prob(self, u, a, v):
        if self.is_constructed and not self._is_qualitative:
            edges = self.graph.get_edge_data(u, v)
            for _, edge_data in edges.items():
                if edge_data["action"] == a:
                    return edge_data["prob"]
            return 0.0

    def get_transition_matrix(self):
        err_msg = f"Get transition matrix function is not implemented. TODO."
        logging.warning(err_msg)
        raise NotImplementedError(err_msg)

    def validate_graph(self, graph, is_qualitative=False, **kwargs):
        """
        Check the following conditions.
        1. Type: nx.DiGraph, nx.MultiDiGraph
        2. Nodes have "turn" attribute.
        3. Edges have "action" attribute.
        4. [Optional] Sum of probabilities of outgoing edges from each state must sum to 1.0

        :param graph: networkx.MultiDiGraph
        :param is_qualitative: True to disable transition probability value validation.
        :return: True, if validation passes. Else, False.
        """
        assert isinstance(graph, (nx.MultiDiGraph, nx.DiGraph)), \
            f"graph must be a nx.MultiDiGraph or nx.DiGraph object."
        assert all("action" in data for _, _, data in graph.edges(data=True)), \
            f"Each graph edge must have 'action' attribute."

        if not is_qualitative:
            assert all("prob" in data for _, _, data in graph.edges(data=True)), \
                f"Each graph edge of quantitative MDP must have 'prob' attribute."

            for u in graph.nodes():
                # noinspection PyArgumentList
                edges = graph.out_edges(data=True, nbunch=u)
                edge_prob_by_actions = dict()
                for _, _, data in edges:
                    act = data["action"]
                    if act not in edge_prob_by_actions:
                        edge_prob_by_actions[act] = 0.0
                    edge_prob_by_actions[act] += data["prob"]

                for act in edge_prob_by_actions.keys():
                    if edge_prob_by_actions[act] != 1.0:
                        err_msg = f"Sum of probabilities for state:{u}, act:{act} is {edge_prob_by_actions[act]}. " \
                                  f"Expected 1.0."
                        logging.error(err_msg)
                        raise AssertionError(err_msg)


def prod_game_dfa(game: MdpGame, dfa: Dfa, name=None):
    return product_tsys_dfa(game, dfa, name)
