import os
import json
import re
from typing import List, Tuple


def is_section_header(line: str) -> bool:
    """Detect if a line is a section header (title-like)."""
    return bool(re.match(r'^[A-Z][A-Za-z\s]+$', line.strip())) and len(line.split()) < 6


def is_math_placeholder(text: str) -> bool:
    """Detect if text is a math placeholder like __MATH_1__."""
    return bool(re.fullmatch(r'__MATH_\d+__', text.strip()))


def split_sentences(paragraph: str) -> List[str]:
    sentences = []
    buffer = ""
    lines = paragraph.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Section headers stay alone
        if is_section_header(line):
            if buffer:
                sentences.append(buffer.strip())
                buffer = ""
            sentences.append(line)
            i += 1
            continue

        if is_math_placeholder(line):
            # Case 1: previous buffer exists → merge into it
            if buffer:
                buffer += " " + line
            # Case 2: previous sentence ends with colon → merge into it
            elif sentences and sentences[-1].endswith(":"):
                sentences[-1] += " " + line
            # Case 3: otherwise attach to next line
            else:
                if i + 1 < len(lines):
                    lines[i + 1] = line + " " + lines[i + 1]
                else:
                    buffer = line
            i += 1
            continue

        # Merge bullet points or continuation lines
        if line.startswith(("-", "*")) or (i > 0 and lines[i - 1].rstrip().endswith(":")):
            buffer += (" " if buffer else "") + line
            i += 1
            continue

        # Normal sentence accumulation
        buffer += (" " if buffer else "") + line
        while True:
            match = re.search(r'([.!?])\s+', buffer)
            if not match:
                break
            end = match.end()
            sentences.append(buffer[:end].strip())
            buffer = buffer[end:]
        i += 1

    if buffer:
        sentences.append(buffer.strip())

    return sentences


def chunk_paragraph(sentences: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
    """Split sentences into overlapping chunks."""
    chunks = []
    i = 0
    while i < len(sentences):
        window = sentences[i:i + chunk_size]
        if window:
            chunks.append(' '.join(window).strip())
        i += max(1, chunk_size - chunk_overlap)
    return chunks


def clean_chunks(chunks: List[str]) -> List[str]:
    """
    Post-process chunks:
    - Merge math-only placeholders into context.
    - Merge bullet points / continuation lines into previous.
    """
    merged = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue

        # Merge math-only placeholders
        if is_math_placeholder(chunk):
            if merged:  # attach to previous
                merged[-1] += " " + chunk
            elif i + 1 < len(chunks):  # attach to next
                chunks[i + 1] = chunk + " " + chunks[i + 1]
            else:
                merged.append(chunk)  # fallback
            continue

        # Merge bullet points / numbered lists
        if chunk.startswith(("-", "*")) or re.match(r'^\d+[.)]\s', chunk):
            if merged:
                merged[-1] += " " + chunk
            else:
                merged.append(chunk)
            continue

        merged.append(chunk)
    return merged


def merge_continuation_paragraphs(paragraphs: List[str]) -> List[str]:
    merged = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if merged:
            prev = merged[-1].rstrip()
            prev_ends_sentence = bool(re.search(r'[.!?]"?$', prev))

            starts_lowercase = para and para[0].islower()
            is_formula_like = (
                is_math_placeholder(para)
                or para.startswith(("$$", "\\["))
                or para.endswith(("$$", "\\]"))
            )
            is_bullet = para.startswith(
                ("-", "*")) or re.match(r'^\d+[.)]\s', para)

            if (not prev_ends_sentence) or starts_lowercase or is_formula_like or is_bullet:
                merged[-1] = prev + " " + para
                continue

        merged.append(para)

    return merged


def load_documents_as_chunks(
    articles_dir: str,
    chunk_size: int = 8,
    chunk_overlap: int = 2,
    save_path: str = "chunks.json"
) -> Tuple[List[str], List[str]]:
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
        paragraphs = merge_continuation_paragraphs(paragraphs)
        chunk_idx = 0
        for para in paragraphs:
            sentences = split_sentences(para)
            para_chunks = chunk_paragraph(sentences, chunk_size, chunk_overlap)
            para_chunks = clean_chunks(para_chunks)

            for chunk in para_chunks:
                chunk_id = f"{article_title}_{chunk_idx}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    "article": article_title,
                    "chunk_id": chunk_id
                })
                chunk_idx += 1

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"id": cid, "text": txt, "metadata": meta}
             for cid, txt, meta in zip(all_ids, all_chunks, all_metadata)],
            f,
            indent=2,
            ensure_ascii=False
        )

    return all_chunks, all_ids


if __name__ == "__main__":
    load_documents_as_chunks(
        articles_dir="data/parsed_placeholder_articles", save_path="data/chunks.json"
    )
