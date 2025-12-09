from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from question_gen import generate_questions
import os
import uuid

app = FastAPI(title="Interview Question Generator API")

class GenerateRequest(BaseModel):
    job_description: str
    language: Optional[str] = None
    save: Optional[bool] = True  # default: save to text file

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        questions = generate_questions(req.job_description, req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ---- SAVE TO TEXT FILE IF ENABLED ----
    if req.save:
        os.makedirs("generated_questions", exist_ok=True)

        file_id = str(uuid.uuid4())[:8]
        filename = f"generated_questions/questions_{file_id}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("JOB DESCRIPTION:\n")
            f.write(req.job_description + "\n\n")
            f.write("GENERATED QUESTIONS:\n\n")
            for q in questions:
                f.write(f"- ({q['role']} | {q['subtype']}) {q['text']}\n")

    return {
        "questions": questions,
        "saved_file": filename if req.save else None
    }
