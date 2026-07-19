import pypdf
import os

def extract_text_from_pdf(pdf_path):
    """
    從 PDF 檔案中提取所有文字內容。
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

def extract_text_from_pdf_page(pdf_path, page_number):
    """
    從 PDF 檔案的指定頁面提取文字內容。
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        if 0 <= page_number < len(reader.pages):
            return reader.pages[page_number].extract_text()
        else:
            return f"Page number {page_number} is out of range. Total pages: {len(reader.pages)}"
    except Exception as e:
        return f"Error extracting text from PDF page: {e}"

def get_pdf_page_count(pdf_path):
    """
    獲取 PDF 檔案的總頁數。
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        return f"Error getting PDF page count: {e}"

def get_pdf_metadata(pdf_path):
    """
    獲取 PDF 檔案的元數據。
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        metadata = reader.metadata
        if metadata:
            return {
                "Title": metadata.title,
                "Author": metadata.author,
                "Subject": metadata.subject,
                "Creator": metadata.creator,
                "Producer": metadata.producer,
                "CreationDate": metadata.creation_date,
                "ModificationDate": metadata.modification_date
            }
        else:
            return "No metadata found."
    except Exception as e:
        return f"Error getting PDF metadata: {e}"

if __name__ == '__main__':
    # 創建一個簡單的測試 PDF 檔案 (需要安裝 reportlab)
    # from reportlab.pdfgen import canvas
    # from reportlab.lib.pagesizes import letter
    #
    # test_pdf_path = "test_document.pdf"
    # c = canvas.Canvas(test_pdf_path, pagesize=letter)
    # c.drawString(100, 750, "Hello, this is a test PDF.")
    # c.drawString(100, 730, "This is the first page.")
    # c.showPage()
    # c.drawString(100, 750, "This is the second page.")
    # c.save()
    # print(f"Created test PDF file: {test_pdf_path}")

    # 假設有一個 test_document.pdf 存在
    # 如果沒有，請手動創建或跳過此測試部分
    test_pdf_path = "test_document.pdf" # 替換為實際存在的 PDF 檔案路徑進行測試

    if os.path.exists(test_pdf_path):
        # 測試文字提取
        extracted_text = extract_text_from_pdf(test_pdf_path)
        print("\nExtracted Text from PDF:")
        print(extracted_text[:500]) # 顯示前500字

        # 測試頁數統計
        page_count = get_pdf_page_count(test_pdf_path)
        print(f"\nPDF Page Count: {page_count}")

        # 測試元數據獲取
        metadata = get_pdf_metadata(test_pdf_path)
        print("\nPDF Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # 測試單頁文字提取 (假設有至少一頁)
        if page_count > 0:
            page_1_text = extract_text_from_pdf_page(test_pdf_path, 0)
            print("\nText from Page 1:")
            print(page_1_text[:200])
    else:
        print(f"Warning: {test_pdf_path} not found. Skipping PDF module tests.")
        print("Please create a 'test_document.pdf' or provide a valid path to run tests.")
