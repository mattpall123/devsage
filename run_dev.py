# run_dev.py
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

# Example target path
target = "../Downloads/Movie-Website-main"

# Run the CLI tool
subprocess.run(["python", "devsage.py", target])