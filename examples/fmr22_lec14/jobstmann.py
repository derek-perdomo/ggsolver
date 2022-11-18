import ggsolver.dtptb as dtptb
from ggsolver.logic.ltl import ScLTL


states = list(range(8))
actions = [(0, 1), (0, 3), (1, 0), (1, 2), (1, 4), (2, 4), (2, 2), (3, 0), (3, 4), (3, 5), (4, 1), (4, 3), (5, 3),
                (5, 6), (6, 6), (6, 7), (7, 0), (7, 3)]
trans_dict = {
    0: {(0, 1): 1, (0, 3): 3},
    1: {(1, 0): 0, (1, 2): 2, (1, 4): 4},
    2: {(2, 4): 4, (2, 2): 2},
    3: {(3, 0): 0, (3, 4): 4, (3, 5): 5},
    4: {(4, 1): 1, (4, 3): 3},
    5: {(5, 3): 3, (5, 6): 6},
    6: {(6, 6): 6, (6, 7): 7},
    7: {(7, 0): 0, (7, 3): 3},
}
atoms = [f"p{i}" for i in states]
label = {i: "p{i}" for i in states}


game = dtptb.DTPTBGame(states=states, actions=actions, trans_dict=trans_dict, atoms=atoms, label=label)
objective = ScLTL("Fp3 | Fp4")
dfa = objective.translate()
prod = dtptb.ProductWithDFA(game, dfa)
