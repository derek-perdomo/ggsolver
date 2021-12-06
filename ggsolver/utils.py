from itertools import chain, combinations
from ggsolver.ds import BaseGame
from ggsolver.logic import Dfa


def powerset(iterable):
    """
    Returns all the subsets of this set. This is a generator.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def product_tsys_dfa(tsys: BaseGame, dfa: Dfa, name=None):
    # Define delta, pred and succ functions for symbolic construction
    def delta(u, a):
        # TODO (SU): complete this function.
        pass

    def pred(v):
        # TODO (SU): complete this function.
        pass

    def succ(u):
        # TODO (SU): complete this function.
        pass

    # Define product game components
    name = name if name is not None else f"{tsys.name} x {dfa.name}"
    states = (((s, q), ds | dq) for s, ds in tsys.states(data=True) for q, dq in dfa.states(data=True))
    actions = tsys.actions

    # Construct product game
    product_game = tsys.__class__(name=name)
    product_game.construct_symbolic(states=states, actions=actions, delta=delta, pred=pred, succ=succ)

    return product_game
