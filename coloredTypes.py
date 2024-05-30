from dataclasses import dataclass

@dataclass
class ColoredCharacter:
    character: str
    color: tuple[int, int, int]


@dataclass
class ColoredCharacterLine:
    characters: list[ColoredCharacter]


@dataclass
class ColoredCharacterFrame:
    lines: list[ColoredCharacterLine]