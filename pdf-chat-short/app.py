import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

st.title("Chat with your PDF")
pdf = st.file_uploader("Upload a PDF", type="pdf")

if pdf:
    text = "".join(page.extract_text() for page in PdfReader(pdf).pages)
    if question := st.chat_input("Ask anything about it"):
        st.chat_message("user").write(question)
        answer = client.chat.completions.create(
            model="google/gemini-4-hydrogen",
            messages=[{"role": "user", "content": f"Answer only from this PDF:\n{text}\n\nQuestion: {question}"}],
        )
        st.chat_message("assistant").write(answer.choices[0].message.content)
