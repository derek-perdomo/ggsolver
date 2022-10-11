__version__ = "0.1.4"


CHANGELOG = {
    "0.1.2": [
        "Added new docker latest, devel images. Updated installation instructions in documentation.",
        "Added `is_isomorphic_to` function to Graph class. Updated docs and example.",
    ],
    "0.1.3": [
        "Added `logic.pl` module with `simplify, evaluate, to_plformula` and `all_sat` methods for PL formulas.",
        "Moved `sigma` method to `Automaton` class with default implementation.",
        "Fixed the representation of `Automaton` acceptance conditions.",
        "Added new module: `automata`, with `DFA, Monitor, DBA, DCBA, DPA` classes. Docs and example added.",
        "Automaton can be constructed by passing components (Q, AP, Trans, q0, F) to the constructor.",
    ],
    "0.1.4": [
        "Bugfix in `SpotAutomaton.is_semi_deterministic() function. ",
        "SpotAutomaton.acc_cond adheres to ggsolver.models.Automaton convention.",
        "Made init arguments to classes in ggsolver.automata optional.",
        "Added Automaton.from_automaton() function to construct DFA, DBA ... from SpotAutomaton."
        "Added example for translating LTL to DFA."
    ]

}
