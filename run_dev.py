# run_dev.py
import os
import sys
from dotenv import load_dotenv
import subprocess
from pathlib import Path
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_TOKENS = 10000  # Adjust as needed
global_summaries = []

def get_files_to_summarize(directory):
    return [f for f in Path(directory).rglob("*") if f.suffix in ['.py', '.js', '.html', '.css']]

def summarize_batch(batch, client, prior_summaries=""):
    content = "\n\n".join(f"# {f.name}\n{f.read_text()}" for f in batch)

    prompt = f"""
You are analyzing one part of a larger software system.

Previously summarized parts:
{prior_summaries}

Now, summarize this new batch of code files.
- Focus on what this batch contributes to the system.
- Do NOT repeat what was already described.
- Group related files by functionality.
- Emphasize newly introduced roles or logic.

Batch content:
{content}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message.content.strip()
    return summary

if len(sys.argv) != 2:
    print("Usage: python run_dev.py <target_directory>")
    sys.exit(1)

target = sys.argv[1]

# Run summarization in batches
files = get_files_to_summarize(target)
batch, size = [], 0
global_summaries = []
for f in files:
    text = f.read_text()
    if size + len(text) > MAX_TOKENS:
        print(f"Summarizing {len(batch)} files...")
        summary = summarize_batch(batch, client, "\n".join(global_summaries))
        global_summaries.append(summary)
        batch, size = [], 0
    batch.append(f)
    size += len(text)

if batch:
    print(f"Summarizing {len(batch)} files...")
    summary = summarize_batch(batch, client, "\n".join(global_summaries))
    global_summaries.append(summary)

# Final synthesis step
final_prompt = f"""
You are a senior developer writing documentation for a project composed of the following parts.

Below are summaries of each code section. Based on this, write:
- A high-level description of what the entire project does
- An overview of how the main components interact
- Any design patterns, architectural choices, or key libraries
- Keep it concise, clear, and structured like a README overview

{"\n".join(global_summaries)}
"""

final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": final_prompt}]
)

print("\n\n=== Final Project Overview ===\n")
print(final_response.choices[0].message.content.strip())