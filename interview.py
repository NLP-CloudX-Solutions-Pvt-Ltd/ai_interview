import os
from dotenv import load_dotenv

env_path = os.path.abspath(".env")
print("Loading ENV from:", env_path)
load_dotenv(env_path)

print("Loaded API KEY?:", os.getenv("OPENAI_API_KEY"))

import os
import cv2
import pyaudio
import wave
import threading
import speech_recognition as sr
from gtts import gTTS
from question_gen import generate_questions

BASE = "static"
Q_DIR = os.path.join(BASE, "questions")
TTS_DIR = os.path.join(BASE, "tts")
REC_DIR = os.path.join(BASE, "recordings")

os.makedirs(Q_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)
os.makedirs(REC_DIR, exist_ok=True)

class InterviewRecorder:
    def __init__(self):
        self.video_writer = None
        self.audio_stream = None
        self.audio_frames = []
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        video_path = os.path.join(REC_DIR, "interview_video.avi")
        self.video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (640,480))
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=1024)

        def loop():
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    self.video_writer.write(frame)
                data = self.audio_stream.read(1024)
                self.audio_frames.append(data)

        self.thread = threading.Thread(target=loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.audio_stream.stop_stream()
        self.audio_stream.close()

        audio_path = os.path.join(REC_DIR, "interview_audio.wav")
        wf = wave.open(audio_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(self.audio_frames))
        wf.close()

        self.cap.release()
        self.video_writer.release()

        return {"video": "interview_video.avi","audio": "interview_audio.wav"}

recorder = InterviewRecorder()

def generate_tts(text, filename):
    path = os.path.join(TTS_DIR, filename)
    tts = gTTS(text=text, lang="en")
    tts.save(path)
    return path

def capture_answer():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Could not understand."

def create_interview(job_desc, lang=None):
    questions = generate_questions(job_desc, lang)
    qfile = os.path.join(Q_DIR, f"{job_desc.replace(' ','_')}.txt")
    with open(qfile, "w") as f:
        for q in questions:
            f.write(q["type"] + " : " + q["text"] + "\n")

    tts_files = []
    for i, q in enumerate(questions):
        tts_path = generate_tts(q["text"], f"q{i+1}.mp3")
        tts_files.append(tts_path)
    return questions, tts_files

def get_answer():
    return capture_answer()
