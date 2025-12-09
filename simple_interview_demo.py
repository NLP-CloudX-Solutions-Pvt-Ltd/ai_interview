import os
import uuid
import time
import threading
import cv2
import pyaudio
import wave
import subprocess
import speech_recognition as sr
from gtts import gTTS

QUESTIONS_FILE = "questions.txt"

# Output folders

os.makedirs("recordings", exist_ok=True)
os.makedirs("transcripts", exist_ok=True)

# -----------------------------
# TTS (Text to Speech)
# -----------------------------
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("tts_output.mp3")
    os.system("start tts_output.mp3")  # Windows playback

# -----------------------------
# STT (Speech to Text)
# -----------------------------
def listen_user_answer():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except:
        print("Could not understand speech.")
        return "(Unrecognized Speech)"

# -----------------------------
# VIDEO + AUDIO Recorder
# -----------------------------
def start_recording(video_output_path, audio_output_path, final_output_path):

    global RECORDING_FLAG
    RECORDING_FLAG = True

    # ---- VIDEO (OpenCV) ----
    def record_video():
        cap = cv2.VideoCapture(0)
        codec = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_output_path, codec, 20.0, (640, 480))

        while RECORDING_FLAG:
            ret, frame = cap.read()
            if ret:
                out.write(frame)

        cap.release()
        out.release()

    # ---- AUDIO (PyAudio) ----
    def record_audio():
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        pa = pyaudio.PyAudio()
        stream = pa.open(format=format,
                         channels=channels,
                         rate=rate,
                         input=True,
                         frames_per_buffer=chunk)

        frames = []

        while RECORDING_FLAG:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Save WAV
        wf = wave.open(audio_output_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(pa.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    # Start threads
    t1 = threading.Thread(target=record_video)
    t2 = threading.Thread(target=record_audio)

    t1.start()
    t2.start()

    return t1, t2

# -----------------------------
# COMBINE AUDIO + VIDEO using FFmpeg
# -----------------------------
def merge_audio_video(video_path, audio_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# -----------------------------
# MAIN INTERVIEW LOGIC
# -----------------------------
def run_interview():
    interview_id = str(uuid.uuid4())[:8]

    raw_video = f"recordings/video_raw_{interview_id}.mp4"
    raw_audio = f"recordings/audio_raw_{interview_id}.wav"
    final_video = f"recordings/interview_{interview_id}.mp4"
    transcript_path = f"transcripts/transcript_{interview_id}.txt"

    # Load questions
    with open(QUESTIONS_FILE, "r") as f:
        questions = [q.strip() for q in f.readlines() if q.strip()]
    questions = questions[:5]

    # Start recording
    vt1, vt2 = start_recording(raw_video, raw_audio, final_video)

    # Create transcript file
    with open(transcript_path, "w") as f:
        f.write("Interview Transcript\n=====================\n\n")

    print("\n=== INTERVIEW STARTED ===\n")

    for idx, q in enumerate(questions, start=1):

        print(f"\nQuestion {idx}: {q}")
        speak(q)

        input("Press ENTER after audio finishes, then answer...")

        answer = listen_user_answer()

        with open(transcript_path, "a") as f:
            f.write(f"Q{idx}: {q}\nA{idx}: {answer}\n\n")

        if idx < len(questions):
            input("Press ENTER for next question...")

    # Stop recording
    global RECORDING_FLAG
    RECORDING_FLAG = False
    vt1.join()
    vt2.join()

    # Merge audio + video
    merge_audio_video(raw_video, raw_audio, final_video)

    print("\nInterview Completed!")
    print(f"Transcript Saved: {transcript_path}")
    print(f"Video Saved: {final_video}")

if __name__ == "__main__":
    run_interview()
