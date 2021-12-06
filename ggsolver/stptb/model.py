import logging
import networkx as nx
from ggsolver.mdp.model import MdpGame
from ggsolver.logic import Dfa
from ggsolver.utils import product_tsys_dfa


class StptbGame(MdpGame):
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
        assert all("turn" in data for _, data in graph.nodes(data=True)), f"Each graph node must have 'turn' attribute."
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


def prod_game_dfa(game: StptbGame, dfa: Dfa, name=None):
    return product_tsys_dfa(game, dfa, name)
