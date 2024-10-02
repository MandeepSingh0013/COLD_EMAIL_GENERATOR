import pandas as pd
import PyPDF2
import docx
import openpyxl

class FileHandler:
    def process_file(self, uploaded_file):
        file_type = uploaded_file.name.split('.')[-1]
        
        if file_type == "csv":
            return self.process_csv(uploaded_file)
        elif file_type == "pdf":
            return self.process_pdf(uploaded_file)
        elif file_type == "docx":
            return self.process_word(uploaded_file)
        elif file_type == "xlsx":
            return self.process_excel(uploaded_file)
        else:
            return "error", None

    def process_csv(self, file):
        data = pd.read_csv(file)
        return "success", data.to_string()
        

    def process_pdf(self, file):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        # You can customize parsing based on how your PDF is structured
        return "success", text

    def process_word(self, file):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return "success", text

    def process_excel(self, file):
        data = pd.read_excel(file)
        return "success", data.to_string()
        