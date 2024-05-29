import cv2
from cv2.typing import MatLike

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
