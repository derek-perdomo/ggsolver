from ggsolver import *

graph = TGraph()

# Add single node
n1 = graph.add_node()
print(n1.get_node_id())

# Add several nodes
nodes = graph.add_nodes_from(10)
print([n.get_node_id() for n in nodes])