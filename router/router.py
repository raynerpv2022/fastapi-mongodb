from fastapi import APIRouter, HTTPException,status,Depends, Body
from typing import Annotated
from bson.objectid import ObjectId
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm 
from jose import jwt, JWTError
from datetime import timedelta, datetime

from pymongo import ReturnDocument, MongoClient
from client.client_mongodb import client, client_atlas_pyhton, client_atlas_spain,client_atlas_go
from model.db import UserPW, User
from helper.helper_methods import schema_userPW, schema_user, isObjectid_valid

from passlib.context import CryptContext

crypt = CryptContext(schemes="bcrypt")
EXPIRED_TIME = 10
ALGORITH = "HS256"
# openssl rand -hex 32 to generate SECRET_KEY
SECRET_KEY = "4238614503565990aba45ff2553ab0257d0b813f7506c84260cf83ebf1e6bb1a"


oauth2jwt = OAuth2PasswordBearer("/user/login")
user_router = APIRouter(prefix="/user",tags=["user"])

#helper Methods

 
# Get All Users
def get_all_user() :
    # print("all user")
    # remember change chema_user to not show the password
    return [schema_user(user) for user in client.users.find()]

# search user
def search_user(key:str, value: str)-> User | None:
    s= {key:value}
    try:
        user = client.users.find_one(s)
        print("search user",user)
        user = User(**schema_user(user))
        
    except:
        print("in exept",user)
        return None
    
    print("user",user)
   
    print(type(user))
    return user

def search_userPW(key:str, value: str)-> UserPW | None:
    s= {key:value}
    try:
        user = client.users.find_one(s)
        print("search user PW",user)
        user = UserPW(**schema_userPW(user) )
        
    except:
        print("in exept",user)
        return None
    
    print("user",user)
   
    print(type(user))
    return user

# set password hash to be stored.
def set_password_hash(plain_pass: str)->str:
    return  crypt.hash(plain_pass)

# verify password
def password_verify(plain_pass: str, hash_pass:str):
    return crypt.verify(plain_pass,hash_pass)

#get auth for username  or email and pasword
def authentication_user(email:str, password:str)->bool | UserPW:
    userDB = search_userPW("email",email)
    if userDB == None:
        return False
    
    if not  password_verify(password,userDB.passwd):
        return False
     
    return userDB


# check if it is better a  function 
# def decode_token(token:str):
#     try:
#         token_decoded = jwt.decode(token,SECRET_KEY,ALGORITH) 
#     except JWTError:
#         return False
#     return token["sub"]
    



def insert_user(user: UserPW)-> UserPW:
    #hash pasword
    user.passwd = set_password_hash(user.passwd)
    user_dict = dict(user)
    
    try:
        user_inserted = client.users.insert_one(user_dict)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= {"Error": "Item Not Inserted"})
    
    try:
        # check to use searchUSer or Search userPW
        user_found = search_userPW("_id",user_inserted.inserted_id)  
     
    except:
        # this error only to test how bson is checked.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail={"Error": "BSON object ID is incorrect"})
    return user_found

def current_user(token: Annotated[str,Depends(oauth2jwt)])->UserPW:

    auth_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={"Error":"Authentication Failed"})
    
    try:
        token_decoded = jwt.decode(token,SECRET_KEY,ALGORITH)
        print("token",token_decoded)
        user = token_decoded["sub"]
        if user == None:
            print(" in user == none")
            raise auth_exception
        user_found = search_userPW("email",user)
        if user_found == None:
            print(" in user_found == none")
            raise auth_exception
    except JWTError:
        print(" jwt")
        raise auth_exception

    return user_found


def current_user_active(user: Annotated[UserPW,Depends(current_user)]):

    disable_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={"Error":"User is disable"})
    if user.get_disable():
        raise disable_exception
    
    return user



def create_token(exp_time: int, data:str)-> str:

    user_to_encode = {"sub":data,
                      "exp":datetime.utcnow()+timedelta(minutes= exp_time)}
    
    return jwt.encode(user_to_encode,SECRET_KEY,algorithm=ALGORITH)


def delete_by_email(email: str):

    # Not used if find_one_and_delete is implemented.
    # user = search_userPW("email",email)
    # if user == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"Error":"User not Found"}) 
    if is_db_empty():
        return {"Info": "DB is empty"}
    
    filter_delete = {"email":email}
    try:
        delete_result = client.users.find_one_and_delete(filter_delete)
    except:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail={"Error":"not deleted Item "})
    if not delete_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"Error":"User not Found"})
      
    return schema_userPW(delete_result)

def is_db_empty():
     
    return client.users.count_documents({}) == 0


def print_db(client: MongoClient):
    # print(client..name)
    for db in client.list_database_names(): 
        print(db)

# controller methods
@user_router.get("/getatlas")
async def get_atlas(user: UserPW):
    print_db(client_atlas_pyhton)
    # print_db(client_atlas_go)
    # print_db(client_atlas_spain)
    print(user)
    u = [dict(user),dict(user),dict(user)]
    id = client_atlas_pyhton.mkv.grade.insert_one(dict(user))
    r = client_atlas_pyhton.mm.grade.insert_many(u)
    print(id.inserted_id)
    print(r.inserted_ids)
    return {"info1":str(id.inserted_id),
            "info2":str(r.inserted_ids)

    }


@user_router.get("/getall/")
# token: Annotated[str,Depends(current_user)]
async def getall(): 
     
    if is_db_empty():
        return {"Info": "DB is empty"}
    return get_all_user()

@user_router.get("/get/",status_code=status.HTTP_200_OK)
# user: Annotated[str,Depends(current_user_active)]
async def get_by_email(email: Annotated[str,  Body()] = None)->dict:
    # here in a post request as email is str in Body()
    # we have to post  str like this... "josefina@email.com" in json tab

    # print("user found", user)
    if is_db_empty():
        return {"Info": "DB is empty"}
        
    if email == None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail={"error":"No email provided"})
    
    user = search_userPW("email",email)
    if user == None:
        user = "Not user Found"
    return {"Info":user}

@user_router.get("/get/{id}",status_code=status.HTTP_200_OK)
async def get_by_id(id: str)->dict:

    if is_db_empty():
        return {"Info": "DB is empty"}
    ob_id = isObjectid_valid(id)
    if not ob_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail={"error":"ID not valid"})
        
    user = search_userPW("_id",ObjectId(id))
    if user == None:
        user = "No user Found"
    
    return {"info":user}

@user_router.put("/update/",status_code=status.HTTP_200_OK,response_model= dict)
async def update(user: UserPW)->dict:
    if is_db_empty():
        return {"Info": "DB is empty"}
    filter = {"email":user.email}
    value = {"$set":{"name":user.name,"passwd":set_password_hash(user.passwd)}}
    try:
        user_updated = client.users.find_one_and_update(filter,value,return_document=ReturnDocument.AFTER)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail={"Error":"not updated item"})
    
    if not user_updated:
        return {"Error":"Not user found"}
    print(user, user_updated)
    return schema_userPW(dict(user_updated))

    
#create user
@user_router.post("/create",status_code=status.HTTP_201_CREATED,response_model= dict)
async def create_user(user: UserPW) -> dict:
    # Is email regisrtered?
    if type(search_user("email",user.email)) == User:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail={"Error": "User is already registered witch this Email... try again"}  )

    user_found = insert_user(user)
    return {"Info":" Items add",
            "User": user_found
            }

# login user
@user_router.post("/login")
async def login(f : Annotated[OAuth2PasswordRequestForm,Depends()],status_code=status.HTTP_200_OK,response_model=dict):
    userDB = authentication_user(f.username,f.password)
    if not userDB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": "Username or password incorrect"})
    
    # disable can be checked here or in any particlar endpoint
    # if userDB.get_disable():
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={"Error":"User is Disable"})
    
    token = create_token(EXPIRED_TIME,userDB.email)

    # By the spec, you should return a JSON with an access_token and a token_type

    return {"access_token": token,
            "token_type": "bearer"
            }

@user_router.delete("/delete/{email}",response_model=dict,status_code=status.HTTP_202_ACCEPTED)
# user: Annotated[UserPW,Depends(current_user_active)]
async def delete_one(email: str)->dict:
    result = "" 
    if is_db_empty():
         return {"Info": "DB is empty"}
     
    return { "User": delete_by_email(email),
            "Action":"User Deleted"
            }

@user_router.delete("/delete",response_model=dict,status_code=status.HTTP_202_ACCEPTED)
# user: Annotated[UserPW,Depends(current_user_active)]
async def delete_all()->dict:
    result = "Collection is deleted"
    if is_db_empty():
         result  = "DB is empty"
    try:
        client.users.drop()
    except:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail={"Error":"not delete DB "})
    return {"Info":result}
    



# not implement yet
@user_router.post("/logout",response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def logout(token: Annotated[str,Depends(oauth2jwt)]):

    token = create_token(0,"")
    return {"access_token": token,
            "token_type": "bearer"
            }







