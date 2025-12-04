# agent_config.py
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import traceback

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest ")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
TOP_K = int(os.getenv("TOP_K", 2))

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is required")


def build_agent():
    """Build a FAISS-powered agent using similarity search with Mistral AI."""

    # ---------------------------
    # Load FAISS vector store
    # ---------------------------
    def load_vector_store():
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}")

        embeddings = MistralAIEmbeddings(api_key=MISTRAL_API_KEY, model="mistral-embed")
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
        return vector_store

    vector_store = load_vector_store()

    # ---------------------------
    # Initialize Mistral chat LLM
    # ---------------------------
    llm = ChatMistralAI(
    mistral_api_key=MISTRAL_API_KEY,
    model=MISTRAL_MODEL,
    temperature=0.2,
    timeout=20
    )


    # ---------------------------
    # Prompt template
    # ---------------------------
    prompt_template = """
    **System Role and Goal:**
    You are the **Concise and Accurate University Information Portal Assistant** for ENSET Mohammedia. Your sole purpose is to provide direct, friendly, and highly accurate answers based **ONLY** on the information found in the **Context** block below.

    **Constraints (Strict RAG Rules):**
    1.  **Source Constraint:** Answer **MUST** be derived *entirely* from the provided **Context**.
    2.  **External Knowledge Prohibition:** Do not use any external knowledge, assumptions, or general university information. If the Context does not contain the answer, you must state: **"I apologize, but I cannot find that specific information in the provided context documents."**
    3.  **Language:** Respond in the same language as the user's question (French or English).
    4.  **Conciseness:** Keep answers maximally concise and friendly.

    

    **Key Task Enforcement (Timetable Queries):**
    When asked about a schedule or timetable, you **MUST** provide the following details precisely as they appear in the source:
    * Day and Date (if applicable)
    * Time Slot
    * Group (e.g., 1ère année BDCC Groupe A)
    * Course Title (**Must** be enclosed in **bold**).
    * Professor (M. / Mme. [Name])
    * Room/Location (e.g., salle 2).
    *You **MUST** end your answer by citing the source document, your citation must be: **(Source: ...)**Example: (Source : Emploi du temps S1, 2025/2026, ENSET Mohammedia)*
    
    If a class slot is empty, state clearly that there is **"no class"** or **"Pas de cours programmé."**

    **Context:**
    {context}

    **User's Question:**
    {question}

    **Your Concise Answer:**
    """
    prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    # ---------------------------
    # Simple Agent with similarity search
    # ---------------------------
    class SimpleAgent:
        def __init__(self, vector_store, llm, prompt, top_k=TOP_K):
            self.vector_store = vector_store
            self.llm = llm
            self.prompt = prompt
            self.top_k = top_k
            self.chat_history = []

        def run(self, user_message, user_id=None):
            """Process user message via similarity search + LLM"""
            try:
                # ---------------------------
                # Fetch top-k relevant documents
                # ---------------------------
                docs = self.vector_store.similarity_search(user_message, k=self.top_k)
                context = "\n\n".join([doc.page_content for doc in docs])

                # ---------------------------
                # Fill prompt and query LLM
                # ---------------------------
                prompt_text = self.prompt.format(context=context, question=user_message)
                response = self.llm.invoke(prompt_text)

                # ---------------------------
                # Update chat history
                # ---------------------------
                self.chat_history.append({"role": "user", "content": user_message})
                self.chat_history.append({"role": "assistant", "content": response.content})
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]

                class Response:
                    def __init__(self, text):
                        self.text = text
                        self.debug = None

                return Response(response.content)

            except Exception as e:
                print(f"Error in agent run: {str(e)}")
                traceback.print_exc()
                class Response:
                    def __init__(self, text):
                        self.text = text
                        self.debug = None
                return Response(f"Error: {str(e)}")

    return SimpleAgent(vector_store, llm, prompt)
