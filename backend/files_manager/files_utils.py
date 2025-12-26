import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# Folder to store uploaded files
UPLOAD_FOLDER = os.getenv("FEEDING_FILES_FOLDER_PATH")
# Allowed extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx', 'html'}

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def file_metadata(file_path):
    stat = os.stat(file_path)
    return {
        "id": str(uuid.uuid4()),
        "name": os.path.basename(file_path),
        "type": os.path.splitext(file_path)[1][1:],
        "size": format_size(stat.st_size),
        "uploadedAt": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d"),
        "status" : "indexed"
}
