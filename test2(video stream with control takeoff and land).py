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
tello = None

FPS = 25
# dimensions = (960, 720)

@app.route("/")
def web():
    global tello
    tello = Tello()
    if not tello.connect():
        print("Tello not connected")

    if not tello.set_speed(10):
            print("Not set speed to lowest possible")
            return

    return render_template("web.html")

#get the video stream form drone
def video_stream():
    global video_camera 
    global global_frame

    if video_camera == None:
        video_camera = tello

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not video_camera.streamoff():
            print("Could not stop video stream")
            return

        if not video_camera.streamon():
            print("Could not start video stream")
            return
        
    while True:
        frame_read = video_camera.get_frame_read()

        should_stop = False
        video_camera.get_battery()
        
        if True:
            print("DEBUG MODE ENABLED!")

        while not should_stop:
            # update()

            if frame_read.stopped:
                frame_read.stop()
                break

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

def rerender():
    return render_template("web.html")
                       
@app.route("/video_feed")
def video_feed():
        return Response(video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/takeOff")
def takeOff():
    drone_terbang = tello
    
    if not drone_terbang.takeoff():
        print("Drone Takeoff")
        return render_template("web.html")

@app.route("/Land")
def Land():
    drone_terbang = tello
    
    if not drone_terbang.land():
        print("Drone Landing")
        return render_template("web.html")

# @app.route("/Right")
# def Right():
#     drone_terbang = tello
    
#     if not drone_terbang.move_right(100):
#         print("Drone Move Right")
#         return render_template("web.html")
        
# @app.route("/Left")
# def Left():
#     drone_terbang = tello
    
#     if not drone_terbang.move_left(30):
#         print("Drone Move left")
#         return render_template("web.html")        

if __name__ == "__main__":
    app.run(debug=True)
