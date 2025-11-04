# 🧠 Contract Intelligence API (Python 3.12 Compatible)

A self-contained **Contract Intelligence prototype** built with **FastAPI**, compatible with **Python 3.12**.

Supports:
- **POST `/ingest`** — Upload 1..n PDFs, extract text, store metadata, return `document_ids`
- **POST `/extract`** — Given `document_id`, return structured fields (e.g. `parties`, `effective_date`, `governing_law`, `term`, `auto_renewal`, etc.)
- **POST `/ask`** — Question answering grounded in uploaded docs (TF-IDF snippets), returns answer + citations
- **GET `/ask/stream`** — SSE streaming tokens for the same question
- **POST `/audit`** — Detect risky clauses (auto-renewal, unlimited liability, broad indemnity)
- **GET `/healthz`**, **GET `/metrics`** — Health and monitoring endpoints

---

## ⚙️ Quick Start (Local)

### 1️⃣ Create a virtual environment using Python 3.12
```bash
python -m venv venv
.\venv\Scripts\activate     # On Windows PowerShell
source venv/bin/activate    # On macOS / Linux
2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the FastAPI server
uvicorn app.main:app --reload

4️⃣ Open the API docs

http://127.0.0.1:8000/docs

🧩 Endpoints Overview
Method	Endpoint	Description
POST	/ingest	Upload and process PDF(s) into text and store metadata
POST	/extract	Extract structured contract fields from ingested text
POST	/ask	Ask a natural language question and retrieve contextual answers
GET	/ask/stream	Stream Q&A results in real-time (SSE)
POST	/audit	Detect risky or non-compliant contract clauses
GET	/healthz	Health check endpoint
GET	/metrics	System metrics and operational stat

🧠 How It Works

Text Extraction: Uses PyMuPDF
 (fitz) for reliable and fast text extraction from PDFs.

Chunking: Splits extracted text into overlapping segments (default: 1000 chars, 200 overlap).

Retrieval: Uses scikit-learn TF-IDF for semantic snippet search (local, fast, no external API).

Question Answering: Ranks the most relevant text chunks and returns best-matching answers with citations.

Clause Auditing: Flags risky clauses such as:

Automatic Renewal

Unlimited Liability

Broad Indemnification

Storage: Uses simple JSON files inside /data/ to store documents and embeddings.

➤ Ingest PDF(s)
curl -X POST "http://127.0.0.1:8000/ingest" -F "files=@contract1.pdf" -F "files=@contract2.pdf"


Response:

{"document_ids": ["doc_1", "doc_2"]}

➤ Extract Fields
curl -X POST "http://127.0.0.1:8000/extract" \
     -H "Content-Type: application/json" \
     -d '{"document_id": "doc_1"}'


Response:

{
  "parties": ["Company A", "Vendor B"],
  "effective_date": "2024-02-01",
  "governing_law": "California",
  "term": "12 months",
  "auto_renewal": true
}

➤ Ask Questions
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Who are the parties involved?", "top_k": 3}'


Response:

{
  "answer": "The agreement is between Company A and Vendor B.",
  "citations": ["chunk_0", "chunk_1"]
}

➤ Audit Risky Clauses
curl -X POST "http://127.0.0.1:8000/audit" \
     -H "Content-Type: application/json" \
     -d '{"document_id": "doc_1"}'


Response:

{
  "auto_renewal": true,
  "unlimited_liability": false,
  "broad_indemnity": true,
  "summary": "Detected potential auto-renewal and indemnity risks."
}

🧱 Design Highlights

Chunk-based retrieval: Keeps semantic continuity across paragraphs.

Local-first: All processing (extraction, retrieval, audit) runs locally.

LLM-ready: Can be extended with OpenAI or local LLMs for advanced Q&A.

Extendable: Add more structured fields in extractor.py for specific clauses.

🧰 Dependencies

Key dependencies (see requirements.txt for full list):

fastapi
uvicorn
pymupdf
scikit-learn
numpy
pandas
jinja2
pytest


🐳 Optional: Run with Docker
 Copy `.env.example` to `.env` and set `API_KEY` and optionally `OPENAI_API_KEY`.
 Build & run:
```bash
docker compose up --build
```

docker build -t contract-intel-api .
docker run -p 8000:8000 contract-intel-api


Server available at → http://localhost:8000/docs


# Endpoints & example curls
- Ingest:
```bash
curl -X POST -H "x-api-key: $API_KEY" -F "files=@./samples/sample1.pdf" http://localhost:8000/ingest
```
- Extract:
```bash
curl -X POST -H "Content-Type: application/json" -H "x-api-key: $API_KEY" -d '{"document_id":"<id>"}' http://localhost:8000/extract
```
- Ask (synthesized answer using LLM if enabled):
```bash
curl -X POST -H "Content-Type: application/json" -H "x-api-key: $API_KEY" -d '{"question":"Does the contract auto-renew?","synthesize":true}' http://localhost:8000/ask
```
- Audit:
```bash
curl -X POST -H "Content-Type: application/json" -H "x-api-key: $API_KEY" -d '{"document_id":"<id>"}' http://localhost:8000/audit
```

## Design & trade-offs
See `DESIGN.md` for architecture, chunking rationale, fallback behaviors, and security notes.



---

