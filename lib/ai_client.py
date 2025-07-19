from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os

load_dotenv()  # Load from .env

def summarize_code(file_path, code):
    prompt = f"""You are an AI assistant. Explain the following code clearly and concisely.

Focus on:
- The overall purpose
- Key functions and classes
- Structure and logic

FILE: {file_path}

---

{code}
"""

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1000)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error while summarizing {file_path}: {e}"