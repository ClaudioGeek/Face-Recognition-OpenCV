#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import time
from pyfingerprint.pyfingerprint import PyFingerprint
import MySQLdb
import time
import os
import RPi.GPIO as GPIO

#creating variables for storing the names
stdNum= " "
fName = " "
lName = " "
sEmail= " "

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(38,GPIO.OUT)
GPIO.setup(40,GPIO.OUT)


#create a Database object
myDB = MySQLdb.connect("localhost","root","Cms_Ucc928","prototype")

## Enrolls new finger
##
## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print("\n")
print('System Information')
print('Number of Finger Registered on the System: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
print("\n")

def StudentFingerRegister():
    print("\n")
    print("#############################################")
    print("Welcome to Student Finger System Registration")
    print("\n")
    while 1:
        stdNum =  input("Please enter student number:")
        stdNum =  int(stdNum)
        fName  =  input("Please enter student name:")
        lName  =  input("Please enter student surname:")
        sEmail =  input("Please enter student email:")
        ## Tries to enroll new finger
        try:
            
            print('Waiting for finger...')

            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Checks if finger is already enrolled
            result = f.searchTemplate()
            positionNumber = result[0]

            if ( positionNumber >= 0 ):
                print('This fingerprint already exists at position #' + str(positionNumber))
                exit(0)

            print('Remove finger...')
            time.sleep(2)

            print('Place the same finger again...')

            ## Wait that finger is read again
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)

            ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                raise Exception('Fingers do not match')

            ## Creates a template
            f.createTemplate()

            ## Saves template at new position number
            positionNumber = f.storeTemplate()
            #print('Finger enrolled successfully!')
            #print('New template position #' + str(positionNumber))
            
            try:
                myCursor = myDB.cursor()
                myCursor.execute("INSERT INTO tb_student_finger(std_id,std_fName,std_lName,std_email,finger_pos) VALUES (%s,%s,%s,%s,%s)", (stdNum,fName,lName,sEmail,positionNumber))
                myDB.commit()
                print('Finger enrolled successfully!')
                GPIO.output(40,True)
                time.sleep(2)
                GPIO.output(40,False)
                GPIO.cleanup()
                print('New template position #' + str(positionNumber))
                print('\n')
                
            except (myDB.Error, myDB.Warning) as e:
                print("Error message: "+ str(e))
                
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            GPIO.output(38,True)
            time.sleep(2)
            GPIO.output(38,False)
            GPIO.cleanup()
            exit(1)

def TeacherFingerRegister():
    print("\n")
    print("#############################################")
    print("Welcome to Staff Finger System Registration")
    print("\n")
    while 1:
        fName = input("Please enter staff name:")
        lName = input("Please enter staff surmane:")
        staffName = (str(fName)+" " +str(lName)) 
        sEmail= input("Please enter staff email:")
        subject = input("Please enter subject code:")
        ## Tries to enroll new finger
        try:
            
            print('Waiting for finger...')

            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Checks if finger is already enrolled
            result = f.searchTemplate()
            positionNumber = result[0]

            if ( positionNumber >= 0 ):
                print('This fingerprint already exists at position #' + str(positionNumber))
                exit(0)

            print('Remove finger...')
            time.sleep(2)

            print('Place the same finger again...')

            ## Wait that finger is read again
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)

            ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                raise Exception('Fingers do not match')

            ## Creates a template
            f.createTemplate()

            ## Saves template at new position number
            positionNumber = f.storeTemplate()
            #print('Finger enrolled successfully!')
            #print('New template position #' + str(positionNumber))
            
            try:
                myCursor = myDB.cursor()
                myCursor.execute("INSERT INTO tb_teacher_finger(t_Name,t_email,t_subject,t_check,finger_pos) VALUES (%s,%s,%s,%s,%s)", (staffName,sEmail,subject,"Y",positionNumber))
                myDB.commit()
                print('Finger enrolled successfully!')
                print('New template position #' + str(positionNumber))
            except (myDB.Error, myDB.Warning) as e:
                print("Error message: "+ str(e))
                
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

while 1:
    ##Welcome Message To the System
    print("\n")
    print("#############################################")
    print("Please select: [A: for Students] or [B: for Staff]")
    
    select = input("Please enter your option: A or B >")
    if (select ==str("A")):
        try:
            StudentFingerRegister()
        except:
            print("Student's System could not be initialized")
            break
    elif(select ==str("B")):
        try:
            TeacherFingerRegister()
        except:
            print("Staff's System could not be initialized")
            break
    else:
        print("Sorry no such option")
        print("\n")

