import chromadb
import streamlit as st


def index_in_chromadb(model_name, chunk_texts, embeddings, persist_directory="chromadb_data"):
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(
        model_name.replace(" ", "_").lower())

    if collection.count() == 0:
        collection.add(
            documents=chunk_texts,
            embeddings=embeddings,
            ids=[str(i) for i in range(len(chunk_texts))]
        )
    return collection


def display_chromadb_contents(collection):
    results = collection.get()
    docs = results['documents']
    ids = results['ids']

    st.subheader("📦 ChromaDB Contents")
    for doc_id, doc_text in zip(ids, docs):
        st.markdown(f"**{doc_id}**")
        st.text(doc_text[:200] + "...")
