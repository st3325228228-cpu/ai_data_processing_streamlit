import fitz  # PyMuPDF
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import pandas as pd


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def get_pdf_page_count(file_path):
    with fitz.open(file_path) as doc:
        return doc.page_count


def get_pdf_metadata(file_path):
    with fitz.open(file_path) as doc:
        return doc.metadata


def extract_tables_from_pdf(file_path):
    import pdfplumber
    import pandas as pd

    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue
                header, rows = table[0], table[1:]
                header = _make_columns_unique(header)
                try:
                    df = pd.DataFrame(rows, columns=header)
                    tables.append(df)
                except Exception:
                    # 該表格結構異常，跳過但不中斷整個文件處理
                    continue
    return tables


def _make_columns_unique(columns):
    """將 None / 空字串 / 重複欄名，轉為唯一且可讀的欄位名稱"""
    seen = {}
    result = []
    for i, col in enumerate(columns):
        name = str(col).strip() if col not in (None, "") else f"欄位_{i+1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.append(name)
    return result



def extract_text_ocr(file_path):
    """OCR 提取：適用於掃描版 PDF"""
    text = ""
    images = convert_from_path(file_path)
    for img in images:
        text += pytesseract.image_to_string(img, lang="chi_tra+eng")
    return text
