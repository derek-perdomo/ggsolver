import pytest
from parsers.formula import ParsingError
from parsers.scltl import ScLTLFormula


def test_parsers_scltl_atom():
    _ = ScLTLFormula("false")
    _ = ScLTLFormula("true")
    assert ScLTLFormula("true") == ScLTLFormula("True")

    _ = ScLTLFormula("a")
    _ = ScLTLFormula("b0")
    _ = ScLTLFormula("c_2")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("A")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("aH")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("a_Z")


def test_parsers_scltl_negation():
    _ = ScLTLFormula("~a")
    _ = ScLTLFormula("!b")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("~Z")


def test_parsers_scltl_next():
    _ = ScLTLFormula("X(b)")
    _ = ScLTLFormula("X b")
    _ = ScLTLFormula("Xb")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("X(Z)")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("!X(z)")


def test_parsers_scltl_eventually():
    _ = ScLTLFormula("Fa")
    _ = ScLTLFormula("F(b)")
    _ = ScLTLFormula("F b")
    _ = ScLTLFormula("F !b")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("F(Z)")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("!F(z)")


def test_parsers_scltl_always():
    _ = ScLTLFormula("Ga")
    _ = ScLTLFormula("G(b)")
    _ = ScLTLFormula("G b")
    _ = ScLTLFormula("G !b")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("G(Z)")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("!G z)")


def test_parsers_scltl_and():
    _ = ScLTLFormula("a & b")
    _ = ScLTLFormula("a && b")


def test_parsers_scltl_or():
    _ = ScLTLFormula("a | b")
    _ = ScLTLFormula("a || b")


def test_parsers_scltl_implies():
    _ = ScLTLFormula("a -> b")
    _ = ScLTLFormula("a => b")
    _ = ScLTLFormula("a -> b -> c")


def test_parsers_scltl_equivalence():
    _ = ScLTLFormula("a <-> b")
    _ = ScLTLFormula("a <=> b")


def test_parsers_scltl_until():
    _ = ScLTLFormula("a U b")
    _ = ScLTLFormula("(!a U b)")
    _ = ScLTLFormula("(a U !b)")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("!(a U !b)")


def test_parsers_scltl_complex():
    _ = ScLTLFormula("a & false & true")
    _ = ScLTLFormula("!a | b <-> (!a & !b) <-> a->b")

    with pytest.raises(ParsingError):
        _ = ScLTLFormula("!a | b <-> !(a & !b) <-> a->b")


def test_parsers_scltl_substitute():
    a = ScLTLFormula("a & b")
    b = a.substitute({"a": "c"})
    assert b == ScLTLFormula("c & b")

    c = a.substitute({"a": "true", "b": "false"})
    assert c == ScLTLFormula("false")


def test_parsers_scltl_evaluate():
    a = ScLTLFormula("a & b")
    b = a.substitute({"a": True})
    assert b == ScLTLFormula("b")

    c = a.substitute({"a": True, "b": False})
    assert c == ScLTLFormula("false")


def test_parsers_scltl_translate():
    p = ScLTLFormula("p & !q")
    aut = p.translate()
    print(p)
    print(aut)

    p = ScLTLFormula("F(p & Fq)")
    aut = p.translate()
    print(p)
    print(aut)

    p = ScLTLFormula("Fp & Fq")
    aut = p.translate()
    print(p)
    print(aut)
