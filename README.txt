============================================================
AI INTERVIEW SYSTEM — COMPLETE README

This project contains a complete AI-based interview pipeline with:

Question Generation API

Interview Flow API (start/end)

Local Interview Script for running the real interview

Full Video + Audio Recording

Transcript generation

Speech-to-Text + Text-to-Speech

Question saving as text files

No database is required inside this project, but the system is designed so a Database Team can integrate easily.

============================================================

PROJECT STRUCTURE
============================================================

AI_INTERVIEW/
│── question_api.py
│── question_gen.py
│── interview.py
│── simple_interview_demo.py
│── questions.txt
│── README.txt
│── .env
│── requirements.txt
│── generated_questions/
│── transcripts/
│── recordings/
│── .venv/

============================================================
2. SETUP INSTRUCTIONS

Create a virtual environment:

Windows:

python -m venv .venv
.\.venv\Scripts\Activate.ps1


Install all dependencies:

pip install -r requirements.txt


Create .env:

OPENAI_API_KEY=your_openai_key_here


Install FFmpeg (required for audio + video recording):

Download Windows build:
https://www.gyan.dev/ffmpeg/builds/

Add ffmpeg/bin to PATH.
Verify:

ffmpeg -version

============================================================
3. QUESTION GENERATION API

Run:

uvicorn question_api:app


Endpoint:

POST /generate


Example JSON:

{
  "job_description": "Python developer with Django and DSA skills.",
  "language": "Python"
}


Response:

Exactly 5 structured interview questions

Saved automatically in:
generated_questions/questions_<id>.txt

============================================================
4. INTERVIEW FLOW API

Run:

uvicorn interview:app


Endpoints:

POST /start-interview

Generates a new interview session ID

POST /end-interview

Marks session closed

This API is optional and designed for UI / admin dashboards.

============================================================
5. RUNNING THE INTERVIEW LOCALLY

Run:

python simple_interview_demo.py


Features:

Reads questions from questions.txt

Speaks questions using TTS

User presses ENTER before answering (prevents echo)

STT captures the answer

Transcript saved to transcripts/

Webcam + mic recorded together

Final merged interview video saved at:
recordings/interview_<id>.mp4

============================================================
6. OUTPUT FILE LOCATIONS

Generated Questions
generated_questions/questions_<id>.txt

Final Interview Video
recordings/interview_<id>.mp4

Transcript
transcripts/transcript_<id>.txt

============================================================
7. REQUIREMENTS (requirements.txt)
fastapi
uvicorn
openai
python-dotenv
opencv-python
pyaudio
ffmpeg-python
speechrecognition
gtts
pydantic

============================================================
8. WORKFLOW FOR DATABASE TEAM (INTEGRATION FLOW)

The system is designed so the Database Team controls the final interview content and the overall interview pipeline.

Below is the recommended integration flow.

A) QUESTION GENERATION FLOW

HR/Admin provides a job description

Frontend calls:
POST /generate

The Question Generator API returns:

5 questions in JSON

a saved .txt file

Database Team stores these questions into your central DB (e.g., SQL, MongoDB):
Suggested table:

TABLE: interview_questions
-----------------------------------------
question_id (PK)
interview_id (FK)
question_text
question_type     (technical / hr)
subtype           (scenario / tech_stack / coding / general)
created_at
approved_by


Database team implements an “Approve / Reject” process:

The hiring team reviews the AI-generated questions

Approves the final set

Only approved questions become available for interview

B) INTERVIEW START FLOW

UI calls: POST /start-interview

This returns an interview_id

Database team links this ID with chosen questions:

SELECT * FROM interview_questions WHERE interview_id = ? AND approved = TRUE;

The system writes the approved questions into:
questions.txt

Local interview script (simple_interview_demo.py) starts with the same interview_id

C) DURING INTERVIEW

The Python script:

Uses TTS to ask questions

Uses STT to capture answers

Saves transcript

Saves full interview video

Database team does NOT need to interact here.

D) AFTER INTERVIEW ENDS

Script saves:

transcripts/transcript_<id>.txt

recordings/interview_<id>.mp4

Backend system or Database Team:

Uploads transcript + video into storage (AWS S3, Firebase, etc.)

Updates interview status in DB

Example DB table:

TABLE: interview_results
-----------------------------------------
interview_id
candidate_id
transcript_path
video_path
rating (optional)
status (completed / pending review)

============================================================
END OF README