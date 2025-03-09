from booksummarize.PDFAnalyzer import PDFAnalyzer


class ReportGenerator:
    def __init__(self, pdf_file_path):
        self.analyzer = PDFAnalyzer(pdf_name=pdf_file_path, test_pages=100)

    def generate_report(self):
        print("🔍 Starting PDF Analysis...")
        self.analyzer.run()
        print("📊 Report generation complete!")

