import html
import json
import traceback
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from . import storage

# Globals
_chunks: List[tuple] = []    # list of (doc_id, start, end, text)
_vectors = None              # TF-IDF matrix (sparse)
_tfidf: Optional[TfidfVectorizer] = None
_meta: List[dict] = []       # list of metadata dicts matching _chunks positions


def safe_chunk_text(text: str, doc_id: str, chunk_size: int = 1000, overlap: int = 200):
    """Split large text safely into overlapping chunks."""
    chunks = []
    n = len(text)
    if n == 0:
        return chunks
    try:
        i = 0
        while i < n:
            start = i
            end = min(n, i + chunk_size)
            chunk_text = text[start:end]
            chunks.append((doc_id, start, end, chunk_text))
            if end >= n:
                break
            i = end - overlap
    except MemoryError:
        print(f"⚠️ MemoryError while chunking doc {doc_id}. Skipping remainder.")
    except Exception:
        print(f"⚠️ Unexpected error while chunking doc {doc_id}:")
        traceback.print_exc()
    return chunks


def init_index():
    """Build TF-IDF index over all stored docs."""
    global _chunks, _vectors, _tfidf, _meta
    print("🔍 Initializing document index...")
    _chunks = []
    _meta = []
    try:
        docs = storage.list_docs()
        for doc_id in docs:
            rec = storage.load_doc(doc_id)
            if not rec or "text" not in rec:
                continue
            text = rec["text"] or ""
            # Optionally truncate extremely large docs to a reasonable limit
            if len(text) > 2_000_000:
                print(f"⚠️ Document {doc_id} is very large; truncating to 2,000,000 chars for indexing.")
                text = text[:2_000_000]
            doc_chunks = safe_chunk_text(text, doc_id)
            _chunks.extend(doc_chunks)
        texts = [c[3] for c in _chunks]
        if texts:
            print(f"✅ Building TF-IDF matrix for {len(texts)} chunks...")
            _tfidf = TfidfVectorizer(stop_words="english")
            _vectors = _tfidf.fit_transform(texts)
            _meta = [{"doc_id": c[0], "start": c[1], "end": c[2]} for c in _chunks]
            print("✅ Index initialization complete.")
        else:
            print("ℹ️ No text chunks to index.")
            _tfidf = None
            _vectors = None
            _meta = []
    except MemoryError:
        print("❌ MemoryError during index build. Try smaller documents or increase RAM.")
        _tfidf = None
        _vectors = None
        _meta = []
    except Exception:
        print("❌ Unexpected error during index build:")
        traceback.print_exc()
        _tfidf = None
        _vectors = None
        _meta = []


def invalidate_index():
    """Clear current index (force rebuild next request)."""
    global _chunks, _vectors, _tfidf, _meta
    _chunks = []
    _vectors = None
    _tfidf = None
    _meta = []


def answer_question(question: str, top_k: int = 3, document_id: Optional[str] = None):
    """
    Answer the question. If document_id provided, search only that document.
    Returns {'answer': <text>, 'citations': [ {document_id,start,end,score}, ... ] }
    """
    global _vectors, _meta, _chunks, _tfidf

    # ensure index
    if _vectors is None or _tfidf is None or len(_chunks) == 0:
        init_index()

    if _vectors is None or _tfidf is None or _vectors.shape[0] == 0:
        return {"answer": "No indexed data available.", "citations": []}

    try:
        # transform the question using the same fitted TF-IDF (important!)
        vec_q = _tfidf.transform([question])

        # If filtering by document_id, select subset rows from _vectors
        if document_id:
            indices = [i for i, m in enumerate(_meta) if m["doc_id"] == document_id]
            if not indices:
                return {"answer": f"No data found for document {document_id}", "citations": []}
            docs_matrix = _vectors[indices, :]
            sims = cosine_similarity(vec_q, docs_matrix).flatten()
            # sims corresponds to indices list; need to map back to global indices
            ordered_pairs = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:top_k]
            snippets = []
            citations = []
            for local_idx, score in ordered_pairs:
                global_idx = indices[local_idx]
                text = _chunks[global_idx][3].strip()
                meta = _meta[global_idx]
                snippets.append(text)
                citations.append({
                    "document_id": meta["doc_id"],
                    "start": meta["start"],
                    "end": meta["end"],
                    "score": float(score)
                })
        else:
            sims = cosine_similarity(vec_q, _vectors).flatten()
            idx_sorted = sims.argsort()[::-1][:top_k]
            snippets = []
            citations = []
            for i in idx_sorted:
                score = float(sims[i])
                meta = _meta[i]
                text = _chunks[i][3].strip()
                snippets.append(text)
                citations.append({
                    "document_id": meta["doc_id"],
                    "start": meta["start"],
                    "end": meta["end"],
                    "score": score
                })

        answer = "\n\n".join(snippets)
        return {"answer": answer, "citations": citations}
    except Exception:
        print("❌ Error in answer_question:")
        traceback.print_exc()
        return {"answer": "", "citations": []}


def stream_answer(question: str, top_k: int = 3, document_id: Optional[str] = None):
    """SSE-style generator that yields tokens for the answer then the citations."""
    res = answer_question(question, top_k=top_k, document_id=document_id)
    answer = res.get("answer", "")
    for token in answer.split():
        yield f"data: {html.escape(token)}\n\n"
    yield f"data: [CITATIONS] {json.dumps(res.get('citations', []))}\n\n"
