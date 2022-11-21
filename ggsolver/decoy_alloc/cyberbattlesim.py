import json
import itertools
from ggsolver.decoy_alloc.models import ReachabilityGame
import networkx as nx
from networkx.readwrite import json_graph

class CBSGame(ReachabilityGame):
    """
    CyberBattleSim game
    """
    def __init__(self, json_fname, final_node):
        super(ReachabilityGame, self).__init__()
        self._init_state = ("client", (0, 0, 0), (1, 1, 1, 1, 1), 1)

        self._json_fname = json_fname
        self._final_node = final_node
        self._cbs_network = self._decode()
        self._states, self._credential_set, self._possible_firewall_states, self._connections, self._final_states = self._construct_states()
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
        ### state is of form (source_node, obtained_credentials, firewall_state, turn) ###
        source_node = state[0]
        obtained_credentials = state[1]
        firewall_state = state[2]
        turn = state[3]
        ## attacker actions ##
        if turn == 2:
            if act == "no_attacker_action":
                return (source_node, obtained_credentials, firewall_state, 1)
            elif act[0:13] == "move_to_node_":
                pass
                # TODO how to restrict movement to only owned nodes (need to modify the graph to add edges returning to previous states?)
                # for every state1
                    # for each incoming edge state2
                        # for each incoming edge state3
                            # if everything is the same between state3 and state1 except firewall_state and attacker location
                                # for every different attacker location in the set of state3s
                                    # add an edge from state1 to every defender state (state with turn=2) with the new attacker location
                target_node = act[13:]
            elif act[0:16] == "local_attack_on_":
                target_node = act[16:]
                if target_node == source_node:
                    new_obtained_credentials = list(obtained_credentials)
                    for credential in self._cbs_network.nodes[target_node]["creds_stored"]:
                        # the "creds_stored" is a list of credentials of form (node_to_be_used_on, service, credential)
                        if new_obtained_credentials[int(credential[2])] == 0:
                            new_obtained_credentials[int(credential[2])] = 1
                    return (source_node, tuple(new_obtained_credentials), firewall_state, 1)
                else:
                    return (source_node, obtained_credentials, firewall_state, 1)
            elif act[0:11] == "connect_to_":
                index = act.find("_with_")
                target_node = act[11:index]
                credential = act[index+6:]

                source_connected_to_target = False
                connection_index = 0
                for i, connection in enumerate(self._connections):
                    if connection == (source_node, target_node):
                        source_connected_to_target = True
                        connection_index = i
                target_accepts_credential = credential in self._cbs_network.nodes[target_node]["allowed_creds"]
                connection_allowed_by_firewall = bool(firewall_state[connection_index])

                if source_connected_to_target and target_accepts_credential and connection_allowed_by_firewall:
                    # return state that is the same as passed state but at new node
                    # add node to list of visited nodes??
                    return (target_node, obtained_credentials, firewall_state, 1)
                else:
                    return (source_node, obtained_credentials, firewall_state, 1)
        ## defender action ##
        else:
            if act[0:19] == "change_firewall_to_":
                new_firewall_state_string = act[19:]
                new_firewall_state = [int(i) for i in new_firewall_state_string.strip(')(').split(', ')]
                return (source_node, obtained_credentials, tuple(new_firewall_state), 2)

    def final(self, state):
        return self._final_states

    def turn(self, state):
        print(state)
        return state[3]

    def _construct_states(self):
        states = []  # list of state objects that can be used to construct game graph
        final_states = []

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

        for node_name in network_nodes:
            for firewall_state in possible_firewall_states:
                for obtained_credentials in possible_obtained_credentials_states:
                    # State is of form (id, i, bool[k], bool[n], turn)
                    # Where i is the agent's location, k is the number of credentials, and n is the
                    # number of firewalls (connections between computers in the network, edges in the network graph)
                    states.append((node_name, obtained_credentials, firewall_state, 1))
                    states.append((node_name, obtained_credentials, firewall_state, 2))
                    if node_name == self._final_node:
                        final_states.append((node_name, obtained_credentials, firewall_state, 1))
                        final_states.append((node_name, obtained_credentials, firewall_state, 2))
        return states, unique_credentials, possible_firewall_states, connections, final_states

    def _construct_actions(self):
        actions = []
        ### attacker actions ###
        # no action
        actions.append("no_attacker_action")
        for node in self._cbs_network.nodes:
            # change i to another owned node
            # actions.append(f"move_to_node_{node}")
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
    game = CBSGame("network.json", final_node="5")
    print(f"{len(game.states())=}")
    print(f"{len(game.actions())=}")
    if None in game.states():
        print("Yes")
    else:
        print("no")
    for i in range(10):
        print(game.states()[i])
    # graph = game.graphify(pointed=True)
    # print(f"{graph.number_of_nodes()=}")
    # print(f"{graph.number_of_edges()=}")