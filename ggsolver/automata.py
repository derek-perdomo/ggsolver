from ggsolver.models import Automaton


class DFA(Automaton):
    """
    Represents a Deterministic Finite-state Automaton.

    - Acceptance Type: `Automaton.ACC_REACH`
    - Acceptance condition: `(Reach, 0)`

        - **Accepts:** Finite words.
        - **Interpretation:** :math:`\mathsf{Last}(\\rho) \in F` where :math:`F = \{q \in Q \mid \mathsf{AccSet}(q) = 0\}`

    - Number of Acceptance Sets: `1`
    - `final(state)` function returns either `-1` to indicate that the state is not accepting or `0` to
      indicate that the state is accepting with acceptance set `0`.
    """
    def __init__(self, states, atoms, trans_dict, init_state, final):
        """
        Constructs a DFA.

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (Iterable[states]) The set of final states, a subset of states iterable.
        """
        super(DFA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  final=final,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_REACH, 0))


class Monitor(Automaton):
    """
    Represents a Safety automaton.

    - Acceptance Type: `Automaton.ACC_SAFETY`
    - Acceptance condition: `(Safety, 0)`

        - **Accepts:** Infinite words.
        - **Interpretation:** :math:`\mathsf{Occ}(\\rho) \subseteq F` where :math:`F = \{q \in Q \mid \mathsf{AccSet}(q) = 0\}`

    - Number of Acceptance Sets: `1`
    - `final(state)` function returns either `-1` to indicate that the state is not accepting or `0` to
      indicate that the state is accepting with acceptance set `0`.
    """
    def __init__(self, states, atoms, trans_dict, init_state, final):
        """
        Constructs a Monitor.

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (Iterable[states]) The set of final states, a subset of states iterable.
        """
        super(Monitor, self).__init__(states=states,
                                      atoms=atoms,
                                      trans_dict=trans_dict,
                                      init_state=init_state,
                                      final=final,
                                      is_deterministic=True,
                                      acc_cond=(Automaton.ACC_SAFETY, 0))


class DBA(Automaton):
    """
    Represents a Deterministic Buchi automaton.

    - Acceptance Type: `Automaton.ACC_BUCHI`
    - Acceptance condition: `(Buchi, 0)`

        - **Accepts:** Infinite words.
        - **Interpretation:** :math:`\mathsf{Inf}(\\rho) \\cap F \\neq \\emptyset` where :math:`F = \{q \in Q \mid \mathsf{AccSet}(q) = 0\}`

    - Number of Acceptance Sets: `1`
    - `final(state)` function returns either `-1` to indicate that the state is not accepting or `0` to
      indicate that the state is accepting with acceptance set `0`.
    """
    def __init__(self, states, atoms, trans_dict, init_state, final):
        """
        Constructs a DBA.

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (Iterable[states]) The set of final states, a subset of states iterable.
        """
        super(DBA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  final=final,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_BUCHI, 0))


class DCBA(Automaton):
    """
    Represents a Deterministic co-Buchi automaton.

    - Acceptance Type: `Automaton.ACC_COBUCHI`
    - Acceptance condition: `(co-Buchi, 0)`

        - **Accepts:** Infinite words.
        - **Interpretation:** :math:`\mathsf{Inf}(\\rho) \\subseteq F` where :math:`F = \{q \in Q \mid \mathsf{AccSet}(q) = 0\}`

    - Number of Acceptance Sets: `1`
    - `final(state)` function returns either `-1` to indicate that the state is not accepting or `0` to
      indicate that the state is accepting with acceptance set `0`.
    """
    def __init__(self, states, atoms, trans_dict, init_state, final):
        """
        Constructs a DCBA.

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (Iterable[states]) The set of final states, a subset of states iterable.
        """
        super(DCBA, self).__init__(states=states,
                                   atoms=atoms,
                                   trans_dict=trans_dict,
                                   init_state=init_state,
                                   final=final,
                                   is_deterministic=True,
                                   acc_cond=(Automaton.ACC_COBUCHI, 0))


class DPA(Automaton):
    """
    Represents a Deterministic Buchi automaton.

    - Acceptance Type: `Automaton.ACC_PARITY`
    - Acceptance condition: `(Parity Min Even , 0)`

        - **Accepts:** Infinite words.
        - **Interpretation:** :math:`\\min_{q \\in \\mathsf{Inf}(\\rho)} \\chi(q)` is even, where :math:`\\chi: Q \\rightarrow \\mathbb{N}` is a coloring function that associates every state in DPA with a color (an integer).

    - Number of Acceptance Sets: `k`, where `k` is a positive integer.
    - `final(state)` a value between `0` and `k-1` to indicate that the color of a state.
    """
    def __init__(self, states, atoms, trans_dict, init_state, final):
        """
        Constructs a DPA.

        :param states: (Iterable) An iterable over states in the automaton.
        :param atoms: (Iterable[str]) An iterable over atomic propositions in the automaton.
        :param trans_dict: (dict) A dictionary defining the (deterministic) transition function of automaton.
                      Format of dictionary: {state: {logic.PLFormula: state}}
        :param init_state: (object) The initial state, a member of states iterable.
        :param final: (dict[state: int]) A state to color mapping.
        """
        super(DPA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_PARITY, 0))
