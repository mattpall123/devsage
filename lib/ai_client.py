from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os

load_dotenv()  # Load from .env

def summarize_code(file_path, code):
    prompt = f"""\You are a technical writer AI that specializes in writing clear and concise high-level documentation for software projects.

You will be given the raw text of several source code files concatenated together.

Your task is to:
1. **Summarize the purpose of the project**
2. **Explain what the main components or files do**
3. **Describe how the system works overall**
4. **Mention any important design patterns, data structures, or dependencies used**
5. Format the output as if it will be pasted into a README.md or internal documentation

Write for developers who have never seen this code before but know how to program.

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