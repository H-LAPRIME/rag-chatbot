# 🤖 ENSET Mohammedia RAG & SQL Chatbot

A powerful, hybrid intelligent assistant for **ENSET Mohammedia**. This chatbot combines **RAG (Retrieval-Augmented Generation)** for unstructured document search (PDFs, TXT, MD) with **SQL-based structured data retrieval** for database queries.

---

## 🌟 Features

- **Hybrid Intelligence**: Automatically switches between searching documents (RAG) and querying the database (SQL).
- **Pro Timetables**: Specifically optimized to extract and format class schedules into clean, readable tables.
- **Deep Extraction**: Uses `MarkItDown` with PDF support to index complex documents.
- **Smart Formatting**: Returns responses in structured JSON for a modern, component-based UI.
- **Mistral AI Powered**: Utilizes state-of-the-art Mistral models for both embeddings and reasoning.

---

## 🏗️ Project Structure

- `backend/`: Flask API, Agent logic, Vector Store (FAISS), and Database handlers.
- `frontend/`: Modern Next.js Chat Interface.
- `docs/`: (Temporary) Folder for user-uploaded documents.

---

## 🚀 Getting Started

### 1️⃣ Backend Setup
1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r Requirements.txt
   pip install markitdown[pdf]  # Ensure PDF support
   ```
4. **Configure `.env`**:
   Create a `.env` file in the `backend/` directory:
   ```env
   MISTRAL_API_KEY=your_key_here
   MISTRAL_MODEL=mistral-small-latest
   TOP_K=8
   USE_RELOADER=False
   ```
5. **Run the server**:
   ```bash
   python app.py
   ```

### 2️⃣ Frontend Setup
1. **Navigate to the frontend folder**:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install  # or pnpm install
   ```
3. **Run the development server**:
   ```bash
   npm run dev
   ```
4. **Access the App**: Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🛠️ Key Components

### RAG System
Located in `backend/embedding/`, the system converts PDFs and text files into a FAISS vector index. The `agent_config.py` handles semantic search.

### SQL Integration
Located in `backend/database/`, it handles natural language to SQL translation, allowing the agent to query structured data about courses, departments, and faculty.

### The Agent
The core logic resides in `backend/agent/agent_config.py`. It uses specialized prompt engineering to prioritize context and prevent hallucinations.

---

## 📋 Best Practices for Usage

- **Timetables**: Upload PDF schedules and rebuild the index via the UI for the best results.
- **Questions**: Ask about specific departments, teachers, or schedules.
- **Cleanup**: The `faiss_index` and `temp_uploads` are ignored by git to keep your repository clean.

---

## 🤝 Contributing
Feel free to fork this project and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
