from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import zipfile, tempfile, subprocess, os
import sys
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize")
async def summarize(project: UploadFile):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "project.zip")
        with open(zip_path, "wb") as f:
            f.write(await project.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Use the virtual environment's Python executable
    
        python_exe = sys.executable
        
        result = subprocess.run(
            [python_exe, "run_dev.py", tmpdir],
            capture_output=True,
            text=True
        )

        return {"summary": result.stdout.strip()}