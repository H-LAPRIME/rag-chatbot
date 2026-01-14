# Updated build_index.py fully compatible with Mistral AI

import os
import time
from uuid import uuid4
import faiss
from pathlib import Path
from dotenv import load_dotenv
from markitdown import MarkItDown
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import traceback
import shutil

load_dotenv()

# Load Mistral API key and models
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
DOCS_FOLDER = os.getenv("DOCS_FOLDER", "../docs")


def extract_text_from_document(file_path):
    md = MarkItDown(enable_plugins=True)
    result = md.convert(file_path)
    return result.text_content


def split_text_into_chunks(text, source):
    candidate_name = os.path.splitext(source)[0]
    document = Document(
        page_content=text,
        metadata={"source": source, "candidate": candidate_name}
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents([document])


def init_embeddings():
    try:
        print(f"Initializing Mistral embeddings: {MISTRAL_EMBED_MODEL}")
        embeddings = MistralAIEmbeddings(api_key=MISTRAL_API_KEY, model=MISTRAL_EMBED_MODEL)
        test_vec = embeddings.embed_query("test")
        print(f"Mistral embedding dimension: {len(test_vec)}")
        return embeddings
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        traceback.print_exc()
        raise


def create_new_faiss_index(embeddings):
    print("Creating new FAISS index...")
    dim = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(dim)
    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )


def create_and_populate_new_index(chunks, embeddings):
    vector_store = create_new_faiss_index(embeddings)
    if chunks:
        ids = [str(uuid4()) for _ in chunks]
        vector_store.add_documents(documents=chunks, ids=ids)
    return vector_store


def add_to_faiss_index(chunks, embeddings):
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            existing_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            if chunks:
                new_store = create_new_faiss_index(embeddings)
                ids = [str(uuid4()) for _ in chunks]
                new_store.add_documents(documents=chunks, ids=ids)
                existing_store.merge_from(new_store)
            return existing_store
        except Exception as e:
            backup = f"faiss_index_backup_{int(time.time())}"
            shutil.move(FAISS_INDEX_PATH, backup)
            return create_and_populate_new_index(chunks, embeddings)
    else:
        return create_and_populate_new_index(chunks, embeddings)


def load_documents_from_folder(folder_path):
    documents = []
    folder = Path(folder_path)
    supported_formats = ['*.txt', '*.pdf', '*.md', '*.docx', '*.html']
    for pattern in supported_formats:
        for file_path in folder.glob(f"**/{pattern}"):
            try:
                content = extract_text_from_document(str(file_path))
                if content.strip():
                    documents.append({
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "content": content,
                        "char_count": len(content)
                    })
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
    return documents


def build_index(folder_path=None):
    folder = folder_path or DOCS_FOLDER
    print(f"Building index from folder: {folder}")

    documents = load_documents_from_folder(folder)
    if not documents:
        return {
            "success": False,
            "message": "No documents found",
            "chunks_created": 0,
            "documents_processed": 0
        }

    all_chunks = []
    for doc in documents:
        chunks = split_text_into_chunks(doc['content'], doc['file_name'])
        all_chunks.extend(chunks)

    embeddings = init_embeddings()
    vector_store = create_and_populate_new_index(all_chunks, embeddings)

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vector_store.save_local(FAISS_INDEX_PATH)

    return {
    "success": True,
    "message": "Index built successfully",
    "chunks_created": len(all_chunks),
    "documents_processed": len(documents),
    "index_path": FAISS_INDEX_PATH
    }


if __name__ == "__main__":
    build_index()
