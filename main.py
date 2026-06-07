from fastapi import FastAPI
from api import auth
from api import chatbot
from api import test_generator

app = FastAPI()

app.include_router(auth.router)
app.include_router(chatbot.router)
app.include_router(test_generator.router)

@app.get("/")
def home():
    return {"message": "FastAPI Project Running"}
