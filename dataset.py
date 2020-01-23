#Created by: CD Manuel
#Date: 06/08/2018
#Project: RFID and Biometric Technology using Raspberry Pi

import os
import cv2
import numpy
import time
import MySQLdb
from picamera.array import PiRGBArray
from picamera import PiCamera


#Cretaing the Dataset

#Initialize the camera here
myCamera = PiCamera()
myCamera.resolution = (640,480)
myCamera.framerate =32
myCapture = PiRGBArray(myCamera,size=(640,480))

#load the cascede face classifier
face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_default.xml')

def DataBaseConnect():
    myDB = MySQLdb.connect('localhost','root','Cms_Ucc928','prototype')
    return myDB


id = input('Enter ID: ')
name = input('Enter student name       : ')
surname = input('Enter student surname : ')
email   = input('Enter student email   : ')

db = DataBaseConnect()
myCursor = db.cursor()

myCursor.execute("INSERT INTO tb_face_register(id,name,surname,email) VALUES (%s,%s,%s,%s)", (id,name,surname,email))
db.commit()

id=myCursor.lastrowid
        
faceSample = 0
time.sleep(0.1)

#Video Streaming
for frame in myCamera.capture_continuous(myCapture,format="bgr",use_video_port=True):
    #Getting the image from the frame as an array
    img_src = frame.array
    #Convert the image into gray array
    gray = cv2.cvtColor(img_src,cv2.COLOR_BGR2GRAY)
    #Detect face scale
    face = face_cascade.detectMultiScale(gray,1.3,5)

    #Now loop through the frame top take the pictures and store in the dataset folder
    for (x,y,w,h) in face:
        faceSample = faceSample+1
        cv2.imwrite("dataset/User." + str(id) + '.' + str(faceSample) + ".jpg", gray[y:y+h,x:x+w])
        img_src = cv2.rectangle(img_src,(x,y),(x+w, y+h),(255,0,0),2)

    #Show the frame and take the picture        
    cv2.imshow("Frame",img_src)

    #Escape Key
    if cv2.waitKey(100) & 0xFF==ord('q'):
        break
    elif faceSample>=10:
        print("Faces  for: " + " " + name + " have been recorded")
        break
    myCapture.truncate(0)
    
