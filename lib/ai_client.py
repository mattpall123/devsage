from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os

load_dotenv()  # Load from .env

def summarize_code(file_path, code):
    prompt = f"""\You are a senior software engineer and expert technical writer. Below is a raw concatenation of source code files from a single codebase. Your task is to generate professional, clear documentation that helps developers understand the project.

Instructions:
- Determine the overall purpose of the project.
- Group explanations by component, class, function, or logical section.
- Describe key functions, methods, and modules, along with what they do and how they interact.
- Skip boilerplate. Focus on meaningful logic and flow.
- Include example usage if it can be inferred from the code.
- Keep the documentation readable in a CLI (use Markdown-style formatting where helpful).
- Do not repeat code unnecessarily — explain what it does.
- Output in a format suitable for terminal or markdown viewer.

Begin analysis of the code below:

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