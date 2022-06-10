from imp import reload
import uvicorn
from fastapi import FastAPI

from routers.user import user
from routers.auth import auth

app = FastAPI()


app.include_router(auth)
app.include_router(user)

@app.get('/')
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)