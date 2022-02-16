"""
Parser for Syntactically Co-safe Linear Temporal Logic (ScLTL).

Reference:
    1. O. Kupferman and M. Y. Vardi, "Model checking of safety properties",
        Formal Methods System Design, vol. 19, no. 3, pp. 291-314, Oct. 2001.
    2. Belta C, Yordanov B, Gol EA. Formal methods for discrete-time dynamical systems.
        Cham: Springer International Publishing; 2017 Jan 1.
"""

import logging
import networkx as nx

from pathlib import Path
from lark import Lark, Transformer, Visitor
from lark.exceptions import UnexpectedCharacters, UnexpectedToken, UnexpectedInput, UnexpectedEOF
from ggsolver.logic.formula import BaseFormula, ParsingError, PARSERS_DIR
from ggsolver.logic.pl import PLFormula
from ggsolver.logic.automata import Dfa
from ggsolver.logic.utils import powerset

try:
    import spot
except ImportError:
    import_err = "spot library not available. ScLTL formula creation, manipulation depends on spot library."
    logging.error(import_err)
    raise ImportError(import_err)


class ScLTLParser:
    """ ScLTL Parser class. """

    def __init__(self):
        """Initialize."""
        self._parser = Lark(open(str(Path(PARSERS_DIR, "scltl.lark"))), parser="lalr")

    def __call__(self, text):
        """Call."""
        parse_tree = self._parser.parse(text)
        return parse_tree


class ScLTLSubstitutor(Transformer):

    def __init__(self):
        super(ScLTLSubstitutor, self).__init__()
        self.eval_map = None

    def __call__(self, tree, eval_map):
        return self.substitute(tree, eval_map)

    def substitute(self, tree, eval_map):
        self.eval_map = eval_map
        return super(ScLTLSubstitutor, self).transform(tree)

    # noinspection PyMethodMayBeStatic
    def start(self, args):
        """Entry point."""
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def scltl_formula(self, args):
        """Parse ScLTL formula."""
        assert len(args) == 1
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def scltl_equivalence(self, args):
        """Parse ScLTL Equivalence."""
        if len(args) == 1:
            return str(str(args[0]))
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") <-> (".join(sub_formulas) + ")"
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_implication(self, args):
        """Parse ScLTL Implication."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") -> (".join(sub_formulas) + ")"
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_or(self, args):
        """Parse ScLTL Or."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") | (".join(sub_formulas) + ")"
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_and(self, args):
        """Parse ScLTL And."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") & (".join(sub_formulas) + ")"
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_until(self, args):
        """Parse ScLTL Until."""
        if len(args) == 1:
            return str(args[0])
        elif (len(args) - 1) % 2 == 0:
            sub_formulas = [str(f) for f in args[::2]]
            return "(" + ") U (".join(sub_formulas) + ")"
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_always(self, args):
        """Parse ScLTL Always."""
        if len(args) == 1:
            return str(args[0])
        else:
            f = str(args[-1])
            for _ in args[:-1]:
                f = f"G({f})"
            return f

    # noinspection PyMethodMayBeStatic
    def scltl_eventually(self, args):
        """Parse ScLTL Eventually."""
        if len(args) == 1:
            return str(args[0])
        else:
            f = str(args[-1])
            for _ in args[:-1]:
                f = f"F({f})"
            return f

    # noinspection PyMethodMayBeStatic
    def scltl_next(self, args):
        """Parse ScLTL Next."""
        if len(args) == 1:
            return str(args[0])
        else:
            f = str(args[-1])
            for _ in args[:-1]:
                f = f"X({f})"
            return f

    # noinspection PyMethodMayBeStatic
    def scltl_not(self, args):
        """Parse ScLTL Not."""
        if len(args) == 1:
            return str(args[0])
        else:
            f = str(args[-1])
            for _ in args[:-1]:
                f = f"!({f})"
            return f

    # noinspection PyMethodMayBeStatic
    def scltl_wrapped(self, args):
        """Parse ScLTL wrapped formula."""
        if len(args) == 1:
            return str(args[0])
        elif len(args) == 3:
            _, formula, _ = args
            return str(formula)
        else:
            msg = f"ScLTL Substitution failed. args:{args}"
            logging.error(msg)
            raise ParsingError(msg)

    # noinspection PyMethodMayBeStatic
    def scltl_atom(self, args):
        """Parse ScLTL Atom."""
        assert len(args) == 1
        return str(args[0])

    # noinspection PyMethodMayBeStatic
    def scltl_symbol(self, args):
        """Parse ScLTL Symbol."""
        assert len(args) == 1
        token = str(args[0])
        try:
            print(str(self.eval_map[token]))
            return str(self.eval_map[token])
        except KeyError:
            return token

    # noinspection PyMethodMayBeStatic
    def scltl_true(self, args):
        """Parse Propositional True."""
        assert len(args) == 1
        return "true"

    # noinspection PyMethodMayBeStatic
    def scltl_false(self, args):
        """Parse Propositional False."""
        assert len(args) == 1
        return "false"


class ScLTLEvaluator(Transformer):
    def __call__(self, tree, f_str, eval_map):
        return self.evaluate(tree, f_str, eval_map)

    # noinspection PyMethodMayBeStatic
    def evaluate(self, tree, f_str, eval_map):
        if str(spot.mp_class(f_str)).lower() in ["b", "g"]:
            val = SUBSTITUTE_ScLTL(tree, eval_map)
            f = spot.formula(val)
            if f.is_tt():
                return True
            elif f.is_ff():
                return False

        msg = f"ScLTL Evaluation failed. Inputs: f_str: {f_str}, args: {eval_map}"
        logging.error(msg)
        raise ParsingError(msg + f"Did you forget to substitute all atoms?")


class ScLTLAtomGlobber(Visitor):
    def __init__(self):
        self._alphabet = set()

    def __call__(self, tree):
        self._alphabet = set()
        super(ScLTLAtomGlobber, self).visit(tree)
        return self._alphabet

    def add_alphabet(self, sym):
        self._alphabet.add(sym)

    def scltl_symbol(self, args):
        """ Glob Atom."""
        self.add_alphabet(args.children[0].value)


class ScLTLToStringVisitor(Visitor):
    def __init__(self):
        self.f_str = ""

    def __call__(self, tree):
        self.f_str = ""
        self.visit(tree)
        return self.f_str

    def scltl_equivalence(self, tree):
        """Parse ScLTL Equivalence."""
        left_visitor = ScLTLToStringVisitor()
        right_visitor = ScLTLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) <-> ({right_visitor.f_str})"
        return tree.children[1]

    def scltl_implication(self, tree):
        left_visitor = ScLTLToStringVisitor()
        right_visitor = ScLTLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) -> ({right_visitor.f_str})"
        return tree.children[1]

    def scltl_or(self, tree):
        left_visitor = ScLTLToStringVisitor()
        right_visitor = ScLTLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) | ({right_visitor.f_str})"
        return tree.children[1]

    def scltl_and(self, tree):
        left_visitor = ScLTLToStringVisitor()
        right_visitor = ScLTLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) & ({right_visitor.f_str})"
        return tree.children[1]

    def scltl_until(self, tree):
        left_visitor = ScLTLToStringVisitor()
        right_visitor = ScLTLToStringVisitor()
        left_visitor.visit(tree.children[0])
        right_visitor.visit(tree.children[2])
        self.f_str = f"({left_visitor.f_str}) U ({right_visitor.f_str})"
        return tree.children[1]

    def scltl_always(self, tree):
        self.f_str = f"G({self.f_str})"
        return tree.children[0]

    def scltl_eventually(self, tree):
        self.f_str = f"F({self.f_str})"
        return tree.children[0]

    def scltl_next(self, tree):
        self.f_str = f"X({self.f_str})"
        return tree.children[0]

    def scltl_not(self, tree):
        self.f_str = f"!({self.f_str})"
        return tree.children[0]

    def scltl_atom(self, tree):
        self.f_str += str(tree.children[0])
        return tree.children[0]

    def scltl_symbol(self, tree):
        self.f_str += str(tree.children[0])
        return tree.children[0]

    def scltl_true(self, tree):
        self.f_str += "true"
        return tree.children[0]

    def scltl_false(self, tree):
        self.f_str += "false"
        return tree.children[0]


PARSE_ScLTL = ScLTLParser()
SUBSTITUTE_ScLTL = ScLTLSubstitutor()
EVALUATE_ScLTL = ScLTLEvaluator()
ATOMGLOB_ScLTL = ScLTLAtomGlobber()
TOSTRING_ScLTL = ScLTLToStringVisitor()


class ScLTLFormula(BaseFormula):
    def __init__(self, f_str, alphabet=None):
        super(ScLTLFormula, self).__init__(f_str, alphabet)
        try:
            self.parse_tree = PARSE_ScLTL(f_str)
        except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput, UnexpectedEOF) as err:
            msg = f"Given formula {f_str} is not a valid ScLTL formula.\n{err}"
            logging.error(msg)
            raise ParsingError(msg)

    def __hash__(self):
        return hash(str(spot.formula(self.f_str)))

    def __eq__(self, other):
        if isinstance(other, BaseFormula):
            return spot.formula(self.f_str) == spot.formula(other.f_str)
        elif isinstance(other, str):
            return spot.formula(self.f_str) == spot.formula(other)
        raise AssertionError(f"PLFormula.__eq__: type(other)={type(other)}.")

    def __str__(self):
        return TOSTRING_ScLTL(self.parse_tree)
        # return str(spot.formula(self.f_str))

    def translate(self):
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
                graph.add_edge(int(edge.src), int(edge.dst), symbol=f_lbl)
                # for sigma in powerset(self.alphabet):
                #     eval_map = {sym: True for sym in self.alphabet if sym in sigma}
                #     eval_map.update({sym: False for sym in self.alphabet if sym not in sigma})
                #     if f_lbl.evaluate(eval_map):
                #         graph.add_edge(int(edge.src), int(edge.dst), symbol=sigma)

                # Final state is the source of accepting edge.
                #   See: `G(p1 | p2 | F!p0)` in spot app by toggling `force transition-based` option.
                #   Observe edge from 0 -> 1.
                if edge.acc.count() > 0:
                    final.add(int(edge.src))

        dfa = Dfa(name=self.f_str)
        dfa.construct_explicit(graph=graph, init_st=init_st, final=final)
        return dfa

    def mp_class(self, verbose=False):
        return spot.mp_class(spot.formula(self.f_str), "v" if verbose else "")

    def substitute(self, subs_map=None):
        if subs_map is None:
            subs_map = dict()

        subs_str = SUBSTITUTE_ScLTL(self.parse_tree, subs_map)
        return ScLTLFormula(subs_str)

    def evaluate(self, eval_map=None):
        if eval_map is None:
            eval_map = dict()
        return EVALUATE_ScLTL(self.parse_tree, self.f_str, eval_map)

    @property
    def alphabet(self):
        if self._alphabet is not None:
            return self._alphabet

        return ATOMGLOB_ScLTL(self.parse_tree)
