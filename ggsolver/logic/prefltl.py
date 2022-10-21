import itertools
from functools import reduce

import spot

from ggsolver.automata import DFA
from ggsolver.models import Automaton

import ggsolver.interfaces.i_spot as i_spot
from ggsolver.automata import DFA
from ggsolver.graph import *
from ggsolver.logic.formula import BaseFormula, ParsingError, PARSERS_DIR
from ggsolver.logic.ltl import LTL, ScLTL
from lark import Lark, Transformer, Tree, Visitor
from pathlib import Path

from ggsolver.models import Automaton


class PrefLTL(BaseFormula):
    """
    PrefLTL formula is internally represented as a PrefModel instance.
    """
    def __init__(self, f_str, atoms=None, null_assumption=True):
        super(PrefLTL, self).__init__(f_str, atoms)

        # Parse input string
        parser = LTLPrefParser()
        self.tree = parser.parse(self.f_str)

        # Build preference model
        atoms = set() if atoms is None else set(atoms)
        self._repr = Formula2Model(self.tree, atoms, null_assumption).model

        # Construct atoms and outcomes
        #   Ensure all LTL formulas share same set of atoms.
        self._atoms = self._repr.atoms()
        self._outcomes = self._repr.outcomes()

    def __str__(self):
        return str(self.f_str)

    # ==================================================================
    # IMPLEMENTATION OF ABSTRACT METHODS
    # ==================================================================
    def translate(self):
        automata = []
        # Note: We do not use alpha0 for DFA construction.
        for i in range(1, len(self._outcomes)):
            dfa = DFA()
            dfa.from_automaton(aut=self._outcomes[i].translate())
            automata.append(dfa)

        return DFPA(automata=automata, pref_model=self._repr)

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


class PrefScLTL(PrefLTL):
    """
    PrefLTL formula is internally represented as a PrefModel instance.
    """
    def __init__(self, f_str, atoms=None, null_assumption=True):
        super(PrefScLTL, self).__init__(f_str, atoms, null_assumption)
        assert all(ScLTL(f.f_str) for f in self._outcomes[1:])

    def __str__(self):
        return str(self.f_str)

    # ==================================================================
    # IMPLEMENTATION OF ABSTRACT METHODS
    # ==================================================================
    def translate(self):
        automata = []
        # Note: We do not use alpha0 for DFA construction.
        for i in range(1, len(self._outcomes)):
            dfa = DFA()
            dfa.from_automaton(aut=self._outcomes[i].translate())
            automata.append(dfa)

        return DFPA(automata=automata, pref_model=self._repr)

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


class PrefModel:
    def __init__(self, outcomes, atoms, relation, null_assumption=True):
        # Instance variables
        self._atoms = set(atoms)            # set of atoms
        self._outcomes = list(outcomes)     # list to have indexing.

        # Complete outcomes
        self._complete_outcomes()

        # Cache for speedup
        self._outcomes2index = {
            outcome: self._outcomes.index(outcome)
            for outcome in self._outcomes
        }

        # Define relations (we will store index pairs for compactness)
        self._relation = {
            (self._outcomes2index[out1], self._outcomes2index[out2])
            for out1, out2 in relation
        }

        # Impose null assumption
        if null_assumption:
            self._null_assumption()

        # Make relation reflexive
        self.make_reflexive()

        # Apply transitive closure
        self.transitive_closure()

    # ============================================================================
    # GRAPHICAL MODEL
    # ============================================================================
    def graphify(self):
        """
        Preference model is not a GraphicalModel. So, it has different properties than a GraphicalModel.

        :param base_only:
        :return:
        """
        # Initialize graph object
        graph = Graph()

        # Set graph properties
        graph["atoms"] = self._atoms
        graph["outcomes"] = [str(outcome) for outcome in self._outcomes]

        # Node property
        np_state = NodePropertyMap(graph)

        # Add nodes
        node_ids = graph.add_nodes(len(self._outcomes))

        # Cache states as a dictionary {state: uid}
        states2id = dict(zip(self._outcomes, node_ids))

        # Update state property
        for outcome in self._outcomes:
            np_state[states2id[outcome]] = outcome
        graph["state"] = np_state

        # Add edges
        for out1, out2 in self._relation:
            uid = states2id[self._outcomes[out1]]
            vid = states2id[self._outcomes[out2]]
            graph.add_edge(vid, uid)

        # Return graph
        return graph

    # ============================================================================
    # PREFERENCE DETERMINATION
    # ============================================================================
    def is_weakly_preferred(self, idx1, idx2):
        return (idx1, idx2) in self._relation

    def is_strictly_preferred(self, idx1, idx2):
        return (idx1, idx2) in self._relation and (idx2, idx1) not in self._relation

    def is_indifferent(self, idx1, idx2):
        return (idx1, idx2) in self._relation and (idx2, idx1) in self._relation

    def is_incomparable(self, idx1, idx2):
        return (idx1, idx2) not in self._relation and (idx2, idx1) not in self._relation

    # ============================================================================
    # PROPERTIES AND HELPER FUNCTIONS
    # ============================================================================
    def atoms(self):
        return self._atoms

    def outcomes(self):
        return self._outcomes

    def relation(self):
        return self._relation

    def index2outcome(self, idx):
        return self._outcomes[idx]

    def outcome2index(self, outcome):
        return self._outcomes2index[outcome]

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================
    def _complete_outcomes(self):
        alpha0_str = " & ".join([f"(!{str(f)})" for f in self._outcomes])
        alpha0 = LTL(f_str=alpha0_str)
        self._outcomes.insert(0, alpha0)

    def _null_assumption(self):
        for outcome_idx in range(1, len(self._outcomes)):
            self._relation.add((outcome_idx, 0))

    def transitive_closure(self):
        model = set(self._relation)
        while True:
            new_relations = set((x, w) for x, y in model for z, w in model if z == y)
            # print(f"new_relations={[str(x), str(y) for x, y in new_relations]}")
            # print(f"{new_relations=}")
            closure_until_now = model | new_relations
            if closure_until_now == model:
                break
            model = closure_until_now
        self._relation |= model

    def make_reflexive(self):
        for i in range(len(self._outcomes)):
            self._relation.add((i, i))


class Formula2Model(Transformer):
    """
    Transforms a preference formula to a preference model :math:`(U, \succeq)`.

    .. warn:: Generated model does not support ORing of preference formulas.
    """
    def __init__(self, tree, atoms, null_assumption):
        super(Formula2Model, self).__init__()

        # Instance variables
        self.tree = tree
        self.null_assumption = null_assumption
        self.outcomes = set()
        self.atoms = set(atoms)

        # Build preference model
        self.model = self.transform(self.tree)

    # ============================================================================
    # LARK TRANSFORMER FUNCTIONS
    # ============================================================================
    def start(self, args):
        return PrefModel(outcomes=self.outcomes, atoms=self.atoms, relation=args[0],
                         null_assumption=self.null_assumption)

    def pref_and(self, args):
        return set.union(*args[::2])

    def pref_or(self, args):
        # TODO. See following tip.
        # Tip. When preference formula is in DNF (disjunctive normal form),
        #   a preference model of a formula containing OR will be a list of
        #   AND-constrained PrefModels.
        # This will require proving that DNF exists for arbitrary preference formula.
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


# class PrefModel2(Transformer):
#     def __init__(self, tree):
#         super(PrefModel, self).__init__()
#
#         # Instance variables
#         self.tree = tree
#         self.outcomes = set()
#         self.atoms = set()
#
#         # Build preference model
#         #  FIXME Typically, a model is list of sets (due to ORing).
#         self.model = self.transform(self.tree)
#
#         # Define all outcomes over same set of atoms.
#         for outcome in self.outcomes:
#             outcome.update_atoms(self.atoms)
#
#         # Fix indices of outcomes
#         self.outcomes = list(self.outcomes)
#
#         # Complete preference model. (add alpha0)
#         self._complete_outcomes()
#         print(self.outcomes)
#
#         # Force all outcomes to be preferred to alpha0.
#         self._assumption1()
#
#         # Make reflexive.
#         self.make_reflexive()
#
#         # Transitive closure.
#         self.transitive_closure()
#
#     # ============================================================================
#     # HELPER FUNCTIONS
#     # ============================================================================
#     def _complete_outcomes(self):
#         alpha0_str = " & ".join([f"(!{str(f)})" for f in self.outcomes])
#         alpha0 = LTL(f_str=alpha0_str)
#         self.outcomes.insert(0, alpha0)
#
#     def _assumption1(self):
#         for model_idx in range(len(self.model)):
#             for outcome_idx in range(1, len(self.outcomes)):
#                 self.model[model_idx].add((self.outcomes[outcome_idx], self.outcomes[0]))
#
#     def transitive_closure(self):
#         for model_idx in range(len(self.model)):
#             model = self.model[model_idx]
#             while True:
#                 new_relations = set((x, w) for x, y in model for z, w in model if z == y)
#                 # print(f"new_relations={[str(x), str(y) for x, y in new_relations]}")
#                 print(f"{new_relations=}")
#                 closure_until_now = model | new_relations
#                 if closure_until_now == model:
#                     break
#                 model = closure_until_now
#             self.model[model_idx] |= model
#
#     def make_reflexive(self):
#         for model_idx in range(len(self.model)):
#             for outcome in self.outcomes:
#                 self.model[model_idx].add((outcome, outcome))
#
#     # ============================================================================
#     # VISUALIZATIONS
#     # ============================================================================
#     def graphify(self):
#         """
#         Preference model is not a GraphicalModel. So, it has different properties than a GraphicalModel.
#
#         :param base_only:
#         :return:
#         """
#         # Initialize graph object
#         graph = Graph()
#
#         # Set graph properties
#         graph["atoms"] = self.atoms
#         graph["outcomes"] = [str(outcome) for outcome in self.outcomes]
#
#         # Node property
#         np_state = NodePropertyMap(graph)
#
#         # Add nodes
#         node_ids = graph.add_nodes(len(self.outcomes))
#
#         # Cache states as a dictionary {state: uid}
#         states2id = dict(zip(self.outcomes, node_ids))
#
#         # Update state property
#         for outcome in self.outcomes:
#             np_state[states2id[outcome]] = outcome
#         graph["state"] = np_state
#
#         # Add edges
#         # PATCH (Temp. Remove this on 19 Oct 22)
#         for out1, out2 in self.model[0]:
#             uid = states2id[out2]
#             vid = states2id[out1]
#             graph.add_edge(uid, vid)
#
#         # Return graph
#         return graph
#
#     # ============================================================================
#     # USER FUNCTIONS
#     # ============================================================================
#     def is_preferred(self, idx1, idx2):
#         # PATCH: Assumed AND-fragment. Hence, only 0th model is available.
#         return (idx1, idx2) in self.model[0]
#
#     def is_indifferent(self, idx1, idx2):
#         # PATCH: Assumed AND-fragment. Hence, only 0th model is available.
#         return (idx1, idx2) in self.model[0] and (idx2, idx1) in self.model[0]
#
#     def is_incomparable(self, idx1, idx2):
#         # PATCH: Assumed AND-fragment. Hence, only 0th model is available.
#         return (idx1, idx2) not in self.model[0] and (idx2, idx1) not in self.model[0]
#
#     # ============================================================================
#     # LARK TRANSFORMER FUNCTIONS
#     # ============================================================================
#     def start(self, args):
#         if type(args[0]) == set:
#             return [args[0]]
#         return args[0]
#
#     def pref_and(self, args):
#         return set.union(*args[::2])
#
#     def pref_or(self, args):
#         # Tip. When preference formula is in DNF (disjunctive normal form),
#         #   a preference model of a formula containing OR will be a list of
#         #   AND-constrained PrefModels.
#         # This will require proving that DNF exists for arbitrary preference formula.
#         raise NotImplementedError("Currently, ORing of preference formulas is not supported.")
#
#     def prefltl_weakpref(self, args):
#         return {(args[0], args[2])}
#
#     def prefltl_strictpref(self, args):
#         return {(args[0], args[2])}
#
#     def prefltl_indifference(self, args):
#         return {(args[0], args[2]), (args[2], args[0])}
#
#     def prefltl_incomparable(self, args):
#         return set()
#
#     def ltl_formula(self, args):
#         f = LTL(args[0])
#         self.outcomes.add(f)
#         self.atoms.update(set(f.atoms()))
#         return f


class DFPA(Automaton):
    def __init__(self, automata, pref_model):
        super(DFPA, self).__init__(acc_cond=Automaton.ACC_PREF_MP)
        assert all(isinstance(aut, DFA) for aut in automata)
        self._automata = automata
        self._pref_model = pref_model
        self._pref_graph = None

    # =========================================================================
    # IMPLEMENTATION OF ABSTRACT METHODS
    # =========================================================================
    def states(self):
        return list(itertools.product(*[aut.states() for aut in self._automata]))

    def atoms(self):
        return reduce(set.union, [set(aut.atoms()) for aut in self._automata])

    def init_state(self):
        return tuple(aut.init_state() for aut in self._automata)

    def delta(self, state, inp):
        return tuple(self._automata[idx].delta(state[idx], inp) for idx in range(len(self._automata)))

    def final(self, state):
        """
        Returns the acceptance set to which the state belongs to.
        """
        # TODO. Depends on Preference graph construction.
        pass

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================
    def pref_graph(self, cache=False):
        pref_graph = Graph()

        # Construct set of unique maximal elements.
        #   Use tuple of sorted lists to avoid duplicates. Lists needed to avoid unhashable error.
        nodes = dict()
        for q in self.states():
            maximal_q = tuple(sorted(list(self.maximal(q))))
            print(f"{q=}, {maximal_q=}, {self.outcomes(q)=}")
            if maximal_q in nodes:
                nodes[maximal_q].add(q)
            else:
                nodes[maximal_q] = {q}
        node_ids = pref_graph.add_nodes(len(nodes))

        np_state = pref_graph["state"] = NodePropertyMap(pref_graph)
        np_state.update(dict(zip(node_ids, nodes.keys())))

        partition = pref_graph["partition"] = NodePropertyMap(pref_graph)
        for i in range(len(nodes)):
            partition[i] = nodes[np_state[i]]

        if cache:
            self._pref_graph = pref_graph

        return pref_graph

    def outcomes(self, state):
        out = set()
        for i in range(len(state)):
            if 0 in self._automata[i].final(state[i]):
                out.add(i+1)

        if len(out) == 0:
            out.add(0)

        return {self._pref_model.outcomes[i] for i in out}

    def maximal(self, state):
        outcomes = self.outcomes(state)
        remove = {i for i in outcomes if any(self._pref_model.is_preferred(j+1, i+1) for j in outcomes - {i})}
        return outcomes - remove


if __name__ == '__main__':
    # parser_ = LTLPrefParser()
    # formula_ = PrefScLTL("Fa > Gb && Fb > Ga && Fb > Fa", atoms={"c"})
    # print([(str(f), f.atoms()) for f in formula_.outcomes()])
    # print(formula_.atoms())
    #
    # print()
    # from pprint import pprint
    # outcomes = formula_._repr.outcomes
    # pprint([(outcomes.index(x), outcomes.index(y)) for x, y in formula_._repr.model[0]])
    # pprint([(str(x), str(y)) for x, y in formula_._repr.model[0]])
    #
    # graph = formula_._repr.graphify()
    # graph.to_png("pref.png", nlabel=["state"])

    formula_ = PrefScLTL("(a U b) > Fb")
    model_ = formula_.model()
    graph_ = model_.graphify()
    graph_.to_png("graph.png", nlabel=["state"])

    # dfpa = formula_.translate()
    # print(f"{dfpa.states()=}")
    # print(f"{dfpa.atoms()=}")
    # print(f"{dfpa.init_state()=}")
    # print(f"{dfpa.delta((1, 1), {'a'})=}")
    # print(f"{dfpa.delta((1, 1), {'b'})=}")
    # pref_graph = dfpa.pref_graph()
    # pref_graph.to_png("pref_graph.png", nlabel=["state"])
    # print(f"{dfpa.pref_graph()=}")
    # TODO. Try nested ANDing with parenthesis.