import cv2 as cv
import numpy as np
import MySQLdb
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import strftime,gmtime
import time
import smtplib

faceDetect = cv.CascadeClassifier('/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_default.xml');

recogniser = cv.face.LBPHFaceRecognizer_create();

recogniser.read('trainer/trainer.yml')

#Database Connection
myDB = MySQLdb.connect('localhost','root','Cms_Ucc928','prototype')

#initialise camera
camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size = (640,480))

time.sleep(2)

id       = 0
status   = 0
name     = ""
stdEmail = " "
surname  = " "

def SendEmail(toEmail,firstname,lastname,cTime):
    #Creating Variables from The Email Settings
    smtpUser ='cs928799210@gmail.com'
    smtpPass='Cms_Ucc928'
    fromAdd=smtpUser
    
    subject ='School Notification'
    header = 'To: ' + toEmail + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
    body = 'Your son' + firstname + '\n' + lastname + '\n' + 'has attended at school at:' +'\n' +cTime 
    s=smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser,smtpPass)
    s.sendmail(fromAdd,toEmail,header+'\n\n'+body)
    s.quit()
    print('Email Sent to your parents:' + toEmail)
    
#font = cv.InitFont(cv.FONT_HERSHEY_COMPLEX_SMALL,5,1,0,4)

for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    image = frame.array

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray,1.3,5);

    for(x,y,w,h) in faces:

        cv.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
      
        id,conf = recogniser.predict(gray[y:y+h,x:x+w])
        
        myCursor = myDB.cursor()
        myCursor.execute("SELECT id,name FROM tb_face_register WHERE id =%s",(id,))
        for row in myCursor.fetchall():
            
            stdNum  = str(row[0])
            name    = str(row[1])
            surname = str(row[2])
            stEmail = str(row[3])
            
            stdNum=int(stdNum)
            id=int(id)
            
            print('Student Number: ' + str(stdNum))
            print('Identification Number: ' + str(id))
           
        if(stdNum==id):
            att="Present"
            cTime = strftime("%H:%M:%S",gmtime())
            SendEmail(stdEmail,name, surname,cTime)
            try:
                myCursor = myDB.cursor()
                myCursor.execute("INSERT INTO logs_face(id,name,time_in,status) VALUES (%s,%s,%s,%s)", (id,name,cTime,att))
                myDB.commit()
                print('Attendance recorded')
                print('-----------------------------------------')
            except:
                print('\n')
                print("System Error: Database access denied")
            finally:
                name     = ""
                stdEmail = " "
                surname  = " "
        else:
            print('not recorded')
            
        if conf>50:
            cv.putText(image,str(name),(x+2,y+h-5),cv.FONT_HERSHEY_SIMPLEX,1,(150,255,0),2);
            #cv.putText(image,str(stdNum),(x,y+h),cv.FONT_HERSHEY_SIMPLEX,1,(150,255,0),3);
            
        else:
            cv.putText(image,"No Match",(x,y+h),cv.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,255),2);
    
    cv.imshow("Face Recognition System", image)
    
    key = cv.waitKey(1) & 0xFF

    rawCapture.truncate(0)
    
    
    if(key == ord("q")):  
        break

cv.destroyAllWindows()