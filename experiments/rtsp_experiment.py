import cv2
import sys
import time
import requests
import _thread
import json
import io
from PIL import Image
 
"""
    Because this reads from an RTSP source, we must keep reading the frames else we will get behind
    in the code below, if not "isScoring", then we spin a thread to go score the image to a remote REST server
"""
 
minScore    = .99
RTSPURL     = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
scoringURL  = 'http://192.168.15.200:8484/'
timeout     = 6     # timeout to connect to the scoring URL
isScoring   = False
#headers = {'Content-type': 'application/octet-stream', 'Prediction-Key': 'insert prediction_key here if using Azure'}
 
def scoreImage(frame):
    global isScoring
    isScoring=True
    try:
        image = Image.fromarray(frame)
        stream = io.BytesIO()       # creating a steam object to not write to the disk
        image.save(stream, format="JPEG")
        stream.seek(0)
        img_for_post = stream.read()
        score = requests.post(scoringURL, files={'file': img_for_post}, timeout=timeout).json()
        if score["score"] >= minScore and score["label"] != 'Negative':
            filename = str(int(time.time() * 1000))
            image.save(filename + ".jpg")
            file = open(filename + ".txt","w") 
            file.write(json.dumps(score))
            file.close() 
            print(score)
    except:
        e = sys.exc_info()[0]
        print("Unexpected error with scoring: %s" % e)
    isScoring=False
 
while True:         # outer loop to catch errors
    try:
        video = cv2.VideoCapture(RTSPURL)
        while True: # inner loop for each frame
            ret, frame = video.read()
            if ret and isScoring == False:
                _thread.start_new_thread(scoreImage, (frame, ))
            elif ret == False:
                video.release()
                video = cv2.VideoCapture(RTSPURL)
    except:
        e = sys.exc_info()[0]
        print("Unexpected error with prediction: %s" % e)