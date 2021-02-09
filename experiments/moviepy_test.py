# https://github.com/Zulko/moviepy
# use: python moviepy_test.py -i https://videoURL.mp4 -o ./test.webm

from moviepy.editor import *
import argparse

def main():
    parser = argparse.ArgumentParser()

    # start of arguments
    parser.add_argument('-i', '--input', required=True, help='video URL required')

    parser.add_argument('-o', '--output', required=True, help='output path with file name requrired')
    # end of arguments

    args = parser.parse_args()
    return args

if __name__ == "__main__":

    args = main()
    video_url = args.input
    output_path = args.output

    print("Loading video from URL...")
    video = VideoFileClip(video_url)
    print("Creating a subclip...")
    video_clip = video.subclip(3,5)
    print("Writing the output file to:", output_path)
    video_clip.write_videofile(output_path,fps=25)