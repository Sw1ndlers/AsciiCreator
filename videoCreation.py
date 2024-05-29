from io import BytesIO
import numpy as np
import math
from PIL import ImageFont, ImageDraw, Image
import cv2
from cv2.typing import MatLike
import threading

from characters import characterGradient

# Create a black image
imageSize = (1920, 1080)
# 3840.0x2160.0

image = Image.new("RGB", (imageSize[0], imageSize[1]), color="black")
imageDraw = ImageDraw.Draw(image)

fontSize = None
font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", 1)

framesLock = threading.Lock()

completedFrames = 0

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
            fontSize -= 1
            font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", fontSize)

            print(f"Using font size: {fontSize}")
            break

        fontSize += 0.1
        font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", fontSize)

def createFrame(text: str, matFrames, i: int) -> MatLike:
    global completedFrames

    if fontSize == None:
        setFontSize(text.split("\n")[0])

    image = Image.new("RGB", (imageSize[0], imageSize[1]), color="black")

    imageDraw = ImageDraw.Draw(image)
    imageDraw.text((0, 0), text, (255, 255, 255), font=font)

    imageBGR = pillowToMat(image)

    # return imageBGR
    with framesLock:
        matFrames[i] = imageBGR
        completedFrames += 1

    print(f"\rFrame {completedFrames}/{len(matFrames)}", end="")


def assembleVideo(textFrames: list[str]):
    matFrames = [None] * len(textFrames)
    threads = []

    print("Creating frames from text...")

    for i, textFrame in enumerate(textFrames):
        thread = threading.Thread(target=createFrame, args=(textFrame, matFrames, i))
        thread.start()

        threads.append(thread)

    for thread in threads:
        thread.join()

    # for i, textFrame in enumerate(textFrames):
    #     matFrames.append(createFrame(textFrame))
    #     print(f"\rFrame {i + 1}/{len(textFrames)}", end="")

    print("\nCreated frames from text")

    print("Writing frames to video...", end="")

    movieBuilder = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter("output.mp4", movieBuilder, 30, (imageSize[0], imageSize[1]))

    for matFrame in matFrames:
        video.write(matFrame)

    video.release()

    print("\rWrote frames to video   ")

    

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