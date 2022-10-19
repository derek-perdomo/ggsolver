import spot
import ggsolver.interfaces.i_spot as i_spot
from ggsolver.logic.formula import BaseFormula, ParsingError, PARSERS_DIR
from ggsolver.util import apply_atoms_limit, powerset

from pathlib import Path
from lark import Lark, Transformer, Tree, Visitor, logger

import logging
logger.setLevel(logging.DEBUG)


class PrefLTL(BaseFormula):
    """
    PL formula is internally represented as spot.formula instance.
    """
    def __init__(self, f_str, atoms=None):
        super(PrefLTL, self).__init__(f_str, atoms)
        self._repr = None
        self._atoms = None
        self._outcomes = None

    def __str__(self):
        return str(self.f_str)

    def _collect_atoms(self):
        atoms = set()

        def traversal(node: spot.formula, atoms_):
            if node.is_literal():
                if "!" not in node.to_str():
                    atoms_.add(node.to_str())
                    return True
            return False

        self._repr.traverse(traversal, atoms)
        return self._atoms | atoms

    # ==================================================================
    # IMPLEMENTATION OF ABSTRACT METHODS
    # ==================================================================
    def translate(self):
        return i_spot.SpotAutomaton(formula=self.f_str, atoms=self.atoms())

    def substitute(self, subs_map=None):
        raise NotImplementedError("To be implemented in future.")

    def evaluate(self, true_atoms):
        """
        Evaluates a propositional logic formula given the set of true atoms.

        :param true_atoms: (Iterable[str]) A propositional logic formula.
        :return: (bool) True if formula is true, otherwise False.
        """
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
        return True if transform(self._repr).is_tt() else False

    def atoms(self):
        return self._atoms

    # ==================================================================
    # SPECIAL METHODS OF PL CLASS
    # ==================================================================
    def simplify(self):
        """
        Simplifies a propositional logic formula.

        We use the `boolean_to_isop=True` option for `spot.simplify`.
        See https://spot.lrde.epita.fr/doxygen/classspot_1_1tl__simplifier__options.html

        :return: (str) String representing simplified formula.
        """
        return spot.simplify(self._repr, boolean_to_isop=True).to_str()


class LTLPrefParser:
    """PrefScLTL Parser class."""

    def __init__(self):
        """Initialize."""
        self._parser = Lark(open(str(Path(PARSERS_DIR, "prefltl.lark"))), parser="lalr")

    def __call__(self, f_str):
        """Call."""
        return self.parse(f_str)

    def parse(self, f_str):
        parse_tree = self._parser.parse(f_str)
        return parse_tree


if __name__ == '__main__':
    parser = LTLPrefParser()
    tree = parser.parse("Fa > Gb")