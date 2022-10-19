"""
Development test code for Automaton.graphify.
"""

from ggsolver.interfaces.i_spot import SpotAutomaton


if __name__ == '__main__':
    aut = SpotAutomaton("Fa & Gb")
    graph = aut.graphify()
    graph.to_png("aut.png", nlabel=["state"], elabel=["input"])
