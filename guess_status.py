from enum import Enum


class GuessStatus(Enum):
    CONFIRMED = 1
    DECONFIRMED = 2
    WRONG_POSITION = 3
    INVALID_CHARACTER = 4


def map_letter_to_status(char: str) -> GuessStatus:
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
