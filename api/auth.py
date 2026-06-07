from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# MongoDB Connection
client = MongoClient(os.environ.get("MONGO_URI"))

db = client["testdb"]

users_collection = db["users"]


# Request Body Model
class User(BaseModel):
    username: str
    password: str


# SIGN UP API
@router.post("/signup")
def signup(user: User):

    # Check if user already exists
    existing_user = users_collection.find_one({
        "username": user.username
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Insert user into database
    users_collection.insert_one({
        "username": user.username,
        "password": user.password
    })

    return {
        "message": "User created successfully"
    }


# LOGIN API
@router.post("/login")
def login(user: User):

    db_user = users_collection.find_one({
        "username": user.username,
        "password": user.password
    })

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "message": "Login successful",
        "username": db_user["username"],
        "user_id": str(db_user["_id"])
    }