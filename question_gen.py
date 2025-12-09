import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)


def build_prompt(job_description: str, language: str | None):
    return f"""
Return ONLY valid JSON. No extra text.

Generate EXACTLY 5 interview questions:

Format:
{{
  "questions": [
    {{
      "role": "technical" | "hr",
      "subtype": "scenario" | "tech_stack" | "coding" | "general",
      "text": "..."
    }}
  ]
}}

Rules:
- 5 questions exactly.
- 2 technical:
    - 1 scenario-based
    - 1 tech-stack-based
- Add 1 coding question ONLY if JD mentions DSA/algorithms.
- 2 HR questions.
- Keep questions short.

JOB DESCRIPTION:
\"\"\"{job_description}\"\"\"
LANGUAGE: {language}
"""


def extract_json(content: str):
    try:
        return json.loads(content)
    except:
        start = content.find("{")
        end = content.rfind("}") + 1
        return json.loads(content[start:end])


def generate_questions(job_description: str, language=None):
    prompt = build_prompt(job_description, language)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    content = response.choices[0].message["content"]
    data = extract_json(content)
    return data["questions"]
