import pytest
from parsers.formula import ParsingError
from parsers.pl import PLFormula


def test_parsers_pl_atom():
    _ = PLFormula("true")
    _ = PLFormula("false")
    assert PLFormula("true") == PLFormula("True")

    _ = PLFormula("a")
    _ = PLFormula("b0")
    _ = PLFormula("c_2")

    with pytest.raises(ParsingError):
        _ = PLFormula("A")

    with pytest.raises(ParsingError):
        _ = PLFormula("aH")

    with pytest.raises(ParsingError):
        _ = PLFormula("a_Z")


def test_parsers_pl_negation():
    _ = PLFormula("~a")
    _ = PLFormula("!b")

    with pytest.raises(ParsingError):
        _ = PLFormula("~Z")


def test_parsers_pl_and():
    _ = PLFormula("a & b")
    _ = PLFormula("a && b")


def test_parsers_pl_or():
    _ = PLFormula("a | b")
    _ = PLFormula("a || b")


def test_parsers_pl_implies():
    _ = PLFormula("a -> b")
    _ = PLFormula("a => b")
    _ = PLFormula("a -> b -> c")


def test_parsers_pl_equivalence():
    _ = PLFormula("a <-> b")
    _ = PLFormula("a <=> b")


def test_parsers_pl_complex():
    _ = PLFormula("!a | b <-> !(a & !b) <-> a->b")
    _ = PLFormula("a & false & true")


def test_parsers_pl_substitute():
    a = PLFormula("a & b")
    b = a.substitute({"a": "c"})
    assert b == PLFormula("c & b")

    c = a.substitute({"a": "true", "b": "false"})
    assert c == PLFormula("false")


def test_parsers_pl_evaluate():
    a = PLFormula("a & b")
    b = a.substitute({"a": True})
    assert b == PLFormula("b")

    c = a.substitute({"a": True, "b": False})
    assert c == PLFormula("false")
