import snap
import random
import time
import tracemalloc
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                    # datefmt='%m-%d %H:%M',
                    filename="snap_benchmark.log"
                    )


class SnapGraph:
    def __init__(self):
        self._graph = snap.TNEANet.New()
        self._node_dict = dict()        # {node: {id: {...}}}
        self._edge_dict = dict()        # {(uid, vid): {id: {...}}}

    def __contains__(self, n):
        pass

    def add_node(self, n, **attr):
        """
        No containment check is done.
        """
        nid = self._graph.AddNode()
        self._node_dict[n] = {nid: attr}

    def add_nodes_from(self, nodes, **attr):
        for element in nodes:
            if len(nodes) == 2:
                if isinstance(element[1], dict):
                    attr.update(element[1])
                    self.add_node(element[0], **attr)
                    continue
            else:
                self.add_node(element)

    def remove_node(self, n):
        pass

    def remove_nodes_from(self, nodes):
        pass

    def add_edge(self, u, v, **attr):
        eid = self._graph.AddEdge(u, v)
        uid = self._node_id(u)
        vid = self._node_id(v)
        if (uid, vid) not in self._edge_dict:
            self._edge_dict[(uid, vid)] = {eid: attr}
        else:
            self._edge_dict.update({eid: attr})

    def add_edges_from(self, edges, **attr):
        for element in edges:
            if len(element) == 2:
                self.add_edge(element[0], element[1], **attr)
            elif len(element) == 3:
                if isinstance(element[2], dict):
                    attr.update(element[2])
                    self.add_edge(element[0], element[1], **attr)
                else:
                    raise TypeError("Expected dict as 3rd item in element")

    def remove_edge(self, u, v, key=None):
        pass

    def remove_edges(self, edges):
        pass

    def has_node(self, n):
        pass

    def has_edge(self, u, v, key=None):
        pass

    def clear(self):
        pass

    def clear_edges(self):
        pass

    def nodes(self, data=False):
        pass

    def edges(self, keys=False, data=False):
        pass

    def in_edges(self, nodes, keys=False, data=False):
        pass

    def out_edges(self, nodes, keys=False, data=False):
        pass

    def successors(self, n):
        pass

    def predecessors(self, n):
        pass

    def adjacency(self, n):
        pass

    def number_of_nodes(self):
        pass

    def number_of_edges(self):
        pass

    def size(self):
        pass

    def copy(self):
        pass

    def deepcopy(self):
        pass

    def node_subgraph(self, nodes):
        pass

    def edge_subgraph(self, edges):
        pass

    subgraph = node_subgraph

    def reverse(self):
        pass

    def _node_id(self, n):
        if n in self._node_dict:
            return next(iter(self._node_dict[n].keys()))



def profile(graph, tag):
    num_nodes = int(1e5)
    num_edges = int(1e6)
    num_queries = int(1e6)

    tracemalloc.start()
    # Add a 10K nodes, 100K edges at random.
    start0 = time.time_ns()
    graph.add_nodes_from(range(num_nodes))
    end0 = time.time_ns()
    logging.debug(f"{tag}: {num_nodes} node addition: {10 ** -6 * (end0 - start0)} ms.")

    edges = set()
    while len(edges) < num_edges:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        edges.add((u, v))

    start1 = time.time_ns()
    graph.add_edges_from(edges)
    end1 = time.time_ns()
    logging.debug(f"{tag}: {num_edges} edge addition: {10 ** -6 * (end1 - start1)} ms.")

    # Run a 100K successor and predecessor queries.
    start2 = time.time_ns()
    for _ in range(num_queries):
        n = random.randint(0, num_nodes - 1)
        graph.successors(n)

    end2 = time.time_ns()
    logging.debug(f"{tag}: {num_queries} succcessor queries: {10 ** -6 * (end2 - start2)} ms.")

    for _ in range(num_queries):
        n = random.randint(0, num_nodes - 1)
        graph.predecessors(n)

    end3 = time.time_ns()
    logging.debug(f"{tag}: {num_queries} predecessor queries: {10 ** -6 * (end3 - end2)} ms.")
    _, peak = tracemalloc.get_traced_memory()
    logging.debug(f"Peak was {peak / 10 ** 6} MB")
    tracemalloc.stop()


if __name__ == '__main__':
    # Create a graph
    snap_graph = SnapGraph()

    # Run profiler
    for _ in range(10):
        logging.debug("---------------------------------\n\n")
        profile(snap_graph, tag="snap")
