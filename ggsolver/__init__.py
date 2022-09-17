__version__ = "0.1.3"


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

}
