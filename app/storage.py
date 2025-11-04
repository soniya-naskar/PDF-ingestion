from pathlib import Path
import json
import requests
import traceback
import os

# Directory to store extracted document data
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

def extract_text_from_pdf(path: Path) -> str:
    """
    Extracts plain text from a PDF using PyMuPDF (fitz).
    Returns empty string if PDF cannot be read.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        texts = []
        for p in doc:
            try:
                texts.append(p.get_text('text') or '')
            except Exception:
                texts.append('')
        return '\n\n'.join(texts)
    except Exception as e:
        print(f"⚠️ PDF read error: {e}")
        return ''


def save_doc_json(doc_id: str, metadata: dict, text: str):
    """
    Saves extracted document data (metadata + text) into a JSON file.
    """
    rec = {'id': doc_id, 'metadata': metadata, 'text': text}
    p = DATA_DIR / f'{doc_id}.json'
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ Saved document: {p.name}")


def load_doc(doc_id: str):
    """
    Loads a stored document JSON by its ID.
    Returns None if file not found.
    """
    p = DATA_DIR / f'{doc_id}.json'
    if not p.exists():
        print(f"⚠️ Document not found: {doc_id}")
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def list_docs():
    """
    Returns a list of all stored document IDs.
    """
    return [p.stem for p in DATA_DIR.glob('*.json')]


# def post_webhook(payload):
#     """
#     Sends the given payload to a webhook URL if valid.
#     URL is read from environment variable WEBHOOK_URL.
#     Skips sending if no valid URL is configured.
#     """
#     url = os.getenv("WEBHOOK_URL")

#     if not url:
#         print("ℹ️ No WEBHOOK_URL set — skipping webhook.")
#         return

#     if not url.startswith(("http://", "https://")):
#         print(f"⚠️ Invalid WEBHOOK_URL: {url}")
#         return

#     try:
#         response = requests.post(url, json=payload, timeout=5)
#         print(f"✅ Webhook POST to {url} — status {response.status_code}")
#     except Exception as e:
#         print(f"⚠️ Webhook POST failed: {e}")
#         traceback.print_exc()

def post_webhook(url=None, payload=None):
    """
    Sends the given payload to a webhook URL if valid.
    URL can be provided as argument or via WEBHOOK_URL environment variable.
    """
    import os

    # Prefer explicit URL, else use env variable
    if not url:
        url = os.getenv("WEBHOOK_URL")

    if not url:
        print("ℹ️ No WEBHOOK_URL set — skipping webhook.")
        return

    if not url.startswith(("http://", "https://")):
        print(f"⚠️ Invalid WEBHOOK_URL: {url}")
        return

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"✅ Webhook POST to {url} — status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Webhook POST failed: {e}")
        traceback.print_exc()
