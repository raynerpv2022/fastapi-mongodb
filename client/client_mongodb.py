from pymongo import MongoClient
import os
from dotenv import load_dotenv

# load_dotenv()
# CLIENT_LOCAL = os.environ["CLIENT_LOCAL"]
# CLIENT_ATLAS_PYTHON = os.environ["CLIENT_ATLAS_PYTHON"]
# CLIENT_ATLAS_MONGODBSPAIN = os.environ["CLIENT_ATLAS_MONGODBSPAIN"]
# CLIENT_ATLAS_GO = os.environ["CLIENT_ATLAS_GO"]

CLIENT_LOCAL='mongodb://172.25.0.2:27017'
CLIENT_ATLAS_PYTHON = "mongodb+srv://resba:resba@cluster0.s8hks9w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
CLIENT_ATLAS_GO = "mongodb+srv://resba:resba@cluster0.awuzw0u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
CLIENT_ATLAS_MONGODBSPAIN = "mongodb+srv://raynerpv2022:resba@cluster0.yefed32.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"



client = MongoClient(CLIENT_LOCAL).fastapi
client_atlas_pyhton = MongoClient(CLIENT_ATLAS_PYTHON)
client_atlas_spain = MongoClient(CLIENT_ATLAS_MONGODBSPAIN)
client_atlas_go = MongoClient(CLIENT_ATLAS_GO) 


