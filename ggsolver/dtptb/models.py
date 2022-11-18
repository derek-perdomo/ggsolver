import itertools

from ggsolver.models import Game
from ggsolver.automata import DFA


class DTPTBGame(Game):
    """
    delta(s, a) -> s
    """
    def __init__(self, **kwargs):
        """
        kwargs:
            * states: List of states
            * actions: List of actions
            * trans_dict: Dictionary of {state: {act: state}}
            * atoms: List of atoms
            * label: Dictionary of {state: List[atoms]}
            * final: List of states
        """
        super(DTPTBGame, self).__init__(
            **kwargs,
            is_deterministic=True,
            is_probabilistic=False,
            is_turn_based=True
        )


class ProductWithDFA(DTPTBGame):
    """
    For the product to be defined, Game must implement `atoms` and `label` functions.
    """
    def __init__(self, game: DTPTBGame, aut: DFA):
        super(ProductWithDFA, self).__init__()
        self._game = game
        self._aut = aut

    def states(self):
        return list(itertools.product(self._game.states(), self._aut.states()))

    def actions(self):
        return self._game.actions()

    def delta(self, state, act):
        s, q = state
        t = self._game.delta(s, act)
        p = self._aut.delta(q, self._game.label(t))
        return t, p

    def init_state(self):
        if self.init_state() is not None:
            s0 = self.init_state()
            q0 = self._aut.init_state()
            return s0, self._aut.delta(q0, self._game.label(s0))

    def final(self, state):
        return self._aut.final(state[0]) == 0


