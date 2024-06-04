import time
import math
import cv2
from cv2.typing import MatLike
import os
import multiprocessing

from colors import getColorCharacter
from videoCreation import TextToVideo
from videoProcessing import resizeVideo

videoPath = None
while videoPath == None or not os.path.exists(videoPath):
    videoPath = input("Enter the path to the video file: ")
print("")

videoCapture = cv2.VideoCapture(videoPath)

# Check if the video file exists
if not os.path.exists(videoPath):
    print("Error: Video does not exist")
    exit()

# Check if the video can be opened
if not videoCapture.isOpened():
    print("Error: Video could not be opened")
    exit()

videoName = os.path.splitext(os.path.basename(videoPath))[0]

# Get original video dimensions
videoWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
videoHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Define scaling parameters
scaleFactor = 1 / 6
maxWidth = 320  # Max width takes priority

# Adjust scale factor if maxWidth is defined
if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Calculate new dimensions
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

print(f"Video size: {videoWidth}x{videoHeight}")
print(f"Resizing video to: {newWidth}x{newHeight}", end="", flush=True)

# Resize video frames
resizedFrames = resizeVideo(videoCapture, newWidth, newHeight)
print(f"\rResized video to: {newWidth}x{newHeight}     \n")

framesLength = len(resizedFrames)


# Class to convert video frames to text
class FramesToText:
    def __init__(self):
        self.manager = multiprocessing.Manager()

        # Create a list to store output frames
        self.outputFrames = self.manager.list([None] * framesLength)
        self.completedFrames = multiprocessing.Value("i", 0)

        self.processes = []

    # Convert a single frame to text
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

        # Store the text representation of the frame
        self.outputFrames[i] = output

        # Update the count of completed frames
        with self.completedFrames.get_lock():
            self.completedFrames.value += 1
            print(
                f"\rCompleted frames: {self.completedFrames.value}/{framesLength}",
                end="",
            )

    # Generate text for all frames
    def generateText(self) -> list[str]:
        start = time.time()
        print("Converting frames to text...")

        # Start a process for each frame
        for i, frame in enumerate(resizedFrames):
            process = multiprocessing.Process(target=self.frameToText, args=(frame, i))
            process.start()

            self.processes.append(process)

        # Wait for all processes to complete
        for process in self.processes:
            process.join()

        print(
            "\nConverted frames to text in", round(time.time() - start, 2), "seconds \n"
        )

        return self.outputFrames


# Generate text from frames
frameTextGenerator = FramesToText()
outputFrames = frameTextGenerator.generateText()

# Convert text frames to a video
textToVideo = TextToVideo()
textToVideo.assembleVideo(outputFrames, videoName)
