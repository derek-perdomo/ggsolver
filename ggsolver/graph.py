import json
import os
import pickle

import networkx as nx
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

    @property
    def node_properties(self):
        return self._node_properties

    @property
    def edge_properties(self):
        return self._edge_properties

    @property
    def graph_properties(self):
        return self._graph_properties

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

    def has_property(self, pname):
        if pname in self._node_properties or pname in self._edge_properties or pname in self._graph_properties:
            return True
        return False

    def save(self, fpath, overwrite=False, protocol="json"):
        pass

    def load(self, fpath, protocol="json"):
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
        return [self.add_node() for _ in range(num_nodes)]

    def add_edge(self, uid, vid):
        return self._graph.add_edge(uid, vid)

    def add_edges(self, edges):
        """ (uid, vid) pairs """
        return [self.add_edge(uid, vid) for uid, vid in edges]

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
        return self._graph.predecessors(uid)

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
            successors = list(self.successors(uid))
            if len(list(successors)) == 0:
                continue

            graph["edges"][uid] = dict()
            for vid in successors:
                graph["edges"][uid].update({vid: self._graph.number_of_edges(uid, vid)})

        # Add node properties
        graph["node_properties"] = self._node_properties
        graph["edge_properties"] = {
            prop_name: [
                {
                    "edge": edge,
                    "pvalue": pvalue
                }
                for edge, pvalue in prop_value.items()
            ]
            for prop_name, prop_value in self._edge_properties.items()
        }
        graph["graph_properties"] = self._graph_properties

        # Warn about any properties that were ignored.
        ignored_attr = set(self.__dict__.keys()) - set(self._graph_properties.keys())
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
        graph_dict = obj_dict["graph"]

        # Add nodes
        obj.add_nodes(num_nodes=int(graph_dict["nodes"]))

        # Add edges
        edges = graph_dict["edges"]
        for uid in edges:
            for vid in edges[uid]:
                for key in range(edges[uid][vid]):
                    obj._graph.add_edge(int(uid), int(vid), key=int(key))

        # Add properties
        for node_prop, np_value in graph_dict["node_properties"].items():
            np_map = NodePropertyMap(graph=obj)
            np_map.update({int(k): v for k, v in np_value.items()})
            obj[node_prop] = np_map

        for graph_prop, gp_value in graph_dict["graph_properties"].items():
            obj[graph_prop] = gp_value

        for edge_prop, ep_value in graph_dict["edge_properties"].items():
            ep_map = EdgePropertyMap(graph=obj)
            ep_map.update({
                tuple(d["edge"]): d["pvalue"]
                for d in ep_value
            })
            obj[edge_prop] = ep_map

        # Return constructed object
        return obj

    def save(self, fpath, overwrite=False, protocol="json"):
        if not overwrite and os.path.exists(fpath):
            raise FileExistsError("File already exists. To overwrite, call Graph.save(..., overwrite=True).")

        graph_dict = self.serialize()
        if protocol == "json":
            with open(fpath, "w") as file:
                json.dump(graph_dict, file, indent=2)
        elif protocol == "pickle":
            with open(fpath, "wb") as file:
                pickle.dump(graph_dict, file)
        else:
            raise ValueError(f"Graph.save() does not support '{protocol}' protocol. One of ['json', 'pickle'] expected")

    @classmethod
    def load(cls, fpath, protocol="json"):
        if not os.path.exists(fpath):
            raise FileNotFoundError("File does not exist.")

        if protocol == "json":
            with open(fpath, "r") as file:
                obj_dict = json.load(file)
                graph = cls.deserialize(obj_dict)
        elif protocol == "pickle":
            with open(fpath, "rb") as file:
                obj_dict = pickle.load(file)
                graph = cls.deserialize(obj_dict)
        else:
            raise ValueError(f"Graph.load() does not support '{protocol}' protocol. One of ['json', 'pickle'] expected")

        return graph
