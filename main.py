from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth
from api import chatbot
from api import test_generator
from api import imagetotext
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chatbot.router)
app.include_router(test_generator.router)
app.include_router(imagetotext.router)
@app.get("/")
def home():
    return {"message": "FastAPI Project Running"}
