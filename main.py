from moviepy.editor import *
from PIL import Image
import numpy as np
import time
import math
import cv2
from cv2.typing import MatLike

from colors import getColorCharacter
from processing import assembleVideo

start = time.time()
# imageName = "cube.jpg"
# imageName = "landscape.webp"
videoName = "assets/flowers2.mp4"


videoCapture = cv2.VideoCapture(videoName)

videoWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
videoHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
videoLength = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT) / videoCapture.get(
    cv2.CAP_PROP_FPS
)

# constantWidth = 320

# Scale image by a factor or by max width, maxWidth takes priority
scaleFactor = 1 / 6
maxWidth = 320  # 400

if maxWidth != None:
    scaleFactor = 1 / (videoWidth / maxWidth)

# Scale the image by a defined factor
newWidth = math.floor(videoWidth * scaleFactor)
newHeight = math.floor(videoHeight * scaleFactor * 0.4)

print(f"Video size: {videoWidth}x{videoHeight}")

frames: list[MatLike] = []

success, frame = videoCapture.read()
while success:
    frame = cv2.resize(frame, (newWidth, newHeight))
    frames.append(frame)
    success, frame = videoCapture.read()

print(len(frames))

outputFrames: list[str] = []

for frame in frames:
    output = ""
    for y in range(newHeight):
        for x in range(newWidth):
            # pixel = videoCapture.getpixel([x, y])
            # [r, g, b] = pixel[:3]
            pixel = frame[y, x]
            [b, g, r] = pixel[:3]

            output += getColorCharacter(r, g, b)

        # New line
        output += "\n"

    outputFrames.append(output)

    break


assembleVideo(outputFrames)

print(f"Processing took {round(time.time() - start, 3)}s")
print(f"Wrote output to output.txt")

# Write the ascii output to output.txt
with open("output.txt", "w", encoding="utf-8") as file:
    file.write(outputFrames[0])
