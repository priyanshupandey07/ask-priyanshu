"""
rag.py — the brain of "Ask Priyanshu's AI".

This is a complete RAG (Retrieval-Augmented Generation) pipeline in one file,
written to be readable by a complete beginner. Every step is commented.

WHAT IS RAG, IN ONE SENTENCE?
  Instead of hoping an AI "knows" the answer, we (1) RETRIEVE the most relevant
  facts from our own documents, then (2) ask the AI to GENERATE an answer using
  only those facts. Retrieval + Generation = RAG.

THE 4 STEPS THIS FILE DOES:
  1. LOAD   — read profile.md and split it into small "chunks" (facts).
  2. INDEX  — turn each chunk into numbers (an "embedding") so we can compare meaning.
  3. RETRIEVE — for a question, find the chunks whose meaning is closest.
  4. GENERATE — feed those chunks to an LLM and get a grounded answer (or, with no
                API key, just show the best-matching facts — "extractive" mode).

Try it from the terminal:
    python rag.py "What are Priyanshu's strongest skills?"
"""

import os
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), "profile.md")
TOP_K = 3  # how many chunks to retrieve per question


# ---------- STEP 1: LOAD + CHUNK ----------
def load_chunks(path=DATA_FILE):
    """Read the knowledge file and split it into chunks on blank lines.
    Each paragraph becomes one searchable fact."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = []
    for block in text.split("\n\n"):
        block = block.strip()
        # skip empty blocks and the '#' comment lines at the top of the file
        if block and not block.startswith("#"):
            chunks.append(block)
    return chunks


# ---------- STEPS 2 + 3: INDEX + RETRIEVE ----------
def build_retriever(chunks):
    """Return a function retrieve(question) -> list of relevant chunks.

    Prefers SEMANTIC search (sentence-transformers) which understands meaning.
    If that library isn't installed, falls back to KEYWORD search (TF-IDF) so
    the app still runs anywhere with no heavy downloads.
    """
    # --- Option A: semantic embeddings (best quality) ---
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        chunk_vectors = model.encode(chunks, convert_to_tensor=True)

        def retrieve(question, k=TOP_K):
            q_vector = model.encode(question, convert_to_tensor=True)
            scores = util.cos_sim(q_vector, chunk_vectors)[0]
            top = scores.argsort(descending=True)[:k]
            return [chunks[i] for i in top]

        return retrieve, "semantic (sentence-transformers)"

    # --- Option B: TF-IDF keyword fallback (zero heavy deps) ---
    except Exception:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(chunks)

        def retrieve(question, k=TOP_K):
            q_vec = vectorizer.transform([question])
            sims = cosine_similarity(q_vec, matrix)[0]
            top = sims.argsort()[::-1][:k]
            return [chunks[i] for i in top]

        return retrieve, "keyword (TF-IDF fallback)"


# ---------- STEP 4: GENERATE ----------
def generate_answer(question, context_chunks):
    """Turn retrieved chunks into a final answer.

    Uses an LLM if an API key is set (Groq is free and recommended for beginners;
    OpenAI also supported). With NO key, returns the best-matching facts directly
    so you can see RAG working at zero cost.
    """
    context = "\n\n".join(f"- {c}" for c in context_chunks)
    system = (
        "You are an assistant that answers questions about Priyanshu Pandey for "
        "recruiters. Answer ONLY from the context provided. If the context does not "
        "contain the answer, say you don't have that information. Be concise, "
        "friendly, and speak about Priyanshu in the third person."
    )
    user = f"Context about Priyanshu:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    # Groq (free, OpenAI-compatible) — set GROQ_API_KEY
    if os.getenv("GROQ_API_KEY"):
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
                        base_url="https://api.groq.com/openai/v1")
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0.2)
        return resp.choices[0].message.content

    # OpenAI — set OPENAI_API_KEY
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0.2)
        return resp.choices[0].message.content

    # No key: extractive mode — just present the most relevant facts.
    return ("(No LLM key set — showing the most relevant facts. Add a free GROQ_API_KEY "
            "for a natural-language answer.)\n\nBased on Priyanshu's profile:\n\n" + context)


# ---------- Put it all together ----------
def answer_question(question, retrieve):
    chunks = retrieve(question)
    return generate_answer(question, chunks), chunks


def main():
    question = " ".join(sys.argv[1:]) or "What is Priyanshu's experience with LLMs?"
    chunks = load_chunks()
    retrieve, mode = build_retriever(chunks)
    print(f"[retrieval mode: {mode}]  [{len(chunks)} chunks loaded]\n")
    print(f"Q: {question}\n")
    reply, used = answer_question(question, retrieve)
    print("A:", reply)
    print("\n--- retrieved facts used ---")
    for i, c in enumerate(used, 1):
        print(f"{i}. {c[:120]}...")


if __name__ == "__main__":
    main()
