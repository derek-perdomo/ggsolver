from parsers.scltl import ScLTLFormula


def demo_scltl_formula():
    print(ScLTLFormula("true"))
    print(ScLTLFormula("false"))
    print(ScLTLFormula("a"))
    print(ScLTLFormula("!a & b"))
    print(ScLTLFormula("a & b"))
    print(ScLTLFormula("a | b"))

    f = ScLTLFormula("(a | b) & b")
    print(f"formula={f}")

    new_f = f.substitute({"a": "x"})
    print(f"formula.substitute({{'a': 'x'}}) = {new_f}")

    val = f.evaluate({"x": True, "b": False})
    print(f"formula.evaluate({{'x': True, 'b': False}}) = {val}")

    val = f.evaluate({"x": True, "b": True})
    print(f"formula.evaluate({{'x': True, 'b': True}}) = {val}")

    f = ScLTLFormula("!p0")
    aut = f.translate()
    print()
    print(f"f={f}, \naut={aut}")


if __name__ == '__main__':
    demo_scltl_formula()