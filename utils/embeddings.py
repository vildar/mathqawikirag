def embed_documents(model, docs):
    return model.encode(docs, show_progress_bar=False)


def embed_queries(model, queries):
    return model.encode(queries, show_progress_bar=False)
