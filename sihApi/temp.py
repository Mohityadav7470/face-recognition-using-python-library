import pickle
import cv2
import numpy as np
import face_recognition
import os
from fastapi import FastAPI, File,UploadFile ,Form
from fastapi import FastAPI

app = FastAPI()


@app.get("/{username}")
def getData(text):
    return {
            'user_name' : text
    }

@app.post('/text/')
async def text(id: str = Form()):
    return id
