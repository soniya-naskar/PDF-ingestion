import sqlite3
from pathlib import Path
import json
DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'contracts.db'

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT,
        metadata TEXT,
        text TEXT
    )''')
    conn.commit()
    conn.close()

def save_document(doc_id, metadata, text):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO documents(id, filename, metadata, text) VALUES (?,?,?,?)',
                (doc_id, metadata.get('filename'), json.dumps(metadata), text))
    conn.commit()
    conn.close()

def get_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, filename, metadata, text FROM documents WHERE id=?', (doc_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {'id': row[0], 'filename': row[1], 'metadata': json.loads(row[2]), 'text': row[3]}

def list_documents():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, filename FROM documents')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'filename': r[1]} for r in rows]

def all_text_chunks(chunk_size=1000, overlap=200):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, text FROM documents')
    rows = cur.fetchall()
    conn.close()
    chunks = []
    for doc_id, text in rows:
        if not text:
            continue
        n = len(text)
        i = 0
        while i < n:
            start = i
            end = min(n, i + chunk_size)
            chunks.append((doc_id, start, end, text[start:end]))
            i = end - overlap
    return chunks
