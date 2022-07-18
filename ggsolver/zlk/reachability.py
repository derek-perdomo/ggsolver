from ggsolver.models import Solver


class SureWin(Solver):
    # TODO. Remember Solver is a Game. Hence, we can use states(), actions() functions.
    #   In general, the game may be constructed from game object or graph or file.

    def __init__(self):
        super(SureWin, self).__init__(is_tb=True, is_stoch=False, is_quant=False)
        self._win1 = None

    def solve(self):
        pass

    def p1_win(self, state):
        pass

    def p2_win(self, state):
        pass

    def pi1(self, state):
        pass

    def pi2(self, state):
        pass
