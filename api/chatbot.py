from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)

# MongoDB
mongo = MongoClient(os.environ.get("MONGO_URI"))

db = mongo["testdb"]

chat_collection = db["chat_history"]

# Groq
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


class ChatRequest(BaseModel):
    user_id: str
    message: str


def generate_reply(user_id, message):

    # Load previous messages
    previous = list(
        chat_collection.find(
            {"user_id": user_id}
        ).sort("created_at", 1)
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful chatbot."
        }
    ]

    # Add history
    for chat in previous[-10:]:
        messages.append({
            "role": "user",
            "content": chat["user_message"]
        })

        messages.append({
            "role": "assistant",
            "content": chat["bot_reply"]
        })

    # Current message
    messages.append({
        "role": "user",
        "content": message
    })

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    return response.choices[0].message.content


@router.post("/send")
def send_message(data: ChatRequest):

    try:

        reply = generate_reply(
            data.user_id,
            data.message
        )

        chat_collection.insert_one({
            "user_id": data.user_id,
            "user_message": data.message,
            "bot_reply": reply,
            "created_at": datetime.utcnow()
        })

        return {
            "reply": reply
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/history/{user_id}")
def history(user_id):

    chats = list(
        chat_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", 1)
    )

    return {
        "user_id": user_id,
        "history": chats
    }
