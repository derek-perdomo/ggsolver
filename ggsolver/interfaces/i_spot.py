"""
Defines an interface from spot automaton to ggsolver automaton.
"""

import spot
from ggsolver.graph import Graph, NodePropertyMap, EdgePropertyMap
from ggsolver.models import Automaton


def to_spot_aut(f_str, options=None):
    """
    Translates `f_str` to spot automaton. Depending on the class of LTL formula,
    the acceptance condition is selected automatically. By default, the automaton uses following options:
    "deterministic", "high, "complete", "unambiguous", "SBAcc". If selected acceptance condition
    is parity, then we use "colored" option as well.

    The default options can be overridden by passing `options` argument.


    [From spot documentation: spot.lrde.epita.fr/doxygen]
    The optional arguments should be strings among the following:
    - at most one in 'GeneralizedBuchi', 'Buchi', or 'Monitor',
      'generic', 'parity', 'parity min odd', 'parity min even',
      'parity max odd', 'parity max even', 'coBuchi'
      (type of acceptance condition to build)
    - at most one in 'Small', 'Deterministic', 'Any'
      (preferred characteristics of the produced automaton)
    - at most one in 'Low', 'Medium', 'High'
      (optimization level)
    - any combination of 'Complete', 'Unambiguous',
      'StateBasedAcceptance' (or 'SBAcc' for short), and
      'Colored' (only for parity acceptance)

    The default corresponds to 'tgba', 'small' and 'high'.
    """
    if options is not None:
        print(options)
        return spot.translate(f_str, *options)

    cls = spot.mp_class(f_str)
    if cls.upper() == "B" or cls.upper() == "S":
        return spot.translate(f_str, 'Monitor', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc")
    elif cls.upper() == "G" or cls.upper() == "O" or cls.upper() == "R":
        return spot.translate(f_str, 'Buchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc")
    elif cls.upper() == "P":
        return spot.translate(f_str, 'coBuchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc")
    else:  # cls.upper() == "T":
        return spot.translate(f_str, 'parity', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc", "colored")


def from_spot(spot_aut, f_str=None) -> Graph:
    """
    Programmer's Notes:
    # TODO. If all outgoing edges are accepting, state s is accepting with that acceptance set.
        #   see state_acc_sets()
        #   [https://spot.lrde.epita.fr/doxygen/classspot_1_1twa__graph.html#a7af8f4e62f46ef360fbbd1693e78fc91]
    """
    # Get BDD dictionary from spot
    bdd_dict = spot_aut.get_dict()

    # Instantiate a graph
    aut = Graph()

    # Set graph properties
    aut["acc_name"] = spot_aut.acc().name()
    aut["acc_cond"] = str(spot_aut.get_acceptance())
    aut["num_sets"] = spot_aut.num_sets()
    aut["num_states"] = spot_aut.num_states()
    aut["init_state"] = spot_aut.get_init_state_number()
    aut["atoms"] = {str(ap): bdd_dict.varnum(ap) for ap in spot_aut.ap()}
    aut["name"] = f_str if spot_aut.get_name() is None else spot_aut.get_name()
    aut["is_deterministic"] = bool(spot_aut.prop_universal() and spot_aut.is_existential())
    aut["is_unambiguous"] = bool(spot_aut.prop_unambiguous())
    aut["is_state_based_acc"] = bool(spot_aut.prop_state_acc())
    aut["is_terminal"] = bool(spot_aut.prop_terminal())
    aut["is_weak"] = bool(spot_aut.prop_weak())
    aut["is_inherently_weak"] = bool(spot_aut.prop_inherently_weak())
    aut["is_stutter_invariant"] = bool(spot_aut.prop_stutter_invariant())

    edge_label = EdgePropertyMap(graph=aut)
    if bool(spot_aut.prop_state_acc()):
        acc_set = NodePropertyMap(graph=aut)
    else:
        acc_set = EdgePropertyMap(graph=aut)

    aut.add_nodes(spot_aut.num_states())
    for s in range(0, spot_aut.num_states()):
        if bool(spot_aut.prop_state_acc()):
            acc_set[int(s)] = list(spot_aut.state_acc_sets(s).sets())
        for t in spot_aut.out(s):
            key = aut.add_edge(int(s), int(t.dst))
            edge_label[(int(s), int(t.dst), key)] = spot.bdd_format_formula(bdd_dict, t.cond)
            if not bool(spot_aut.prop_state_acc()):
                acc_set[(int(s), int(t.dst), key)] = list(t.acc.sets())

    aut["edge_label"] = edge_label
    aut["acc_set"] = acc_set

    # return Automaton.from_graph(aut)
    return aut


if __name__ == '__main__':
    # aut = to_spot_aut("G(p2 U !XFp1)", options=('tgba', 'small' and 'high'))
    aut = to_spot_aut("G!G(p0 <-> G!F(!p1 U Xp2))", options=('tgba', 'small', 'high'))
    aut = from_spot(aut)
    print("is_deterministic ", aut["is_deterministic"])
    from pprint import pprint
    pprint(aut.serialize())
    aut.to_png("dfa.png", nlabel=["acc_set"], elabel=["edge_label"])

    # from ggsolver.interfaces.i_png import *
    # f_str = "XFp0 R XFp2"
    # spot_aut = spot.translate(f_str)
    # aut = from_spot(spot_aut, f_str=f_str)
    # to_png(aut, "dfa.png", elabel=["edge_label"])
    # pprint(aut.serialize())
