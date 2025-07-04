import streamlit as st
from utils import embed_documents, embed_queries, compute_similarity, evaluate_retrieval, load_documents_as_chunks, index_in_chromadb, display_chromadb_contents, Constants, load_chunks, save_chunks, clean_latex, generate_prompt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os

st.set_page_config(layout="wide")
st.title("MathQA RAG")

st.header("Indexing into ChromaDB")
model_index = Constants.MPNET

with st.spinner("Chunking and embedding wikipedia articles..."):
    chunk_texts, chunk_doc_ids, vectors_cache = load_chunks(
        Constants.VECTOR_CHUNKS)
    if chunk_texts is None or chunk_doc_ids is None or vectors_cache is None:
        chunk_texts, chunk_doc_ids = load_documents_as_chunks(
            Constants.ARTICLES_DIR)
        vectors_cache = embed_documents(
            Constants.EMBEDDERS[Constants.MPNET], chunk_texts)
        save_chunks(chunk_texts, chunk_doc_ids,
                    vectors_cache, Constants.VECTOR_CHUNKS)
    st.success(f"{len(chunk_texts)} chunks loaded from 25 Wikipedia articles.")

with st.spinner(f"Indexing {model_index}..."):
    collection = index_in_chromadb(
        model_index, chunk_texts, vectors_cache, persist_directory="chromadb_data")
    st.success("Indexing complete.")

st.subheader("Sample chunks from ChromaDB")
results = collection.get(limit=3)
for doc_id, doc_text in zip(results['ids'], results['documents']):
    st.markdown(f"**{doc_id}**")
    st.text(doc_text[:300] + "...")


tab1, tab2, tab3 = st.tabs(
    ["MathQA", "Embedder Evaluation", "LLM Evaluation"])

with tab1:
    st.header("Ask a Question")
    user_query = st.text_input("Enter your question:")
    if user_query:
        mpnet_model = Constants.EMBEDDERS[Constants.MPNET]
        query_vec = embed_queries(mpnet_model, [user_query])
        all_docs = collection.get()
        mpnet_model = Constants.EMBEDDERS[Constants.MPNET]
        query_vec = embed_queries(mpnet_model, [user_query])
        sims = cosine_similarity(query_vec, vectors_cache)[0]
        best_idx = int(np.argmax(sims))
        best_chunk = chunk_texts[best_idx]
        payload = {
            "model": os.environ[Constants.LLM_NAME],
            "prompt": generate_prompt(user_query, best_chunk),
            "stream": False
        }
        response = requests.post(
            os.environ[Constants.OLLAMA_URL], json=payload)
        answer = response.json().get(
            'response', "Sorry, I couldn't generate a response.")
        st.caption("LLM Answer")
        st.latex(clean_latex(answer))
        st.text_area("Context", best_chunk, height=150, disabled=True)

with tab2:
    if st.button("Run Evaluation"):
        results = {}
        vectors_cache = {}

        query_list = list(Constants.QUERIES.keys())

        for name, model in Constants.EMBEDDERS.items():
            st.write(f"Evaluating: {name}")

            chunk_vectors = embed_documents(model, chunk_texts)
            query_vectors = embed_queries(model, query_list)

            sim_matrix = compute_similarity(query_vectors, chunk_vectors)
            metrics = evaluate_retrieval(
                sim_matrix, query_list, chunk_doc_ids, Constants.QUERIES)
            results[name] = metrics

        st.subheader("Evaluation Results")
        metrics_table = {
            "Embedder": [],
            "nDCG": [],
            "MRR": []
        }
        for name, metrics in results.items():
            metrics_table["Embedder"].append(name)
            metrics_table["nDCG"].append(round(metrics["nDCG"], 4))
            metrics_table["MRR"].append(round(metrics["MRR"], 4))

        st.table(metrics_table)
