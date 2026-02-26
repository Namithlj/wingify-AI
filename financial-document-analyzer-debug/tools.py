## Importing libraries and files
import os
try:
    from dotenv import load_dotenv  # type: ignore[reportMissingImports]
except Exception:
    def load_dotenv(*a, **k):
        return None

load_dotenv()

from crewai_tools import tools
from crewai_tools.tools.serper_dev_tool import SerperDevTool

# Try to use langchain's PyPDFLoader if available; otherwise provide a minimal fallback
try:
    from langchain.document_loaders import PyPDFLoader as Pdf  # type: ignore[reportMissingImports]
except Exception:
    class _PdfPage:
        def __init__(self, content):
            self.page_content = content

    class Pdf:
        def __init__(self, file_path=None):
            self.file_path = file_path

        def load(self):
            # Fallback: return file bytes decoded as text as single page
            try:
                with open(self.file_path, 'rb') as f:
                    raw = f.read()
                text = raw.decode('utf-8', errors='replace')
            except Exception:
                text = f"<could not read file {self.file_path}>"
            return [_PdfPage(text)]

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool():
    async def read_data_tool(path='data/sample.pdf'):
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """
        
        docs = Pdf(file_path=path).load()

        full_report = ""
        for data in docs:
            # Clean and format the financial document data
            content = data.page_content
            
            # Remove extra whitespaces and format properly
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
                
            full_report += content + "\n"
            
        return full_report

## Creating Investment Analysis Tool
class InvestmentTool:
    async def analyze_investment_tool(financial_document_data):
        # Process and analyze the financial document data
        processed_data = financial_document_data
        
        # Clean up the data format
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":  # Remove double spaces
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1
                
        # TODO: Implement investment analysis logic here
        return "Investment analysis functionality to be implemented"

## Creating Risk Assessment Tool
class RiskTool:
    async def create_risk_assessment_tool(financial_document_data):        
        # TODO: Implement risk assessment logic here
        return "Risk assessment functionality to be implemented"