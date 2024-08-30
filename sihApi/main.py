import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from routes import util, searching
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import firestore
#from db import connectDb
import basicfastapi

load_dotenv()
app = FastAPI()
# connectDb()
db = firestore.client()

PORT_NUMBER = os.environ.get("PORT")
HOST = os.environ.get("HOST")
origins = [
    "http://localhost:8000",
    "http://192.168.50.73:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hii/{inte}")
def index(inte: int):
    return inte


@app.get('/hey')
async def index():
    return {"data": "rohan"}


app.include_router(basicfastapi.router)

# if _name_ == "_main_":
#     uvicorn.run(app, host=HOST, port=PORT_NUMBER)