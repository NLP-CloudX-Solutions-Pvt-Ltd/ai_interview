import os
from dotenv import load_dotenv

env_path = os.path.abspath(".env")
print("Loading ENV from:", env_path)
load_dotenv(env_path)

print("Loaded API KEY?:", os.getenv("OPENAI_API_KEY"))


import json
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_questions(job_description: str, language=None):
    prompt = f"""
Generate exactly 5 interview questions.
Rules:
- 2-3 technical (1 scenario)
- Remaining HR
- If language or DSA present → add 1 coding question
Return JSON:
{{"questions":[{{"type":"technical","text":"..."}}]}}
JOB: {job_description}
LANG: {language}
"""

    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return json.loads(res.choices[0].message["content"])["questions"]
