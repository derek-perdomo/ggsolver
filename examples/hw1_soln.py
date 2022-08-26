"""
EEL 4930/5934 Formal Methods in Robotics and AI
Instructor: Dr. Jie Fu
TAs: Abhishek N. Kulkarni and Haoxiang Ma

HW1: Gridworld Transition System
Task:
    In this assignment, we will implement a gridworld transition system
    containing one robot with a battery with fixed capacity. Robot can move
    NESW, with bouncy walls. Some cells may have obstacles and some cells have flag.

[The story for the exercise will be designed by HM]
"""
import itertools
from ggsolver.models import TSys
from pprint import pprint

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Gridworld(TSys):
    def __init__(self, dim, batt, obs, flag):
        """
        Parameters for the gridworld.

        :param dim: Dimensions of gridworld (row, col)
        :param batt: Maximum battery level.
        :param obs: List of cells (r, c) that contain an obstacle.
        :param flag: List of cells (r, c) that contain a flag.
        """
        assert dim[0] > 0 and dim[1] > 0
        super(Gridworld, self).__init__(is_deterministic=True)
        self.dim = dim
        self.batt = batt
        self.obs = obs
        self.flag = flag

    def states(self):
        """
        Returns a list of states in gridworld.
        """
        return [(row, col, batt) for row, col, batt in
                itertools.product(range(self.dim[0]), range(self.dim[1]), range(self.batt + 1))]

    def actions(self):
        """
        Return a list of actions. Each action is identified by a string label.
        """
        return ["N", "E", "S", "W"]

    def delta(self, state, inp):
        """
        Implement the transition function.

        :param state: A state from the list returned by states().
        :param inp: An action from the list returned by actions().
        :return: The next state, which is the result of applying the action `inp` to `state`.
        """
        row, col, batt = state
        if batt == 0:
            return state

        if inp == "N":
            return (row + 1, col, batt - 1) if 0 <= row + 1 < self.dim[0] else (row, col, batt - 1)
        elif inp == "E":
            return (row, col + 1, batt - 1) if 0 <= col + 1 < self.dim[1] else (row, col, batt - 1)
        elif inp == "S":
            return (row - 1, col, batt - 1) if 0 <= row - 1 < self.dim[0] else (row, col, batt - 1)
        else:  # inp == "W":
            return (row, col - 1, batt - 1) if 0 <= col - 1 < self.dim[1] else (row, col, batt - 1)

    def atoms(self):
        """
        Returns a list of atomic propositions. Each atomic proposition is a string.
        """
        return ["f", "o"]

    def label(self, state):
        """
        Returns a list of atoms that are true in the `state`.
        :param state: A state from the list returned by states().
        :return: List of atoms.
        """
        row, col, batt = state
        if (row, col) in self.obs:
            return ["o"]

        if (row, col) in self.obs:
            return ["f"]

        return list()


class SynchronousProduct(Gridworld):
    def __init__(self, gw1: Gridworld, gw2: Gridworld):
        super(Gridworld, self).__init__(is_deterministic=True)
        self.gw1 = gw1
        self.gw2 = gw2

    def states(self):
        """
        Returns a list of states in gridworld.
        """
        return list(itertools.product(self.gw1.states(), self.gw2.states()))

    def actions(self):
        """
        Return a list of actions. Each action is identified by a string label.
        """
        assert set(self.gw1.actions()) == set(self.gw2.actions())
        return self.gw1.actions()

    def delta(self, state, inp):
        """
        Implement the transition function.

        :param state: A state from the list returned by states().
        :param inp: An action from the list returned by actions().
        :return: The next state, which is the result of applying the action `inp` to `state`.
        """
        s1, s2 = state
        t1 = self.gw1.delta(s1, inp)
        t2 = self.gw2.delta(s2, inp)
        return t1, t2

    def atoms(self):
        """
        Returns a list of atomic propositions. Each atomic proposition is a string.
        """
        assert set(self.gw1.atoms()) == set(self.gw2.atoms())
        return self.gw1.atoms()

    def label(self, state):
        """
        Returns a list of atoms that are true in the `state`.
        :param state: A state from the list returned by states().
        :return: List of atoms.
        """
        s1, s2 = state
        label1 = self.gw1.label(s1)
        label2 = self.gw2.label(s2)
        return label1 + label2


def gridworld_main():
    gw = Gridworld(dim=(2, 2), batt=2, obs=[(0, 0)], flag=[(1, 1)])
    graph = gw.graphify()
    graph.to_png(fname="gw.png", nlabel=["state"], elabel=["input"])
    # graph.to_png(fname="gw.png")
    pprint([(n, graph["state"][n]) for n in graph.nodes()])


def product_main():
    gw1 = Gridworld(dim=(2, 2), batt=2, obs=[(0, 0)], flag=[(1, 1)])
    gw2 = Gridworld(dim=(2, 2), batt=2, obs=[(1, 0)], flag=[(1, 1)])
    product = SynchronousProduct(gw1, gw2)
    graph = product.graphify()
    graph.to_png(fname="gw.png")
    pprint([(n, graph["state"][n]) for n in graph.nodes()])


if __name__ == '__main__':
    gridworld_main()
    # product_main()
