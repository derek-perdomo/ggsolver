"""
Defines an interface from spot automaton to ggsolver automaton.
"""

import spot
from ggsolver.models import Automaton, register_property
from ggsolver.util import powerset
from dd.autoref import BDD


class SpotAutomaton(Automaton):
    """

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

        print(f"[INFO] Translating {self._formula} with options={options} ...")
        self.spot_aut = spot.translate(formula, *options)

    def sigma(self):
        if len(self.atoms()) >= 16:
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

    @register_property(Automaton.GRAPH_PROPERTY)
    def acc_cond(self):
        return str(self.spot_aut.get_acceptance())

    @register_property(Automaton.GRAPH_PROPERTY)
    def num_acc_sets(self):
        return self.spot_aut.num_sets()

    @register_property(Automaton.GRAPH_PROPERTY)
    def formula(self):
        return self._formula

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_deterministic(self):
        return bool(self.spot_aut.prop_universal() and self.spot_aut.is_existential())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_unambiguous(self):
        return bool(self.spot_aut.prop_unambiguous())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_state_based_acc(self):
        return bool(self.spot_aut.prop_state_acc())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_terminal(self):
        return bool(self.spot_aut.prop_terminal())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_weak(self):
        return bool(self.spot_aut.prop_weak())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_inherently_weak(self):
        return bool(self.spot_aut.prop_inherently_weak())

    @register_property(Automaton.GRAPH_PROPERTY)
    def is_stutter_invariant(self):
        return bool(self.spot_aut.prop_stutter_invariant())
