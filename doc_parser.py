import io
from pypdf import PdfReader
import docx2txt
import openpyxl

def extract_text_from_bytes(file_bytes, filename):
    filename = filename.lower()
    
    if filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="replace")
        
    elif filename.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception:
            return ""
            
    elif filename.endswith(".docx"):
        try:
            return docx2txt.process(io.BytesIO(file_bytes))
        except Exception:
            return ""
            
    elif filename.endswith(".xlsx"):
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
            text = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_text = " : ".join([str(cell) for cell in row if cell is not None])
                    if row_text:
                        text.append(row_text)
            return "\n".join(text)
        except Exception:
            return ""
            
    return ""
