# https://github.com/Zulko/moviepy
# use: python moviepy_experiment.py -i https://videoURL.mp4 -s 1000 -e 1005 -o ./test.webm -fr 30

import argparse

from moviepy.editor import VideoFileClip


def main():
    parser = argparse.ArgumentParser()

    # start of arguments
    parser.add_argument("-i", "--input", required=True, help="video URL required")
    parser.add_argument(
        "-s", "--start", required=True, help="start time (seconds) required"
    )
    parser.add_argument(
        "-e", "--end", required=True, help="end time (seconds) required"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="output path with file name requrired"
    )
    parser.add_argument("-fr", "--fps", required=True, help="FPS required")
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
    video_clip = video.subclip(int(args.start), int(args.end))
    print("Writing the output file to:", output_path)
    video_clip.write_videofile(
        output_path, fps=int(args.fps), verbose=False, logger=None
    )
    print("Process completed...")
