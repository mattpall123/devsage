# 📁 Project DevSage: AI-Powered Folder Documentation Generator

Project Sage is a full-stack tool that lets users upload an entire project folder and receive auto-generated high-level documentation powered by AI. It visually displays folder structure and file contents, and summarizes code logic to help developers onboard quickly and improve technical communication.

## Features

- Drag-and-drop folder upload 
- Real-time project tree and file preview UI
- Auto-documentation generation via AI using GPT-4
- FastAPI backend with support for `.zip` file handling
- Next.js 15 (App Router, React 19)

## Built With

- [Next.js 15.2.4](https://nextjs.org/) — frontend framework
- [React 19](https://react.dev/)
- [FastAPI](https://fastapi.tiangolo.com/) — Python backend server
- [JSZip](https://stuk.github.io/jszip/) — in-browser zipping of uploaded directories
- [Tailwind CSS](https://tailwindcss.com/) — utility-first CSS
- [Radix UI](https://www.radix-ui.com/) — component primitives
- [Lucide React](https://lucide.dev/) — icons
- [Shadcn UI](https://ui.shadcn.com/) — component templates
- [OpenAI GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4) — summarization engine


## How It Works

1. The frontend uses `webkitdirectory` to let users upload folders (and preserve path structure).
2. Files are parsed and read via FileReader in the browser.
3. The folder structure is built into a tree and displayed via collapsible UI.
4. When "Generate Documentation" is clicked:
   - Files are zipped in-browser using JSZip.
   - The zip is POSTed to a FastAPI endpoint (`/summarize`).
   - The backend extracts files and uses OpenAI’s API to summarize logic.
5. The frontend receives and displays a Markdown-style summary.

## Setup Instructions


### Backend

```bash
# In the project root (where main.py exists)

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### 🔧  frontend
cd frontend
pnpm install
pnpm dev