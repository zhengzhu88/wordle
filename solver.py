#!/usr/bin/python3
from collections import Counter
from typing import List, Dict
from guess_status import GuessStatus, map_letter_to_status
from position import Position, generate_regex_from_positions

import re


def word_contains_known_letters(word: str, known_letters: Dict[str, int]) -> bool:
    counter = Counter(word)
    for letter, count in known_letters.items():
        if count > counter[letter]:
            return False
    return True


def find_matches_in_word_list(letter_count: Dict[str, int], word_list: List[str]):
    return [word for word in word_list if word_contains_known_letters(word, letter_count)]


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


def recommend_word(possible_words: List[str]):
    # do a letter count and recommend the word with the highest heuristic value.
    counter = Counter(''.join(possible_words))
    print(f"Sorted letter count {counter.most_common()}")


class Session:
    # TODO: Add support for recommending a word when there are too many options.
    # TODO: Add a UI for setting status instead of doing text input.
    def __init__(self):
        self.known_letters = {}
        self.positions: List[Position] = [Position(), Position(), Position(), Position(), Position()]
        with open("words_alpha_length_5.txt") as dictionary:
            self.dictionary: str = dictionary.read()
        recommend_word(self.dictionary.split())
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
            matches: List[str] = match_positions_and_letters(self.positions, self.known_letters, self.dictionary)
            print(f"Found {len(matches)} matches:")
            if len(matches) == 1:
                print(matches[0])
                print("Congrats!")
                return
            recommendations: List[str] = matches
            for word in recommendations:
                print(word.strip())
            iteration += 1
        print("Better luck next time!")

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
        statuses: List[GuessStatus] = [map_letter_to_status(char) for char in result]
        if GuessStatus.INVALID_CHARACTER in statuses:
            return False
        known_letters_for_word = {}
        for i in range(len(guess)):
            letter = guess[i]
            status: GuessStatus = map_letter_to_status(result[i])
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


# Guesses must be input in the form "guess result" where guess is the word guessed and result is a length 5 string
# of _'s, ?'s, and +'s corresponding to the positions of black, yellow, and green letters respectively.
if __name__ == "__main__":
    session = Session()
