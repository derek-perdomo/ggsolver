from ggsolver import *
import random

graph = TGraph()

# Add single node
n1 = graph.add_node()
print(n1, n1.get_node_id())

# Add several nodes
nodes = graph.add_nodes_from(10)
print([n.get_node_id() for n in nodes])

# Add single edge
e1 = graph.add_edge(0, 1)
print(e1, e1.get_edge_id())

#Add several edges
edges = graph.add_edges_from([(random.randint(0, 9), random.randint(0, 9)) for _ in range(10)])
print([(e.get_edge_id(), e.get_uid(), e.get_vid()) for e in edges])