import spot
from ggsolver.graph import Graph, EdgePropertyMap


def translate(formula, options=None):
    if options is None or options == []:
        options = ["BA", "High", "SBAcc", "Complete"]

    spot_aut = spot.translate(formula, *options)
    bdd_dict = spot_aut.get_dict()

    aut = Graph()

    aut["acc_name"] = spot_aut.acc().name()
    aut["acc_cond"] = str(spot_aut.get_acceptance())
    aut["num_sets"] = spot_aut.num_sets()
    aut["num_states"] = spot_aut.num_states()
    aut["init_state"] = spot_aut.get_init_state_number()
    aut["atoms"] = {str(ap): bdd_dict.varnum(ap) for ap in spot_aut.ap()}
    aut["name"] = formula if spot_aut.get_name() is None else spot_aut.get_name()
    aut["is_deterministic"] = bool(spot_aut.prop_universal() and spot_aut.is_existential())
    aut["is_unambiguous"] = bool(spot_aut.prop_unambiguous())
    aut["is_state_based_acc"] = bool(spot_aut.prop_state_acc())
    aut["is_terminal"] = bool(spot_aut.prop_terminal())
    aut["is_weak"] = bool(spot_aut.prop_weak())
    aut["is_inherently_weak"] = bool(spot_aut.prop_inherently_weak())
    aut["is_stutter_invariant"] = bool(spot_aut.prop_stutter_invariant())

    edge_label = EdgePropertyMap(graph=aut)
    acc_set = EdgePropertyMap(graph=aut)
    aut.add_nodes(spot_aut.num_states())
    for s in range(0, spot_aut.num_states()):
        # aut.state2edges[s] = dict()
        for t in spot_aut.out(s):
            key = aut.add_edge(int(s), int(t.dst))
            edge_label[(int(s), int(t.dst), key)] = spot.bdd_format_formula(bdd_dict, t.cond)
            acc_set[(int(s), int(t.dst), key)] = list(t.acc.sets())
            # aut.state2edges[s][t.dst] = [spot.bdd_format_formula(bdd_dict, t.cond), list(t.acc.sets())]
        # aut.state2edges[s]["acc_sets"] = list(aut.state2edges[s]["acc_sets"])

    aut["edge_label"] = edge_label
    aut["acc_set"] = acc_set
    return aut

