import docx
import pandas as pd


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def get_docx_metadata(file_path):
    doc = docx.Document(file_path)
    props = doc.core_properties
    return {
        "作者": props.author,
        "標題": props.title,
        "建立時間": str(props.created),
        "最後修改時間": str(props.modified),
        "段落數": len(doc.paragraphs),
    }


def extract_tables_from_docx(file_path):
    doc = docx.Document(file_path)
    tables = []
    for table in doc.tables:
        data = [[cell.text for cell in row.cells] for row in table.rows]
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            tables.append(df)
    return tables
