import tempfile

import streamlit as st

from rag import ask, build_store

st.title("Chat with your PDF")

uploaded = st.file_uploader("Upload a PDF", type="pdf")

if uploaded:
    if "store" not in st.session_state or st.session_state.file_name != uploaded.name:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(uploaded.getvalue())
        with st.spinner("Reading your PDF..."):
            st.session_state.store = build_store(f.name)
        st.session_state.file_name = uploaded.name
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if question := st.chat_input("Ask something about your PDF"):
        with st.chat_message("user"):
            st.write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        answer, pages = ask(st.session_state.store, question)
        sources = "Sources: page " + ", ".join(str(p) for p in pages) if pages else ""
        reply = answer + "\n\n" + sources
        with st.chat_message("assistant"):
            st.write(answer)
            st.caption(sources)
        st.session_state.messages.append({"role": "assistant", "content": reply})
