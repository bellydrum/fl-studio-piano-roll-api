from flpianoroll import *

from constants import ACCIDENTALS, INTERVAL_NAMES, NOTES


class Theory:
    @staticmethod
    def is_valid_note(name):
        """
        :param name:    C
        :return:        True

        :param name:    C#
        :return:        True

        :param name:    Cb4
        :return:        True

        :param name:    C#4
        :return:        True

        :param name:    C10
        :return:        False

        :param name:     C4#
        :return:        False

        :param name:    H
        :return:        False

        :param name:    C-#4
        :return:        False
        """
        note_is_valid = False

        if type(name) is not str:
            raise Exception("ERROR | is_valid_note(name=<str>)")
        if not len(name):
            raise Exception("WARNING | is_valid_note was provided an empty string.")

        if name[0].upper() in NOTES:
            if len(name) == 1:
                note_is_valid = True
            elif len(name) == 2:
                if (name[1].isdigit() and int(name[1]) in range(10)) or name[1] in ACCIDENTALS:
                    note_is_valid = True
            elif len(name) == 3:
                if name[1] in ACCIDENTALS and (name[2].isdigit() and int(name[2]) in range(10)):
                    note_is_valid = True

        return note_is_valid

    @staticmethod
    def has_octave(name):
        """
        :param name:    C#4 flat 7
        :return:        True

        :param name:    C# flat 7
        :return:        False
        """
        has_octave_number = False
        if len(name) in [2, 3]:
            has_octave_number = name[-1].isdigit()
        elif len(name) > 3:
            has_octave_number = name[1].isdigit() or (name[1] == "#" and name[2].isdigit())

        return has_octave_number

    @staticmethod
    def has_accidental(name):
        """
        :param name:    C#4 flat 7
        :return:        True

        :param name:    C4 flat 7
        :return:        False

        :param name:    C#M7#6
        :return:        True

        :param name:    CM7#6
        :return:        False
        """
        return name[1] in ACCIDENTALS if len(name) > 1 else False

    @staticmethod
    def extract_octave(name):
        """
        :param name:    C#4 flat 7
        :return:        ['C#', 4]
        """
        octave = None

        for char in name:
            if char.isdigit():
                octave = int(char)
                char_index = name.index(char)
                name = name[:char_index] + name[char_index + 1:]
                break

        return [name, octave]

    def get_chord_root_from_name(self, name):
        """
        :param name:    CM7
        :return:        C
        :param name:    C#m7
        :return:        C#
        """
        has_accidental_sign = self.has_accidental(name)
        has_octave_number = self.has_octave(name)

        name_length = 1
        if (has_accidental_sign and not has_octave_number) or (not has_accidental_sign and has_octave_number):
            name_length = 2
        if has_accidental_sign and has_octave_number:
            name_length = 3

        return name[:name_length]

    def get_interval(self, note_a, note_b):
        """
        :param note_a:      C#4
        :param note_b:      D5
        :return:            [13, 'minor ninth']
        """
        if not all([self.has_octave(note) for note in [note_a, note_b]]):
            note_a_has_octave = self.has_octave(note_a)
            note_b_has_octave = self.has_octave(note_b)
            if not (not note_a_has_octave and not note_b_has_octave):
                if not note_a_has_octave:
                    note_a = f"{note_a}{str(self.extract_octave(note_b)[1])}"
                else:
                    note_b = f"{note_b}{str(self.extract_octave(note_a)[1])}"

        note_a = note_a.upper()
        note_b = note_b.upper()

        note_a_name, note_a_octave = self.extract_octave(note_a)
        note_b_name, note_b_octave = self.extract_octave(note_b)

        index_a = NOTES.index(note_a_name)
        index_b = NOTES.index(note_b_name)

        if note_a_octave == note_b_octave:
            delta = max(index_a, index_b) - min(index_a, index_b)
        else:
            note_a_is_higher = max(note_a_octave, note_b_octave) == note_a_octave
            higher_note = note_a if note_a_is_higher else note_b
            lower_note = note_b if note_a_is_higher else note_a
            lower_note_name = note_b_name if note_a_is_higher else note_a_name
            lower_note_octave = note_b_octave if note_a_is_higher else note_a_octave

            current_note = lower_note
            current_note_name = lower_note_name
            current_note_octave = lower_note_octave

            interval_accumulator = 0
            infinite_loop_protection = 0

            while current_note != higher_note and infinite_loop_protection < 108:
                interval_accumulator += 1
                current_note_name = NOTES[(NOTES.index(current_note_name) + 1) % len(NOTES)]
                if current_note_name.upper() == "C":
                    current_note_octave += 1
                current_note = f"{current_note_name}{current_note_octave}"
                infinite_loop_protection += 1

            delta = interval_accumulator

        if delta < len(INTERVAL_NAMES):
            interval_name = INTERVAL_NAMES[delta]
        else:
            number_of_octaves = delta // 12
            inversion_interval = delta - (number_of_octaves * 12)
            reduced_interval_name = INTERVAL_NAMES[inversion_interval]
            if reduced_interval_name == INTERVAL_NAMES[0]:
                reduced_interval_name_display = ""
            else:
                reduced_interval_name_display = f" + {reduced_interval_name}"
            interval_name = f"{number_of_octaves} octaves{reduced_interval_name_display}"

        return [delta, interval_name]

    def get_note_by_interval(self, root_note, interval):
        """
        :param root_note:       C4
        :param interval:        7
        :return:                G4
        """
        """ handle case where root_note has no octave """
        if not self.has_octave(root_note):
            root_note = f"{root_note}4"
            no_octave_flag = True
        else:
            no_octave_flag = False

        """ handle case where interval is an interval name"""
        if type(interval) == str:
            interval = interval.lower()
            if interval in INTERVAL_NAMES:
                interval = INTERVAL_NAMES.index(interval)
            else:
                raise Exception("ERROR | Provided interval is not recognized.")

        notes_list = [note for note in NOTES]
        if interval < 0:
            notes_list.reverse()

        root_name, root_octave = self.extract_octave(root_note)
        if root_name.lower() == "ab":
            root_name = "G#"
        elif root_name.lower() == "bb":
            root_name = "A#"
        elif root_name.lower() == "cb":
            root_name = "B"
        elif root_name.lower() == "db":
            root_name = "C#"
        elif root_name.lower() == "eb":
            root_name = "D#"
        elif root_name.lower() == "fb":
            root_name = "E"
        elif root_name.lower() == "gb":
            root_name = "F#"
        root_index = notes_list.index(root_name)

        destination_note = None
        destination_octave = root_octave

        for i in range(abs(interval) + 1):
            current_note_index = (root_index + i) % len(notes_list)
            current_note_name = notes_list[current_note_index]

            octave_note_switch = "C" if interval >= 0 else "B"

            if current_note_name == octave_note_switch and i != 0:
                destination_octave = destination_octave + 1 if interval >= 0 else destination_octave - 1

            destination_note = f"{current_note_name}{str(destination_octave) if not no_octave_flag else ''}"

        return destination_note
