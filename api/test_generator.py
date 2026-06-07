from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import base64
import json
import os

load_dotenv()

router = APIRouter(
    prefix="/test",
    tags=["Test Generator"]
)

# Groq
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


class TextTestRequest(BaseModel):
    topic: str
    num_questions: int = 5


PROMPT_TEMPLATE = """
Generate {num_questions} multiple choice questions based on the provided content.

Return ONLY a valid JSON array with this exact structure, no extra text:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation why this is correct."
  }}
]
"""


def parse_questions(raw: str) -> list:
    # Extract JSON array from response
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON array found in response")
    return json.loads(raw[start:end])


@router.post("/from-text")
def generate_from_text(data: TextTestRequest):
    try:
        prompt = f"Topic: {data.topic}\n\n" + PROMPT_TEMPLATE.format(
            num_questions=data.num_questions
        )

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        questions = parse_questions(raw)

        return {
            "topic": data.topic,
            "total_questions": len(questions),
            "questions": questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-image")
async def generate_from_image(
    file: UploadFile = File(...),
    num_questions: int = Form(5)
):
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
                            "text": PROMPT_TEMPLATE.format(
                                num_questions=num_questions
                            )
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

        raw = response.choices[0].message.content
        questions = parse_questions(raw)

        return {
            "total_questions": len(questions),
            "questions": questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
