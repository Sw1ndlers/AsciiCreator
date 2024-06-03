import time
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2
from cv2.typing import MatLike
import multiprocessing
import subprocess
import os

# Define image and text properties
imageSize = (1920, 1080)
backgroundColor = (0, 0, 0)
textColor = (255, 255, 255)

keepRawVideo = False
lineSpacingSubtract = 1.5


# Convert a PIL image to an OpenCV Mat
def pillowToMat(image: Image) -> MatLike:
    imageNumpy = np.array(image)
    imageBGR = cv2.cvtColor(imageNumpy, cv2.COLOR_RGB2BGR)
    return imageBGR


# Class to convert text frames to a video
class TextToVideo:
    def __init__(self):
        self.fontSize = None
        self.font = ImageFont.truetype("fonts/AnonymousPro-Regular.ttf", 1)

        self.finalVideoWidth = None
        self.finalVideoHeight = None

        self.characterWidth = None
        self.characterHeight = None

        self.manager = multiprocessing.Manager()
        self.completedFrames = multiprocessing.Value("i", 0)

        self.maxProcesses = multiprocessing.cpu_count() - 1

    # Set the appropriate font size based on the sample frame
    def setFontSize(self, sampleFrame: str) -> None:
        self.fontSize = 1
        text = sampleFrame.split("\n")[0]

        while True:
            textLength = self.font.getlength(text)
            if textLength >= imageSize[0]:
                self.fontSize -= 0.1
                self.font = ImageFont.truetype(
                    "fonts/AnonymousPro-Regular.ttf", self.fontSize
                )
                return
            self.fontSize += 0.1
            self.font = ImageFont.truetype(
                "fonts/AnonymousPro-Regular.ttf", self.fontSize
            )

    # Set the final video size based on the text dimensions
    def setFinalVideoSize(self, text: str) -> None:
        textSplit = text.split("\n")

        self.characterWidth = self.font.getlength("A")
        self.characterHeight = self.font.getlength("A", direction="ttb")

        horizontalTextLength = self.font.getlength(textSplit[0])
        verticalTextLength = self.font.getlength("A" * len(textSplit), direction="ttb")

        self.finalVideoWidth = int(horizontalTextLength)
        self.finalVideoHeight = int(verticalTextLength) - int(
            lineSpacingSubtract * len(textSplit)
        )

        print(f"Final video size: {self.finalVideoWidth}x{self.finalVideoHeight}")

    # Create a single frame from text
    def createFrame(
        self, text: str, matFrames, matFramesAmount: int, index: int
    ) -> MatLike:
        image = Image.new(
            "RGB", (self.finalVideoWidth, self.finalVideoHeight), color="black"
        )
        imageDraw = ImageDraw.Draw(image)

        # Draw text lines onto the image
        for i, line in enumerate(text.split("\n")):
            imageDraw.text(
                (0, i * (self.characterHeight - lineSpacingSubtract)),
                line,
                textColor,
                font=self.font,
            )

        imageBGR = pillowToMat(image)

        # Update the completed frame count
        with self.completedFrames.get_lock():
            matFrames[index] = imageBGR
            self.completedFrames.value += 1

        print(f"\rFrame {self.completedFrames.value}/{matFramesAmount}", end="")

    # Create frames from a list of text frames
    def createFrames(self, textFrames: list[str]) -> list[MatLike]:
        matFrames = self.manager.list([None] * len(textFrames))
        matFramesAmount = len(matFrames)

        start = time.time()
        print("Creating frames from text...")

        self.setFontSize(textFrames[0])
        self.setFinalVideoSize(textFrames[0])

        processes = []

        # Start a process for each frame
        for i, frame in enumerate(textFrames):
            process = multiprocessing.Process(
                target=self.createFrame, args=(frame, matFrames, matFramesAmount, i)
            )
            process.start()
            processes.append(process)

        # Wait for all processes to complete
        for process in processes:
            process.join()

        print(
            "\nCreated frames from text in ", round(time.time() - start, 2), "seconds\n"
        )
        return matFrames

    # Compress the raw video to a final output format
    def compressVideo(self, fileName: str) -> None:
        print("Compressing video...", end="", flush=True)

        # Compress the video using ffmpeg
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                f"output/{fileName}_raw.avi",
                f"output/{fileName}.mp4",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-nostats",
            ],
            stdout=subprocess.PIPE,
        )

        if not keepRawVideo:
            os.remove(f"output/{fileName}_raw.avi")

        print("\rCompressed video  ")

    # Assemble the final video from text frames
    def assembleVideo(self, textFrames: list[str], fileName: str) -> None:
        frames = self.createFrames(textFrames)

        print("Writing frames to video...", end="")

        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        videoWriter = cv2.VideoWriter(
            f"output/{fileName}_raw.avi",
            fourcc,
            30,
            (self.finalVideoWidth, self.finalVideoHeight),
        )

        for matFrame in frames:
            videoWriter.write(matFrame)

        videoWriter.release()
        print("\rWrote frames to video", " " * 20)

        self.compressVideo(fileName)
