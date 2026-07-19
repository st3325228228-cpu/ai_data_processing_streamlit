from deep_translator import GoogleTranslator

def translate_text(text, dest_lang='en', src_lang='auto'):
    """
    使用 Google Translate 翻譯文字（透過 deep-translator）。
    :param text: 要翻譯的文字。
    :param dest_lang: 目標語言代碼 (例如: 'en', 'zh-TW')。
    :param src_lang: 來源語言代碼 (例如: 'auto', 'zh-TW')。
    :return: 翻譯後的文字。
    """
    try:
        translated = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        return translated
    except Exception as e:
        return f"翻譯錯誤: {e}"


if __name__ == '__main__':
    chinese_text = '你好，世界！這是一個測試翻譯的句子。'
    english_translation = translate_text(chinese_text, dest_lang='en')
    print(f"原始中文: {chinese_text}")
    print(f"翻譯成英文: {english_translation}")
