from googletrans import Translator

def translate_text(text, dest_lang='en', src_lang='auto'):
    """
    使用 Google Translate 翻譯文字。
    :param text: 要翻譯的文字。
    :param dest_lang: 目標語言代碼 (例如: 'en', 'zh-tw')。
    :param src_lang: 來源語言代碼 (例如: 'auto', 'zh-tw')。
    :return: 翻譯後的文字。
    """
    try:
        translator = Translator()
        translated = translator.translate(text, dest=dest_lang, src=src_lang)
        return translated.text
    except Exception as e:
        return f"翻譯錯誤: {e}"


if __name__ == '__main__':
    # 測試翻譯功能
    chinese_text = '你好，世界！這是一個測試翻譯的句子。'
    english_translation = translate_text(chinese_text, dest_lang='en')
    print(f"原始中文: {chinese_text}")
    print(f"翻譯成英文: {english_translation}")

    english_text = 'Hello, world! This is a test sentence for translation.'
    chinese_translation = translate_text(english_text, dest_lang='zh-tw')
    print(f"\n原始英文: {english_text}")
    print(f"翻譯成中文: {chinese_translation}")

    # 測試自動檢測語言
    auto_detect_translation = translate_text('Bonjour le monde!', dest_lang='zh-tw')
    print(f"\n原始法文: Bonjour le monde!")
    print(f"自動檢測並翻譯成中文: {auto_detect_translation}")
