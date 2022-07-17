# import graph_tool as gt
import networkx as nx
from tqdm import tqdm
from ggsolver import util


class IGraph:
    """
    Graph interface. A graphical model must implement a IGraph interface.
    """
    def __init__(self):
        self._graph = None
        self._node_properties = dict()
        self._edge_properties = dict()
        self._graph_properties = dict()

    def __getitem__(self, pname):
        if pname in self._node_properties:
            return self._node_properties[pname]
        elif pname in self._edge_properties:
            return self._edge_properties[pname]
        elif pname in self._graph_properties:
            return self._graph_properties[pname]
        else:
            raise KeyError(f"{pname} is not a valid node/edge/graph property.")

    def __setitem__(self, pname, pmap):
        if isinstance(pmap, NodePropertyMap):
            pmap.graph = self
            self._node_properties[pname] = pmap
        elif isinstance(pmap, EdgePropertyMap):
            pmap.graph = self
            self._edge_properties[pname] = pmap
        else:
            self._graph_properties[pname] = pmap

    def add_node(self):
        pass

    def add_nodes(self, num_nodes):
        pass

    def add_edge(self, uid, vid):
        pass

    def add_edges(self, edges):
        """ (uid, vid) pairs """
        pass

    def rem_node(self, uid):
        pass

    def rem_edge(self, uid, vid, key):
        pass

    def has_node(self, uid):
        pass

    def has_edge(self, uid, vid, key=None):
        pass

    def nodes(self):
        pass

    def edges(self):
        pass

    def successors(self, uid):
        pass

    def predecessors(self, uid):
        pass

    def neighbors(self, uid):
        pass

    def ancestors(self, uid):
        pass

    def descendants(self, uid):
        pass

    def in_edges(self, uid):
        pass

    def out_edges(self, uid):
        pass

    def number_of_nodes(self):
        pass

    def number_of_edges(self):
        pass

    def clear(self):
        pass

    def serialize(self):
        pass

    def deserialize(self, obj_dict):
        pass


class NodePropertyMap(dict):
    def __init__(self, graph, default=None):
        super(NodePropertyMap, self).__init__()
        self.graph = graph
        self.default = default

    def __repr__(self):
        return f"<NodePropertyMap graph={repr(self.graph)}>"

    def __missing__(self, node):
        if self.graph.has_node(node):
            return self.default
        raise ValueError(f"[ERROR] NodePropertyMap.__missing__:: {repr(self.graph)} does not contain node {node}.")

    def __getitem__(self, node):
        try:
            return super(NodePropertyMap, self).__getitem__(node)
        except KeyError:
            return self.__missing__(node)

    def __setitem__(self, node, value):
        assert self.graph.has_node(node), f"Node {node} not in {self.graph}."
        if value != self.default:
            super(NodePropertyMap, self).__setitem__(node, value)


class EdgePropertyMap(dict):
    def __init__(self, graph, default=None):
        super(EdgePropertyMap, self).__init__()
        self.graph = graph
        self.default = default

    def __repr__(self):
        return f"<EdgePropertyMap graph={repr(self.graph)}>"

    def __missing__(self, edge):
        if self.graph.has_edge(edge):
            return self.default
        raise ValueError(f"[ERROR] EdgePropertyMap.__missing__:: {repr(self.graph)} does not contain node {edge}.")

    def __getitem__(self, edge):
        try:
            return dict.__getitem__(self, edge)
        except KeyError:
            return self.__missing__(edge)

    def __setitem__(self, node, value):
        if value != self.default:
            super(EdgePropertyMap, self).__setitem__(node, value)


class Graph(IGraph):
    def __init__(self):
        super(Graph, self).__init__()
        self._graph = nx.MultiDiGraph()

    def __str__(self):
        return f"<Graph with |V|={self.number_of_nodes()}, |E|={self.number_of_edges()}>"

    def add_node(self):
        uid = self._graph.number_of_nodes()
        self._graph.add_node(uid)
        return uid
    
    def add_nodes(self, num_nodes):
        return (self.add_node() for _ in range(num_nodes))

    def add_edge(self, uid, vid):
        return self._graph.add_edge(uid, vid)

    def add_edges(self, edges):
        """ (uid, vid) pairs """
        return (self.add_edge(uid, vid) for uid, vid in edges)

    def rem_node(self, uid):
        raise NotImplementedError("Removal of nodes is not supported. Use SubGraph instead.")

    def rem_edge(self, uid, vid, key):
        raise NotImplementedError("Removal of nodes is not supported. Use SubGraph instead.")

    def has_node(self, uid):
        return self._graph.has_node(uid)

    def has_edge(self, uid, vid, key=None):
        return self._graph.has_edge(uid, vid, key)

    def nodes(self):
        return self._graph.nodes()

    def edges(self):
        return self._graph.edges(keys=True)

    def successors(self, uid):
        return self._graph.successors(uid)

    def predecessors(self, uid):
        self._graph.predecessors(uid)

    def neighbors(self, uid):
        return self._graph.neighbors(uid)

    def ancestors(self, uid):
        return nx.ancestors(self._graph, uid)

    def descendants(self, uid):
        return nx.descendants(self._graph, uid)

    def in_edges(self, uid):
        return self._graph.in_edges(uid, keys=True)

    def out_edges(self, uid):
        return self._graph.out_edges(uid, keys=True)

    def number_of_nodes(self):
        return self._graph.number_of_nodes()

    def number_of_edges(self):
        return self._graph.number_of_edges()

    def clear(self):
        self._graph.clear()

    def serialize(self):
        # Initialize a graph dictionary
        graph = dict()

        # Add nodes
        graph["nodes"] = self.number_of_nodes()

        # Add edges
        graph["edges"] = dict()
        for uid in range(self.number_of_nodes()):
            successors = self.successors(uid)
            if len(successors) == 0:
                continue

            graph["edges"][uid] = dict()
            for vid in successors:
                graph["edges"][uid].update({vid: self._graph.number_of_edges(uid, vid)})

        # Add node properties
        graph["node_properties"] = self._node_properties
        graph["edge_properties"] = self._node_properties
        graph["graph_properties"] = self._node_properties

        # Warn about any properties that were ignored.
        ignored_attr = set(self.__dict__.keys()) - {
            "_graph",
            "_node_properties",
            "_edge_properties",
            "_graph_properties"
        }
        print(util.BColors.WARNING, f"[WARN] Attributes {ignored_attr} were not serialized because they are not "
                                     f"node/edge/graph properties.", util.BColors.ENDC)

        # TODO. Add metadata such as time of serialization, serializer version etc.
        obj_dict = {"graph": graph}

        # Return serialized object
        return obj_dict

    @classmethod
    def deserialize(cls, obj_dict):
        # Instantiate new object
        obj = cls()

        # Get serialized graph object
        graph = obj_dict["graph"]

        # Add nodes
        obj.add_nodes(num_nodes=int(obj_dict["nodes"]))

        # Add edges
        edges = obj_dict["edges"]
        for uid in edges:
            for vid in edges[uid]:
                for key in edges[uid][vid]:
                    obj._graph.add_edge(int(uid), int(vid), key=int(key))

        # Add properties
        obj._node_properties = obj_dict["node_properties"]
        obj._edge_properties = obj_dict["edge_properties"]
        obj._graph_properties = obj_dict["graph_properties"]

        # Return constructed object
        return obj
