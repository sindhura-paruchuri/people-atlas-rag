"""Pure functions shared by live agents and offline regression tests."""
import re
from urllib.parse import urlparse
STOP = set('find who with the and in a an me people engineers is has are for can work on tell about'.split())
def terms(query):
    return [t for t in re.findall(r'[a-z0-9]+', query.lower()) if t not in STOP]
def safe_url(url):
    p = urlparse(url or '')
    return url if p.scheme == 'https' and p.hostname and not p.username and not p.password else None

def rank(query, people):
    words = terms(query)
    ranked = []
    for person in people:
        hay = str(person).lower()
        hits = sum(t in hay for t in words)
        if hits:
            ranked.append((hits / max(len(words), 1), person))
    return sorted(ranked, key=lambda x: x[0], reverse=True)[:6]

def evidence_sufficient(query, sources, threshold=0.78):
    """Conservative heuristic, not calibrated confidence or factual verification."""
    words = terms(query)
    if not words or not sources:
        return False
    return any(s.get('score', 0) >= threshold and all(w in s['text'].lower() for w in words) for s in sources)

def validate_answer(answer, sources):
    allowed = {str(s['id']) for s in sources}
    cited = set(re.findall(r'\[(\d+)\]', answer))
    if cited - allowed or (sources and not cited):
        return 'I could not produce a reliably cited answer. Please review the retrieved sources.', False
    return answer, True
