from flask import Flask, request, jsonify ,send_from_directory
from flask_cors import CORS
from agent.agent_config import build_agent
from embedding.build_index import build_index
from embedding.rebuild_index import rebuild_index
import os
from werkzeug.utils import secure_filename
from files_manager.files_utils import *
from database.insert_db import process_file_and_insert, process_multiple_files, process_folder
from database.read_db import process_query_and_select
import re
app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = './temp_uploads'
UPLOAD_SQL_FOLDER = './temp_sql_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx', 'html'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

try:
 agent = build_agent()  # initialize once
except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200



@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint - process user messages"""
    data = request.json
    user_msg = data.get("message", "")
    user_id = data.get("user_id")  # for per-user memory if you want

    def clean_json_response(raw_response: str) -> dict:
        """
        Cleans a string containing JSON wrapped in triple backticks and converts it to a Python dict.
        """
        # Remove ```json at the start and ``` at the end
        cleaned = re.sub(r"^```json\s*|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()
        # Convert to Python dict
        return cleaned
            
    
# ask the agent to handle the message and return answer
    global agent
    if agent is None:
        try:
            print("Trying to re-initialize agent...")
            agent = build_agent()
        except Exception as e:
            return jsonify({"error": f"Agent could not be initialized: {str(e)}"}), 500

    response = agent.run(user_message=user_msg, user_id=user_id)
    return jsonify({
        "reply": clean_json_response(response.text), 
        "thoughts": response.debug if hasattr(response, "debug") else None
    }), 200





@app.route("/api/build-index", methods=["POST"])
def build_index_endpoint():
    """Build FAISS index from uploaded documents"""
    data = request.json or {}
    folder_path = data.get("folder_path", UPLOAD_FOLDER)
        
    print(f"Building index from: {folder_path}")
   



def rebuild_logic(folder_path):
     try:
        # Call build_index function from build_index.py
        # This is a long-running operation, so we set a longer timeout
        result = rebuild_index(folder_path)
        
        if result["success"]:
            return jsonify({
                "message": "Index built successfully",
                "chunks_created": result["chunks_created"],
                "documents_processed": result["documents_processed"]
            }), 200
        else:
            error_msg = result.get("error", "Failed to build index")
            # Check if it's a quota error
            status_code = 429 if "quota" in error_msg.lower() or "429" in error_msg else 400
            return jsonify({
                "error": error_msg
            }), status_code
    
     except Exception as e:
        error_str = str(e)
        print(f"Error in Rebuild_index_endpoint: {error_str}")
        import traceback
        traceback.print_exc()
        
        # Check if it's a quota error
        if "quota" in error_str.lower() or "429" in error_str:
            return jsonify({
                "error": error_str
            }), 429
        else:
            return jsonify({
                "error": error_str
            }), 500

@app.route("/api/rebuild-index", methods=["GET"])
def rebuild_index_endpoint():
    return rebuild_logic(UPLOAD_FOLDER)

# FEEDING FILES MANAGEMENT END POINTS #####################
# ---------- POST: Upload Files ----------
@app.route("/api/files", methods=["POST"])
def upload_files():
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist("files")
        response = []

        for file in files:
            filename = secure_filename(file.filename)

            if not allowed_file(filename):
                response.append({
                    "name": filename,
                    "status": "rejected",
                    "reason": "unsupported file type"
                })
                continue

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            return rebuild_logic(UPLOAD_FOLDER)
        

# ---------- GET: List Files ----------
@app.route("/api/files", methods=["GET"])
def list_files():
    files = []

    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path) and allowed_file(filename):
            files.append(file_metadata(file_path))

    return jsonify(files), 200

# ---------- DELETE: Remove File ----------
@app.route("/api/files/<string:filename>", methods=["DELETE"])
def delete_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    os.remove(file_path)
    return jsonify({"message": f"{filename} deleted successfully"}), 200

# DOWLOAD FILE END POINT
@app.route("/api/files/<string:filename>/download", methods=["GET"])
def download_file(filename):
    filename = secure_filename(filename)

    if not allowed_file(filename):
        return jsonify({"error": "Unsupported file type"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(
        directory=UPLOAD_FOLDER,
        path=filename,
        as_attachment=True
    )


# SQL DATA EXTRACTION AND INSERTION ENDPOINTS #####################
# ---------- POST: Extract and Insert Data from Single File ----------
@app.route("/api/sql/insert-file", methods=["POST"])
def insert_file_data():
    """Extract structured data from a file and insert into PostgreSQL database"""
    try:
        data = request.json or {}
        file_path = data.get("file_path")
        filename = data.get("filename")
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        # Process file and insert data
        result = process_file_and_insert(file_path, filename)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Data inserted successfully",
                "file": result.get("file"),
                "statements_count": result.get("statements_count", 0),
                "parsed_queries": result.get("parsed_queries", []),
                "execution_results": result.get("execution_results", []),
                "text_length": result.get("text_length", 0)
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to insert data"),
                "file": result.get("file"),
                "execution_results": result.get("execution_results", [])
            }), 400
    
    except Exception as e:
        error_str = str(e)
        print(f"Error in insert_file_data: {error_str}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": error_str
        }), 500

# ---------- POST: Extract and Insert Data from Multiple Files ----------
@app.route("/api/sql/insert-files", methods=["POST"])
def insert_files_data():
    """Extract structured data from multiple files and insert into PostgreSQL database"""
    try:
        data = request.json or {}
        file_paths = data.get("file_paths", [])
        
        if not file_paths or not isinstance(file_paths, list):
            return jsonify({"error": "file_paths must be a non-empty list"}), 400
        
        # Check if all files exist
        missing_files = [fp for fp in file_paths if not os.path.exists(fp)]
        if missing_files:
            return jsonify({
                "error": f"Files not found: {', '.join(missing_files)}"
            }), 404
        
        # Process files and insert data
        results = process_multiple_files(file_paths)
        
        # Count successes and failures
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        return jsonify({
            "success": len(failed) == 0,
            "message": f"Processed {len(results)} files: {len(successful)} successful, {len(failed)} failed",
            "total_files": len(results),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "results": results
        }), 200 if len(failed) == 0 else 207  # 207 Multi-Status
    
    except Exception as e:
        error_str = str(e)
        print(f"Error in insert_files_data: {error_str}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": error_str
        }), 500

# ---------- POST: Extract and Insert Data from Folder ----------
@app.route("/api/sql/insert-folder", methods=["POST"])
def insert_folder_data():
    """Extract structured data from all files in a folder and insert into PostgreSQL database"""
    try:
        data = request.json or {}
        folder_path = data.get("folder_path", UPLOAD_SQL_FOLDER)
        file_extensions = data.get("file_extensions", None)
        
        if not os.path.exists(folder_path):
            return jsonify({"error": f"Folder not found: {folder_path}"}), 404
        
        if not os.path.isdir(folder_path):
            return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400
        
        # Process folder and insert data
        results = process_folder(folder_path, file_extensions)
        
        # Count successes and failures
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        return jsonify({
            "success": len(failed) == 0,
            "message": f"Processed {len(results)} files from folder: {len(successful)} successful, {len(failed)} failed",
            "folder_path": folder_path,
            "total_files": len(results),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "results": results
        }), 200 if len(failed) == 0 else 207  # 207 Multi-Status
    
    except Exception as e:
        error_str = str(e)
        print(f"Error in insert_folder_data: {error_str}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": error_str
        }), 500

# ---------- POST: Extract and Insert Data from Uploaded Files ----------
@app.route("/api/sql/insert-uploaded", methods=["POST"])
def insert_uploaded_files():
    """Extract structured data from uploaded files and insert into PostgreSQL database"""
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "No files provided"}), 400
        
        file_paths = []
        saved_files = []
        
        # Save uploaded files temporarily
        for file in files:
            filename = secure_filename(file.filename)
            
            if not allowed_file(filename):
                continue
            
            os.makedirs(UPLOAD_SQL_FOLDER, exist_ok=True)
            file_path = os.path.join(UPLOAD_SQL_FOLDER, filename)
            file.save(file_path)
            file_paths.append(file_path)
            saved_files.append(filename)
        
        if not file_paths:
            return jsonify({"error": "No valid files to process"}), 400
        
        # Process files and insert data
        results = process_multiple_files(file_paths)
        
        # Count successes and failures
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        return jsonify({
            "success": len(failed) == 0,
            "message": f"Processed {len(results)} files: {len(successful)} successful, {len(failed)} failed",
            "uploaded_files": saved_files,
            "total_files": len(results),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "results": results
        }), 200 if len(failed) == 0 else 207  # 207 Multi-Status
    
    except Exception as e:
        error_str = str(e)
        print(f"Error in insert_uploaded_files: {error_str}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": error_str
        }), 500

@app.route("/api/sql/test-select", methods=["POST"])
def test_select():
    data = request.json
    user_msg = data.get("message", "")
    
    # ask the agent to handle the message and return answer
    response = process_query_and_select(question=user_msg)
    return jsonify(response), 200



if __name__ == "__main__":
    # Configure to prevent constant restarts from venv file changes
    # The watchdog reloader detects changes in venv, causing connection resets during uploads
    
    # Option 1: Disable reloader for production-like stability (recommended for file uploads)
    # Set USE_RELOADER=False in environment to disable, or keep True for development
    use_reloader = os.environ.get('USE_RELOADER', 'True').lower() == 'true'
    
    app.run(
        host="0.0.0.0", 
        port=5000, 
        debug=True,
        use_reloader=use_reloader,  # Set to False to prevent restarts during uploads
        threaded=True  # Enable threading for better concurrent request handling
    )
