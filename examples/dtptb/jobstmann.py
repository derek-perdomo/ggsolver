import networkx as nx
import random
from ggsolver.dtptb.model import DtptbGame
from ggsolver.dtptb.solvers import SWinReach, ASWinReach


def test_jobstmann_example():
    graph = nx.MultiDiGraph()

    # Define nodes
    graph.add_nodes_from([(0, {"turn": 1}),
                          (1, {"turn": 2}),
                          (2, {"turn": 2}),
                          (3, {"turn": 2}),
                          (4, {"turn": 1}),
                          (5, {"turn": 2}),
                          (6, {"turn": 1}),
                          (7, {"turn": 2})])

    # Define edges
    graph.add_edges_from([(0, 1, {"action": str((0, 1))}),
                          (0, 3, {"action": str((0, 3))}),
                          (1, 0, {"action": str((1, 0))}),
                          (1, 2, {"action": str((1, 2))}),
                          (1, 4, {"action": str((1, 4))}),
                          (2, 2, {"action": str((2, 2))}),
                          (2, 4, {"action": str((2, 4))}),
                          (3, 0, {"action": str((3, 0))}),
                          (3, 4, {"action": str((3, 4))}),
                          (3, 5, {"action": str((3, 5))}),
                          (4, 1, {"action": str((4, 1))}),
                          (4, 3, {"action": str((4, 3))}),
                          (5, 3, {"action": str((5, 3))}),
                          (5, 6, {"action": str((5, 6))}),
                          (6, 6, {"action": str((6, 6))}),
                          (6, 7, {"action": str((6, 7))}),
                          (7, 0, {"action": str((7, 0))}),
                          (7, 3, {"action": str((7, 3))})])

    final_nodes = [3, 4]

    game = DtptbGame(name="jobstmann example")
    game.construct_explicit(graph)

    swin1 = SWinReach(game=game, final=final_nodes, player=1)
    swin1.solve()
    print("Graph based implementation.")
    print(f"Win1={swin1.p1_winning_region}, Win2={swin1.p2_winning_region}")
    print(f"Win1 Edges = {swin1.p1_strategy_map}")
    print(f"pi_1({0}) = {swin1.p1_strategy(0)}")
    print(f"pi_1({6}) = {swin1.p1_strategy(6)}")
    print(f"pi_2({1}) = {swin1.p2_strategy(1)}")

    aswin = ASWinReach(game, final_nodes)
    aswin.solve()
    print("----")
    print(aswin.p1_winning_region, aswin.p2_winning_region)
    print(f"pi_1 strategy map = {aswin.p1_strategy_map}")
    print(f"pi_1({6}) = {aswin.p1_strategy(6)}")
    print(f"pi_2({1}) = {aswin.p2_strategy(1)}")
    random.seed(0)
    print("random.seed(0)")
    print(f"pi_2({7}) = {aswin.p1_strategy(7)}")
    random.seed(10)
    print("random.seed(10)")
    print(f"pi_2({7}) = {aswin.p1_strategy(7)}")


if __name__ == '__main__':
    test_jobstmann_example()
