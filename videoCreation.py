import time
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2
from cv2.typing import MatLike
import threading


# Create a black image
imageSize = (1920, 1080)

# image = Image.new("RGB", (imageSize[0], imageSize[1]), color="black")
# imageDraw = ImageDraw.Draw(image)

# fontSize = None
# font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", 1)

# framesLock = threading.Lock()
# completedFrames = 0

# finalVideoWidth = None
# finalVideoHeight = None

# characterWidth = None
# characterHeight = None

backgroundColor = (255, 255, 255)
textColor = (0, 0, 0)

def pillowToMat(image: Image) -> MatLike:
    imageNumpy = np.array(image)
    imageBGR = cv2.cvtColor(imageNumpy, cv2.COLOR_RGB2BGR)

    return imageBGR


class TextToVideo:
    def __init__(self):
        self.fontSize = None
        self.font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", 1)

        self.framesLock = threading.Lock()
        self.completedFrames = 0

        self.finalVideoWidth = None
        self.finalVideoHeight = None

        self.characterWidth = None
        self.characterHeight = None


    def setFontSize(self, text: str) -> None:
        self.fontSize = 1

        while True:
            textLength = self.font.getlength(text)

            if textLength >= imageSize[0]:
                self.fontSize -= 0.1
                self.font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", self.fontSize)

                return

            self.fontSize += 0.1
            self.font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", self.fontSize)

    def setFinalVideoSize(self, text: str) -> None:
        textSplit = text.split("\n")

        self.characterWidth = self.font.getlength("A")
        self.characterHeight = self.font.getlength("A", direction="ttb")

        horizontalTextLength = self.font.getlength(textSplit[0])
        verticalTextLength = self.font.getlength("A" * len(textSplit), direction="ttb")

        self.finalVideoWidth = int(horizontalTextLength)
        self.finalVideoHeight = int(verticalTextLength) 

        print(f"Final video size: {self.finalVideoWidth}x{self.finalVideoHeight}")

    def createFrame(self, text: str, matFrames, index: int) -> MatLike:
        image = Image.new("RGB", (self.finalVideoWidth, self.finalVideoHeight), color=backgroundColor)

        imageDraw = ImageDraw.Draw(image)
        imageDraw.text((0, 0), text, textColor, font=self.font)

        imageBGR = pillowToMat(image)

        with self.framesLock:
            matFrames[index] = imageBGR
            self.completedFrames += 1

        print(f"\rFrame {self.completedFrames}/{len(matFrames)}", end="")

    def createFrames(self, textFrames: list[str]) -> list[MatLike]:
        matFrames = [None] * len(textFrames)
        threads = []

        start = time.time()
        print("Creating frames from text...")

        self.setFontSize(textFrames[0])
        self.setFinalVideoSize(textFrames[0])

        for i, frame in enumerate(textFrames):
            thread = threading.Thread(target=self.createFrame, args=(frame, matFrames, i))

            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        print("\nCreated frames from text in ", round(time.time() - start, 2), "seconds\n")

        return matFrames

    def assembleVideo(self, textFrames: list[str]) -> None:
        frames = self.createFrames(textFrames)

        print("Writing frames to video...", end="")

        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        videoWriter = cv2.VideoWriter(
            "output.avi", fourcc, 30, (self.finalVideoWidth, self.finalVideoHeight)
        )

        for matFrame in frames:
            videoWriter.write(matFrame)

        videoWriter.release()
        print("\rWrote frames to video", " " * 20)


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
