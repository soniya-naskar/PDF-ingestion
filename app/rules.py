import re
def run_audit_rules(doc_id, text):
    findings = []
    lower = text.lower()
    m = re.search(r'auto[- ]renew.*?(\d{1,3})\s*day', lower)
    if m:
        days = int(m.group(1))
        sev = 'high' if days < 30 else 'medium'
        findings.append({'rule': 'auto_renewal_notice', 'severity': sev, 'evidence': _near_sentence(text, m.start()), 'doc_id': doc_id})
    elif 'auto-renew' in lower or 'auto renew' in lower:
        findings.append({'rule': 'auto_renewal', 'severity': 'medium', 'evidence': _near_sentence(text, lower.find('auto')), 'doc_id': doc_id})
    if 'unlimited liability' in lower or 'no cap' in lower or 'without limitation' in lower:
        findings.append({'rule': 'liability_unlimited', 'severity': 'high', 'evidence': _find_sentence_with(text, 'liability'), 'doc_id': doc_id})
    if 'indemnify' in lower and ('all' in lower or 'every' in lower):
        findings.append({'rule': 'broad_indemnity', 'severity': 'high', 'evidence': _find_sentence_with(text, 'indemn'), 'doc_id': doc_id})
    if 'confidential' not in lower:
        findings.append({'rule': 'missing_confidentiality', 'severity': 'medium', 'evidence': 'no confidentiality clause found', 'doc_id': doc_id})
    return findings

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
