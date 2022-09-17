import spot
from ggsolver.util import apply_atoms_limit, powerset


def simplify(plformula):
    """
    Simplifies a propositional logic formula.

    We use the `boolean_to_isop=True` option for `spot.simplify`.
    See https://spot.lrde.epita.fr/doxygen/classspot_1_1tl__simplifier__options.html

    :param plformula: (str or `spot.formula`) A propositional logic formula.
    """
    plformula = spot.formula(plformula)
    if not plformula.is_boolean():
        raise ValueError(f"Given formula: {plformula} is not a propositional logic formula.")

    return spot.simplify(plformula, boolean_to_isop=True).to_str()


def evaluate(plformula, true_atoms):
    """
    Evaluates a propositional logic formula given the set of true atoms.

    :param plformula: (str or `spot.formula`) A propositional logic formula.
    :param true_atoms: (Iterable[str]) A propositional logic formula.
    """
    # Ensure plformula is a spot.formula instance.
    plformula = spot.formula(plformula)

    # Check if plformula is indeed a propositional logic formula.
    if not plformula.is_boolean():
        raise ValueError(f"Given formula: {plformula} is not a propositional logic formula.")

    # Define a transform to apply to AST of spot.formula.
    def transform(node: spot.formula):
        if node.is_literal():
            if "!" not in node.to_str():
                if node.to_str() in true_atoms:
                    return spot.formula.tt()
                else:
                    return spot.formula.ff()

        return node.map(transform)

    # Apply the transform and return the result.
    # Since every literal is replaced by true or false,
    #   the transformed formula is guaranteed to be either true or false.
    return True if transform(plformula).is_tt() else False


def to_plformula(atoms, sat_assignments):
    """
    Given a subset of elements from powerset(atoms), generates a propositional logic formula
    that accepts exactly those elements.

    :param atoms: (Iterable[str]) A set of atomic propositions.
    :param sat_assignments: (Iterable[powerset(atoms)]) A subset of powerset(atoms) representing
                            satisfiable assignments of the formula to be generated.
    """
    # Generate all clauses
    formula = []
    for assignment in sat_assignments:
        # Each clause includes an ANDing of atoms in assignment and ANDing of negation of atoms not in assignment
        complete_acc = [p if p in assignment else f"!{p}" for p in atoms]
        formula.append(f"({' & '.join(complete_acc)})")

    # Construct DNF formula by joining all clauses using disjunction
    formula = " | ".join(formula)

    # Simplify the formula
    return simplify(formula)


def all_sat(atoms, plformula):
    """
    Generates the set of all satisfying assignments to atoms of the given propositional logic formula.

    :param atoms: (Iterable[str]) A set of atomic propositions.
    :param plformula: (str or `spot.formula`) A propositional logic formula.
    """
    # Apply limitation on atoms we allow in ggsolver. Raises ValueError if |atoms| exceeds limit.
    apply_atoms_limit(atoms)

    # For each assignment, check whether the formula evaluates to True.
    # If yes, include it in set of all satisfying assignments.
    sat_assignments = []
    for assignment in powerset(atoms):
        if evaluate(plformula, assignment):
            sat_assignments.append(assignment)
    return sat_assignments


# if __name__ == '__main__':
#     # example: simplify
#     print(simplify("(a & !b) | (!a & !b) | (c & b)"))
#
#     # example: accepting_atoms_to_plformula
#     atoms = ["a", "b"]
#     acc_sets = [("a", "b"), ("b",)]
#     print(to_plformula(atoms, acc_sets))
#
#     # Spot substitute
#     print(evaluate("a & !b", {"a", "b"}))
#     print(evaluate("a & !b", {"a"}))
#
#     # Generate acceptance atom sets
#     print(all_sat(atoms, "b"))