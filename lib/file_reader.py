import os

def get_source_files(path, extensions={'.py', '.js', '.ts', '.java', '.html', '.css'}):
    source_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                source_files.append(full_path)
    return source_files