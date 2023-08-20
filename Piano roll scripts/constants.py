from flpianoroll import *


NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
MODES = {
    "ionian": {
        "interval_set": [2, 2, 1, 2, 2, 2, 1],
        "root": "C"
    },
    "dorian": {
        "interval_set": [2, 1, 2, 2, 2, 1, 2],
        "root": "D",
    },
    "phrygian": {
        "interval_set": [1, 2, 2, 2, 1, 2, 2],
        "root": "E",
    },
    "lydian": {
        "interval_set": [2, 2, 2, 1, 2, 2, 1],
        "root": "F",
    },
    "mixolydian": {
        "interval_set": [2, 2, 1, 2, 2, 1, 2],
        "root": "G",
    },
    "aeolian": {
        "interval_set": [2, 1, 2, 2, 1, 2, 2],
        "root": "A",
    },
    "locrian": {
        "interval_set": [1, 2, 2, 1, 2, 2, 2],
        "root": "B",
    },
}
INTERVAL_NAMES = [
    "unison",
    "minor second",
    "major second",
    "minor third",
    "major third",
    "perfect fourth",
    "augmented fourth",
    "perfect fifth",
    "minor sixth",
    "major sixth",
    "minor seventh",
    "major seventh",
    "octave",
    "minor ninth",
    "major ninth",
    "minor tenth",
    "major tenth",
    "perfect eleventh",
    "augmented eleventh",
    "perfect twelfth"
]
QUALITIES = ["major", "minor", "augmented", "diminished"]
ACCIDENTALS = ["#", "b"]

"""
CHORD DEGREE NAMES
[ 'unison', 'second', 'third', 'fourth', 'fifth', ..., ]
"""
CHORD_DEGREE_NAMES = [interval.split(" ")[-1] for interval in INTERVAL_NAMES]
CHORD_DEGREE_NAMES = sorted(
    list(set(CHORD_DEGREE_NAMES)),
    key=lambda name: CHORD_DEGREE_NAMES.index(name)
)

"""
NOTE MAP
    {
        "A4": {
            "number": 69,
            "name": "A",
        }
    }
"""
NOTE_MAP = {}
midi_number_counter = 21
scale_counter = 0
infinite_loop_safety = 0
while scale_counter < 10 and infinite_loop_safety < 100:
    infinite_loop_safety += 1
    for i in NOTES:
        if midi_number_counter < 128:
            if i == "C":
                scale_counter += 1
            NOTE_MAP[f"{i}{scale_counter}"] = {
                "number": midi_number_counter,
                "name": i,
            }
            midi_number_counter += 1

