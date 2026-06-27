from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
import base64
import os

load_dotenv()

router = APIRouter(
    prefix="/ocr",
    tags=["Image to Text"]
)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract and return ALL text visible in this image exactly as it appears. Do not summarize, explain, or add anything. Just return the raw text."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        extracted = response.choices[0].message.content

        return {
            "extracted_text": extracted
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))