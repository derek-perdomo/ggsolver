import os
import inspect
from abc import ABC, abstractmethod

# Global Variable
PARSERS_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))
PARSERS_DIR = os.path.join(PARSERS_DIR, "grammars")


class ParsingError(ValueError):
    pass


class BaseFormula(ABC):
    def __init__(self, f_str, atoms=None):
        self.f_str = f_str
        self._atoms = set(atoms) if atoms is not None else set()

    def __str__(self):
        return str(self.f_str)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.f_str})"

    def __hash__(self):
        return hash(self.f_str)

    def __eq__(self, other):
        raise NotImplementedError("Marked abstract.")

    def update_atoms(self, atoms):
        self._atoms |= set(atoms)

    @abstractmethod
    def translate(self):
        pass

    @abstractmethod
    def substitute(self, subs_map):
        pass

    @abstractmethod
    def evaluate(self, true_atoms):
        pass

    @abstractmethod
    def atoms(self):
        pass
