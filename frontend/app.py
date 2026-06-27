import streamlit as st
import sys
import os

# Add backend folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from answer_generator import generate_answer

st.set_page_config(
    page_title="NyayaAI",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ NyayaAI")
st.subheader("Indian Legal AI Assistant")

question = st.text_input(
    "Ask your legal question:",
    placeholder="Example: What is Article 21?"
)

if st.button("Ask"):

    if question.strip() == "":
        st.warning("Please enter a legal question.")
    else:
        with st.spinner("Searching legal documents..."):
            answer = generate_answer(question)

        st.success("Answer")

        st.write(answer)