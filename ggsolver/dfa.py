from ggsolver.models import Automaton
import logging, sys
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class Dfa(Automaton):
    def __init__(self, states, atoms, delta, init_state, final):
        super(Dfa, self).__init__(states=states, atoms=atoms, init_state=init_state, final=final,
                                  acc_cond=Automaton.ACC_REACH)
        self.delta = delta


if __name__ == '__main__':
    from pprint import pprint

    def delta1(state, inp):
        # raise NotImplementedError(f"{self}.delta() function is not implemented.")
        if state == 0:
            return 0
        if state == 1 and 'a' in inp:
            return 0

    def delta2(state, inp):
        # raise NotImplementedError(f"{self}.delta() function is not implemented.")
        if state == 0:
            return 0
        if state == 1 and 'b' in inp:
            return 0
        else:
            return state

    states_ = list(range(2))
    atoms_ = ['a', 'b']
    init_state_ = [1]
    final_ = [0]

    dfa1 = Dfa(states_, atoms_, delta1, init_state_, final_)
    dfa1_graph = dfa1.graphify()
    pprint(list(dfa1_graph["edge_label"].items()))

    dfa2 = Dfa(states_, atoms_, delta2, init_state_, final_)
    dfa2_graph = dfa2.graphify()
    pprint(list(dfa2_graph["edge_label"].items()))

