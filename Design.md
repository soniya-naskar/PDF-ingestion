# Design

## Architecture
- **FastAPI** microservice exposing three primary endpoints:  
  - `/ingest`: Upload one or more PDF contracts, extract text using **PyMuPDF**, store metadata and text.  
  - `/extract`: Retrieve stored document metadata and content in JSON form.  
  - `/ask`: Perform question answering via text retrieval and similarity matching.  
- **Storage layer:**  
  - Metadata and extracted text stored as JSON files in `/data` (local disk) for simplicity.  
  - Optional **SQLite** integration for metadata indexing and persistence.  
- **Retrieval engine:**  
  - Uses **sentence-transformers** embeddings with **FAISS** index (if available) for semantic search.  
  - Falls back to **TF-IDF + cosine similarity** when embeddings or FAISS are not initialized.  
- **Chunking strategy:** Text is divided into overlapping windows (≈ 1 000 chars, 200 overlap) to ensure context continuity during retrieval.  
- **Optional LLM integration:** OpenAI or local LLM synthesizes concise answers from top-ranked chunks.  
  - If no LLM key is configured, fallback summarization concatenates top chunks with rule-based trimming.  
- **Deployment:** Containerized via Docker with a lightweight image (Python 3.12 + FastAPI + Uvicorn).  
  - Can be orchestrated using `docker-compose` for local testing and isolation.

---

## Data Model
**documents** table / object structure:
| Field | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique document identifier |
| `filename` | TEXT | Original uploaded filename |
| `metadata` | JSON | Upload timestamp, size, source info |
| `text` | TEXT | Full extracted contract text |
| `chunks` | LIST | List of chunk strings for embedding/indexing |
| `embedding_index` | Optional | Path or reference to FAISS index |

Example (stored in `/data/<uuid>.json`):
```json
{
  "id": "5a2f1e10-33b1-4e0f-9a82-dc11b57f8f33",
  "filename": "NDA_Acme.pdf",
  "metadata": {"uploaded_at": "2025-11-04T13:22:00Z"},
  "text": "...full extracted text...",
  "chunks": ["Clause 1 ...", "Clause 2 ..."]
}
