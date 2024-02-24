from fastapi import FastAPI,status
from router.router import user_router

app = FastAPI()
app.include_router(user_router)
@app.get("/",status_code=status.HTTP_200_OK)
async def get():
    return {"Info":"Server is UP"}
