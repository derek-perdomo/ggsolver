import json
import itertools
from ggsolver.decoy_alloc.models import ReachabilityGame
import networkx as nx
from networkx.readwrite import json_graph

class CBSGame(ReachabilityGame):
    """
    CyberBattleSim game
    """
    def __init__(self, json_fname):
        super(ReachabilityGame, self).__init__()

        self._json_fname = json_fname
        self._cbs_network = self._decode()
        self._states, self._credential_set, self._possible_firewall_states = self._construct_states()
        self._actions = self._construct_actions()

    def _decode(self):
        # do something with self._json
        # return nx.MultiDiGraph()
        with open(self._json_fname) as f:
            data = json.load(f)
        network = json_graph.adjacency_graph(data, directed=True, multigraph=True)
        return network

    def states(self):
        return self._states

    def actions(self):
        return self._actions

    def delta(self, state, act):
        ### state is of form (state_number, node_name, obtained_credentials, firewall_state, turn) ###
        # defender action
        if act[0:19] == "change_firewall_to_":
            firewall_settings_string = act[19:]
            firewall_settings = [int(i) for i in firewall_settings_string.strip(')(').split(', ')]
            return (state[0], state[1], state[2], tuple(firewall_settings), 2)

    def final(self, state):
        pass

    def turn(self, state):
        return state[4]

    def _construct_states(self):
        states = []  # list of state objects that can be used to construct game graph

        unique_credentials = set()
        connections = []
        network_nodes = []
        for name, node in self._cbs_network.nodes.items():
            network_nodes.append(name)
            connections.extend([(name, target_node) for target_node in node["connected_nodes"]])
            unique_credentials.update(
                node["allowed_creds"])  # add credentials that can be used to connect to the node
            for leaked_credential in node["creds_stored"]:
                unique_credentials.update(leaked_credential[2])  # add credentials that are stored on the node

        possible_firewall_states = list(itertools.product([0, 1], repeat=len(connections)))
        possible_obtained_credentials_states = list(itertools.product([0, 1], repeat=len(unique_credentials)))

        state_number = 0
        for node_name in network_nodes:
            for firewall_state in possible_firewall_states:
                for obtained_credentials in possible_obtained_credentials_states:
                    # State is of form (id, i, bool[k], bool[n], turn)
                    # Where i is the agent's location, k is the number of credentials, and n is the
                    # number of firewalls (connections between computers in the network, edges in the network graph)
                    states.append((state_number, node_name, obtained_credentials, firewall_state, 1))
                    state_number += 1
                    states.append((state_number, node_name, obtained_credentials, firewall_state, 2))
                    state_number += 1
        return states, unique_credentials, possible_firewall_states

    def _construct_actions(self):
        actions = []
        ### attacker actions ###
        # no action
        actions.append("no_attacker_action")
        for node in self._cbs_network.nodes:
            # change i to another owned node
            actions.append(f"move_to_node_{node}")
            # perform a local attack (add credentials from the current node i to the obtained credentials)
            actions.append(f"local_attack_on_{node}")
            # connect to a new node using obtained credentials
            for credential in self._credential_set:
                actions.append(f"connect_to_{node}_with_{credential}")
        ### defender actions ###
        # change firewall
        for firewall_state in self._possible_firewall_states:
            actions.append(f"change_firewall_to_{firewall_state}")
        return actions
if __name__ == '__main__':
    game = CBSGame("network.json")
    print(f"{len(game.states())=}")
    print(f"{len(game.actions())=}")
    for action in game.actions():
        print(f"{action=}")
    print(game.states()[0])
    print(game.delta(game.states()[0], "change_firewall_to_(1, 1, 1, 1, 0)"))
    # graph = game.graphify(pointed=True)
    # print(f"{graph.number_of_nodes()=}")
    # print(f"{graph.number_of_edges()=}")