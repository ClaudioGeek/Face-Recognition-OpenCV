#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
from datetime import datetime 
import os
import time
import MySQLdb
from time import strftime,gmtime
from time import time
import smtplib

##create a Database object
myDB = MySQLdb.connect("localhost","root","Cms_Ucc928","prototype")


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
##print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))


def SendEmail(toEmail,firstname,lastname,cTime,subcode):
    #Creating Variables from The Email Settings
    smtpUser ='cs928799210@gmail.com'
    smtpPass='Cms_Ucc928'
    fromAdd=smtpUser
    
    subject ='School Notification'
    header = 'To: ' + toEmail + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
    body = 'Your son '+ ' ' + firstname + ' ' + lastname + '\n' + 'has attended the subject' + ' ' + subcode + ' ' +'at school at: ' +'\n' +cTime  
    s=smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser,smtpPass)
    s.sendmail(fromAdd,toEmail,header+'\n\n'+body)
    s.quit()
    print('Email Sent to your parents:' + toEmail)



##----------------------------------CREATING FUNCTION FOR TAKING STUDENT ATTENDANCE--------------------##
def StudentAttendance(subCode):
    stdName = " "
    stdSurname = " "
    stdNumber = " "
    subjectCode = subCode
    status = "Present"
    email = " "
    
    #get the current time
    cTime = strftime("%H:%M:%S",gmtime())
    cDate = strftime("%x",gmtime())
    print('\n')
    print('#--------STUDENT ATTENDANCE-----------#')
    
    while 1:
    
        try:
            print('\n')
            print('Waiting for Student finger...')
            print('\n')
            
            sTime = time()
            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Searchs template
            result = f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if ( positionNumber == -1 ):
                print('Sorry, fingerprint match not found!')
                print('System exit.')
                exit(0)
            else:
                try:
                    myCursor = myDB.cursor()
                    myCursor.execute("SELECT * FROM tb_student_finger WHERE finger_pos= %s",(positionNumber,))
                    for row in myCursor.fetchall():
                        stdNumber = str(row[0])
                        stdName = str(row[1])
                        stdSurname = str(row[2])
                        email = str(row[3])
                except:
                    print('System error message: Students data could not be retrieved')
                
                try:
                    SendEmail(email,stdName,stdSurname,cTime,subjectCode)
                    myCursor = myDB.cursor()
                    myCursor.execute("INSERT INTO logs_finger(std_id,finger_pos,date_in,time_in,status,subject) VALUES (%s,%s,%s,%s,%s,%s)", (stdNumber,positionNumber,cDate,cTime,status,subjectCode))
                    myDB.commit()
                except (myDB.Error, myDB.Warning) as e:
                        print("Error message: "+ str(e))
                finally:
                    
                    print('#---------------------------------------------#')
                    print('Found template at position #' + str(positionNumber))
                    print('The accuracy score is: ' + str(accuracyScore))
                    print('Attendance taken : ' + stdName)
                    
                    
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)
            
        print('It took ', round(time()-sTime,3), 'seconds to take attendance.')

#Getting the Date and Time
SysDate = datetime(1,1,1).now()
t_check = " "
Name    = " "
Subject = " "
## Tries to search the finger and calculate hash
print("#---------------------------------------#")
print("WELCOME TO FINGERPRINT ATTENDANCE SYSTEM")
print("System " + 'Time: {}:{:02d} - Date: {}/{}/{}'.format(SysDate.hour,SysDate.minute,SysDate.day,SysDate.month,SysDate.year))
print("\n")

print('[System info: Teacher must initiate the system by fingerprint authentication]')
try:
    print('\n')
    print('Waiting for teacher finger...')
    print('\n')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Searchs template
    result = f.searchTemplate()

    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found!')
        exit(0)
    else:
        try:
            myCursor = myDB.cursor()
            myCursor.execute("SELECT * FROM tb_teacher_finger WHERE finger_pos= %s",(positionNumber,))
            for row in myCursor.fetchall():
                Name = str(row[0])
                Subject = str(row[2])
                t_check = str(row[3])
        except:
             print('System Error: Staff information could not be retrieved')
        finally:
            print('#---------------------------------------------#')
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            print("Teacher: " + Name)
            print('Subject-Code:' + Subject)
        if(t_check!='Y'):
            print('Sorry you are not a registered Teacher on our System')
            print('System exit')
            exit(0)
        else: 
            StudentAttendance(Subject)

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)

