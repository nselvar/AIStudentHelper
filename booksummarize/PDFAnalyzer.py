from pathlib import Path
from pydantic import BaseModel
import json
from openai import OpenAI
import fitz  # PyMuPDF
from termcolor import colored

# Configuration Constants
BASE_DIR = Path("book_analysis")
PDF_DIR = BASE_DIR / "pdfs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_bases"
SUMMARIES_DIR = BASE_DIR / "summaries"
ANALYSIS_INTERVAL = 1
MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "o1-mini"
TEST_PAGES = 160

class PageContent(BaseModel):
    has_content: bool
    knowledge: list[str]

class PDFAnalyzer:
    def __init__(self, pdf_name: str, test_pages: int = TEST_PAGES):
        """
        Initialize the PDF Analyzer with a specific PDF file.

        :param pdf_name: Name of the PDF file (must be inside `PDF_DIR` or full path).
        :param test_pages: Number of pages to process (default: TEST_PAGES).
        """
        self.PDF_NAME = pdf_name
        self.PDF_PATH = Path(pdf_name) if Path(pdf_name).is_absolute() else PDF_DIR / pdf_name
        self.OUTPUT_PATH = KNOWLEDGE_DIR / f"{self.PDF_NAME.replace('.pdf', '_knowledge.json')}"
        self.TEST_PAGES = test_pages
        self.client = OpenAI()

    def setup_directories(self):
        """Ensure necessary directories exist and check the PDF file."""
        for directory in [PDF_DIR, KNOWLEDGE_DIR, SUMMARIES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        if not self.PDF_PATH.exists():
            raise FileNotFoundError(f"PDF file '{self.PDF_PATH}' not found")

    def load_existing_knowledge(self) -> list[str]:
        """Load existing knowledge base if available."""
        if self.OUTPUT_PATH.exists():
            print(colored("📚 Loading existing knowledge base...", "cyan"))
            with open(self.OUTPUT_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("knowledge", [])
        print(colored("🆕 Starting with fresh knowledge base", "cyan"))
        return []

    def save_knowledge_base(self, knowledge_base: list[str]):
        """Save extracted knowledge to a JSON file."""
        print(colored(f"💾 Saving knowledge base ({len(knowledge_base)} items)...", "blue"))
        with open(self.OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump({"knowledge": knowledge_base}, f, indent=2)

    def process_page(self, page_text: str, current_knowledge: list[str], page_num: int) -> list[str]:
        """Process a single page using OpenAI to extract knowledge."""
        print(colored(f"\n📖 Processing page {page_num + 1}...", "yellow"))

        completion = self.client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Analyze this page as if you're studying from a book."},
                {"role": "user", "content": f"Page text: {page_text}"}
            ],
            response_format=PageContent
        )

        result = completion.choices[0].message.parsed
        if result.has_content:
            print(colored(f"✅ Found {len(result.knowledge)} new knowledge points", "green"))
        else:
            print(colored("⏭️  Skipping page (no relevant content)", "yellow"))

        updated_knowledge = current_knowledge + (result.knowledge if result.has_content else [])
        self.save_knowledge_base(updated_knowledge)
        return updated_knowledge

    def analyze_knowledge_base(self, knowledge_base: list[str]) -> str:
        """Generate a final book analysis from extracted knowledge."""
        if not knowledge_base:
            print(colored("\n⚠️  Skipping analysis: No knowledge points collected", "yellow"))
            return ""

        print(colored("\n🤔 Generating final book analysis...", "cyan"))
        completion = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Summarize the extracted knowledge in markdown format"},
                {"role": "user", "content": "\n".join(knowledge_base)}
            ]
        )

        print(colored("✨ Analysis generated successfully!", "green"))
        return completion.choices[0].message.content

    def save_summary(self, summary: str, is_final: bool = False):
        """Save the generated summary as a Markdown file."""
        if not summary:
            print(colored("⏭️  Skipping summary save: No content to save", "yellow"))
            return

        summary_path = SUMMARIES_DIR / f"{self.PDF_NAME.replace('.pdf', '')}_{'final' if is_final else 'interval'}.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(colored(f"✅ Summary saved to: {summary_path}", "green"))

    def run(self):
        """Main function to analyze the PDF document."""
        self.setup_directories()
        knowledge_base = self.load_existing_knowledge()

        pdf_document = fitz.open(self.PDF_PATH)
        pages_to_process = self.TEST_PAGES if self.TEST_PAGES is not None else pdf_document.page_count

        print(colored(f"\n📚 Processing {pages_to_process} pages from '{self.PDF_PATH.name}'...", "cyan"))
        for page_num in range(min(pages_to_process, pdf_document.page_count)):
            page = pdf_document[page_num]
            page_text = page.get_text()

            knowledge_base = self.process_page(page_text, knowledge_base, page_num)

            if ANALYSIS_INTERVAL and (page_num + 1) % ANALYSIS_INTERVAL == 0:
                print(colored(f"\n📊 Progress: {page_num + 1}/{pages_to_process} pages processed", "cyan"))
                interval_summary = self.analyze_knowledge_base(knowledge_base)
                self.save_summary(interval_summary, is_final=False)

        final_summary = self.analyze_knowledge_base(knowledge_base)
        self.save_summary(final_summary, is_final=True)

        print(colored("\n✨ Processing complete! ✨", "green", attrs=['bold']))