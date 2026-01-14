from .build_index import build_index
from dotenv import load_dotenv
import os
load_dotenv()
from pathlib import Path

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")

def delete_all_files(folder_path):
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    for item in folder.iterdir():
        if item.is_file():
            item.unlink()

def rebuild_index(FOLDER_PATH: str):
    delete_all_files(FAISS_INDEX_PATH)
    return build_index(folder_path=FOLDER_PATH)
          
