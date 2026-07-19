import re
from collections import Counter


def keyword_search(text, keyword):
    if not keyword:
        return []
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    matches = []
    for m in pattern.finditer(text):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        matches.append(f"...{text[start:end]}...")
    return matches


def simple_summary(text, top_n=3):
    """規則式抽取式摘要，不需外部 API"""
    sentences = re.split(r'(?<=[。！？.!?])\s*', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return "內容過短，無法生成摘要"

    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)

    scored = []
    for s in sentences:
        score = sum(word_freq[w] for w in re.findall(r'\w+', s.lower()))
        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    return " ".join([s for _, s in scored[:top_n]])
