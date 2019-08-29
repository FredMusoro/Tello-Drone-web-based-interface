from flask import Flask, render_template, Response
app = Flask(__name__)
from djitellopy import Tello
import cv2
import numpy as np
import time
import os
import datetime

video_camera = None
global_frame = None
camera_frame = None
# global tello

FPS = 25
# dimensions = (960, 720)

if True:
    ddir = "Sessions"

    if not os.path.isdir(ddir):
        os.mkdir(ddir)

    ddir = "Sessions/Session {}".format(str(datetime.datetime.now()).replace(':','-').replace('.','_'))
    os.mkdir(ddir)

@app.route("/")
def web():
    return render_template("web.html")

def video_stream():
    global video_camera 
    global global_frame
    global camera_frame
    # global tello
    # imgCount = 0

    if video_camera == None:
        video_camera = Tello()

        if not video_camera.connect():
            print("Tello not connected")
            return

        if not video_camera.set_speed(10):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not video_camera.streamoff():
            print("Could not stop video stream")
            return

        if not video_camera.streamon():
            print("Could not start video stream")
            return
        
    while True:

        # ret, frame = video_camera.get_frame_read().frame
        # frame = video_camera.get_video_capture().frame
        frame_read = video_camera.get_frame_read()

        should_stop = False
        # imgCount = 0
        # OVERRIDE = False
        # oSpeed = 1
        # tDistance = 3
        video_camera.get_battery()
        
        # Safety Zone X
        #szX = 100

        # Safety Zone Y
        #szY = 55
        
        if True:
            print("DEBUG MODE ENABLED!")

        while not should_stop:
            # update()

            if frame_read.stopped:
                frame_read.stop()
                break

            # theTime = str(datetime.datetime.now()).replace(':','-').replace('.','_')

            # frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB).frame
            # output = cv2.imencode('.jpeg', frame)
            ori_frame = frame_read.frame
            frame = ori_frame
            if ori_frame.any():
                success, jpeg = cv2.imencode('.jpg', ori_frame)
                if success:
                    frame = jpeg.tobytes()

            if frame != None:
                global_frame = frame
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
                # print("frame\n")
                # print(frame.tobytes())
                
                # print("frameRet\n\n\n")
                # print(frameRet)
                #vid = self.tello.get_video_capture()

                # if True:
                    # cv2.imwrite("{}/tellocap{}.jpg".format(ddir,imgCount),frameRet)

                            
@app.route("/video_feed")
def video_feed():
        return Response(video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("landing")
def land():
    video_camera
        return Response(video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

# @staticmethod
# def get_frame(self):
#     ret, frame = self.cap.read()

#     if ret:
#         ret, jpeg = cv2.imencode('.jpg', frame)

        # Record video
        # if self.is_record:
        #     if self.out == None:
        #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
            
        #     ret, frame = self.cap.read()
        #     if ret:
        #         self.out.write(frame)
        # else:
        #     if self.out != None:
        #         self.out.release()
        #         self.out = None  

        # return jpeg.tobytes()


if __name__ == "__main__":
    app.run(debug=True)

    # global tello 
    # Init Tello object that interacts with the Tello drone
    # tello = Tello()
    
    # if not tello.streamon():
    #     print("Could not start video stream")
    # else:
    #     print("Success")
