from parsers.pl import PLFormula


def demo_pl_formula():
    print(PLFormula("true"))
    print(PLFormula("false"))
    print(PLFormula("a"))
    print(PLFormula("!a & b"))
    print(PLFormula("a & b"))
    print(PLFormula("a | b"))

    f = PLFormula("(a | b) & b")
    print(f"formula={f}")

    new_f = f.substitute({"a": "x"})
    print(f"formula.substitute({{'a': 'x'}}) = {new_f}")

    val = f.evaluate({"x": True, "b": False})
    print(f"formula.evaluate({{'x': True, 'b': False}}) = {val}")

    val = f.evaluate({"x": True, "b": True})
    print(f"formula.evaluate({{'x': True, 'b': True}}) = {val}")

    f = PLFormula("!p0")
    aut = f.translate()
    print()
    print(f"f={f}, \naut={aut}")


if __name__ == '__main__':
    demo_pl_formula()