import pickle
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from fastapi.responses import FileResponse
from pathlib import Path

#FOR FIREBASE CREDENTIAL;
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://facerecognition-43d8d-default-rtdb.firebaseio.com/",
    'storageBucket' : "facerecognition-43d8d.appspot.com"
})

bucket = storage.bucket()

from typing import Union
from fastapi import FastAPI, File,UploadFile ,Form,APIRouter
router = APIRouter()
import uuid

IMAGEDIR = 'Images/' #To Store Image Directory
FIREDIR = 'toStoreData/'

#FUNCTIONS

def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def dumpEncodingToPickel(encodeListKnownWithIds):
    file = open("encodedFile.p", 'wb') #if does not exist, it will create
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

#function for criminal Detection
def imagDetect(images):
    img = cv2.imread(images)

    #load encoding file
    file = open("encodedFile.p",'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown,personId = encodeListKnownWithIds

    counter = 0
    id = -1
    # print(personId)

    while True:
        # success, img = cap.read()
        # cv2.imshow("pepole",img)
        imgWithBox = img
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # cv2.imshow('img',img)

        faceCurrentFrame = face_recognition.face_locations(img)
        encodeCurrentFrame = face_recognition.face_encodings(img,faceCurrentFrame)
        for encoFace, faceLoc in zip(encodeCurrentFrame,faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encoFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encoFace)
            print("matches",matches)
            print("distance",faceDis)

            matchIndex = np.argmin(faceDis)
            print("matchIndex",matchIndex)

            if matches[matchIndex]:
                myColor = (0, 255, 0)
                x1, y1, x2,y2 = faceLoc
                bbox = x1, y1, x2 - x1, y2 - y1
                imgWithBox = cv2.rectangle(img,bbox,(0,255,0),2)
                id = personId[matchIndex]
                if counter == 0:
                    counter = 1
        if counter!= 0:
            if counter == 1:

                #fetched info from Real time Database
                personInfo = db.reference(f'Criminal/{id}').get()
                print(personInfo)

                #getting image from firebase storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgPerson = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                # cv2.imshow("img",imgPerson)

                return (personInfo)


def FectchMatchIndex(images):
    img = cv2.imread(images)

    #load encoding file
    file = open("encodedFile.p",'rb')

    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown,personId = encodeListKnownWithIds

    counter = 0
    id = -1
    # print(personId)

    while True:
        # success, img = cap.read()
        # cv2.imshow("pepole",img)
        imgWithBox = img
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

        faceCurrentFrame = face_recognition.face_locations(img)
        encodeCurrentFrame = face_recognition.face_encodings(img,faceCurrentFrame)
        for encoFace, faceLoc in zip(encodeCurrentFrame,faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encoFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encoFace)
            # print("matches",matches)
            # print("distance",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("matchIndex",matchIndex)

            if matches[matchIndex]:
                myColor = (0, 255, 0)
                x1, y1, x2,y2 = faceLoc
                bbox = x1, y1, x2 - x1, y2 - y1
                imgWithBox = cv2.rectangle(img,bbox,(0,255,0),2)
                id = personId[matchIndex]
                if counter == 0:
                    counter = 1
        if counter!= 0:
            if counter == 1:

                #fetched info from Real time Database
                personInfo = db.reference(f'Criminal/{id}').get()
                print(personInfo)
                return id


#Adding Criminal INfo Real Time DATABASE
ref = db.reference('Criminal') #root folder/directory
def addDatatiDB(id,name,age): #three input id,name,age
    data = {
        id :
            {
                "name" : name,
                "Age" : age
            }
    }

    for key,value in data.items():
        ref.child(key).set(value)




app = FastAPI()

@router.get("/")
def read_root():
    return {"hello" : "World"}

@router.post("/upload/")
async  def create_upload_file(file: UploadFile = File(),id: str = Form()):

    file.filename = f"{id}.jpg"
    contents = await  file.read()

    #save the file
    with open(f"{IMAGEDIR}{file.filename}","wb")as f:
        f.write(contents)

    imgList = []
    personId = []

    def uploadImg_encoding(folder):
        folderPath = folder
        PathList = os.listdir(folderPath)

        for path in PathList:
            imgList.append(cv2.imread(os.path.join(folderPath, path)))
            personId.append(os.path.splitext(path)[0])

            # UPLOAD IMAGE TO FIREBASE STORAGE
            fileName = f'{folderPath}/{path}'
            bucket = storage.bucket()
            blob = bucket.blob(fileName)
            blob.upload_from_filename(fileName)

    #upload img to firebase FUnction
    uploadImg_encoding('Images')

    #generating encoding & dumping into pickle file
    encodeListKnown = findEncoding(imgList)
    encodeListKnownWithIds = [encodeListKnown, personId]
    dumpEncodingToPickel(encodeListKnownWithIds)

    personInfo = imagDetect(f"Images/{id}.jpg")
    matchIndex = FectchMatchIndex(f"Images/{id}.jpg")

    return {
                "personInfo": personInfo,
                "id" : matchIndex
            }
#-----------------------------------------------------------------------------------------------------------------

