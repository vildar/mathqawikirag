import os
import json
import re
from typing import List, Tuple


def is_formula(sentence: str) -> bool:
    # Heuristic: contains '=', '^', '_', or looks like a formula
    return bool(re.search(r'(\=|\^|_|\d+\s*[a-zA-Z]+\s*\=)', sentence)) and len(sentence.strip()) < 120


def split_sentences(paragraph: str) -> List[str]:
    # Split by sentence-ending punctuation, keep formulas as part of sentences
    # This version keeps formulas with their context, not as separate lines
    sentences = []
    buffer = ""
    for line in paragraph.split('\n'):
        line = line.strip()
        if not line:
            continue
        if is_formula(line):
            if buffer:
                sentences.append(buffer.strip())
                buffer = ""
            sentences.append(line)
        else:
            buffer += (" " if buffer else "") + line
            # Split at sentence-ending punctuation
            while True:
                match = re.search(r'([.!?])\s+', buffer)
                if not match:
                    break
                end = match.end()
                sentences.append(buffer[:end].strip())
                buffer = buffer[end:]
    if buffer:
        sentences.append(buffer.strip())
    return sentences


def chunk_paragraph(sentences: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = []
        length = 0
        # Always include formulas and their context (previous and next sentence)
        while i < len(sentences) and length < chunk_size:
            chunk.append(sentences[i])
            length += len(sentences[i])
            # If current is formula, add previous and next sentence if available
            if is_formula(sentences[i]):
                if i > 0 and sentences[i-1] not in chunk:
                    chunk.insert(0, sentences[i-1])
                    length += len(sentences[i-1])
                if i+1 < len(sentences) and sentences[i+1] not in chunk:
                    chunk.append(sentences[i+1])
                    length += len(sentences[i+1])
            i += 1
        chunks.append(' '.join(chunk).strip())
        # Overlap by sentences, not characters
        i = max(i - chunk_overlap, i)
    return chunks


def load_documents_as_chunks(
    articles_dir: str,
    chunk_size: int = 800,
    chunk_overlap: int = 2,
    save_path: str = "chunks.json"
) -> Tuple[List[str], List[str]]:
    """
    Load cleaned wiki articles, chunk them with formula and sentence awareness,
    and save to JSON with metadata.
    """
    all_chunks = []
    all_ids = []
    all_metadata = []

    for filename in os.listdir(articles_dir):
        if not filename.endswith(".txt"):
            continue

        article_title = os.path.splitext(filename)[0]

        with open(os.path.join(articles_dir, filename), "r", encoding="utf-8") as f:
            raw_text = f.read()

        paragraphs = [p for p in raw_text.split('\n\n') if p.strip()]
        chunk_idx = 0
        for para in paragraphs:
            sentences = split_sentences(para)
            para_chunks = chunk_paragraph(sentences, chunk_size, chunk_overlap)
            for chunk in para_chunks:
                chunk_id = f"{article_title}_{chunk_idx}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    "article": article_title,
                    "chunk_id": chunk_id,
                })
                chunk_idx += 1

    # Save chunks to JSON
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"id": cid, "text": txt, "metadata": meta}
             for cid, txt, meta in zip(all_ids, all_chunks, all_metadata)],
            f,
            indent=2,
            ensure_ascii=False
        )

    return all_chunks, all_ids


# Example usage
load_documents_as_chunks(
    articles_dir="data/plaintext_articles", save_path="data/chunks.json")
