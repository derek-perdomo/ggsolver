import logging
from abc import ABC, abstractmethod


class BaseGame(ABC):
    """
    Abstract class for representing different games on graphs.

    Data structure.
        * (attr) _mode: `EXPLICIT` or `SYMBOLIC`.
            In `EXPLICIT` mode, the edges of graph are explicitly stored in `_graph` attribute.
            In `SYMBOLIC` mode, the edges of graph are encoded symbolically in `delta` function.
        * (attr) _is_initialized: encodes whether game has been defined or not.
        * (attr) _graph: Stores the states of game. In `EXPLICIT` mode, it also stores the edges.
        * (attr) actions: Set of actions.
        * (fcn) delta(u, a) -> Set(v) is the transition function.
        * (fcn) pre(v) -> Set((u, data)) is the predecessor function given transition function, delta.
        * (fcn) post(u) -> Set((v, data)) is the successor function given transition function, delta.
    """
    EXPLICIT = "explicit"
    SYMBOLIC = "symbolic"

    def __init__(self, name):
        self._name = name
        self._graph = None
        self._actions = set()
        self._delta = None
        self._pred = None
        self._succ = None
        self._init_st = None
        self._atoms = set()
        self._labeling_function = None
        self._properties = dict()
        self._is_constructed = False
        self._mode = None

    def __repr__(self):
        return f"{self.__class__.__name__} object."

    def __str__(self):
        return repr(self)

    def __extend__(self):
        pass

    def construct_explicit(self, graph, **kwargs):
        err_msg = f"{repr(self)}.construct_explicit method is not implemented by user."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    def construct_symbolic(self, states, actions, delta, pred, succ, **kwargs):
        err_msg = f"{repr(self)}.construct_symbolic method is not implemented by user."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    def get_state_property(self, v, prop_name):
        try:
            return self._graph.nodes[v][prop_name]
        except KeyError as err:
            if v not in self._graph.nodes:
                logging.critical(f"State {v} is not in {repr(self)}.")
            if prop_name not in self._graph.nodes[v]:
                logging.critical(f"State {v} in {repr(self)} does not have property {prop_name}.")
            raise err

    def label(self, v):
        pass

    def make_explicit(self):
        err_msg = f"{repr(self)}.make_explicit method is not implemented by user."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    def make_complete(self):
        err_msg = f"Not yet implemented. TODO."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    def make_labeled(self, atoms, labeling_func):
        if len(self._atoms) != 0 or self._labeling_function is not None:
            logging.warning(f"{repr(self)}.make_labeled is overwrites atoms or labeling function.")
        self._atoms = set(atoms)
        self._labeling_function = labeling_func

    def set_init_st(self, init_st):
        if self._init_st is not None:
            logging.warning(f"{repr(self)}.init_st is updated from {self._init_st} to {init_st}.")
        self._init_st = init_st

    def states(self, data=False):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.states. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._graph.nodes(data=data)

    def validate_graph(self, graph, **kwargs):
        err_msg = f"{repr(self)}.validate_graph method is not implemented by user. Returning True."
        logging.warning(err_msg)
        return True

    @abstractmethod
    def delta(self, u, a):
        err_msg = f"{repr(self)}.delta method is not defined."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def pred(self, v):
        err_msg = f"{repr(self)}.pred method is not implemented by user."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def succ(self, u):
        err_msg = f"{repr(self)}.succ method is not implemented by user."
        logging.critical(err_msg)
        raise NotImplementedError(err_msg)

    @property
    def actions(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.actions. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._actions

    @property
    def graph(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.states. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        if self._mode == self.EXPLICIT:
            return self._graph

        raise ValueError(f"Cannot access graph in {self._mode} mode. Use make_explicit to change the mode to EXPLICIT.")

    @property
    def init_st(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.init_st. Game is not constructed."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._init_st

    @property
    def is_complete(self):
        if not self.is_constructed:
            err_msg = f"{repr(self)}.is_complete is not implemented. TODO."
            logging.critical(err_msg)
            raise NotImplementedError(err_msg)

    @property
    def is_constructed(self):
        return self._is_constructed
