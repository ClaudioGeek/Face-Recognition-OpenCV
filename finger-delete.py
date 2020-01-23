#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

from pyfingerprint.pyfingerprint import PyFingerprint
import MySQLdb
import time
import os

#creating variables for storing the names
Name    = " "
Subject = " "
Email   = " "
Surname = " "
count = 0

#create a Database object
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
print("\n")
print("{:>10s}" .format("WELCOME TO FINGERPRINT DE-REGISTRATION SYSTEM"))
print("#---------------------------------------------#")
print('System Information')
print('Number of Finger Registered on the System: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
print("\n")

def StaffDeleteFinger():
    print("\n")
    print("#############################################")
    print("Welcome to Staff Finger System De-Registration")
    print("\n")
    
    while 1:
        ## Tries to delete the template of the finger
        try:
            
            SubCode= input('Please enter staff subject code:')
            
            myCursor = myDB.cursor()
            myCursor.execute("SELECT * FROM tb_teacher_finger WHERE t_subject= %s",(SubCode,))
            for row in myCursor.fetchall():
                Name = str(row[0])
                Email = str(row[1])
                Subject = str(row[2])
                positionNumber = str(row[3])
                positionNumber = int(positionNumber)
                
            if ( f.deleteTemplate(positionNumber) == True ):
                try:
                    print("#----------------------------#")
                    print("Staff Information")
                    print("Name : " + Name)
                    print("Email: " + Email)
                    print("Subject Code : " + Subject)
                    try:
                        myCursor = myDB.cursor()
                        myCursor.execute("DELETE FROM tb_teacher_finger WHERE finger_pos= %s",(positionNumber,))
                        myDB.commit()
                        print("Deleted from the System")
                        print("\n")
                        print("#----------------------------------#")
                        print('System Information After Operation')
                        print('Updated Number of Finger Registered on the System: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
                        print("\n")
                    except:
                        print("System Error")
                    finally:
                        SubCode = " "
                        Name    = " "
                        Subject = " "
                        Email   = " "
                        Surname = " "
                        
                except:
                    print("Error message: There might be a problem with Database Server")
                    
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

##-------------------CREATING STUDENT FUNCTION DO DELETE FINGERPRINTS-------------------------------##
def StudentDeleteFinger():
    print("\n")
    print("#############################################")
    print("Welcome to Student Finger System De-Registration")
    print("\n")
    
    while 1:
        ## Tries to delete the template of the finger
        try:
            StdNumber=input('Please enter Student Number:')
            StdNumber = int(StdNumber)
            
            myCursor = myDB.cursor()
            myCursor.execute("SELECT * FROM tb_student_finger WHERE std_id=%s",(StdNumber,))
            for row in myCursor.fetchall():
                Name = str(row[1])
                Surname = str(row[2])
                Email = str(row[3])
                positionNumber = str(row[4])
                
                
            if ( f.deleteTemplate(positionNumber) == True ):
                try:
                    print("#----------------------------#")
                    print("Student Information")
                    print("Name : " + Name + " " + Surmane)
                    print("Email: " + Email)
                    try:
                        myCursor = myDB.cursor()
                        myCursor.execute("DELETE FROM tb_student_finger WHERE finger_pos= %s",(positionNumber,))
                        myDB.commit()
                        print("Deleted from the System")
                        ## Gets some sensor information
                        print("\n")
                        print("#----------------------------------#")
                        print('System Information After Operation')
                        print('Updated Number of Finger Registered on the System: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))  
                    except:
                        print("System Error")
                except:
                    print("Error message: There might be a problem with Database Server")
                    
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

while 1:
    print("\n")
    print("#############################################")
    print("Please select: [A: To Delete Students] or [B: To Delete Staff]")
    
    select = input("Please enter your option: A or B >")
    if (select =="A"):
        try:
            StudentDeleteFinger()
        except:
            print("Student's System could not be initialized")
            break
    elif(select =="B"):
        try:
            StaffDeleteFinger()
        except:
            print("Staff's System could not be initialized")
            break
    else:
        print("Sorry no such option")
        print("\n")
    