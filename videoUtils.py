import cv2
from cv2.typing import MatLike
from PIL import ImageFont, ImageDraw, Image
import cv2
from cv2.typing import MatLike
import numpy as np

# Resize a video given a cv2 video capture
def resizeVideo(
    videoCapture: cv2.VideoCapture, newWidth: int, newHeight: int
) -> list[MatLike]:
    resizedFrames: list[MatLike] = []

    success, frame = videoCapture.read()
    while success:
        frame = cv2.resize(frame, (newWidth, newHeight))
        resizedFrames.append(frame)
        success, frame = videoCapture.read()

    return resizedFrames

# Convert a PIL image to an OpenCV Mat
def pillowToMat(image: Image) -> MatLike:
    imageNumpy = np.array(image)
    imageBGR = cv2.cvtColor(imageNumpy, cv2.COLOR_RGB2BGR)
    return imageBGR
