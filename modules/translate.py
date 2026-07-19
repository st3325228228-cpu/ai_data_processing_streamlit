from deep_translator import GoogleTranslator, MyMemoryTranslator
import time


def _safe_translate(text, target, source, retries=2):
    """先試 GoogleTranslator，失敗自動重試，最終切換 MyMemoryTranslator 備援"""
    last_error = None

    for attempt in range(retries):
        try:
            return GoogleTranslator(source=source, target=target).translate(text)
        except Exception as e:
            last_error = e
            time.sleep(1)  # 短暫等待後重試，避免瞬時連線問題

    try:
        # 備援引擎：MyMemoryTranslator（社群已驗證可繞過此問題）
        src = "auto" if source == "auto" else source
        return MyMemoryTranslator(source=src, target=target).translate(text)
    except Exception:
        raise RuntimeError(f"主要與備援翻譯引擎皆失敗，原始錯誤：{last_error}")


def translate_text(text, target='en', source='auto'):
    try:
        return _safe_translate(text, target, source)
    except Exception as e:
        return f"翻譯錯誤: {e}"


def translate_long_text(text, target='en', source='auto', chunk_size=800):
    paragraphs = [p for p in text.split('\n') if p.strip()]
    translated_chunks = []
    buffer = ""

    for p in paragraphs:
        if len(buffer) + len(p) < chunk_size:
            buffer += p + "\n"
        else:
            translated_chunks.append(_safe_translate(buffer, target, source))
            buffer = p + "\n"
    if buffer:
        translated_chunks.append(_safe_translate(buffer, target, source))

    return "\n".join(translated_chunks)


def translate_bilingual(text, target='en', source='auto'):
    paragraphs = [p for p in text.split('\n') if p.strip()]
    pairs = []
    for p in paragraphs:
        translated = _safe_translate(p, target, source)
        pairs.append((p, translated))
    return pairs
