import cv2
import sys
import time
import requests
import _thread
import io
from PIL import Image
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

"""
    Original code from: https://kevinsaye.wordpress.com/2019/06/11/python-using-opencv-to-process-rtsp-video-with-threads/
    Because this reads from an RTSP source, we must keep reading the frames else we will get behind
    in the code below, if not "is_inferring", then we spin a thread to do an inferrence for the image to a remote REST server
"""
 
RTSPURL                 = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
INFERENCE_SERVER_URL    = 'http://localhost:8000/detect/'
timeout                 = 6     # timeout to connect to the scoring URL
is_inferring            = False
 
def infer_image(frame):
    global is_inferring
    is_inferring=True
    try:
        image = Image.fromarray(frame)
        stream = io.BytesIO()       # creating a steam object to not write to the disk
        image.save(stream, format="JPEG")
        stream.seek(0)
        img_for_post = stream.read()
        
        multipart_data = MultipartEncoder(
            fields={
                'file_list': (
                    'a_frame.JPEG', # create a pseudo file from memory
                    img_for_post,
                ),
                'model_name': (None, 'yolov5s'),
                'img_size': (None, '640'),
                'download_image': (None, 'false'),
            }
        )
        
        headers = {
            'Content-Type': multipart_data.content_type
        }
        
        response = requests.post(INFERENCE_SERVER_URL, headers=headers, data=multipart_data, timeout=timeout).json()
        print(response) #do something with the response from the inference server
    except:
        e = sys.exc_info()[0]
        print("Unexpected error with the inference: %s" % e)
    is_inferring=False

#process only X frames
limit = 20
processing_count = 0
running = True
while running:         # outer loop to catch errors
    try:
        video = cv2.VideoCapture(RTSPURL)
        while True: # inner loop for each frame
            ret, frame = video.read()
            if ret and is_inferring == False and processing_count < limit:
                _thread.start_new_thread(infer_image, (frame, ))
                processing_count += 1
            elif processing_count >= limit:
                # stop the stream when processing limit is reached
                video.release()
                running = False
                break
            elif ret == False:
                # TODO: add an exit clause here since this will retry the RTSP when any error occurs
                video.release()
                video = cv2.VideoCapture(RTSPURL)
            # elif frame is not None:
                # TODO: confirm if this is the skipped frame
                # print("Skipping frame received, currently busy...")
    except:
        e = sys.exc_info()[0]
        print("Unexpected error with prediction: %s" % e)
        
print("RTSP test done!")