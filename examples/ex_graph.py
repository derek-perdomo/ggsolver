"""
The example shows how to use graph.Graph class.
"""

from ggsolver import graph
from pprint import pprint


if __name__ == '__main__':
    # Creating a graph
    g = graph.Graph()
    print(g)

    # Add single node
    n0 = g.add_node()
    print(f"g.add_node() -> {n0}")

    # Add multiple nodes
    n1, n2 = g.add_nodes(num_nodes=2)
    print(f"g.add_nodes(num_nodes=2) -> n1:{n1}, n2:{n2}")

    nodes = g.add_nodes(num_nodes=5)
    print(f"g.add_nodes(num_nodes=5) -> nodes:{nodes}")

    # Create an edge (returns a key corresponding to edge).
    key0 = g.add_edge(n0, n1)
    print(f"g.add_edge(n0, n1) -> key0:{key0}")

    key1 = g.add_edge(n0, n1)
    print(f"When two edges are added between same nodes, the key is incremented.")
    print(f"Every edge is represented by a unique triple: (uid, vid, key).")
    print(f"g.add_edge(n0, n1) -> key1:{key1}")

    key2 = g.add_edge(n0, n2)
    print(f"g.add_edge(n0, n2) -> key2:{key2}")

    # Add multiple edges
    keys = g.add_edges([(n0, n1), (n1, n2)])
    print(f"g.add_edges([(n0, n1), (n1, n2)]) -> keys:{keys}")

    # Check successors of a node
    successors = g.successors(n0)
    print(f"g.successors(n0) -> {list(successors)}  ... Node IDs of successors.")

    # Check predecessors of a node
    predecessors = g.predecessors(n1)
    print(f"g.predecessors(n1) -> {list(predecessors)}  ... Node IDs of predecessors.")

    # Check out_edges from a node
    out_edges = g.out_edges(n0)
    print(f"g.out_edges(n0) -> {list(out_edges)}  ... Edge triples of out edges.")

    # Check in_edges to a node
    in_edges = g.in_edges(n1)
    print(f"g.in_edges(n1) -> {list(in_edges)}  ... Edge triples of out edges.")

    # Check all nodes
    nodes = g.nodes()
    print(f"g.nodes() -> {list(nodes)}  ... Node IDs.")

    # Check all edges
    edges = g.edges()
    print(f"g.edges() -> {list(edges)}  ... Edge triples of out edges.")

    # Get number of nodes, edges
    print(f"g.number_of_nodes() -> {g.number_of_nodes()}")
    print(f"g.number_of_edges() -> {g.number_of_edges()}")

    # Associate a property with nodes
    # Approach 1: Create the property separately and then associate it with graph.
    name = graph.NodePropertyMap(g)
    name[n0] = "n0"
    g["name"] = name
    print(f"g['name'][n0] -> {g['name'][n0]}  ... If property value is assigned, then the value is returned.")
    print(f"g['name'][n1] -> {g['name'][n1]}  ... If property value is NOT assigned, then default value is returned.")

    # Approach 2: Create the property directly.
    g["name"] = graph.NodePropertyMap(g, default="default-name")
    g["name"][n0] = "n0"
    print(f"g['name'][n0] -> {g['name'][n0]}  ... If property value is assigned, then the value is returned.")
    print(f"g['name'][n1] -> {g['name'][n1]}  ... If property value is NOT assigned, then default value is returned.")

    # Associate a property with edges (edge properties can also be associated in two ways like node properties).
    g["label"] = graph.EdgePropertyMap(g)
    g["label"][(n0, n1, key0)] = "(n0, n1, 0)"
    print(f"g['label'][(n0, n1, key0)] -> {g['label'][(n0, n1, key0)]}  "
          f"... If property value is assigned, then the value is returned.")
    print(f"g['label'][(n0, n1, key1)] -> {g['label'][(n0, n1, key1)]}  "
          f"... If property value is NOT assigned, then default value is returned.")

    # Graph properties are assigned similarly, except we do not have GraphPropertyMap class.
    g["graph_prop0"] = 10
    g["graph_prop1"] = "I am a graph property!"

    print(f'g["graph_prop0"] -> {g["graph_prop0"]}')
    print(f'g["graph_prop1"] -> {g["graph_prop1"]}')

    # A graph object can be serialized into a dictionary.
    g_dict = g.serialize()
    pprint(g_dict)

    # A dictionary can be deserialized to get a graph object.
    new_g = graph.Graph.deserialize(g_dict)

    # A graph can be saved and loaded to/from a file
    #   fpath: gives a complete path of the file to which the graph will be saved. (include extension)
    #   overwrite: if the file should overwrite an existing file.
    #   protocol: either json or pickle.
    g.save(fpath="mygraph.graph", overwrite=True, protocol="json")
    loaded_g = graph.Graph.load(fpath="mygraph.graph", protocol="json")

    # Draw graph
    loaded_g.to_png("graph.png", nlabel=["name"], elabel=["label"])
    print("ok")
