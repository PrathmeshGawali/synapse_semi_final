import streamlit as st
from utils.processing import process_inputs, create_vector_db
from features import *

# Page configuration
st.set_page_config(page_title="SynapseIQ", layout="wide")

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'feature_output' not in st.session_state:
    st.session_state.feature_output = None
if 'feature_type' not in st.session_state:
    st.session_state.feature_type = None

# Layout
col1, col2, col3 = st.columns([1, 2, 1])

# ==========================
# 🛠️ Left Panel: Inputs
# ==========================
with col1:
    st.header("📥 Upload Content")
    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True)
    url_input = st.text_input("Enter Website URL")
    yt_link = st.text_input("YouTube Link")

    if st.button("🚀 Process Documents"):
        if uploaded_files or url_input or yt_link:
            with st.spinner("Processing documents..."):
                try:
                    processed_text = process_inputs(
                        pdf_files=uploaded_files,
                        url=url_input,
                        yt_link=yt_link
                    )
                    st.session_state.vector_store = create_vector_db(processed_text)
                    st.success("✅ Documents processed successfully!")
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
        else:
            st.warning("⚠️ Please upload files or enter URLs first!")

# ==========================
# 📊 Middle Panel: Output
# ==========================
with col2:
    st.header("📊 Output")
    
    if st.session_state.feature_output and st.session_state.feature_type:
        try:
            if st.session_state.feature_type == "Quiz":
                render_quiz(st.session_state.feature_output)
            elif st.session_state.feature_type == "Flashcards":
                render_flashcards(st.session_state.feature_output)
            elif st.session_state.feature_type == "Flowchart":
                render_flowchart(st.session_state.feature_output)
            elif st.session_state.feature_type == "Mindmap":
                render_mindmap(st.session_state.feature_output)
            elif st.session_state.feature_type == "Summary":
                render_summary(st.session_state.feature_output)
        except Exception as e:
            st.error(f"❌ Error displaying output: {str(e)}")

# ==========================
# ✨ Right Panel: Features
# ==========================
with col3:
    st.header("✨ Features")
    feature = st.radio("Choose Feature", ["Quiz", "Flashcards", "Flowchart", "Mindmap", "Summary"])
    
    if st.button("🚀 Run Feature"):
        if not st.session_state.vector_store:
            st.warning("⚠️ Please process documents first!")
        else:
            try:
                if feature == "Quiz":
                    st.session_state.feature_output = generate_quiz(
                        st.session_state.vector_store
                    )
                elif feature == "Flashcards":
                    st.session_state.feature_output = generate_flashcards(
                        st.session_state.vector_store
                    )
                elif feature == "Flowchart":
                    st.session_state.feature_output = generate_flowchart(
                        st.session_state.vector_store
                    )
                elif feature == "Mindmap":
                    st.session_state.feature_output = generate_mindmap(
                        st.session_state.vector_store
                    )
                elif feature == "Summary":
                    st.session_state.feature_output = generate_summary(
                        st.session_state.vector_store
                    )
                
                st.session_state.feature_type = feature
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ {feature} generation failed: {str(e)}")

# ==========================
# 💬 Chatbot Button
# ==========================
st.markdown("""
<style>
.chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 15px 30px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 10px;
    z-index: 999;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    transition: 0.3s;
}
.chat-button:hover {
    background-color: #45a049;
    transform: scale(1.05);
}
</style>
<a href="/chatbot_page" target="_self">
    <button class="chat-button">💬 Chatbot</button>
</a>
""", unsafe_allow_html=True)