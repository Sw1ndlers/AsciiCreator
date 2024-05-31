from PIL import Image
import numpy as np
import time
import math
import cv2
from cv2.typing import MatLike
import threading
import os
from multiprocessing import Pool
import multiprocessing

from colors import getColorCharacter
from videoCreation import TextToVideo
from videoProcessing import resizeVideo


videoName = "assets/waterfall.mp4"
# videoName = "assets/flowers2.mp4"
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
maxWidth = 600  # 200, 320, 600

if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Scale the image by a defined factor
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

print(f"Video size: {videoWidth}x{videoHeight}")

print(f"Resizing video to: {newWidth}x{newHeight}", end="", flush=True)

resizedFrames = resizeVideo(videoCapture, newWidth, newHeight)
print(f"\rResized video to: {newWidth}x{newHeight}     \n")


framesLength = len(resizedFrames)


class FramesToText:
    def __init__(self):
        self.manager = multiprocessing.Manager()

        self.outputFrames = self.manager.list([None] * framesLength)
        self.completedFrames = multiprocessing.Value("i", 0)

        self.processes = []


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

        self.outputFrames[i] = output

        with self.completedFrames.get_lock():
            self.completedFrames.value += 1
            print(f"\rCompleted frames: {self.completedFrames.value}/{framesLength}", end="")

    def generateText(self) -> list[str]:
        start = time.time()
        print("Converting frames to text...")

        for i, frame in enumerate(resizedFrames):
            process = multiprocessing.Process(target=self.frameToText, args=(frame, i))
            process.start()

            self.processes.append(process)

        for process in self.processes:
            process.join()

        print(
            "\nConverted frames to text in", round(time.time() - start, 2), "seconds \n"
        )

        return self.outputFrames

frameTextGenerator = FramesToText()
outputFrames = frameTextGenerator.generateText()

time.sleep(5) # Let cpu cool down
 
textToVideo = TextToVideo()
textToVideo.assembleVideo(outputFrames)