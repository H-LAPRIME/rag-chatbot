import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import shutil

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="UniRAG Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS moderne et élégant
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.1em;
        opacity: 0.95;
        font-weight: 300;
    }
    
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08);
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0;
        margin-left: auto;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
        animation: slideInRight 0.3s ease-out;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
        color: #2d3748;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 12px 0;
        margin-right: auto;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 24px;
        font-size: 13px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .status-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .status-online {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
        color: white;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        border: 2px dashed #667eea;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #764ba2;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
    }
    
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    .quick-help-card {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 16px 0;
    }
    
    .quick-help-card h4 {
        color: #667eea;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    .quick-help-card ul {
        list-style: none;
        padding: 0;
    }
    
    .quick-help-card li {
        padding: 8px 0;
        border-bottom: 1px solid rgba(102, 126, 234, 0.1);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .quick-help-card li:hover {
        padding-left: 10px;
        color: #667eea;
    }
    
    .quick-help-card li:last-child {
        border-bottom: none;
    }
    
   
    
    .stButton button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .footer {
        text-align: center;
        color: #718096;
        font-size: 13px;
        padding: 20px;
        margin-top: 40px;
        border-top: 2px solid #e0e0e0;
    }
    
    .welcome-message {
        background: linear-gradient(135deg, #fff9e6 0%, #ffe5b4 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
        border-left: 4px solid #ffa500;
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:5000"

# Sidebar configuration
with st.sidebar:
    st.image("ENSET Mohammedia 40th Ann-vector.ma.png", use_container_width=True)
    st.markdown("---")
    
    st.markdown("### ⚙️ Paramètres")
    
    # Backend status check avec animation
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        status = "En ligne"
        status_class = "status-online"
        status_icon = "🟢"
    except:
        status = "Hors ligne"
        status_class = "status-offline"
        status_icon = "🔴"
    
    st.markdown(f'<div class="status-badge {status_class}">{status_icon} Backend {status}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📚 Base de Connaissances")
    
    # Upload section améliorée
    
    st.markdown("**📤 Télécharger des Documents**")
    
    uploaded_files = st.file_uploader(
        "Formats acceptés: .txt, .pdf",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        help="Ajoutez des documents à la base de connaissances",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} fichier(s) sélectionné(s)")
        # Choix: où insérer les documents
        insert_target = st.radio(
            "Si vous avez besoin : choisir où insérer",
            options=("Vector DB (index seulement)", "Database (SQL)", "Both (Vector + Database)"),
            index=0,
            help="Choisissez d'insérer le(s) document(s) dans la base de vecteurs, la base de données relationnelle, ou les deux."
        )

        if insert_target == "Both (Vector + Database)":
            st.warning("⚠️ Attention : sélectionner les deux peut prendre beaucoup de temps, surtout pour les gros fichiers.")
        
        if st.button("🚀 Construire l'Index", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("⚙️ Traitement en cours..."):
                try:
                    # Create temp folder
                    temp_folder = "./temp_uploads"
                    os.makedirs(temp_folder, exist_ok=True)
                    
                    # Save uploaded files
                    for i, uploaded_file in enumerate(uploaded_files):
                        progress_bar.progress((i + 1) / len(uploaded_files) * 0.5)
                        status_text.text(f"💾 Sauvegarde: {uploaded_file.name}")
                        
                        file_path = os.path.join(temp_folder, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    progress_bar.progress(0.6)
                    status_text.text("🔨 Préparation des opérations demandées...")

                    # Determine actions based on user's choice
                    build_index_needed = insert_target in ("Vector DB (index seulement)", "Both (Vector + Database)")
                    insert_db_needed = insert_target in ("Database (SQL)", "Both (Vector + Database)")
                    abort_after_index_failure = False

                    # Build index if requested
                    if build_index_needed:
                        status_text.text("🔨 Construction de l'index...")
                        response = requests.post(
                            f"{BACKEND_URL}/api/build-index",
                            json={"folder_path": temp_folder},
                            timeout=120
                        )

                        progress_bar.progress(0.95)

                        if response.status_code == 200:
                            data = response.json()
                            status_text.empty()
                            st.success(f"✅ {data.get('message', 'Index créé avec succès!')}")
                            st.balloons()
                            st.info(f"📊 {data.get('chunks_created', 0)} segments créés")
                        else:
                            st.error(f"❌ Erreur lors de la construction de l'index: {response.text}")
                            # If only vector was requested and index failed, abort further actions
                            if not insert_db_needed:
                                shutil.rmtree(temp_folder, ignore_errors=True)
                                abort_after_index_failure = True

                    # Insert into DB if requested
                    if insert_db_needed and not abort_after_index_failure:
                        status_text.text("💾 Insertion des données structurées en base de données...")
                        try:
                            insert_resp = requests.post(
                                f"{BACKEND_URL}/api/sql/insert-folder",
                                json={"folder_path": temp_folder},
                                timeout=300
                            )

                            if insert_resp.status_code in (200, 207):
                                insert_data = insert_resp.json()
                                st.success(f"✅ Insertion en base terminée: {insert_data.get('successful_count', 0)} réussies, {insert_data.get('failed_count', 0)} échouées")
                            else:
                                st.error(f"❌ Échec de l'insertion en base: {insert_resp.status_code} {insert_resp.text}")
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'insertion en base: {e}")

                    # Final cleanup
                    shutil.rmtree(temp_folder, ignore_errors=True)
                
                except Exception as e:
                    st.error(f"❌ Échec du téléchargement: {str(e)}")
                finally:
                    progress_bar.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        total_messages = len(st.session_state.messages)
        user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
        bot_messages = total_messages - user_messages
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📨 Total", total_messages, delta=None)
        with col2:
            st.metric("👤 Vous", user_messages, delta=None)
        with col3:
            st.metric("🤖 Bot", bot_messages, delta=None)
    else:
        st.info("💬 Commencez une conversation pour voir les statistiques")
    
    st.markdown("---")
    
    # Clear history button
    if st.button("🗑️ Effacer l'Historique", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.success("✅ Historique effacé!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Astuce")
    st.info("Posez des questions claires et précises pour obtenir les meilleures réponses!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main header
st.markdown("""
    <div class="main-header">
        <h1>🎓 UniRAG Chatbot</h1>
        <p>Assistant intelligent pour vos questions académiques</p>
    </div>
""", unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([2.5, 1])

with col1:
    st.markdown("### 💬 Conversation")
    
    # Chat container
    st.markdown('<div class="chat-messages-container" id="chat-container">', unsafe_allow_html=True)
    
    if len(st.session_state.messages) == 0:
        st.markdown("""
            <div class="welcome-message">
                <h3>👋 Bienvenue!</h3>
                <p>Je suis votre assistant universitaire. Posez-moi vos questions sur:</p>
                <p>📅 Emplois du temps • 📚 Cours • 🧪 Laboratoires • 📝 Examens • 👨‍🏫 Enseignants</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Display messages in normal order (oldest first)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">👤 <strong>Vous:</strong><br/>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 <strong>Assistant:</strong><br/>{msg["content"]}</div>', unsafe_allow_html=True)
        
        # Auto-scroll to bottom with JavaScript
        st.markdown("""
            <script>
                var chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            </script>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 🎯 Questions")
    
    st.markdown("""
        <div class="quick-help-card">
            <h4>Exemples</h4>
            <ul>
                <li>📅 Emploi du temps?</li>
                <li>📚 Prérequis cours X?</li>
                <li>🧪 Heures laboratoire?</li>
                <li>📝 Dates examens?</li>
                <li>👨‍🏫 Contact prof Y?</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Activité Récente")
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        recent_count = min(3, len([m for m in st.session_state.messages if m["role"] == "user"]))
        st.metric("Dernières Questions", recent_count)
    else:
        st.info("Aucune activité récente")

st.markdown("### 📝 Posez votre Question")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Votre question",
            placeholder="Tapez votre question ici... (Ex: Quel est mon emploi du temps?)",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Envoyer 🚀", use_container_width=True, type="primary")
    
    if submit_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show loading spinner
        with st.spinner("🔄 Recherche de la meilleure réponse..."):
            try:
                # Send to backend
                response = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={"message": user_input, "user_id": "streamlit_user"},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    bot_reply = data.get("reply", "Aucune réponse reçue")
                    
                    # Add bot message
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    
                    st.success("✅ Réponse reçue!")
                    st.rerun()
                else:
                    st.error(f"❌ Erreur backend: {response.status_code}")
                    st.write(response.text)
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de se connecter au backend. Assurez-vous que Flask tourne sur le port 5000")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Footer amélioré
st.markdown("""
    <div class="footer">
        <p><strong>UniRAG Chatbot</strong> v2.0 | Propulsé par RAG & IA</p>
        <p>Dernière mise à jour: """ + datetime.now().strftime("%d/%m/%Y à %H:%M") + """</p>
        <p>💡 Besoin d'aide? Consultez la section "Exemples de Questions"</p>
    </div>
""", unsafe_allow_html=True)