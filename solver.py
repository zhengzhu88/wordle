#!/usr/bin/python3
import sys, getopt
from collections import Counter
from typing import List, Dict, Tuple, Optional
from guess_status import GuessStatus, map_symbol_to_status
from position import Position, generate_regex_from_positions

import re
import os

try:
    from tkinter import *

    VISUAL_MODE = True
    if os.environ.get('DISPLAY', '') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')
except ImportError:
    VISUAL_MODE = False

MAX_NUM_WORDS_TO_DISPLAY = 10


def word_contains_known_letters(word: str, known_letters: Dict[str, int]) -> bool:
    counter = Counter(word)
    for letter, count in known_letters.items():
        if count > counter[letter]:
            return False
    return True


def find_matches_in_word_list(letter_count: Dict[str, int], word_list: List[str]):
    return [word.strip() for word in word_list if word_contains_known_letters(word, letter_count)]


def match_positions_and_letters(
        positions: List[Position],
        letter_requirements: Dict[str, int],
        search_space: str) -> List[str]:
    pattern: str = generate_regex_from_positions(positions)
    # Filter out words based on letter position.
    regex_matches: List[str] = re.findall(pattern, search_space)
    # Filter out words that don't use all known letters.
    return find_matches_in_word_list(letter_requirements, regex_matches)


def merge_known_letters(known_letters_tracker: Dict[str, int], known_letters_for_word: Dict[str, int]):
    for letter, count in known_letters_for_word.items():
        known_letters_tracker[letter] = max(count, known_letters_tracker.get(letter, 0))


def get_heuristic_values(possible_words: List[str]):
    counter = Counter(''.join(possible_words))

    def word_to_heuristic_func(word: str) -> Tuple[str, int]:
        def letter_to_heuristic_func(letter: str) -> int:
            return counter.get(letter, 0)

        char_set = set(word)
        return word, sum(map(letter_to_heuristic_func, char_set))

    heuristic_values = map(word_to_heuristic_func, possible_words)
    return sorted(heuristic_values, key=lambda elem: elem[1], reverse=True)


def recommend_word(possible_words: List[str]):
    sorted_heuristics = get_heuristic_values(possible_words)
    num_words_to_print = min(len(sorted_heuristics), MAX_NUM_WORDS_TO_DISPLAY)
    if len(sorted_heuristics) > MAX_NUM_WORDS_TO_DISPLAY:
        print("Too many possible words to display. These are good words to choose from:")
    else:
        print("These are the possible remaining words:")
    for tup in sorted_heuristics[:num_words_to_print]:
        print(f"{tup[0]} with score {tup[1]}")


class Session:
    # TODO: Add a UI for setting status instead of doing text input.
    def __init__(self):
        self.known_letters = {}
        self.positions: List[Position] = [Position(), Position(), Position(), Position(), Position()]
        with open("words_alpha_length_5.txt") as dictionary:
            self.dictionary: List[str] = dictionary.read().splitlines()
        recommend_word(self.dictionary)
        self._initiate_input_loop()

    def _initiate_input_loop(self):
        iteration: int = 1
        search_space: List[str] = self.dictionary
        while iteration <= 6:
            print(f"Please enter your {iteration}-th guess and the result.")
            guess_result = input("> ").strip()
            parsed_tuple = self._parse_input(guess_result)
            if parsed_tuple is None:
                continue
            guess: str
            result: List[GuessStatus]
            guess, result = parsed_tuple
            if not self._process_guess(guess, result):
                continue
            matches: List[str] = match_positions_and_letters(self.positions, self.known_letters,
                                                             "\n".join(search_space))
            print(f"Found {len(matches)} matches:")
            if len(matches) == 1:
                print(matches[0])
                print("Congrats!")
                return
            recommend_word(matches)
            search_space = matches
            iteration += 1
        print("Better luck next time!")

    def _parse_input(self, input_str: str) -> Optional[Tuple[str, List[GuessStatus]]]:
        input_sections = input_str.split()
        num_sections = len(input_sections)
        if num_sections != 2:
            if num_sections < 2:
                print(f"Not enough inputs. Both a guess and a result string are needed.")
            if num_sections > 2:
                print(f"Too many inputs. Only input a guess and a result.")
            return None
        guess: str = input_sections[0]
        result: List[GuessStatus] = list(map(map_symbol_to_status, input_sections[1]))
        is_valid = True
        if len(guess) != 5:
            print(f"Guess {guess} was not 5 letters long.")
            is_valid = False
        if len(result) != 5:
            print(f"Result {result} was not 5 letters long.")
            is_valid = False
        if not guess.isalpha():
            print(f"Guess {guess} was not alphabetical.")
            is_valid = False
        return guess, result if is_valid else None

    def _process_guess(self, guess: str, statuses: List[GuessStatus]) -> bool:
        if GuessStatus.INVALID_CHARACTER in statuses:
            return False
        known_letters_for_word = {}
        for i in range(len(guess)):
            letter: str = guess[i]
            status: GuessStatus = statuses[i]
            if status == GuessStatus.CONFIRMED:
                self.positions[i].confirm_letter(letter=letter)
                known_letters_for_word[letter] = known_letters_for_word.get(letter, 0) + 1
            elif status == GuessStatus.DECONFIRMED:
                for pos_i in range(len(self.positions)):
                    self.positions[pos_i].deconfirm_letter(letter=letter)
            elif status == GuessStatus.WRONG_POSITION:
                self.positions[i].deconfirm_letter(letter=letter)
                known_letters_for_word[letter] = known_letters_for_word.get(letter, 0) + 1
        merge_known_letters(self.known_letters, known_letters_for_word)
        return True


def set_up_gui():
    root = Tk()
    root.title("Wordle Solver")
    frame = Frame(root, bg="black")
    frame.grid(column=0, row=0)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    stringvar_grid = []
    for y in range(6):
        stringvar_grid.append([])
        for x in range(5):
            stringvar_grid[y].append(StringVar())
            Entry(
                frame,
                bg="#101010",
                fg="white",
                width=2,
                font="Helvetica 75 bold",
                justify=CENTER,
                borderwidth=0,
                insertbackground="white",
                textvariable=stringvar_grid[y][x],
            ).grid(row=y, column=x, padx=5, pady=5)
    root.mainloop()


def main(argv):
    opts, args = getopt.getopt(argv, shortopts="", longopts=["visual_mode="])
    run_visual_mode = VISUAL_MODE
    print(run_visual_mode)
    for opt, arg in opts:
        if opt == "--visual_mode":
            run_visual_mode = arg == "True"
    if run_visual_mode:
        print("Running Wordle solver in visual mode.")
        set_up_gui()
    else:
        print("Running Wordle solver in text mode.")
        session = Session()


# Guesses must be input in the form "guess result" where guess is the word guessed and result is a length 5 string
# of _'s, ?'s, and +'s corresponding to the positions of black, yellow, and green letters respectively.
if __name__ == "__main__":
    main(sys.argv[1:])
