import time
import flpianoroll as flp


def findall(p, s):
    """
    Yields all the positions of
    the pattern p in the string s.
    """
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


def rand_int(seed=None):
    """
    Generate a random non-negative integer

    seed: int or None (generate a seed from current time)
    """
    state = time.time_ns() if seed is None else seed

    while True:
        state = (75 * state + 74) % 65537
        yield state
