#load the pdf
#extract the text from the pdf

#options - PyMuPDF, PDFPlumber, PyPDF2
#used PyMuPDF - https://pymupdf.readthedocs.io/en/latest/

#Task: Create a document loader that can load a PDF file and extract its text content.

'''
import pymupdf

doc = pymupdf.open("../assets/pdf/sample1.pdf")  
out = open("../assets/pdf/sample1.txt", "w")  

for page in doc:
    text = page.get_text()
    out.write(text)
    out.write("\n")  # Add a newline after each page


out.close()
'''


import os
import pymupdf
import uuid
from app.document_chunking.chunking import chunk_document
from app.helpers.data_classes import ChunkedJSONFileData, JSONChunkData, JSONFileData, JSONPageData
from app.helpers.text_cleanup import clean_text


class PDFExporter:

    def __init__(self, text_path):
        self.txt_path = text_path
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.txt_path), exist_ok=True)

    def export_all_pdfs(self, pdf_dir):
        import os

        self.json = []  # Clear previous JSON data
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                self.pdf_path = os.path.join(pdf_dir, filename)
                self.export_text_to_json_list(self.pdf_path, filename)
        
        return self.json

    def export_text_to_json_list(self, pdf_path, filename):
        self.pdf_path = pdf_path
        self.validate()

        file_id = str(uuid.uuid4())
        self.txt_path += f"{file_id}.txt"

        json = ChunkedJSONFileData(file_id=file_id, filename=filename, chunks=[])
        doc = pymupdf.open(self.pdf_path)  
        for page in doc:
            text = page.get_text()
            cleaned_text = clean_text(text)
            chunked_data = chunk_document(cleaned_text, chunk_size=1000)  # Example chunk size
            for i, chunk in enumerate(chunked_data):
                chunk_data = JSONChunkData(
                    chunkid=str(uuid.uuid4()),
                    chunk_index=i,
                    pagenumber=page.number + 1,
                    text=chunk,
                    char_count=len(chunk)
                )
                json.chunks.append(chunk_data)

        print(json)
        json.save(self.txt_path + f"{file_id}.json")

    def validate(self):
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        if not self.pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"Invalid file type: {self.pdf_path}. Expected a PDF file.")
        
        # validate not empty
        if os.path.getsize(self.pdf_path) == 0:
            raise ValueError(f"PDF file is empty: {self.pdf_path}")
        
        # validate readable
        try:
            with open(self.pdf_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            raise ValueError(f"PDF file is not readable: {self.pdf_path}. Error: {str(e)}")
        
        # validate not too large (e.g., 100MB)
        if os.path.getsize(self.pdf_path) > 100 * 1024 * 1024:
            raise ValueError(f"PDF file is too large: {self.pdf_path}. Maximum allowed size is 100MB.")
        

exporter = PDFExporter("data/processed/")
a = exporter.export_all_pdfs("data/pdf/")
#print(a)