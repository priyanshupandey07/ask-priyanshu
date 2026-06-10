"""
app.py — the web page for "Ask Priyanshu's AI".

A simple Streamlit chat UI on top of rag.py. Recruiters type a question and get
a grounded answer plus the facts it used.

Run:
    streamlit run app.py
"""

import streamlit as st
from rag import load_chunks, build_retriever, answer_question

st.set_page_config(page_title="Ask Priyanshu's AI", page_icon="🤖")

# Load + index once, then cache so it's fast on every question.
@st.cache_resource
def setup():
    chunks = load_chunks()
    retrieve, mode = build_retriever(chunks)
    return chunks, retrieve, mode

chunks, retrieve, mode = setup()

st.title("🤖 Ask Priyanshu's AI")
st.caption("A RAG chatbot that answers questions about Priyanshu Pandey — "
           "final-year AI/ML engineer. Ask about his skills, projects, or experience.")

with st.sidebar:
    st.subheader("How this works")
    st.write("This is a **Retrieval-Augmented Generation (RAG)** app: it finds the "
             "most relevant facts about Priyanshu, then answers using only those.")
    st.write(f"Retrieval mode: `{mode}`")
    st.write(f"Knowledge chunks: `{len(chunks)}`")
    st.markdown("**Try asking:**")
    for q in ["What are Priyanshu's strongest skills?",
              "Tell me about his LLM experience.",
              "What did he build at NDMC?",
              "Is he available for full-time roles?"]:
        st.markdown(f"- {q}")

if "history" not in st.session_state:
    st.session_state.history = []

# show past turns
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

question = st.chat_input("Ask about Priyanshu...")
if question:
    st.session_state.history.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Retrieving facts and answering..."):
            reply, used = answer_question(question, retrieve)
        st.markdown(reply)
        with st.expander("📚 Facts used to answer"):
            for i, c in enumerate(used, 1):
                st.markdown(f"**{i}.** {c}")
    st.session_state.history.append(("assistant", reply))
