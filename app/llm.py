import os
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
USE_SENTENCE = True  # fallback to sentence-transformers if available
_llm_ready = False
_model = None
_encoder = None

def init_llm():
    global _llm_ready, _encoder
    if OPENAI_KEY:
        _llm_ready = True
        return
    try:
        from sentence_transformers import SentenceTransformer
        _encoder = SentenceTransformer('all-MiniLM-L6-v2')
        _llm_ready = True
    except Exception as e:
        _llm_ready = False

def available():
    return _llm_ready

def embed_texts(texts):
    """Return vector embeddings for list of texts. Uses OpenAI embeddings if key present, else sentence-transformers."""
    if OPENAI_KEY:
        import openai
        openai.api_key = OPENAI_KEY
        resp = openai.Embedding.create(model='text-embedding-3-small', input=texts)
        return [r['embedding'] for r in resp['data']]
    else:
        if _encoder is None:
            raise RuntimeError('No embedding model available')
        return _encoder.encode(texts).tolist()

def synthesize_answer(question, snippets):
    """Simple synthesis: call OpenAI to produce a concise answer given question + snippets."""
    if not OPENAI_KEY:
        # fallback: naive join
        return "\n\n".join(snippets)
    import openai, json
    openai.api_key = OPENAI_KEY
    prompt = f"You are a contract assistant. Answer the question concisely using ONLY the provided source snippets.\nQuestion: {question}\n\nSOURCES:\n" + "\n\n".join(snippets) + "\n\nProvide a short answer and bullet point the sources as (doc_id:start-end)."
    resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=[{'role':'user','content':prompt}], max_tokens=300)
    return resp['choices'][0]['message']['content']

