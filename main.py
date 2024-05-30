
from PIL import Image
import numpy as np
import time
import math
import cv2
from cv2.typing import MatLike
import threading
import os

from coloredTypes import ColoredCharacter, ColoredCharacterFrame, ColoredCharacterLine
from colors import getColorCharacter
from videoCreation import assembleVideo
from videoProcessing import resizeVideo


# videoName = "assets/flowers2.mp4"
# videoName = "assets/waterfall.mp4"
videoName = "assets/rotatecube.mov"
videoCapture = cv2.VideoCapture(videoName)

if not os.path.exists(videoName):
    print("Error: Video does not exist")
    exit()

if not videoCapture.isOpened():
    print("Error: Video could not be opened")
    exit()

videoWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
videoHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Scale image by a factor or by max width, maxWidth takes priority
scaleFactor = 1 / 6
# maxWidth = 200
maxWidth = 320
# maxWidth = 600

if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Scale the image by a defined factor
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

coloredText = False

print(f"Video size: {videoWidth}x{videoHeight}")

print(f"Resizing video to: {newWidth}x{newHeight}", end="")
resizedFrames = resizeVideo(videoCapture, newWidth, newHeight)
print(f"\rResized video to: {newWidth}x{newHeight}     \n")

outputFrames: list[str] = [None] * len(resizedFrames)
coloredOutputFrames: list[ColoredCharacterFrame] = [None] * len(resizedFrames)
completedFrames = 0

outputLock = threading.Lock()
threads = []

framesLength = len(resizedFrames)


def frameToText(frame: MatLike, i: int, returnOutput=False):
    global completedFrames

    output = ""
    for y in range(newHeight):
        for x in range(newWidth):
            pixel = frame[y, x]
            [b, g, r] = pixel[:3]

            output += getColorCharacter(r, g, b)

        output += "\n"

    if returnOutput:
        return output

    with outputLock:
        outputFrames[i] = output
        completedFrames += 1

        print(f"\rCompleted frames: {completedFrames}/{framesLength}", end="")


def frameToTextColored(frame: MatLike, i: int):
    global completedFrames

    coloredOutputFrame = ColoredCharacterFrame(lines=[])

    for y in range(newHeight):
        line = ColoredCharacterLine(characters=[])

        for x in range(newWidth):
            pixel = frame[y, x]
            [b, g, r] = pixel[:3]

            line.characters.append(
                ColoredCharacter(character=getColorCharacter(r, g, b), color=(r, g, b))
            )

        coloredOutputFrame.lines.append(line)

    with outputLock:
        coloredOutputFrames[i] = coloredOutputFrame
        completedFrames += 1

        print(f"\rCompleted frames: {completedFrames}/{framesLength}", end="")


start = time.time()
print("Converting frames to text...")

for i, frame in enumerate(resizedFrames):
    if coloredText:
        thread = threading.Thread(target=frameToTextColored, args=(frame, i))
    else:
        thread = threading.Thread(target=frameToText, args=(frame, i))

    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("\nConverted frames to text in", round(time.time() - start, 2), "seconds \n")



# print(outputFrames)
# assembleVideo(outputFrames, True, sampleFrame)

if coloredText:
    sampleFrame = frameToText(resizedFrames[0], 0, True)
    assembleVideo(coloredOutputFrames, True, sampleFrame)
else:
    assembleVideo(outputFrames, False, outputFrames[0])
