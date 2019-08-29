from flask import Flask, render_template, Response
app = Flask(__name__)
from djitellopy import Tello
import cv2
import numpy as np
import time
import os
import datetime

# import the openCV file for face detection 
face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

# colour and thickness for the box face
color=(0,255,0)
thickness=3

# declaration for onnection to tello drone and video stream 
video_camera = None
global_frame = None
tello = None

# # Drone velocities between -100~100
# for_back_velocity = 0
# left_right_velocity = 0
# up_down_velocity = 0
# yaw_velocity = 0
# speed = 10
# oSpeed = 0

# send_rc_control = False

# 
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

            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=2)

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
                roi_color = frame[y:y+h, x:x+w]
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness) # box for face


            if frame.any():
                success, jpeg = cv2.imencode('.jpg', frame)
                if success:
                    frame = jpeg.tobytes()

            if frame != None:
                global_frame = frame
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

                       
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
    
#     if not drone_terbang:
#         for_back_velocity = int(S * oSpeed)
#     elif k == ord('s'):
#         self.for_back_velocity = -int(S * oSpeed)
#     else:
#         self.for_back_velocity = 0

#         return render_template("web.html")
        
# @app.route("/Left")
# def Left():
#     drone_terbang = tello
    
#     if not drone_terbang.move_left(30):
#         print("Drone Move left")
#         return render_template("web.html")        

if __name__ == "__main__":
    app.run(debug=True)
