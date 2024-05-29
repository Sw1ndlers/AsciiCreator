from PIL import Image
import numpy as np
import time
import math
import cv2
from cv2.typing import MatLike
import threading

from colors import getColorCharacter
from videoCreation import assembleVideo
from videoProcessing import resizeVideo


# videoName = "assets/rotatecube.mov"
videoName = "assets/flowers.mp4"
videoCapture = cv2.VideoCapture(videoName)

# TODO: Verify video exists and is open

videoWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
videoHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Scale image by a factor or by max width, maxWidth takes priority
scaleFactor = 1 / 6
maxWidth = 200
# maxWidth = 600

if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Scale the image by a defined factor
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

print(f"Video size: {videoWidth}x{videoHeight}")

print(f"Resizing video to: {newWidth}x{newHeight}", end="")
resizedFrames = resizeVideo(videoCapture, newWidth, newHeight)
print(f"\rResized video to: {newWidth}x{newHeight}     \n")

outputFrames: list[str] = [None] * len(resizedFrames)
completedFrames = 0

outputLock = threading.Lock()
threads = []

framesLength = len(resizedFrames)

def frameToText(frame: MatLike, i: int):
    global completedFrames

    output = ""
    for y in range(newHeight):
        for x in range(newWidth):
            pixel = frame[y, x]
            [b, g, r] = pixel[:3]

            output += getColorCharacter(r, g, b)

        output += "\n"

    with outputLock:
        outputFrames[i] = output
        completedFrames += 1

    print(f"\rCompleted frames: {completedFrames}/{framesLength}", end="")

start = time.time()
print("Converting frames to text...")

for i, frame in enumerate(resizedFrames):
    thread = threading.Thread(target=frameToText, args=(frame, i))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("\nConverted frames to text in", round(time.time() - start, 2), "seconds \n")
    


assembleVideo(outputFrames)

