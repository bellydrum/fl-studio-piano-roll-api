from flpianoroll import *

from constants import CHORD_DEGREE_NAMES, MODES
from utilities_theory import Theory

theory = Theory()


class Chord:
    def __init__(self, root, mode):
        self.root = root
        interval_accumulator = 0
        interval_set = MODES[mode]["interval_set"]
        for i in range(len(CHORD_DEGREE_NAMES)):
            self.__dict__.update({
                CHORD_DEGREE_NAMES[i]: theory.get_note_by_interval(self.root, interval_accumulator)
            })
            interval_accumulator += interval_set[i % len(interval_set)]


class MajorChord(Chord):
    def __init__(self, root):
        self.mode = "ionian"
        super().__init__(root, self.mode)


class MinorChord(Chord):
    def __init__(self, root):
        self.mode = "aeolian"
        super().__init__(root, self.mode)
