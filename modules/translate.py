from deep_translator import GoogleTranslator


def translate_text(text, dest_lang='en', src_lang='auto'):
    """單段文字翻譯"""
    try:
        return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
    except Exception as e:
        return f"翻譯錯誤: {e}"


def translate_long_text(text, dest_lang='en', src_lang='auto', chunk_size=4500):
    """
    長文件翻譯：deep-translator 單次請求有字數限制，
    這裡自動依段落切塊後逐段翻譯再拼接
    """
    paragraphs = text.split('\n')
    translated_paragraphs = []
    buffer = ""

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
    """
    雙語對照：回傳 [(原文段落, 譯文段落), ...] 的清單，
    方便前端逐段並排顯示
    """
    paragraphs = [p for p in text.split('\n') if p.strip()]
    result = []
    for p in paragraphs:
        translated = translate_text(p, dest_lang, src_lang)
        result.append((p, translated))
    return result
