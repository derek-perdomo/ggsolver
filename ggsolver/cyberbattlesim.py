from ggsolver.decoy_alloc.models import ReachabilityGame


class CBSGame(ReachabilityGame):
    """
    CyberBattleSim game
    """
    def __init__(self, json):
        super(ReachabilityGame, self).__init__()

        self._json = json
        self._cbs_network = self._decode()

    def _decode(self):
        # do something with self._json
        # return nx.MultiDiGraph()
        pass

    def states(self):
        pass

    def actions(self):
        pass

    def delta(self, state, act):
        pass

    def final(self, state):
        pass

    def turn(self, state):
        pass



if __name__ == '__main__':
    game = CBSGame(json_fname)
    graph = game.graphify(pointed=True)
    print(f"{graph.number_of_nodes()=}")
    print(f"{graph.number_of_edges()=}")