from PIL import Image
import numpy as np
import time
import math
import cv2
from cv2.typing import MatLike
import threading
import os
from multiprocessing import Pool

from colors import getColorCharacter
from videoCreation import TextToVideo
from videoProcessing import resizeVideo


videoName = "assets/bird.mp4"
# videoName = "assets/waterfall.mp4"
# videoName = "assets/rotatecube.mov"
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
maxWidth = 800  # 200, 320, 600

if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Scale the image by a defined factor
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

print(f"Video size: {videoWidth}x{videoHeight}")

print(f"Resizing video to: {newWidth}x{newHeight}", end="")
resizedFrames = resizeVideo(videoCapture, newWidth, newHeight)
print(f"\rResized video to: {newWidth}x{newHeight}     \n")


framesLength = len(resizedFrames)


class FramesToText:
    def __init__(self):
        self.outputFrames = [None] * framesLength
        self.coloredOutputFrames = [None] * framesLength
        self.completedFrames = 0

        self.outputLock = threading.Lock()
        self.threads = []

    def frameToText(self, frame: MatLike, i: int, returnOutput=False):
        output = ""
        for y in range(newHeight):
            for x in range(newWidth):
                pixel = frame[y, x]
                [b, g, r] = pixel[:3]

                output += getColorCharacter(r, g, b)

            output += "\n"

        if returnOutput:
            return output

        # with self.outputLock:
        self.outputFrames[i] = output
        self.completedFrames += 1

        print(f"\rCompleted frames: {self.completedFrames}/{framesLength}", end="")

    def generateText(self) -> list[str]:
        start = time.time()
        print("Converting frames to text...")

        for i, frame in enumerate(resizedFrames):
            thread = threading.Thread(target=self.frameToText, args=(frame, i))

            thread.start()
            self.threads.append(thread)

        for thread in self.threads:
            thread.join()

        print(
            "\nConverted frames to text in", round(time.time() - start, 2), "seconds \n"
        )

        return self.outputFrames




# 202.58 seconds

frameTextGenerator = FramesToText()
outputFrames = frameTextGenerator.generateText()

# assembleVideo(outputFrames)
textToVideo = TextToVideo()
textToVideo.assembleVideo(outputFrames)