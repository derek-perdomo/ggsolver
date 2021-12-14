import logging
import inspect
import random
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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
        # self._delta = None
        # self._pred = None
        # self._succ = None
        self._init_st = None
        self._atoms = set()
        self._label = None
        self._properties = dict()
        self._is_constructed = False
        self._mode = None
        self._pkl_encode_func = ["_pred", "_succ", "_delta", "_label"]

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self._name}">'

    def __str__(self):
        return repr(self)

    def __getstate__(self):
        # Encode object state. We specialized function encoding.
        state = dict()
        for param_name, param_value in self.__dict__.items():
            # If parameter stores a method/function and it has been registered with class to pickle,
            # get the source code of function and pickle as string.
            if inspect.ismethod(param_value) or inspect.isfunction(param_value):
                if param_name in self._pkl_encode_func:
                    func_name = param_value.__name__
                    source_lines = inspect.getsourcelines(param_value)
                    assert f"def {func_name}" in source_lines[0][0]
                    indent = len(source_lines[0][0]) - len(source_lines[0][0].lstrip())
                    source_lines = map(lambda x: x[indent:], source_lines[0])
                    source_code = "".join(source_lines)
                    state[param_name] = (func_name, source_code)
                else:
                    state[param_name] = None
                    logger.warning(f"{repr(self)}.__reduce__: Parameter {param_name} has a function value that is " 
                                   f"not registered with self._pkl_encode_func. This function will not be unpickled.")

            else:
                state[param_name] = param_value

        # Return object state
        logger.debug(f"{repr(self)}.__getstate__() -> {state}")
        return state

    def __setstate__(self, state):
        logger.debug(f"{repr(self.__class__)}.__setstate__(): input state -> {state}")

        def pickle_parse_fail_placeholder(*args, **kwargs):
            raise NotImplementedError(f"This function is called when unpickling of game object raises Exception."
                                      f"Check logs, and update the function.")

        # Decode function parameters.
        func_params = state["_pkl_encode_func"]
        for param_name in func_params:
            if state[param_name] is None:
                continue
            func_name, func_str = state[param_name]
            if isinstance(func_str, str):
                try:
                    tmp_globals = dict()
                    exec(func_str, tmp_globals)
                    state[param_name] = tmp_globals[func_name]

                except SyntaxError:
                    logger.error(f"{state['_name']}.{param_name} is registered as function parameter. Encoded syntax"
                                  f"could not be parsed while unpickling. Setting function to dummy function.",
                                  exc_info=True)
                    state[param_name] = pickle_parse_fail_placeholder

                except KeyError:
                    logger.error(f"{state['_name']}.{param_name} is registered as function parameter. "
                                  f"It seems the name of function 'def <name>(...):' in {func_str} is not "
                                  f"the same as {func_name}. Or, it is a lambda expression, which is not supported.",
                                  exc_info=True)
                    state[param_name] = pickle_parse_fail_placeholder

        self.__dict__.update(state)
        logger.debug(f"{repr(self)}.__setstate__(): new_state -> {state}")

    def construct_explicit(self, graph, **kwargs):
        err_msg = f"{repr(self)}.construct_explicit method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def construct_symbolic(self, states, actions, delta, pred, succ, **kwargs):
        err_msg = f"{repr(self)}.construct_symbolic method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def get_state_property(self, v, prop_name):
        try:
            return self._graph.nodes[v][prop_name]
        except KeyError as err:
            if v not in self._graph.nodes:
                logger.critical(f"State {v} is not in {repr(self)}.")
            if prop_name not in self._graph.nodes[v]:
                logger.critical(f"State {v} in {repr(self)} does not have property {prop_name}.")
            raise err

    def label(self, v):
        if not self.is_constructed:
            err_msg = f"{repr(self)}.label method is not implemented. It must be overridden by user."
            logging.critical(err_msg, exc_info=True)
            raise NotImplementedError(err_msg)

    def make_explicit(self):
        err_msg = f"{repr(self)}.make_explicit method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def make_complete(self):
        err_msg = f"Not yet implemented. TODO."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    def make_labeled(self, atoms, labeling_func):
        if len(self._atoms) != 0 or self._label is not None:
            logger.warning(f"{repr(self)}.make_labeled is overwrites atoms or labeling function.")
        self._atoms = set(atoms)
        self._label = labeling_func

    def set_init_st(self, init_st):
        if self._init_st is not None:
            logger.warning(f"{repr(self)}.init_st is updated from {self._init_st} to {init_st}.")
        self._init_st = init_st

    def states(self, data=False):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.states. Game is not constructed."
            logger.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._graph.nodes(data=data)

    def validate_graph(self, graph, **kwargs):
        err_msg = f"{repr(self)}.validate_graph method is not implemented by user. Returning True."
        logger.warning(err_msg)
        return True

    @abstractmethod
    def delta(self, u, a):
        err_msg = f"{repr(self)}.delta method is not defined."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def pred(self, v):
        err_msg = f"{repr(self)}.pred method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @abstractmethod
    def succ(self, u):
        err_msg = f"{repr(self)}.succ method is not implemented by user."
        logger.critical(err_msg)
        raise NotImplementedError(err_msg)

    @property
    def actions(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.actions. Game is not constructed."
            logger.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._actions

    @property
    def graph(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.states. Game is not constructed."
            logger.critical(err_msg)
            raise NotImplementedError(err_msg)

        if self._mode == self.EXPLICIT:
            return self._graph

        raise ValueError(f"Cannot access graph in {self._mode} mode. Use make_explicit to change the mode to EXPLICIT.")

    @property
    def init_st(self):
        if not self.is_constructed:
            err_msg = f"Cannot access {repr(self)}.init_st. Game is not constructed."
            logger.critical(err_msg)
            raise NotImplementedError(err_msg)

        return self._init_st

    @property
    def is_complete(self):
        if not self.is_constructed:
            err_msg = f"{repr(self)}.is_complete is not implemented. TODO."
            logger.critical(err_msg)
            raise NotImplementedError(err_msg)

    @property
    def is_constructed(self):
        return self._is_constructed

    @property
    def name(self):
        return self._name


class Strategy(dict):
    """
    Strategy is a map <state: List of actions>.
    """
    @abstractmethod
    def __call__(self, v):
        pass


class DeterministicStrategy(Strategy):
    def __call__(self, v):
        try:
            return self[v][0]
        except KeyError:
            logger.exception(f"Strategy is not defined at state {v}.")
            raise
        except IndexError:
            logger.exception(f"Strategy at state {v} is empty.")


class RandomizedStrategy(Strategy):
    def __call__(self, v):
        try:
            return random.choice(self[v])
        except KeyError:
            logger.exception(f"Strategy is not defined at state {v}.")
            raise
        except IndexError:
            logger.exception(f"Strategy at state {v} is empty.")

