from ggsolver.models import Automaton
import logging, sys
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class DFA(Automaton):
    def __init__(self, states, atoms, trans_dict, init_state, final):
        super(DFA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  final=final,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_REACH, 0))


class Monitor(Automaton):
    def __init__(self, states, atoms, trans_dict, init_state, final):
        super(Monitor, self).__init__(states=states,
                                      atoms=atoms,
                                      trans_dict=trans_dict,
                                      init_state=init_state,
                                      final=final,
                                      is_deterministic=True,
                                      acc_cond=(Automaton.ACC_SAFETY, 0))


class DBA(Automaton):
    def __init__(self, states, atoms, trans_dict, init_state, final):
        super(DBA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  final=final,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_BUCHI, 0))


class DCBA(Automaton):
    def __init__(self, states, atoms, trans_dict, init_state, final):
        super(DCBA, self).__init__(states=states,
                                   atoms=atoms,
                                   trans_dict=trans_dict,
                                   init_state=init_state,
                                   final=final,
                                   is_deterministic=True,
                                   acc_cond=(Automaton.ACC_COBUCHI, 0))


class DPA(Automaton):
    def __init__(self, states, atoms, trans_dict, init_state, final):
        super(DPA, self).__init__(states=states,
                                  atoms=atoms,
                                  trans_dict=trans_dict,
                                  init_state=init_state,
                                  final=final,
                                  is_deterministic=True,
                                  acc_cond=(Automaton.ACC_PARITY, 0))


