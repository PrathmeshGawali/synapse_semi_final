import json
import streamlit as st
from groq import Groq
from .base import get_rag_context
from pypdf import PdfReader

client = Groq(api_key='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')

# Common response format
RESPONSE_JSON = {
    "mcqs": [
        {
            "mcq": "multiple choice question",
            "options": {
                "a": "choice here",
                "b": "choice here",
                "c": "choice here",
                "d": "choice here",
            },
            "correct": "correct option letter",
        }
    ] * 10
}

def generate_quiz(vector_store) -> dict:
    """Generate quiz using RAG context with unified prompt structure"""
    try:
        context = get_rag_context(vector_store, "Generate quiz questions", k=5)
        
        PROMPT_TEMPLATE = """
        Text: {context}
        You are an expert in generating MCQ type quiz on the basis of provided content. 
        Create a quiz of 10 multiple choice questions keeping difficulty level as easy. 
        Ensure questions are diverse, challenging, and grounded in the context.
        Use this JSON structure:
        {RESPONSE_JSON}
        """
        
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            RESPONSE_JSON=json.dumps(RESPONSE_JSON)
        )
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        quiz_data = json.loads(response.choices[0].message.content)
        
        # Validate structure
        if "mcqs" not in quiz_data or len(quiz_data["mcqs"]) != 10:
            st.error("Invalid quiz format generated")
            return None
            
        return quiz_data
        
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return None

def render_quiz(quiz_data: dict):
    """Render interactive quiz interface with session state management"""
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = []
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = []

    st.header("Generated Quiz")
    
    # Initialize lists if empty
    if not st.session_state.selected_options:
        st.session_state.selected_options = [None] * len(quiz_data.get("mcqs", []))
    if not st.session_state.correct_answers:
        st.session_state.correct_answers = [
            q["options"][q["correct"]] 
            for q in quiz_data.get("mcqs", [])
        ]

    for idx, q in enumerate(quiz_data.get("mcqs", [])):
        with st.expander(f"Question {idx+1}"):
            options = list(q["options"].values())
            st.session_state.selected_options[idx] = st.radio(
                q["mcq"],
                options=options,
                index=None,
                key=f"q{idx}"
            )

    if st.button("Submit Quiz") and not st.session_state.quiz_submitted:
        st.session_state.quiz_submitted = True
        
        score = sum(
            1 for sel, corr in zip(
                st.session_state.selected_options,
                st.session_state.correct_answers
            ) if sel == corr
        )
        
        st.success(f"Score: {score}/{len(quiz_data['mcqs'])}")
        st.header("Quiz Review")
        
        for idx, q in enumerate(quiz_data["mcqs"]):
            st.subheader(f"Question {idx+1}: {q['mcq']}")
            st.write(f"Your answer: {st.session_state.selected_options[idx]}")
            st.write(f"Correct answer: {st.session_state.correct_answers[idx]}")
            st.write("---")