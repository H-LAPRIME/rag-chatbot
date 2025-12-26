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
TOP_K = int(os.getenv("TOP_K", 4))

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

    # ---------------------------F
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
            give answers based only on the **context** in the same language of the question , and if the question about something that need a better response visualization like "emploies de tempes" try to make a table with necessary fields

            **Context:**
            {context}

            **User Question:**
            {question}

            **Answer:**
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
