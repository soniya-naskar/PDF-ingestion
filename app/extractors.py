import re
def extract_structured_fields(text: str):
    lower = text.lower()
    def find_after(labels):
        for lab in labels:
            idx = lower.find(lab)
            if idx!=-1:
                return text[idx: idx+400].strip()
        return None
    parties = []
    m = re.search(r'between\s+([A-Z][A-Za-z0-9 ,.&-]{2,200}?)\s+and\s+([A-Z][A-Za-z0-9 ,.&-]{2,200})', text, re.IGNORECASE)
    if m:
        parties = [m.group(1).strip(), m.group(2).strip()]
    eff = None
    m = re.search(r'effective\s+date[\s:]*([A-Za-z0-9 ,\-]+)', text, re.IGNORECASE)
    if m:
        eff = m.group(1).strip()
    gov = None
    m = re.search(r'governing law[\s:.]*([A-Za-z ,]+)', text, re.IGNORECASE)
    if m:
        gov = m.group(1).strip()
    term = find_after(['term of this agreement','term:','term -','term of agreement','the term shall be'])
    pay = find_after(['payment','fees','compensation','price:'])
    termi = find_after(['termination','terminate this agreement','termination for cause','termination for convenience'])
    auto = None
    m = re.search(r'auto[- ]renew', text, re.IGNORECASE)
    if m:
        s = _near_sentence(text, m.start())
        auto = s
    conf = 'confidential' in lower or 'confidentiality' in lower
    indemn = None
    if 'indemn' in lower:
        indemn = _find_sentence_with(text, 'indemn')
    liab = None
    m = re.search(r'liability.*cap[\s:]*\$?([0-9,]+)', text, re.IGNORECASE)
    if m:
        val = m.group(1).replace(',', '')
        try:
            liab = {'amount': int(val)}
        except:
            liab = {'amount': None}
    else:
        if 'unlimited liability' in lower or 'no cap' in lower:
            liab = {'amount': None, 'note': 'unlimited'}
    signs = []
    for m in re.finditer(r'signed by[:\s\n]*([A-Za-z ,.-]{2,80})', text, re.IGNORECASE):
        signs.append({'name': m.group(1).strip(), 'title': None})
    return {
        'parties': parties,
        'effective_date': eff,
        'term': term,
        'governing_law': gov,
        'payment_terms': pay,
        'termination': termi,
        'auto_renewal': auto,
        'confidentiality': conf,
        'indemnity': indemn,
        'liability_cap': liab,
        'signatories': signs
    }

def _near_sentence(text, pos):
    start = text.rfind('.', 0, pos)
    end = text.find('.', pos)
    if start==-1: start= max(0, pos-200)
    if end==-1: end = min(len(text), pos+200)
    return text[start+1:end+1].strip()

def _find_sentence_with(text, token):
    i = text.lower().find(token)
    if i==-1: return None
    return _near_sentence(text, i)
