from deep_translator import GoogleTranslator


def translate_text(text, dest_lang='en', src_lang='auto'):
    try:
        return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
    except Exception as e:
        return f"翻譯錯誤: {e}"


def translate_long_text(text, dest_lang='en', src_lang='auto', chunk_size=4500):
    paragraphs = text.split('\n')
    translated_paragraphs, buffer = [], ""
    for p in paragraphs:
        if len(buffer) + len(p) < chunk_size:
            buffer += p + "\n"
        else:
            translated_paragraphs.append(translate_text(buffer, dest_lang, src_lang))
            buffer = p + "\n"
    if buffer:
        translated_paragraphs.append(translate_text(buffer, dest_lang, src_lang))
    return "\n".join(translated_paragraphs)


def translate_bilingual(text, dest_lang='en', src_lang='auto'):
    paragraphs = [p for p in text.split('\n') if p.strip()]
    return [(p, translate_text(p, dest_lang, src_lang)) for p in paragraphs]
