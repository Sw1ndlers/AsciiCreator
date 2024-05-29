from characters import characterMap

# Return the brightness from a color, this method is not the mos accurate
def getColorBrightness(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

# Return the character corresponding to the color value
def getColorCharacter(r, g, b):
    pixelBrightness = getColorBrightness(r, g, b)

    # Set the starting values to the lowest brightness
    currentChar = characterMap[0][1]
    bestBrightness = 0

    for [brightness, character] in characterMap:
        # Brightness is not greater than the pixel brightness, so we havent found the highest value
        if pixelBrightness >= brightness: 
            if brightness > bestBrightness:
                # Update the values for the next iteration
                currentChar = character
                bestBrightness = brightness
        else:
            break

    return currentChar

