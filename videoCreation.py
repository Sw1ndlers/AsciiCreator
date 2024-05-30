import time
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2
from cv2.typing import MatLike
import threading

from coloredTypes import ColoredCharacterFrame

# Create a black image
imageSize = (1920, 1080)

# image = Image.new("RGB", (imageSize[0], imageSize[1]), color="black")
# imageDraw = ImageDraw.Draw(image)

fontSize = None
font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", 1)

framesLock = threading.Lock()
completedFrames = 0

finalVideoWidth = None
finalVideoHeight = None

characterWidth = None
characterHeight = None


def pillowToMat(image: Image) -> MatLike:
    imageNumpy = np.array(image)
    imageBGR = cv2.cvtColor(imageNumpy, cv2.COLOR_RGB2BGR)

    return imageBGR


def setFontSize(text: str) -> None:
    global fontSize, font, fullText

    fontSize = 1

    while True:
        textLength = font.getlength(text)

        if textLength >= imageSize[0]:
            fontSize -= 0.1
            font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", fontSize)

            return

        fontSize += 0.1
        font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", fontSize)


def setupGlobals(text: str) -> None:
    global finalVideoWidth, finalVideoHeight, characterWidth, characterHeight

    setFontSize(text.split("\n")[0])

    textSplit = text.split("\n")

    characterWidth = font.getlength("A")
    characterHeight = font.getlength("A", direction="ttb")

    horizontalTextLength = font.getlength(textSplit[0])
    verticalTextLength = font.getlength("A" * len(textSplit), direction="ttb")

    finalVideoWidth = int(horizontalTextLength)
    finalVideoHeight = int(verticalTextLength) * 1.3

    print(f"Final video size: {finalVideoWidth}x{finalVideoHeight}")


def createFrameColored(frame: ColoredCharacterFrame, matFrames, i: int) -> MatLike:
    global completedFrames

    image = Image.new("RGB", (finalVideoWidth, finalVideoHeight), color="black")

    imageDraw = ImageDraw.Draw(image)

    y = 0
    for line in frame.lines:
        x = 0

        for character in line.characters:
            imageDraw.text(
                (x, y), text=character.character, fill=character.color, font=font
            )
            x += characterWidth

        y += characterHeight

    imageBGR = pillowToMat(image)

    with framesLock:
        matFrames[i] = imageBGR
        completedFrames += 1
        
        print(f"\rFrame {completedFrames}/{len(matFrames)}", end="")


def createFrame(text: str, matFrames, i: int) -> MatLike:
    global completedFrames

    image = Image.new("RGB", (finalVideoWidth, finalVideoHeight), color="black")

    imageDraw = ImageDraw.Draw(image)
    imageDraw.text((0, 0), text, (255, 255, 255), font=font)

    imageBGR = pillowToMat(image)

    with framesLock:
        matFrames[i] = imageBGR
        completedFrames += 1

    print(f"\rFrame {completedFrames}/{len(matFrames)}", end="")


def createFrames(inputFrames: list[str] | list[ColoredCharacterFrame], colored: bool, sampleFrame) -> list[MatLike]:
    matFrames = [None] * len(inputFrames)
    threads = []

    start = time.time()
    print("Creating frames from text...")

    setupGlobals(sampleFrame)

    for i, frame in enumerate(inputFrames):
        # thread = threading.Thread(target=createFrame, args=(textFrame, matFrames, i))
        if colored:
            thread = threading.Thread(
                target=createFrameColored, args=(frame, matFrames, i)
            )
        else:
            thread = threading.Thread(target=createFrame, args=(frame, matFrames, i))

        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("\nCreated frames from text in ", round(time.time() - start, 2), "seconds\n")


    return matFrames


def assembleVideo(textFrames: list[str], colored: bool, sampleFrame: str=None) -> None:
    frames = createFrames(textFrames, colored, sampleFrame)

    print("Writing frames to video...", end="")

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    videoWriter = cv2.VideoWriter(
        "output.avi", fourcc, 30, (finalVideoWidth, finalVideoHeight)
    )

    for matFrame in frames:
        videoWriter.write(matFrame)

    videoWriter.release()
    print("\rWrote frames to video                ")


# read output.txt to get the text
# outputFile = open("output.txt", "r")
# outputText = outputFile.read()
# outputFile.close()

# # Create a frame with the text
# frame = createFrame(outputText)

# # Display the frame
# cv2.imshow("Frame", frame)
# cv2.waitKey(0)

# imageDraw.text((0, 0), "X" * 320, (255, 255, 255), font=font)
# image.show()
