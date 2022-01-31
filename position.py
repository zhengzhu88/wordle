from typing import List

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


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


def generate_regex_from_positions(positions: List[Position]) -> str:
    return "".join([pos.get_regex_string() for pos in positions]) + "\n"
