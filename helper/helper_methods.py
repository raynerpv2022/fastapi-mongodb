
from client.client_mongodb import client
from bson.objectid import ObjectId
 
 

def schema_userPW(userpw: dict)-> dict:
    # print("schema userpw",userpw)
    return { "id": str(userpw["_id"]),
            "name": userpw["name"],
            "email":userpw["email"],
            "passwd":userpw["passwd"],
            "disable":userpw["disable"],
            "attemp_false_loging":userpw["attemp_false_loging"]
             

    }

def schema_user(user: dict) -> dict:
    # print("schema user", user)
    return {"id": str(user["_id"]),
            "name": user["name"],
            "email":user["email"]

    }


     



#  not used yet
def isObjectid_valid(oid: ObjectId )-> ObjectId | bool:
    try:
        return ObjectId(oid)
    except:
        return False

# return coroutine check it
# def create_user(user: UserPW):
#     user_dict = schema_userPW(user)
#     print(user_dict)
#     user_inserted = client.users.insert_one(user_dict).inserted_id
#     print(user_inserted, type(user_inserted))
#     return user_inserted 
    