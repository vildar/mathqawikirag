import pickle
import os
import streamlit as st

# TODO: Make this more sophisticated.


def chunk_text(text, max_words=150, overlap=30):
    """
    Split text into chunks of max_words length with specified overlap.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


@st.cache_data
def load_documents_as_chunks(folder_path):
    """
    Loads documents and splits each into chunks.
    Returns:
        chunk_texts: List[str] of all chunks
        chunk_doc_ids: List[str] doc_id for each chunk (which document chunk belongs to)
    """
    chunk_texts = []
    chunk_doc_ids = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            doc_id = file_name.replace(".txt", "")
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunk_text(text)
            chunk_texts.extend(chunks)
            chunk_doc_ids.extend([doc_id] * len(chunks))

    return chunk_texts, chunk_doc_ids


def save_chunks(chunk_texts, chunk_doc_ids, embeddings, path):
    with open(path, "wb") as f:
        pickle.dump((chunk_texts, chunk_doc_ids, embeddings), f)


def load_chunks(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None, None, None


def clean_latex(ans):
    return ans.strip().removeprefix("$$").removeprefix("$").removesuffix("$$").removesuffix("$").strip()


def generate_prompt(query, chunk):
    return f"""
        You are a mathematics and physics expert. Given the following user query and context passages, extract or derive the mathematical formula that answers the query, using only the information in the context. If the formula is described in words, convert it to a mathematical equation.

        ### User Query:
        {query}

        ### Contexts:
        {chunk}

        ### Instructions:
        - Respond ONLY with the formula (in LaTeX if possible), no explanation.
        """

# 1. Map response to context and verify that it exists in the context
# 2. Evaluate for 100 (4 * 25 articles) formula queries. Check across LLMs and also verify that they are repeatable. (temp hyperparam)
# 3. Add 'whether it exists in context' column
# 4. Evaluate the retrieval phase
# 5. Modify the chunking mechanism and evaluate
# 6. Have a context column. Paste the chunk
# 7. top_k=5 for evaluation of embedders. (experiment before evaluating for 100)
# 8. More sophisticated chunking mechanism
