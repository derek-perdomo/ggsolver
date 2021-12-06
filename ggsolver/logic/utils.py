from itertools import chain, combinations


def powerset(iterable):
    """
    Returns all the subsets of this set. This is a generator.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

