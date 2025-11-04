from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uuid, time
from . import storage, extractors, retriever, rules

app = FastAPI(title='Contract Intelligence (py3.12)', version='0.1')

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

METRICS = {'ingest_count': 0, 'extract_count': 0, 'ask_count': 0, 'audit_count': 0}

class IngestResponse(BaseModel):
    document_ids: List[str]

@app.on_event('startup')
def startup():
    retriever.init_index()

@app.post('/ingest', response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None, webhook_url: Optional[str] = Form(None)):
    if not files:
        raise HTTPException(status_code=400, detail='No files uploaded')
    ids = []
    for f in files:
        content = await f.read()
        doc_id = str(uuid.uuid4())
        save_path = DATA_DIR / f'{doc_id}.pdf'
        save_path.write_bytes(content)
        text = storage.extract_text_from_pdf(save_path)
        meta = {'filename': f.filename, 'size': len(content), 'ingested_at': int(time.time())}
        storage.save_doc_json(doc_id, meta, text)
        ids.append(doc_id)
        METRICS['ingest_count'] += 1
    retriever.invalidate_index()
    retriever.init_index()
    if webhook_url:
        background_tasks.add_task(storage.post_webhook, webhook_url, {'event':'ingest_complete','document_ids': ids})
    return {'document_ids': ids}

class ExtractRequest(BaseModel):
    document_id: str

@app.post('/extract')
def extract_body(payload: ExtractRequest):
    METRICS['extract_count'] += 1
    doc = storage.load_doc(payload.document_id)
    if not doc:
        raise HTTPException(404, 'document not found')
    fields = extractors.extract_structured_fields(doc['text'])
    return fields

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

@app.post('/ask')
def ask(payload: AskRequest):
    METRICS['ask_count'] += 1
    results = retriever.answer_question(payload.question, top_k=payload.top_k)
    return results

@app.get('/ask/stream')
def ask_stream(question: str, top_k: int = 3):
    METRICS['ask_count'] += 1
    gen = retriever.stream_answer(question, top_k=top_k)
    return StreamingResponse(gen, media_type='text/event-stream')

class AuditRequest(BaseModel):
    document_id: str

@app.post('/audit')
def audit(payload: AuditRequest):
    METRICS['audit_count'] += 1
    doc = storage.load_doc(payload.document_id)
    if not doc:
        raise HTTPException(404, 'document not found')
    findings = rules.run_audit_rules(payload.document_id, doc['text'])
    return {'findings': findings}

@app.get('/healthz')
def healthz():
    return {'status': 'ok'}

@app.get('/metrics')
def metrics():
    return METRICS
