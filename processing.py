from moviepy.editor import *
from moviepy.config import change_settings
from PIL import ImageFont, ImageDraw, Image

change_settings(
    {
        "IMAGEMAGICK_BINARY": r"C:\Users\lisiale27\Downloads\ImageMagick-7.1.1-32-portable-Q16-HDRI-x64\ImageMagick-7.1.1-32-portable-Q16-HDRI-x64\magick.exe"
    }
)

size = (1920, 1080)

characterWidth = 6
text = "X" * int(1920 // characterWidth)
print(len(text))

background = ColorClip(size=size, color=(255, 255, 255))
background = background.set_duration(1)

def assembleVideo(textFrames: list[str]):
    # frames = []
    clips = []
    
    split = textFrames[0].split("\n")
    for i, row in enumerate(split):
        # print(row)

        if row == "":
            print("Empty row")
            continue

        textClip = (
            TextClip(row, font="Arial", fontsize=9, color="black", size=size)
            .set_position((0, (-size[1] / 2) + ((i + 1) * 10)))
            .set_duration(1)
            
        )
        clips.append(textClip)

        print(f"{i}/{len(split)}")

    video = CompositeVideoClip([background, *clips])
    video.write_videofile("output.mp4", fps=24)



# clips = 

# textClip = (
#     TextClip(text, font="Arial", fontsize=9, color="black", size=size)
#     .set_position((0, (-size[1] / 2) + 4))
#     .set_duration(1)
# )



# video = CompositeVideoClip([background, textClip])
# video.write_videofile("output.mp4", fps=24)
