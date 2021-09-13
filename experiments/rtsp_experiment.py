import _thread
import datetime
import io

# import json
import os
import sys

import cv2
import requests

# from moviepy.editor import *
from PIL import Image
from requests_toolbelt.multipart.encoder import MultipartEncoder
from termcolor import colored

"""
    Original code from: https://kevinsaye.wordpress.com/2019/06/11/python-using-opencv-to-process-rtsp-video-with-threads/
    Because this reads from an RTSP source, we must keep reading the frames else we will get behind
    in the code below, if not "is_inferring", then we spin a thread to do an inferrence for the image to a remote REST server
"""

RTSPURL = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
URL = (
    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
)
INFERENCE_SERVER_URL = "http://localhost:8000/detect/"  # https://github.com/WelkinU/yolov5-fastapi-demo.git
timeout = 6  # timeout to connect to the scoring URL
is_inferring = False


def infer_image(frame):
    global is_inferring
    is_inferring = True
    try:
        image = Image.fromarray(frame)
        stream = io.BytesIO()  # creating a steam object to not write to the disk
        image.save(stream, format="JPEG")
        stream.seek(0)
        img_for_post = stream.read()

        multipart_data = MultipartEncoder(
            fields={
                "file_list": (
                    "a_frame.JPEG",  # create a pseudo file from memory
                    img_for_post,
                ),
                "model_name": (None, "yolov5s"),
                "img_size": (None, "640"),
                "download_image": (None, "false"),
            }
        )

        headers = {"Content-Type": multipart_data.content_type}

        response = requests.post(
            INFERENCE_SERVER_URL, headers=headers, data=multipart_data, timeout=timeout
        ).json()

        print(
            "\r" + "Result: %s          " % response
        )  # do something with the response from the inference server

    except Exception:
        print(Exception)
        e = sys.exc_info()[0]
        print("Unexpected error with the inference: %s" % e)
    is_inferring = False


if __name__ == "__main__":
    # cli coloring stuff
    os.system("cls" if os.name == "nt" else "clear")
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    # process only X frames
    limit = 20
    processing_count = 0
    running = True
    while running:  # outer loop to catch errors
        try:

            video = cv2.VideoCapture(URL)

            print("Camera {} status: {}".format(URL, video.isOpened()))
            total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            # video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            print("[INFO] Total frames: " + colored("%i", "green") % total_frames)
            # frame_offset = 29/30 # values must be between [0,1]
            frame_offset = 7 / 10
            start_frame = int(total_frames * frame_offset)

            print(
                "[INFO] Starting from frame: " + colored("%i", "yellow") % start_frame
            )
            print("[INFO] Seeking to the selected frame...")
            start = datetime.datetime.now()
            # video.set(cv2.CAP_PROP_POS_MSEC, 10000)
            video.set(1, start_frame)  # test, start from calculated frame
            # print("[INFO] Current frame position: ", video.get(cv2.CAP_PROP_POS_FRAMES)) # something wrong here
            # seek average time: 24 seconds
            # TODO: confirm if bandwidth limitation or OpenCV
            # no difference if we start from middle to near end
            # seek time for starting before the middle frame is a bit faster
            end = datetime.datetime.now()
            print("[INFO] Total seek time " + colored("%s", "red") % str(end - start))
            print("[INFO] Inference loop starting...")

            while True:  # inner loop for each frame
                ret, frame = video.read()
                if ret and is_inferring is False and processing_count < limit:
                    # show only processed frames
                    cv2.imshow("RTSP: %s" % URL, frame)
                    _thread.start_new_thread(infer_image, (frame,))
                    processing_count += 1
                    sys.stdout.write(
                        "\rProcessing [%i/%i] " % (processing_count, limit)
                    )
                    # if processing_count > 1:
                    sys.stdout.write("\033[F")  # back to previous line
                    sys.stdout.write("\033[K")  # clear line
                elif processing_count >= limit:
                    # stop the stream when processing limit is reached
                    running = False
                    break
                elif ret is False:
                    # TODO: add an exit clause here since this will retry the RTSP when any error occurs
                    # video.release()
                    # video = cv2.VideoCapture(RTSPURL)
                    running = False
                    break
                # elif frame is not None:
                # TODO: confirm if this is the skipped frame
                # print("Skipping frame received, currently busy...")
                # if frame is not None:
                #     cv2.imshow("RTSP: %s" % RTSPURL, frame)
                if cv2.waitKey(1) == 27:
                    running = False
                    break
        except Exception:
            print(Exception)
            e = sys.exc_info()[0]
            print(colored("[ERROR] ", "red") + "%s" % e)
            running = False

    if video is not None:
        print("[INFO] Releasing the RTSP capture object...")
        video.release()
    print("[INFO] RTSP test done!")
