from fastapi import FastAPI
import uuid
import os

app = FastAPI(title="Interview Flow API")

current_interview = {
    "active": False,
    "id": None
}

@app.post("/start-interview")
def start_interview():
    if current_interview["active"]:
        return {"error": "Interview already running"}

    interview_id = str(uuid.uuid4())[:8]
    current_interview["active"] = True
    current_interview["id"] = interview_id

    os.makedirs("sessions", exist_ok=True)

    return {"status": "started", "interview_id": interview_id}

@app.post("/end-interview")
def end_interview():
    current_interview["active"] = False
    return {"status": "ended"}
