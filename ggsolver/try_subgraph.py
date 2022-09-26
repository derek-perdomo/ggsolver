import networkx as nx


class SubGraph:
    def __init__(self, graph):
        self.graph = nx.subgraph_view(graph, self.hidden_nodes, self.hidden_edges)
        self._hidden_nodes = set()
        self._hidden_edges = set()

    def hidden_nodes(self, n):
        return n not in self._hidden_nodes

    def hidden_edges(self, uid, vid, key):
        return (uid, vid, key) not in self._hidden_edges


if __name__ == '__main__':
    g = nx.MultiDiGraph()
    g.add_nodes_from([1, 2, 3, 4, 5])
    g.add_edges_from([(1, 2), (3, 4), (2, 5)])

    sg = SubGraph(g)

    sg._hidden_nodes = {1}
    print(sg.graph.nodes())
    print(sg.graph.edges())


    sg._hidden_nodes = {1, 3}
    print(sg.graph.nodes())
    print(sg.graph.edges())
