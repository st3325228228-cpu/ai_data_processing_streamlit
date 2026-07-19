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
    """從 PDF 提取表格，回傳 DataFrame 清單"""
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for t in page.extract_tables():
                if len(t) > 1:
                    df = pd.DataFrame(t[1:], columns=t[0])
                    tables.append(df)
    return tables


def extract_text_ocr(file_path):
    """OCR 提取：適用於掃描版 PDF"""
    text = ""
    images = convert_from_path(file_path)
    for img in images:
        text += pytesseract.image_to_string(img, lang="chi_tra+eng")
    return text
