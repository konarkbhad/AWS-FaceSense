#!/usr/bin/python
import picamera
from multiprocessing import Process
import base64
import json
import time
import requests
import argparse


# function to send request to API gateway with the video file
def send_API_request(*args, **kwargs):
    file_h264 = kwargs['file_h264']
    VIDEO_NAME = kwargs['VIDEO_NAME']
    BASE_URL = kwargs['BASE_URL']
    api = BASE_URL +VIDEO_NAME
    # print("API:", api)

    # read the video file
    with open(file_h264, "rb") as f:
        vid_bytes = f.read()
    vid_b64 = base64.b64encode(vid_bytes).decode("utf8")
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    payload = json.dumps({"video": vid_b64, "other_key": "value"})
    
    # send the request to the API Gateway
    start_time = time.time()
    response = requests.post(api, data=payload, headers=headers)
    try:
        # get the response data
        data = response.json()     
        latency = time.time() - start_time
        # print the latency and result
        print("Latency: {:.2f} seconds. Response: {}".format(latency, data))            
    except requests.exceptions.RequestException:
        # Something went wrong, print the response
        print(response.text)


def main(BASE_URL,NUM_CLIPS,CLIP_LENGTH):
    processes = list()

    # start picamera recording
    with picamera.PiCamera() as camera:
        for filename in camera.record_sequence('/home/pi/Desktop/project/videos/clip%02d.h264' % i for i in range(NUM_CLIPS)):
            print('Recording to %s' % filename)
            # record 0.5 seconds video
            camera.wait_recording(CLIP_LENGTH)
            # create process to send request to API gateway
            p1 = Process(
                        target=send_API_request,  
                        kwargs={'file_h264': filename, 'VIDEO_NAME':filename.split("/")[-1], 'BASE_URL':BASE_URL}
            )
            p1.start()
            processes.append(p1)

    for index, proc in enumerate(processes):
        print("Got back from Process: ", index)
        proc.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Capture videos at regular intervals and make API request to get recognition result')
    parser.add_argument('--BASE_URL', type=str, default="https://w97zrvuvtb.execute-api.us-east-1.amazonaws.com/dev/", help='the base URL of the face recognition service API')
    parser.add_argument('--NUM_CLIPS', type=str, default=600, help='the number of clips to be captured')
    parser.add_argument('--CLIP_LENGTH', type=str, default=0.5, help='the length of each clip to be captured in seconds')
    
    args = parser.parse_args()
    BASE_URL = args.BASE_URL
    NUM_CLIPS = int(args.NUM_CLIPS)
    CLIP_LENGTH = float(args.CLIP_LENGTH)
    main(BASE_URL,NUM_CLIPS,CLIP_LENGTH)
