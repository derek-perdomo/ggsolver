"""
Defines an interface from spot automaton to ggsolver automaton.
"""

import spot
from ggsolver.models import Automaton, register_property
from ggsolver.util import powerset
from dd.autoref import BDD


class SpotAutomaton(Automaton):
    """
    `SpotAutomaton` constructs an :class:`Automaton` from an LTL specification string using
    `spot` (https://spot.lrde.epita.fr/) with customizations for `ggsolver`.

    **Customizations:** Since `ggsolver` contains several algorithms for reactive/controller synthesis,
        we prefer to construct deterministic automata. Given an LTL formula, `SpotAutomaton` automatically
        determines the best acceptance condition that would result in a deterministic automaton.

    **Default translation options:** While constructing an automaton using `spot`, we use the following
        options: `deterministic, high, complete, unambiguous, SBAcc`. If selected acceptance condition
        is parity, then we use `colored` option as well.

    The default options can be overriden. For quick reference, the following description is copied from
    `spot` documentation (spot.lrde.epita.fr/doxygen).

    The optional arguments should be strings among the following:
    - at most one in 'GeneralizedBuchi', 'Buchi', or 'Monitor',
      'generic', 'parity', 'parity min odd', 'parity min even',
      'parity max odd', 'parity max even', 'coBuchi'
      (type of acceptance condition to build)
    - at most one in 'Small', 'Deterministic', 'Any'
      (preferred characteristics of the produced automaton)
    - at most one in 'Low', 'Medium', 'High'
      (optimization level)
    - any combination of 'Complete', 'Unambiguous',
      'StateBasedAcceptance' (or 'SBAcc' for short), and
      'Colored' (only for parity acceptance)

    Programmer's note: The graphified version of automaton does not use PL formulas as edge labels.
        This is intentionally done to be able to run our codes on robots that may not have logic libraries installed.
    """
    def __init__(self, formula=None, options=None):
        # Construct the automaton
        super(SpotAutomaton, self).__init__(input_domain=self.sigma)

        # Instance variables
        self._formula = formula

        # If options are not given, determine the set of options to generate deterministic automaton with
        # state-based acceptance condition.
        if options is None:
            options = self._determine_options()

        print(f"[INFO] Translating {self._formula} with options={options}.")
        self.spot_aut = spot.translate(formula, *options)

        # Set the acceptance condition (in ggsolver terms)
        name = self.spot_aut.acc().name()
        if name == "Büchi" and spot.mp_class(formula).upper() in ["B", "S"]:
            self._acc_cond = Automaton.ACC_SAFETY
        elif name == "Büchi" and spot.mp_class(formula).upper() in ["G"]:
            self._acc_cond = Automaton.ACC_REACH
        elif name == "Büchi" and spot.mp_class(formula).upper() in ["O", "R"]:
            self._acc_cond = Automaton.ACC_REACH
        elif name == "co-Büchi":
            self._acc_cond = Automaton.ACC_COBUCHI
        elif name == "all":
            self._acc_cond = Automaton.ACC_SAFETY
        else:  # name contains "parity":
            self._acc_cond = Automaton.ACC_PARITY

    def sigma(self):
        if len(self.atoms()) > 16:
            raise ValueError("To many atoms. Currently support up to 16 atoms.")
        return list(powerset(self.atoms()))

    def _determine_options(self):
        mp_cls = spot.mp_class(self.formula())
        if mp_cls.upper() == "B" or mp_cls.upper() == "S":
            return 'Monitor', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        elif mp_cls.upper() == "G" or mp_cls.upper() == "O" or mp_cls.upper() == "R":
            return 'Buchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        elif mp_cls.upper() == "P":
            return 'coBuchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        else:  # cls.upper() == "T":
            return 'parity', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc", "colored"

    def states(self):
        return list(range(self.spot_aut.num_states()))

    def atoms(self):
        return [str(ap) for ap in self.spot_aut.ap()]

    def delta(self, state, inp):
        """
        :param inp: (list) List of atoms that are true.
        """
        # Preprocess inputs
        inp_dict = {p: True for p in inp} | {p: False for p in self.atoms() if p not in inp}

        # Initialize a BDD over set of atoms. 
        bdd = BDD()
        bdd.declare(*self.atoms())

        # Get spot BDD dict to extract formula 
        bdd_dict = self.spot_aut.get_dict()
        
        # Get next states
        next_states = []
        for t in self.spot_aut.out(state):
            label = spot.bdd_format_formula(bdd_dict, t.cond)
            label = spot.formula(label)
            if label.is_ff():
                continue
            elif label.is_tt():
                next_states.append(int(t.dst))
            else:
                label = spot.formula(label).to_str('spin')
                v = bdd.add_expr(label)
                if bdd.let(inp_dict, v) == bdd.true:
                    next_states.append(int(t.dst))

        # Return based on whether automaton is deterministic or non-deterministic.
        #   If automaton is deterministic but len(next_states) = 0, then automaton is incomplete, return None.
        if self.is_deterministic() and len(next_states) > 0:
            return next_states[0]

        if not self.is_deterministic():
            return next_states

    def init_state(self):
        return int(self.spot_aut.get_init_state_number())

    def final(self, state):
        if not self.is_state_based_acc():
            raise NotImplementedError
        return list(self.spot_aut.state_acc_sets(state).sets())

    @register_property(Automaton.GRAPH_PROPERTY)
    def acc_name(self):
        return self.spot_aut.acc().name()

    def acc_cond(self):
        """
        Returns acceptance condition according to ggsolver definitions.
        See :meth:`SpotAutomaton.spot_acc_cond` for acceptance condition in spot's nomenclature.
        """
        return self._acc_cond

    @register_property(Automaton.GRAPH_PROPERTY)
    def spot_acc_cond(self):
        """
        Acceptance condition in spot's nomenclature.
        """
        return str(self.spot_aut.get_acceptance())

    def num_acc_sets(self):
        return self.spot_aut.num_sets()

    @register_property(Automaton.GRAPH_PROPERTY)
    def formula(self):
        return self._formula

    def is_deterministic(self):
        return bool(self.spot_aut.prop_universal() and self.spot_aut.is_existential())

    def is_unambiguous(self):
        return bool(self.spot_aut.prop_unambiguous())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_state_based_acc(self):
        return bool(self.spot_aut.prop_state_acc())

    def is_terminal(self):
        return bool(self.spot_aut.prop_terminal())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_weak(self):
        return bool(self.spot_aut.prop_weak())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_inherently_weak(self):
        return bool(self.spot_aut.prop_inherently_weak())

    def is_stutter_invariant(self):
        return bool(self.spot_aut.prop_stutter_invariant())
