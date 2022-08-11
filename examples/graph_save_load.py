import random
from ggsolver.graph import Graph, NodePropertyMap, EdgePropertyMap
from pprint import pprint


def construct_graph():
    graph = Graph()

    # Add nodes
    graph.add_nodes(num_nodes=5)

    # Add edges
    for _ in range(10):
        graph.add_edge(random.choice(range(5)), random.choice(range(5)))

    # Add a node property
    name = NodePropertyMap(graph=graph)
    for i in range(5):
        name[i] = f"Node {i}"
    graph["name"] = name

    # Add an edge property
    label = EdgePropertyMap(graph=graph)
    for edge in graph.edges():
        label[edge] = str(f"Edge {edge}")
    graph["label"] = label

    # Add a graph property
    graph["type"] = "MultiDiGraph"

    # Return graph
    return graph


def check_serialize():
    graph = construct_graph()
    print(graph.nodes())
    print(graph.edges())
    pprint(graph.serialize())


def check_save():
    graph = construct_graph()
    graph.save("mygraph.graph", overwrite=True)


def check_deserialize():
    graph = construct_graph()
    graph_dict = graph.serialize()
    pprint(graph_dict)
    ngraph = Graph.deserialize(graph_dict)
    print()
    print()
    pprint(ngraph.serialize())
    assert graph.serialize() == ngraph.serialize()


def check_load():
    graph = construct_graph()
    graph.save("mygraph.graph", overwrite=True)
    ngraph = Graph.load(fpath="mygraph.graph")
    pprint(graph.serialize())
    print()
    print()
    pprint(ngraph.serialize())
    print()
    print()
    pprint({k: v for k, v in ngraph["label"].items()})


if __name__ == '__main__':
    # check_serialize()
    # check_save()
    check_deserialize()
    # check_load()
