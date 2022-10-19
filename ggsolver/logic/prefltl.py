from functools import reduce

import spot
import ggsolver.interfaces.i_spot as i_spot
from ggsolver.graph import *
from ggsolver.logic.formula import BaseFormula, ParsingError, PARSERS_DIR
from ggsolver.logic.ltl import LTL, ScLTL
from lark import Lark, Transformer, Tree, Visitor
from pathlib import Path


class PrefLTL(BaseFormula):
    """
    PrefLTL formula is internally represented as a PrefModel instance.
    """
    def __init__(self, f_str, atoms=None):
        super(PrefLTL, self).__init__(f_str, atoms)

        # Parse input string
        parser = LTLPrefParser()
        self.tree = parser.parse(self.f_str)

        # Build preference model
        self._repr = PrefModel(self.tree)

        # Construct atoms and outcomes
        #   Ensure all LTL formulas share same set of atoms.
        self._atoms |= self._repr.atoms
        self._outcomes = {LTL(f_str=str(outcome), atoms=self._atoms) for outcome in self._repr.outcomes}

    def __str__(self):
        return str(self.f_str)

    # ==================================================================
    # IMPLEMENTATION OF ABSTRACT METHODS
    # ==================================================================
    def translate(self):
        raise NotImplementedError

    def substitute(self, subs_map=None):
        raise NotImplementedError("To be implemented in future.")

    def evaluate(self, true_atoms):
        """
        Evaluates a propositional logic formula given the set of true atoms.

        :param true_atoms: (Iterable[str]) A propositional logic formula.
        :return: (bool) True if formula is true, otherwise False.
        """
        raise NotImplementedError("Evaluation not defined for PrefLTL formula.")

    def atoms(self):
        return self._atoms

    def outcomes(self):
        return self._outcomes

    def model(self):
        return self._repr

    # ==================================================================
    # SPECIAL METHODS OF PrefLTL CLASS
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


class PrefModel(Transformer):
    def __init__(self, tree):
        super(PrefModel, self).__init__()

        # Instance variables
        self.tree = tree
        self.outcomes = set()
        self.atoms = set()

        # Build preference model
        #  FIXME Typically, a model is list of sets (due to ORing).
        self.model = self.transform(self.tree)

        # Define all outcomes over same set of atoms.
        for outcome in self.outcomes:
            outcome.update_atoms(self.atoms)

        # Fix indices of outcomes
        self.outcomes = list(self.outcomes)

        # Complete preference model. (add alpha0)
        self._complete_outcomes()
        print(self.outcomes)

        # Force all outcomes to be preferred to alpha0.
        self._assumption1()

        # Make reflexive.
        self.make_reflexive()

        # Transitive closure.
        self.transitive_closure()

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================
    def _complete_outcomes(self):
        alpha0_str = " & ".join([f"(!{str(f)})" for f in self.outcomes])
        alpha0 = LTL(f_str=alpha0_str)
        self.outcomes.insert(0, alpha0)

    def _assumption1(self):
        for model_idx in range(len(self.model)):
            for outcome_idx in range(1, len(self.outcomes)):
                self.model[model_idx].add((self.outcomes[outcome_idx], self.outcomes[0]))

    def transitive_closure(self):
        for model_idx in range(len(self.model)):
            model = self.model[model_idx]
            while True:
                new_relations = set((x, w) for x, y in model for z, w in model if z == y)
                # print(f"new_relations={[str(x), str(y) for x, y in new_relations]}")
                print(f"{new_relations=}")
                closure_until_now = model | new_relations
                if closure_until_now == model:
                    break
                model = closure_until_now
            self.model[model_idx] |= model

    def make_reflexive(self):
        for model_idx in range(len(self.model)):
            for outcome in self.outcomes:
                self.model[model_idx].add((outcome, outcome))

    # ============================================================================
    # VISUALIZATIONS
    # ============================================================================
    def graphify(self, base_only=False):
        """
        Preference model is not a GraphicalModel. So, it has different properties than a GraphicalModel.

        :param base_only:
        :return:
        """
        # Initialize graph object
        graph = Graph()

        # Set graph properties
        graph["atoms"] = self.atoms
        graph["outcomes"] = [str(outcome) for outcome in self.outcomes]

        # Node property
        np_state = NodePropertyMap(graph)

        # Add nodes
        node_ids = graph.add_nodes(len(self.outcomes))

        # Cache states as a dictionary {state: uid}
        states2id = dict(zip(self.outcomes, node_ids))

        # Update state property
        for outcome in self.outcomes:
            np_state[states2id[outcome]] = outcome
        graph["state"] = np_state

        # Add edges
        # PATCH (Temp. Remove this on 19 Oct 22)
        for out1, out2 in self.model[0]:
            uid = states2id[out2]
            vid = states2id[out1]
            graph.add_edge(uid, vid)

        # Return graph
        return graph

    # ============================================================================
    # LARK TRANSFORMER FUNCTIONS
    # ============================================================================
    def start(self, args):
        if type(args[0]) == set:
            return [args[0]]
        return args[0]

    def pref_and(self, args):
        return set.union(*args[::2])

    def pref_or(self, args):
        raise NotImplementedError("Currently, ORing of preference formulas is not supported.")

    def prefltl_weakpref(self, args):
        return {(args[0], args[2])}

    def prefltl_strictpref(self, args):
        return {(args[0], args[2])}
    
    def prefltl_indifference(self, args):
        return {(args[0], args[2]), (args[2], args[0])}

    def prefltl_incomparable(self, args):
        return set()

    def ltl_formula(self, args):
        f = LTL(args[0])
        self.outcomes.add(f)
        self.atoms.update(set(f.atoms()))
        return f


if __name__ == '__main__':
    parser_ = LTLPrefParser()
    formula_ = PrefLTL("Fa > Gb && Fb > Ga && Fb > Fa", atoms={"c"})
    print([(str(f), f.atoms()) for f in formula_.outcomes()])
    print(formula_.atoms())

    print()
    from pprint import pprint
    outcomes = formula_._repr.outcomes
    pprint([(outcomes.index(x), outcomes.index(y)) for x, y in formula_._repr.model[0]])
    pprint([(str(x), str(y)) for x, y in formula_._repr.model[0]])

    graph = formula_._repr.graphify()
    graph.to_png("pref.png", nlabel=["state"])

    # TODO. Try nested ANDing with parenthesis.