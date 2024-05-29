characterGradient = reversed(" `^\",:;Il!i~+_-?][}{)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$")
characterGradient = '@%#*+=-:. '


length = len(characterGradient)

# Create a color range of [number, character] where number is the brightness mapping to the character
# Reverse the characters, darkest -> brightest
characterMap = [
    [(i / (length - 1)) * 255, character] for i, character in enumerate(characterGradient)
]
