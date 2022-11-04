from ggsolver.logic.prefltl import *


def assign_rank(dfpa: DFPA):
    # FIXME: Creating a subgraph here will add hidden_nodes, hidden_edges property to preference graph.
    #   These properties have no use later on.
    #   (Pending feature request) SubGraph has options to not share hidden_nodes, hidden_edges properties with base graph.
    #   After the feature is available, update this code.
    pg = SubGraph(dfpa.pref_graph())
    np_rank = NodePropertyMap(graph=pg, default=None)

    nodes = set(pg.nodes())
    curr_rank = 0
    while len(nodes) > 0:
        nodes_at_curr_rank = {n for n in nodes if len(pg.successors(n)) == 0}
        for n in nodes_at_curr_rank:
            np_rank[n] = curr_rank
            pg.hide_node(n)
        curr_rank += 1
        nodes = nodes - nodes_at_curr_rank

    dfpa.pref_graph()["rank"] = np_rank
    print(pg["rank"])


if __name__ == '__main__':
    formula_ = PrefScLTL("Fa > Fb")
    model_ = formula_.model()
    aut_ = formula_.translate()
    assign_rank(aut_)