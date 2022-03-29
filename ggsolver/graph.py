from ggsolver import TGraph


class Graph(TGraph):
    def __init__(self, name):
        super(Graph, self).__init__()
        self.__setattr__("name", name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"Graph({self.name})"

    def __setstate__(self, state):
        pass

    def __getstate__(self):
        pass

    def __setattr__(self, key, value):
        if key in dir(self):
            raise AttributeError(f"Cannot overwrite C++ bound functions.")
        if key in ("nodes", "edges", "graph"):       # Needs to be synced with `m_special_attr_names` in graph.h
            raise AttributeError(f"Cannot set values of specialized attributes of {repr(self)}.")
        # TODO If value type is Entity, serialize it.
        super(Graph, self).set_attr(key, value)

    def __getattr__(self, item):
        if item == "nodes":
            return super(Graph, self).get_nodes_factory()
        elif item == "edges":
            return super(Graph, self).get_edges_factory()
        elif item == "graph":
            raise AttributeError(f"Cannot access `graph` attribute in {repr(self)} because it is not bound.")
        else:
            # TODO If value type is Entity, deserialize it.
            return super(Graph, self).get_attr(item)

    def add_node(self, n):
        pass

    def add_edge(self, e):
        pass

    def add_nodes_from(self, nodes):
        pass

    def add_edges_from(self, edges):
        pass

    def rem_node(self, node):
        pass

    def rem_edge(self, edge):
        pass

    def has_node(self, node):
        pass

    def has_edge(self, edge):
        pass


if __name__ == '__main__':
    graph = Graph("new graph")

    # Test str, repr.
    print(repr(graph))
    print(str(graph))

    # Testing getattr, setattr
    graph.mysize = (10, 20)
    print(graph.mysize)

