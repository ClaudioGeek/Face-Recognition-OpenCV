from PIL import Image
import cv2 as cv
import os
import numpy

#assigning the path for the dataset
path = 'dataset'

#creating the faceCascade and the faceRecognizer variables
face_cascade = cv.CascadeClassifier('/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_default.xml')
rec=cv.face.LBPHFaceRecognizer_create()
#rec = cv2.face_LBPHFaceRecognizer()
#This funtion will get the Label Data and the Images
def getImageInfor(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples=[]
    ids=[]

    for imgPath in imagePaths:
        PILimg = Image.open(imgPath).convert('L')
        imgNumpy = numpy.array(PILimg,'uint8')

        id = int(os.path.split(imgPath)[-1].split(".")[1])
        faces = face_cascade.detectMultiScale(imgNumpy)

        for(x,y,w,h) in faces:
            faceSamples.append(imgNumpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

print("\n INFOR: trainning the dataset. Please wait, may take few seconds...")
faces,ids = getImageInfor(path)
rec.train(faces,numpy.array(ids))
rec.write('trainer/trainer.yml')
print("\n [INFOR] {0} faces trained. Exiting training".format(len(numpy.unique(ids))))
cv.destroyAllWindows()