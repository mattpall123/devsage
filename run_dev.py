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

def get_files_to_summarize(directory):
    return [f for f in Path(directory).rglob("*") if f.suffix in ['.py', '.js', '.html', '.css']]

def summarize_batch(batch, client):
    content = "\n\n".join(f"# {f.name}\n{f.read_text()}" for f in batch)
    prompt = f"You will be given multiple files. Summarize their purpose and any important logic:\n\n{content}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content)

if len(sys.argv) != 2:
    print("Usage: python run_dev.py <target_directory>")
    sys.exit(1)

target = sys.argv[1]

# Run summarization in batches
files = get_files_to_summarize(target)
batch, size = [], 0
for f in files:
    text = f.read_text()
    if size + len(text) > MAX_TOKENS:
        input(f"\nAbout to summarize {len(batch)} files. Proceed? (Enter to continue)")
        summarize_batch(batch, client)
        batch, size = [], 0
    batch.append(f)
    size += len(text)

if batch:
    input(f"\nAbout to summarize final batch of {len(batch)} files. Proceed? (Enter to continue)")
    summarize_batch(batch, client)