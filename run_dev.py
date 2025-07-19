# Token counting for tiktoken-aware batching
import asyncio
import httpx
import tiktoken
import re
import hashlib
import json

encoding = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text):
    return len(encoding.encode(text))
# run_dev.py
import os
import sys
from dotenv import load_dotenv
import subprocess
from pathlib import Path

load_dotenv()

MAX_TOKENS = 10000  # Adjust as needed
CACHE_DIR = ".devsage_cache"

def get_file_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_cached_summary(file_hash):
    cache_path = Path(CACHE_DIR) / f"{file_hash}.json"
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("summary")
    return None

def save_cached_summary(file_hash, summary):
    Path(CACHE_DIR).mkdir(exist_ok=True)
    cache_path = Path(CACHE_DIR) / f"{file_hash}.json"
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary}, f)

def extract_definitions(text):
    return "\n".join(
        line for line in text.splitlines()
        if re.match(r"^\s*(def|class)\s+\w+", line)
    )

def get_files_to_summarize(directory):
    excluded_dirs = {"node_modules", "venv", ".venv", "__pycache__"}
    return [
        f for f in Path(directory).rglob("*")
        if f.is_file()
        and f.suffix in ['.py', '.js', '.html', '.css']
        and not any(part in excluded_dirs for part in f.parts)
    ]


async def summarize_batch(batch, api_key, prior_summaries=""):
    summaries = []
    for f in batch:
        text = f.read_text()
        file_hash = get_file_hash(text)
        cached_summary = load_cached_summary(file_hash)
        if cached_summary:
            summaries.append(f"# {f.name}\n{cached_summary}")
        else:
            content = extract_definitions(text) if f.suffix == '.py' else text
            prompt = f"""
You are analyzing one part of a larger software system.

Previously summarized parts:
{prior_summaries}

Now, summarize this new code file.
- Focus on what this file contributes to the system.
- Do NOT repeat what was already described.
- Emphasize newly introduced roles or logic.

File content:
# {f.name}
{content}
""".strip()
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            json_data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json=json_data, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                summary = data["choices"][0]["message"]["content"].strip()
                summaries.append(f"# {f.name}\n{summary}")
                save_cached_summary(file_hash, summary)
    return "\n\n".join(summaries)


async def run_all_batches(files, api_key):
    batch, size = [], 0
    batches = []
    sizes = []
    for f in files:
        text = f.read_text()
        tok = count_tokens(text)
        if size + tok > MAX_TOKENS:
            batches.append(list(batch))
            sizes.append(size)
            batch, size = [], 0
        batch.append(f)
        size += tok
    if batch:
        batches.append(list(batch))
        sizes.append(size)

    # Print batch sizes and estimated token counts before creating tasks
    for i, (batch, token_count) in enumerate(zip(batches, sizes)):
        print(f"Batch {i+1}: Summarizing {len(batch)} files... (estimated {token_count} tokens)")
    # Create tasks for all batches with empty prior_summaries for parallelism
    tasks = [asyncio.create_task(summarize_batch(batch, api_key, "")) for batch in batches]
    results = await asyncio.gather(*tasks)

    # Reconstruct prior_summaries in order to pass into the final prompt
    prior_summaries = "\n".join(results)
    return results


if len(sys.argv) != 2:
    print("Usage: python run_dev.py <target_directory>")
    sys.exit(1)

target = sys.argv[1]

async def main():
    files = get_files_to_summarize(target)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    global_summaries = await run_all_batches(files, api_key)

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
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": final_prompt}]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=json_data, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        print("\n\n=== Final Project Overview ===\n")
        print(data["choices"][0]["message"]["content"].strip())


if __name__ == "__main__":
    asyncio.run(main())