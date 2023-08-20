from flpianoroll import *

from constants import ACCIDENTALS, CHORD_DEGREE_NAMES, NOTE_MAP, QUALITIES
from functions import findall
from models import Chord, MajorChord, MinorChord
from utilities_theory import Theory

Note = Note
Utils = Utils
score = score


theory = Theory()


def log(message):
    if type(message) is not str:
        message = str(message)

    Utils.ShowMessage(message)


class Project:
    @staticmethod
    def get_time_in_ticks(measure=None, beat=None, ppq=None):
        """
        :param measure:     int
        :param beat:        int
        :param ppq:         int
        :return:            int
        """
        measure = 1 if measure is None else measure
        beat = 1 if beat is None else beat
        ppq = 0 if ppq is None else ppq

        if not(type(measure) == int and type(beat) == int and type(ppq) == int):
            raise Exception("set_time(measure=<int>, beat=<int>, fraction=<int>)")

        numerator = score.tsnum
        denominator = score.tsden

        """
        Due to a "quirk" in FL Studio's python API, we must remap denominators to the correct one
        """
        error_remap = {8: 2, 4: 4, 2: 8, 1: 16}
        denominator = error_remap[denominator]

        ticks_per_beat = score.PPQ * (4 / denominator)
        ticks_per_measure = ticks_per_beat * numerator

        return int((ticks_per_measure * (measure - 1) + ticks_per_beat * (beat - 1)) + ppq)

    def write_note(self, name, measure=None, beat=None, ppq=None, length=None):
        """
        :param name:        'C4'        note to write
        :param measure:     2           measure in song
        :param beat:        1           beat in measure
        :param ppq:         0           number of samples past beat (96 per quarter note)
        :param length:      2           length in beats
        :return:            None
        """
        if not theory.is_valid_note(name):
            raise Exception(f"ERROR | Note '{name}' provided to write_note is invalid.")

        measure = 1 if type(measure) is not int else measure
        beat = 1 if type(beat) is not int else beat
        ppq = 0 if type(ppq) is not int else ppq
        length = 1 if type(length) is not int else length

        note_to_write = Note()
        note_to_write.number = NOTE_MAP[name]["number"]
        note_to_write.time = self.get_time_in_ticks(measure, beat, ppq)
        note_to_write.length = length * score.PPQ

        score.addNote(note_to_write)

    @staticmethod
    def parse_chord_symbol(symbol):
        """
        A chord symbol follows the convention of:
            <root>          required        C, C#, Cb
            <quality>       optional        <none>, M, m, maj, min, aug, dim, dom
            <extension>     optional        7, 9, 11, 13
            <altered>       optional        flat5, sharp11, sus2, sus4
            <added>         optional        add2, add4, add9
            <bass>          optional        /G, /A#, /B

        C               C, E, G
        C#              C#, F, G#
        Cmin            C, Eb, G
        Cmaj7           C, E, G, B
        C7              C, E, G, Bb
        C9              C, E, G, Bb, D
        Cdom7           C, E, G, Bb
        Cmaj7flat5      C, E, Gb, B
        C7flat5         C, E, Gb, Bb
        Csus4           C, F, G
        C7flat5/Gb      Gb, Bb, C, E
        C#7flat5/Ab     Ab, Bb, C, E, Gb
        """
        if type(symbol) != str or not len(symbol):
            raise Exception(f"ERROR | Symbol '{symbol}' provided to parse_chord_symbol is not valid.")

        to_parse = "".join([char for char in symbol])
        parsed = ""

        extension = None
        flat = []
        sharp = []
        sus = []
        added = []
        bass = None

        """ parse root """
        root = symbol[0].upper() if (len(symbol) == 1 or symbol[1] not in ACCIDENTALS) else f"{symbol[0].upper()}{symbol[1]}"
        if not theory.is_valid_note(root):
            raise Exception(f"ERROR | '{root}' is not a valid root note.")
        to_parse = to_parse[len(root):]
        parsed += root

        """ parse quality """
        if to_parse:
            if to_parse[0].isdigit() and (int(to_parse[0]) == 7 or int(to_parse[0]) == 9):
                quality_value = to_parse[0]
                quality = "dominant"
                extension = int(to_parse[0])
                flat.append(7)
            elif len(to_parse) > 2:
                next_three_chars = to_parse[:3]
                if next_three_chars.lower() in ["maj", "min", "aug", "dim"]:
                    if next_three_chars.lower() == "maj":
                        quality = "major"
                    elif next_three_chars.lower() == "min":
                        quality = "minor"
                    elif next_three_chars.lower() == "aug":
                        quality = "augmented"
                    else:
                        quality = "diminished"
                    quality_value = next_three_chars
                elif to_parse[0] in ["M", "m", "a", "d"]:
                    if to_parse[0] == "M":
                        quality = "major"
                    elif to_parse[0] == "m":
                        quality = "minor"
                    elif to_parse[0] == "a":
                        quality = "augmented"
                    else:
                        quality = "diminished"
                    quality_value = next_three_chars[0]
                else:
                    quality = "major"
                    quality_value = ""
            else:
                if to_parse[0] in ["M", "m", "a", "d"]:
                    if to_parse[0] == "M":
                        quality = "major"
                    elif to_parse[0] == "m":
                        quality = "minor"
                    elif to_parse[0] == "a":
                        quality = "augmented"
                    else:
                        quality = "diminished"
                    quality_value = to_parse[0]
                else:
                    quality = "major"
                    quality_value = ""

            to_parse = to_parse[len(quality_value):]
            parsed += quality_value
        else:
            quality = "major"

        """ parse extension """
        if to_parse:
            if extension is None:
                potential_extension = to_parse[0]
                if potential_extension == "1":
                    if len(to_parse) > 1 and to_parse[:2] in ["11", "13"]:
                        extension = int(to_parse[:2])
                    else:
                        raise Exception(f"ERROR | Extension '{potential_extension}' is invalid.")
                elif potential_extension in ["7", "9"]:
                    extension = int(potential_extension)
                else:
                    extension = ""
            elif type(extension) != int:
                raise Exception(f"ERROR | Somehow the extension '{extension}' is not an <int>.")

            if quality != "dominant":
                to_parse = to_parse[len(str(extension)):]
            parsed += str(extension)

        """ parse altered """

        if to_parse:
            for altered_symbol in ["flat", "sharp", "sus"]:
                matches = [(
                    i, to_parse[i: i + len(altered_symbol)]
                ) for i in findall(altered_symbol, to_parse)]

                for match in matches:
                    match_index = match[0]
                    match_name = match[1]

                    try:
                        altered_degree = to_parse[match_index + len(match_name)]
                        if altered_degree.isdigit():
                            if altered_degree == "1":
                                try:
                                    altered_degree = f"{altered_degree}{int(to_parse[match_index + len(match_name) + 1])}"
                                    if match_name == "flat":
                                        flat.append(int(altered_degree))
                                    elif match_name == "sharp":
                                        sharp.append(int(altered_degree))
                                    else:
                                        sus.append(int(altered_degree))
                                except IndexError or ValueError:
                                    log(f"WARNING | '{match_name}{altered_degree}' is not a valid degree alteration.")
                                    continue
                                except ValueError:
                                    log(f"WARNING | '{match_name}{altered_degree}' is not a valid degree alteration.")
                                    continue
                            else:
                                if match_name == "flat":
                                    flat.append(int(altered_degree))
                                elif match_name == "sharp":
                                    sharp.append(int(altered_degree))
                                else:
                                    sus.append(int(altered_degree))
                        else:
                            log(f"WARNING | Skipping '{match_name}{altered_degree}' because it's invalid.")
                    except IndexError:
                        log(f"WARNING | Skipping '{match_name}' because of an out of bounds error finding its altered degree.")

            for flat_note in flat:
                to_parse = to_parse.replace(f"flat{flat_note}", "")
            flat = list(set(flat))
            parsed += str("".join([str(flat_note) for flat_note in flat]))
            for sharp_note in sharp:
                to_parse = to_parse.replace(f"sharp{sharp_note}", "")
            sharp = list(set(sharp))
            parsed += str("".join([str(sharp_note) for sharp_note in sharp]))
            for sus_note in sus:
                to_parse = to_parse.replace(f"sus{sus_note}", "")
            sus = list(set(sus))
            parsed += str("".join([str(sus_note) for sus_note in sus]))

        """ parse added """

        if to_parse:
            added_symbol = "add"
            matches = [(
                i, to_parse[i: i + len(added_symbol)]
            ) for i in findall(added_symbol, to_parse)]

            for match in matches:
                match_index = match[0]
                match_name = match[1]

                try:
                    added_degree = to_parse[match_index + len(match_name)]
                    if added_degree.isdigit():
                        if added_degree == "1":
                            try:
                                added_degree = f"{added_degree}{int(to_parse[match_index + len(match_name) + 1])}"
                                if int(to_parse[match_index + len(match_name) + 1]) < len(CHORD_DEGREE_NAMES):
                                    added.append(int(added_degree))
                            except IndexError or ValueError:
                                log(f"WARNING | '{match_name}{added_degree}' is not a valid degree alteration.")
                                continue
                            except ValueError:
                                log(f"WARNING | '{match_name}{added_degree}' is not a valid degree alteration.")
                                continue
                        else:
                            try:
                                if added_degree != "0" and not to_parse[match_index + len(match_name) + 1].isdigit():
                                    added.append(int(added_degree))
                            except Exception:
                                continue
                    else:
                        log(f"WARNING | Skipping '{match_name}{added_degree}' because it's invalid.")
                except IndexError:
                    log(f"WARNING | Skipping '{match_name}' because of an out of bounds error finding its altered degree.")

            for added_degree in added:
                to_parse = to_parse.replace(f"add{added_degree}", "")
            added = list(set(added))
            parsed += str("".join([f"add{added_degree}" for added_degree in added]))

        """ parse bass """
        if to_parse:
            if "/" in to_parse:
                slash_index = to_parse.index("/")
                bass_symbol = to_parse[slash_index:]
                if len(bass_symbol) > 1:
                    bass_note = to_parse[slash_index + 1:]
                    if theory.is_valid_note(bass_note):
                        bass = bass_note
                    else:
                        raise Exception(f"ERROR | '{bass_symbol}' is not a valid slash chord symbol.")
                else:
                    log(f"WARNING | '{bass_symbol}' is not a valid slash chord symbol.")

        return {
            "root": root,
            "quality": quality,
            "extension": extension,
            "flat": flat,
            "sharp": sharp,
            "sus": sus,
            "added": added,
            "bass": bass
        }

    @staticmethod
    def validate_chord_quality(quality):
        if quality in ["M", "maj", "Maj"]:
            quality = "major"
        elif quality in ["m", "min", "Min"]:
            quality = "minor"
        elif quality.lower() in ["a", "aug"]:
            quality = "augmented"
        elif quality.lower() in ["d", "dim"]:
            quality = "diminished"

        if type(quality) != str or quality.lower() not in QUALITIES:
            raise Exception(f"ERROR | Quality '{quality}' provided to validate_chord_quality is invalid.")

        return quality

    def write_chord(
                self,
                root,
                quality,
                voicing=None,
                flat=None,
                sharp=None,
                sus=None,
                added=None,
                bass=None,
                measure=None,
                beat=None,
                ppq=None,
                length=None
            ):
        """
        :param root:        'C#'            name of root note
        :param quality:     'M'             quality of chord
        :param voicing:     [1, 3, 5, 7]    extension (int) or list of voice degrees to write (list)
        :param flat:        [5, 9]          voices to be flatted
        :param sharp:       [11]            voices to be sharped
        :param sus:         2 | 4           voice to replace third
        :param added:       ["add9", ...]   additional voices
        :param bass:        'A'             lowest note in the chord
        :param measure:     2               measure in song
        :param beat:        1               beat in measure
        :param ppq:         0               number of samples past beat (96 per quarter note)
        :param length:      2               length in beats
        :return:            None
        """

        quality = self.validate_chord_quality(quality)

        """ define chord class based on quality """
        if quality == "major" or "dominant":
            chord_class = MajorChord
        elif quality == "minor":
            chord_class = MinorChord
        elif quality == "augmented":
            log(f"WARNING | Quality '{quality}' provided to write_chord is not yet supported.")
            chord_class = MajorChord
        elif quality == "diminished":
            log(f"WARNING | Quality '{quality}' provided to write_chord is not yet supported.")
            chord_class = MajorChord
        else:
            raise Exception(f"ERROR | Quality '{quality}' provided to write_chord is not valid.")

        """ validate root """
        if theory.is_valid_note(root):
            chord = chord_class(root)
        else:
            raise Exception(f"ERROR | Invalid root '{root}' provided to write_chord.")

        """ validate and set voicing """
        if not voicing:
            voicing = ["root", "third", "fifth"]
        elif type(voicing) == list:
            if all(type(voice) == int for voice in voicing):
                voicing = [CHORD_DEGREE_NAMES[voice - 1] for voice in voicing]
            elif all(type(voice) == str for voice in voicing):
                voicing = [voice.lower() for voice in voicing]
        elif type(voicing) == int:
            chord_degrees = [1, 3, 5, 7, 9, 11]
            if voicing in chord_degrees:
                voicing = [
                    CHORD_DEGREE_NAMES[degree - 1] for
                    degree in
                    chord_degrees[:chord_degrees.index(voicing) + 1]
                ]
            else:
                raise Exception(f"ERROR | Voicing '{voicing}' is not yet supported by write_chord.")
        elif type(voicing) == str:
            raise Exception(f"ERROR | Strings such as '{voicing}' are not yet supported by write_chord.")
        else:
            raise Exception("ERROR | write_chord(..., voicing<list|int|str>, ...)")

        if added:
            for degree in added:
                chord_degree_name_index = (degree - 1) * ((degree - 1) > 0)
                voicing_to_add = CHORD_DEGREE_NAMES[chord_degree_name_index]
                if voicing_to_add not in voicing:
                    voicing.append(voicing_to_add)

        for alternation in [
            {"name": "flat", "list": flat},
            {"name": "sharp", "list": sharp},
            {"name": "sus", "list": sus}
        ]:
            for degree in alternation["list"]:
                chord_degree_name_index = (degree - 1) * ((degree - 1) > 0)
                chord_degree_name = CHORD_DEGREE_NAMES[chord_degree_name_index]
                if chord_degree_name not in voicing:
                    voicing.append(chord_degree_name)
                if alternation["name"] == "flat":
                    interval = -1
                elif alternation["name"] == "sharp":
                    interval = 1
                else:
                    chord_degree_name = CHORD_DEGREE_NAMES[2]
                    interval = -1 if degree == 2 else 1
                    if "third" in voicing:
                        voicing.remove("third")

                modified_note = theory.get_note_by_interval(
                    getattr(chord, chord_degree_name),
                    interval
                )
                setattr(chord, chord_degree_name, modified_note)

        notes_to_write = [
            getattr(
                chord,
                "root" if voice.lower() == "first" else voice.lower()
            ) for voice in voicing
        ]
        notes_to_write = sorted(list(set(notes_to_write)), key=lambda name: notes_to_write.index(name))

        for note in notes_to_write:
            if not theory.has_octave(note):
                note = f"{note}4"
            self.write_note(note, measure, beat, ppq, length)

    def write_chord_symbol(self, symbol, measure=None, beat=None, ppq=None, length=None):
        """
        Take the output of parse_chord_symbol and provide it to write_chord.

        :param symbol:          bbmaj11flat5add12sus4flat2add9add16/Ab
        :param measure:         1
        :param beat:            1
        :param ppq:             0
        :param length:          1
        :return:                None
        """
        chord_data = self.parse_chord_symbol(symbol)
        self.write_chord(
            root=chord_data["root"],
            quality=chord_data["quality"],
            voicing=chord_data["extension"],
            flat=chord_data["flat"],
            sharp=chord_data["sharp"],
            sus=chord_data["sus"],
            added=chord_data["added"],
            bass=chord_data["bass"],
            measure=measure,
            beat=beat,
            ppq=ppq,
            length=length
        )
