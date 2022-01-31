#!/usr/bin/python3
from collections import Counter
from enum import Enum
from typing import List, Dict

import re

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class GuessStatus(Enum):
    CONFIRMED = 1
    DECONFIRMED = 2
    WRONG_POSITION = 3
    INVALID_CHARACTER = 4


class Position:
    def __init__(self):
        self.allowed_letters = set()
        for letter in ALPHABET:
            self.allowed_letters.add(letter)

    def get_regex_string(self):
        return f"[{''.join(list(self.allowed_letters))}]"

    def confirm_letter(self, letter: str):
        if len(letter) != 1:
            raise Exception(f"Cannot confirm {letter} because length is not 1")
        self.allowed_letters = set(letter)

    def deconfirm_letter(self, letter: str):
        if len(letter) != 1:
            raise Exception(f"Cannot deconfirm {letter} because length is not 1")
        self.allowed_letters.discard(letter)

    def __repr__(self):
        return self.get_regex_string()


# TODO: Add support for recommending a word when there are too many options.
# TODO: Add a UI for setting status instead of doing text input.
class Session:
    def __init__(self):
        self.known_letters = {}
        self.positions: List[Position] = [Position(), Position(), Position(), Position(), Position()]
        with open("words_alpha_length_5.txt") as dictionary:
            self.dictionary: str = dictionary.read()
        self._initiate_input_loop()

    def _initiate_input_loop(self):
        iteration: int = 1
        while iteration <= 6:
            print(f"Please enter your {iteration}-th guess and the result.")
            guess_result = input("> ").strip()
            guess, result = guess_result.split()
            if not self._validate_input(guess=guess, result=result):
                continue
            if not self._process_guess(guess, result):
                continue
            pattern: str = self._generate_regex()
            # Filter out words based on letter position.
            regex_matches: List[str] = re.findall(pattern, self.dictionary)
            # Filter out words that don't use all known letters.
            matches: List[str] = \
                [word for word in regex_matches if self._word_contains_known_letters(word, self.known_letters)]
            print(f"Found {len(matches)} matches:")
            for match in matches:
                print(match.strip())
            if len(matches) == 1:
                print("Congrats!")
                return
            iteration += 1
        print("Better luck next time!")

    def _word_contains_known_letters(self, word: str, known_letters: Dict[str, int]) -> bool:
        counter = Counter(word)
        for letter, count in known_letters.items():
            if count > counter[letter]:
                return False
        return True

    def _generate_regex(self) -> str:
        return "".join([pos.get_regex_string() for pos in self.positions]) + "\n"

    def _validate_input(self, guess: str, result: str) -> bool:
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
        return is_valid

    def _process_guess(self, guess: str, result: str) -> bool:
        statuses: List[GuessStatus] = [self._map_letter_to_status(char) for char in result]
        if GuessStatus.INVALID_CHARACTER in statuses:
            return False
        known_letters_for_word = {}
        for i in range(len(guess)):
            letter = guess[i]
            status: GuessStatus = self._map_letter_to_status(result[i])
            if status == GuessStatus.CONFIRMED:
                self.positions[i].confirm_letter(letter=letter)
                known_letters_for_word[letter] = known_letters_for_word.get(letter, 0) + 1
            elif status == GuessStatus.DECONFIRMED:
                for pos_i in range(len(self.positions)):
                    self.positions[pos_i].deconfirm_letter(letter=letter)
            elif status == GuessStatus.WRONG_POSITION:
                self.positions[i].deconfirm_letter(letter=letter)
                known_letters_for_word[letter] = known_letters_for_word.get(letter, 0) + 1
        self._merge_known_letters(known_letters_for_word)
        return True

    def _merge_known_letters(self, known_letters_for_word: Dict[str, int]):
        for letter, count in known_letters_for_word.items():
            self.known_letters[letter] = max(count, self.known_letters.get(letter, 0))

    def _map_letter_to_status(self, char: str) -> GuessStatus:
        if len(char) != 1:
            raise Exception(f"Cannot convert char {char} to a guess status.")
        if char == "_":
            return GuessStatus.DECONFIRMED
        elif char == "?":
            return GuessStatus.WRONG_POSITION
        elif char == "+":
            return GuessStatus.CONFIRMED
        print(f"{char} is not a valid status character. Please use _, ?, and +")
        return GuessStatus.INVALID_CHARACTER


# Guesses must be input in the form "guess result" where guess is the word guessed and result is a length 5 string
# of _'s, ?'s, and +'s corresponding to the positions of black, yellow, and green letters respectively.
if __name__ == "__main__":
    session = Session()
