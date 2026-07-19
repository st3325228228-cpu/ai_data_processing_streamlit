import fitz  # PyMuPDF
import pdfplumber
import docx
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from collections import Counter


def extract_text(file_path):
    """依副檔名提取純文字內容"""
    if file_path.endswith('.pdf'):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return "不支援的檔案格式"


def extract_tables(file_path):
    """從 PDF 提取表格，回傳 DataFrame 清單"""
    import pandas as pd
    tables = []
    if not file_path.endswith('.pdf'):
        return tables
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for t in page_tables:
                if len(t) > 1:
                    df = pd.DataFrame(t[1:], columns=t[0])
                    tables.append(df)
    return tables


def extract_text_ocr(file_path):
    """
    OCR 提取：適用於掃描版 PDF（一般文字提取會抓到空白時使用）
    需要系統安裝 tesseract-ocr 和 poppler-utils
    """
    text = ""
    images = convert_from_path(file_path)
    for img in images:
        text += pytesseract.image_to_string(img, lang='chi_tra+eng')
    return text


def smart_extract(file_path):
    """自動判斷：純文字提取失敗或內容過短時，自動切換 OCR"""
    text = extract_text(file_path)
    if len(text.strip()) < 20 and file_path.endswith('.pdf'):
        text = extract_text_ocr(file_path)
        return text, True  # True 表示用了 OCR
    return text, False


def keyword_search(text, keyword):
    """關鍵字搜尋，回傳命中位置的上下文片段"""
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
    """
    簡易抽取式摘要（不依賴外部 LLM API）：
    依句子中的高頻詞密度排序，取前 N 句作為摘要
    """
    sentences = re.split(r'(?<=[。！？.!?])\s*', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return "內容過短，無法生成摘要"

    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)

    scored = []
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = sum(word_freq[w] for w in s_words)
        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored[:top_n]]
    return " ".join(top_sentences)
