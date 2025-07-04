import numpy as np
from sklearn.metrics import ndcg_score, label_ranking_average_precision_score
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(query_embeddings, doc_embeddings):
    return cosine_similarity(query_embeddings, doc_embeddings)


def evaluate_retrieval(sim_matrix, queries, chunk_doc_ids, ground_truth):
    """
    sim_matrix: (num_queries, num_chunks)
    ground_truth: dict of query -> list of relevant doc_ids (documents)
    chunk_doc_ids: list mapping each chunk to its parent doc_id
    """
    relevance = np.zeros_like(sim_matrix)
    for i, q in enumerate(queries):
        relevant_docs = ground_truth[q]
        for j, doc_id in enumerate(chunk_doc_ids):
            if doc_id in relevant_docs:
                relevance[i, j] = 1

    ndcg = ndcg_score(relevance, sim_matrix)
    mrr = label_ranking_average_precision_score(relevance, sim_matrix)
    return {"nDCG": ndcg, "MRR": mrr}
