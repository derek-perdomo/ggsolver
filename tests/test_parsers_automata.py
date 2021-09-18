import networkx as nx
from parsers import *


def test_parsers_automata_dfa_explicit():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(list(range(4)))
    graph.add_edges_from([
        (0, 0, {"symbol": set()}),
        (0, 1, {"symbol": {"a"}}),
        (0, 2, {"symbol": {"b"}}),
        (0, 2, {"symbol": {"a", "b"}}),
        (1, 1, {"symbol": set()}),
        (1, 1, {"symbol": {"a"}}),
        (1, 1, {"symbol": {"b"}}),
        (1, 1, {"symbol": {"a", "b"}}),
        (2, 2, {"symbol": set()}),
        (2, 2, {"symbol": {"a"}}),
        (2, 2, {"symbol": {"b"}}),
        (2, 2, {"symbol": {"a", "b"}}),
    ])

    aut = Dfa()
    aut.construct_explicit(graph=graph, init_st=0, final={1})

    assert len(aut.states()) == 4
    assert aut.delta(0, set()) == 0
    assert aut.delta(0, {"a"}) == 1
    assert aut.pred(0) == {(0, frozenset())}
    assert aut.succ(0) == {
        (0, frozenset()),
        (1, frozenset({"a"})),
        (2, frozenset({"b"})),
        (2, frozenset({"a", "b"}))
    }


def test_parsers_automata_dfa_symbolic():
    states = range(4)

    def delta(q, sigma):
        if q == 0 and sigma == set():
            return 0
        elif q == 0 and sigma == {"a"}:
            return 1
        elif q == 0 and sigma in [{"b"}, {"a", "b"}]:
            return 2
        elif q == 1:
            return 1
        elif q == 2:
            return 2
        else:
            raise ValueError(f"Unexpected inputs: q={q}, sigma={sigma}")

    def pred(q):
        raise NotImplementedError

    def succ(q):
        raise NotImplementedError

    aut = Dfa()
    aut.construct_symbolic(states=states, alphabet={"a", "b"}, delta=delta, pred=pred, succ=succ, init_st=0, final={1})

    assert len(aut.states()) == 4
    assert aut.delta(0, set()) == 0
    assert aut.delta(0, {"a"}) == 1


def test_parsers_automata_dfa_save_explicit():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(list(range(4)))
    graph.add_edges_from([
        (0, 0, {"symbol": set()}),
        (0, 1, {"symbol": {"a"}}),
        (0, 2, {"symbol": {"b"}}),
        (0, 2, {"symbol": {"a", "b"}}),
        (1, 1, {"symbol": set()}),
        (1, 1, {"symbol": {"a"}}),
        (1, 1, {"symbol": {"b"}}),
        (1, 1, {"symbol": {"a", "b"}}),
        (2, 2, {"symbol": set()}),
        (2, 2, {"symbol": {"a"}}),
        (2, 2, {"symbol": {"b"}}),
        (2, 2, {"symbol": {"a", "b"}}),
    ])

    aut = Dfa()
    aut.construct_explicit(graph=graph, init_st=0, final={1})

    aut.save_to_file(file_name="test1", graph_format="pkl")

    load_aut = Dfa()
    load_aut.load_from_file(metadata_file="test1.json")

    assert len(load_aut.states()) == 4
    assert load_aut.delta(0, set()) == 0
    assert load_aut.delta(0, {"a"}) == 1
    assert load_aut.pred(0) == {(0, frozenset())}
    assert load_aut.succ(0) == {
        (0, frozenset()),
        (1, frozenset({"a"})),
        (2, frozenset({"b"})),
        (2, frozenset({"a", "b"}))
    }


def test_parsers_automata_dfa_save_symbolic():
    states = range(4)

    def delta(q, sigma):
        sigma = set(sigma)
        if q == 0 and sigma == set():
            return 0
        elif q == 0 and sigma == {"a"}:
            return 1
        elif q == 0 and sigma in [{"b"}, {"a", "b"}]:
            return 2
        elif q == 1:
            return 1
        elif q == 2:
            return 2
        elif q == 3:
            return 2
        else:
            raise ValueError(f"Unexpected inputs: q={q}, sigma={sigma}")

    def pred(q):
        raise NotImplementedError

    def succ(q):
        raise NotImplementedError

    aut = Dfa()
    aut.construct_symbolic(states=states, alphabet={"a", "b"}, delta=delta, pred=pred, succ=succ, init_st=0, final={1})

    aut.save_to_file(file_name="test1", graph_format="pkl")

    load_aut = Dfa()
    load_aut.load_from_file(metadata_file="test1.json")

    assert len(load_aut.states()) == 4
    assert load_aut.delta(0, set()) == 0
    assert load_aut.delta(0, {"a"}) == 1
