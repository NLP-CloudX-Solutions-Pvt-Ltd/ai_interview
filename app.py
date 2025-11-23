import os
from dotenv import load_dotenv

env_path = os.path.abspath(".env")
print("Loading ENV from:", env_path)
load_dotenv(env_path)

print("Loaded API KEY?:", os.getenv("OPENAI_API_KEY"))


from flask import Flask, request, jsonify
from interview import recorder, create_interview, get_answer

app = Flask(__name__)

questions = []
tts_files = []
current_q = 0

@app.post("/generate")
def gen():
    global questions, tts_files, current_q
    data = request.json
    jd = data["job"]
    lang = data.get("lang")
    questions, tts_files = create_interview(jd, lang)
    current_q = 0
    return jsonify({"ok": True,"questions": questions,"tts": tts_files})

@app.get("/start_recording")
def start_rec():
    recorder.start()
    return {"ok": True}

@app.get("/stop_recording")
def stop_rec():
    files = recorder.stop()
    return {"ok": True,"files": files}

@app.get("/next_question")
def next_q():
    global current_q
    if current_q >= len(questions):
        return {"ok": False, "msg": "no more questions"}
    res = {"question": questions[current_q]["text"],"tts": tts_files[current_q]}
    current_q += 1
    return res

@app.get("/answer")
def ans():
    return {"answer": get_answer()}

if __name__ == "__main__":
    app.run(port=5000)
