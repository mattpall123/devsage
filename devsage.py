import argparse
import os
from lib.file_reader import get_source_files
from lib.ai_client import summarize_code

def main():
    parser = argparse.ArgumentParser(description="DevSage: AI-powered codebase documentation CLI")
    parser.add_argument("path", help="Path to the codebase to document")
    parser.add_argument("--out", default="docs", help="Output directory for generated docs")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    source_files = get_source_files(args.path)

    if not source_files:
        print("❌ No supported source files found.")
        return

    output_path = os.path.join(args.out, "DOCUMENTATION.md")
    with open(output_path, "w") as output_file:
        for file_path in source_files:
            print(f"📄 Processing: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                summary = summarize_code(file_path, code)
                output_file.write(f"## {file_path}\n\n{summary}\n\n---\n\n")
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")

    print(f"\n✅ Documentation saved to: {output_path}")

if __name__ == "__main__":
    main()