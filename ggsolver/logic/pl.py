"""
Parser for Propositional Logic.

Reference: ltlf2dfa (https://github.com/whitemech/LTLf2DFA)
Note. The logic definitions used here may differ from LTLf2DFA library.
"""

import logging
import networkx as nx
from pathlib import Path
from lark import Lark, Transformer, Visitor
from lark.exceptions import UnexpectedCharacters, UnexpectedToken, UnexpectedInput, UnexpectedEOF
from ggsolver.logic.formula import BaseFormula, ParsingError, PARSERS_DIR
from ggsolver.logic.automata import Dfa
from ggsolver.logic.utils import powerset

try:
    import spot
except ImportError:
    logging.warning(f"Spot could not be imported. Some operations on PL formulas may not work.")
    spot = None


class PLParser:
    """
    Parser for Propositional Logic formula.
    """

    def __init__(self):
        """Initialize."""
        self._parser = Lark(open(str(Path(PARSERS_DIR, "pl.lark"))), parser="lalr")

    def __call__(self, text):
        """ Parse the given text. """
        parse_tree = self._parser.parse(text)
        return parse_tree


class PLSubstitutor(Transformer):
    """PL Transformer."""

    def __init__(self):
        super(PLSubstitutor, self).__init__()
        self.eval_map = None

    def __call__(self, tree, eval_map):
        return self.substitute(tree, eval_map)

    def substitute(self, tree, eval_map):
        self.eval_map = eval_map
        return super(PLSubstitutor, self).transform(tree)

    # noinspection PyMethodMayBeStatic
    def start(self, args):
        """Entry point."""
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def pl_formula(self, args):
        """Parse Propositional formula."""
        assert len(args) == 1
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def pl_equivalence(self, args):
        """Parse Propositional Equivalence."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") <-> (".join(sub_formulas) + ")"
        else:
            msg = f"PL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def pl_implication(self, args):
        """Parse Propositional Implication."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") -> (".join(sub_formulas) + ")"
        else:
            msg = f"PL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def pl_or(self, args):
        """Parse Propositional Or."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") | (".join(sub_formulas) + ")"
        else:
            msg = f"PL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def pl_and(self, args):
        """Parse Propositional And."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") & (".join(sub_formulas) + ")"
        else:
            msg = f"PL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def pl_not(self, args):
        """Parse Propositional Not."""
        if len(args) == 1:
            return str(args[0])
        else:
            f = str(args[-1])
            for _ in args[:-1]:
                f = f"!({f})"
            return f

    # noinspection PyMethodMayBeStatic
    def pl_wrapped(self, args):
        """Parse Propositional wrapped formula."""
        if len(args) == 1:
            return str(args[0])
        elif len(args) == 3:
            _, f, _ = args
            return str(f)
        else:
            msg = f"PL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def pl_atom(self, args):
        """Parse Propositional Atom."""
        assert len(args) == 1
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def pl_true(self, args):
        """Parse Propositional True."""
        assert len(args) == 1
        return "true"

    # noinspection PyMethodMayBeStatic
    def pl_false(self, args):
        """Parse Propositional False."""
        assert len(args) == 1
        return "false"

    def atom(self, args):
        """Parse Atom."""
        assert len(args) == 1
        try:
            return str(self.eval_map[args[0]])
        except KeyError:
            return args[0]


class PLEvaluator(Transformer):
    """PL Transformer."""
    def __call__(self, tree, f_str, eval_map):
        return self.evaluate(tree, f_str, eval_map)

    # noinspection PyMethodMayBeStatic
    def evaluate(self, tree, f_str, eval_map):
        if str(spot.mp_class(f_str)).lower() in ["b", "bottom"]:
            val = SUBSTITUTE_PL(tree, eval_map)
            f = spot.formula(val)
            if f.is_tt():
                return True
            elif f.is_ff():
                return False

        msg = f"PL Evaluation failed. Input: f_str:{f_str}, eval_map:{eval_map}."
        logging.error(msg)
        raise ParsingError(msg + f"Did you forget to substitute all atoms?")


class PLAtomGlobber(Visitor):
    def __init__(self):
        self._alphabet = set()

    def __call__(self, tree):
        self._alphabet = set()
        super(PLAtomGlobber, self).visit(tree)
        return self._alphabet

    def add_alphabet(self, sym):
        self._alphabet.add(sym)

    def atom(self, args):
        """ Glob Atom."""
        self.add_alphabet(args.children[0].value)


class PLToStringVisitor(Visitor):
    def __init__(self):
        self.f_str = ""

    def __call__(self, tree):
        self.f_str = ""
        self.visit(tree)
        return self.f_str

    def pl_equivalence(self, tree):
        left_visitor = PLToStringVisitor()
        right_visitor = PLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) <-> ({right_visitor.f_str})"
        return tree.children[1]

    def pl_implication(self, tree):
        left_visitor = PLToStringVisitor()
        right_visitor = PLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) -> ({right_visitor.f_str})"
        return tree.children[1]

    def pl_or(self, tree):
        left_visitor = PLToStringVisitor()
        right_visitor = PLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) | ({right_visitor.f_str})"
        return tree.children[1]

    def pl_and(self, tree):
        left_visitor = PLToStringVisitor()
        right_visitor = PLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) & ({right_visitor.f_str})"
        return tree.children[1]

    def pl_not(self, tree):
        self.f_str = f"!({self.f_str})"
        return tree.children[0]

    def pl_wrapped(self, tree):
        self.f_str = f"({self.f_str})"
        return tree.children[1]

    def pl_atom(self, tree):
        self.f_str += str(tree.children[0])
        return tree.children[0]

    def pl_true(self, tree):
        """Parse Propositional True."""
        self.f_str = "true"
        return tree.children[0]

    def pl_false(self, tree):
        """Parse Propositional False."""
        self.f_str = "false"
        return tree.children[0]


PARSE_PL = PLParser()
SUBSTITUTE_PL = PLSubstitutor()
EVALUATE_PL = PLEvaluator()
ATOMGLOB_PL = PLAtomGlobber()
TOSTRING_PL = PLToStringVisitor()


class PLFormula(BaseFormula):
    """
    Represents a propositional logic formula.

    Internally, `spot` module is used to translate the PL formula to automaton.
    """
    def __init__(self, f_str, alphabet=None):
        super(PLFormula, self).__init__(f_str, alphabet)
        try:
            self.parse_tree = PARSE_PL(f_str)
        except UnexpectedCharacters or UnexpectedToken or UnexpectedInput or UnexpectedEOF as err:
            msg = f"Given formula {f_str} is not a valid PL formula.\n{err}"
            logging.error(msg)
            raise ParsingError(msg)

    def __hash__(self):
        return hash(str(spot.formula(self.f_str)))

    def __eq__(self, other):
        if spot is None:
            msg = f"PL.equality_check() requires spot, which is not available."
            logging.error(msg)
            ImportError(msg)

        if isinstance(other, BaseFormula):
            return spot.formula(self.f_str) == spot.formula(other.f_str)
        elif isinstance(other, str):
            return spot.formula(self.f_str) == spot.formula(other)

        msg = f"PL equality check failed. Inputs: type(other)={type(other)}."
        logging.error(msg)
        raise AssertionError(msg)

    def translate(self):
        """
        Constructs a DFA accepting language defined by PL formula.
        :return: Dfa object.
        """
        if spot is None:
            msg = f"PL.translate() requires spot, which is not available."
            logging.error(msg)
            ImportError(msg)

        # Generate spot automaton
        aut = spot.translate(self.f_str, "BA", "High", "SBAcc", "Complete")
        bdd_dict = aut.get_dict()

        # Convert spot automaton to Dfa object
        #   We will use explicit construction: define a graph and use it to construct Dfa object.
        graph = nx.MultiDiGraph()
        init_st = int(aut.get_init_state_number())
        final = set()
        for src in range(0, aut.num_states()):
            graph.add_node(int(src))
            for edge in aut.out(src):
                f_lbl_str = str(spot.bdd_format_formula(bdd_dict, edge.cond))
                if f_lbl_str == '1':
                    f_lbl_str = "true"
                elif f_lbl_str == '0':
                    f_lbl_str = "false"
                f_lbl = PLFormula(f_lbl_str)
                for sigma in powerset(self.alphabet):
                    eval_map = {sym: True for sym in self.alphabet if sym in sigma}
                    eval_map.update({sym: False for sym in self.alphabet if sym not in sigma})
                    if f_lbl.evaluate(eval_map):
                        graph.add_edge(int(edge.src), int(edge.dst), symbol=sigma)

                # Final state is the source of accepting edge.
                #   See: `G(p1 | p2 | F!p0)` in spot app by toggling `force transition-based` option.
                #   Observe edge from 0 -> 1.
                if edge.acc.count() > 0:
                    final.add(int(edge.src))

        dfa = Dfa(name=f"{self.f_str}")
        dfa.construct_explicit(graph=graph, init_st=init_st, final=final)
        return dfa

    def mp_class(self, verbose=False):
        if spot is None:
            msg = f"PL.mp_class() requires spot, which is not available."
            logging.error(msg)
            ImportError(msg)

        return spot.mp_class(spot.formula(self.f_str), "v" if verbose else "")

    def substitute(self, subs_map):
        return PLFormula(SUBSTITUTE_PL(self.parse_tree, subs_map))

    def evaluate(self, eval_map):
        if spot is None:
            msg = f"PL.evaluate() requires spot, which is not available."
            logging.error(msg)
            ImportError(msg)

        return EVALUATE_PL(self.parse_tree, self.f_str, eval_map)

    @property
    def alphabet(self):
        if self._alphabet is not None:
            return self._alphabet

        return ATOMGLOB_PL(self.parse_tree)
