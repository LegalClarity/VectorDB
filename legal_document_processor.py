"""
Legal Document Processor for RAG Chatbot
Handles PDF processing, text extraction, and intelligent chunking for legal documents.
"""

import os
import glob
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalDocumentProcessor:
    """
    Processes legal documents with specialized chunking strategies for RAG systems.
    """

    def __init__(self, embedding_model: Optional[SentenceTransformer] = None):
        """
        Initialize the document processor.

        Args:
            embedding_model: Pre-loaded embedding model for semantic chunking
        """
        self.embedding_model = embedding_model

        # Legal-specific text splitter configurations
        self.legal_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "; ",    # Semicolon separations
                ": ",    # Colon separations
                ", ",    # Comma separations
                " ",     # Word breaks
                "",      # Character level
            ],
            length_function=len,
            is_separator_regex=False,
        )

        # Token-based splitter for more precise control
        self.token_splitter = TokenTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            encoding_name="cl100k_base"  # GPT-4 tokenizer
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF with error handling and text cleaning.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted and cleaned text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text += page_text + "\n\n"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num} from {pdf_path}: {e}")
                        continue

                # Clean the extracted text
                cleaned_text = self._clean_legal_text(text)
                return cleaned_text

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return ""

    def _clean_legal_text(self, text: str) -> str:
        """
        Clean and normalize legal text for better processing.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # Remove page numbers and headers/footers (common in legal docs)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^.*Page \d+.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)

        # Remove non-printable characters but keep newlines
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

        return text.strip()

    def classify_document_type(self, text: str) -> str:
        """
        Classify the type of legal document based on content analysis.

        Args:
            text: Document text

        Returns:
            Document type classification
        """
        text_lower = text.lower()

        # Define classification patterns
        classifications = {
            "rent_control_act": ["rent", "lease", "tenant", "landlord", "rent control", "eviction"],
            "contract_act": ["contract", "agreement", "parties", "consideration", "breach"],
            "banking_regulation": ["banking", "reserve bank", "financial institution", "deposit"],
            "consumer_protection": ["consumer", "unfair trade", "defective", "complaint"],
            "housing_finance": ["housing finance", "mortgage", "loan", "property"],
            "information_technology": ["information technology", "electronic", "digital", "cyber"],
            "model_tenancy": ["tenancy", "rental", "model act", "housing"],
        }

        scores = {}
        for doc_type, keywords in classifications.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[doc_type] = score

        # Return highest scoring classification or general
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        else:
            return "general_legal"

    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal entities like parties, dates, amounts from text.

        Args:
            text: Document text

        Returns:
            Dictionary of extracted entities
        """
        entities = {
            "parties": [],
            "dates": [],
            "monetary_amounts": [],
            "legal_terms": [],
            "sections": []
        }

        # Extract potential parties (capitalized names)
        party_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_parties = re.findall(party_pattern, text)
        entities["parties"] = list(set(potential_parties))[:10]  # Limit to top 10

        # Extract dates
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text, re.IGNORECASE)[:5]

        # Extract monetary amounts
        money_pattern = r'₹\s*\d+(?:,\d{3})*(?:\.\d{2})?|\$\s*\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*\s*(?:rupees|dollars|euros|pounds)'
        entities["monetary_amounts"] = re.findall(money_pattern, text, re.IGNORECASE)[:5]

        # Extract section references
        section_pattern = r'Section\s+\d+|\(?\d+\)|\([a-z]\)|\([ivx]+\)'
        entities["sections"] = re.findall(section_pattern, text, re.IGNORECASE)[:10]

        return entities

    def create_chunks(self, text: str, method: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Create intelligent chunks from legal documents.

        Args:
            text: Document text
            method: Chunking method ("recursive", "token", "hybrid")

        Returns:
            List of chunk dictionaries with metadata
        """
        if method == "recursive":
            chunks = self.legal_splitter.split_text(text)
        elif method == "token":
            chunks = self.token_splitter.split_text(text)
        elif method == "hybrid":
            # Use recursive first, then token-based for refinement
            initial_chunks = self.legal_splitter.split_text(text)
            chunks = []
            for chunk in initial_chunks:
                if len(chunk.split()) > 100:  # If chunk is too long
                    sub_chunks = self.token_splitter.split_text(chunk)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(chunk)
        else:
            raise ValueError(f"Unknown chunking method: {method}")

        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:  # Skip very small chunks
                continue

            chunk_obj = {
                "id": i,
                "content": chunk.strip(),
                "length": len(chunk),
                "word_count": len(chunk.split()),
                "entities": self.extract_legal_entities(chunk),
                "chunk_type": self._classify_chunk_type(chunk)
            }
            chunk_objects.append(chunk_obj)

        return chunk_objects

    def _classify_chunk_type(self, chunk: str) -> str:
        """
        Classify the type of chunk based on content.

        Args:
            chunk: Text chunk

        Returns:
            Chunk type classification
        """
        chunk_lower = chunk.lower()

        if any(term in chunk_lower for term in ["section", "clause", "article", "sub-section"]):
            return "legal_clause"
        elif any(term in chunk_lower for term in ["whereas", "therefore", "hereby", "shall"]):
            return "legal_provision"
        elif any(term in chunk_lower for term in ["penalty", "punishment", "fine", "imprisonment"]):
            return "legal_penalty"
        elif any(term in chunk_lower for term in ["definition", "means", "includes", "shall mean"]):
            return "definition"
        else:
            return "general_content"

    def process_documents(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Process all documents in a folder and return structured data.

        Args:
            folder_path: Path to folder containing documents

        Returns:
            List of processed document objects
        """
        processed_documents = []

        # Find all PDF files
        pdf_pattern = os.path.join(folder_path, "**", "*.pdf")
        pdf_files = glob.glob(pdf_pattern, recursive=True)

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file}")

            # Extract text
            text = self.extract_text_from_pdf(pdf_file)
            if not text:
                logger.warning(f"No text extracted from {pdf_file}")
                continue

            # Classify document
            doc_type = self.classify_document_type(text)

            # Create chunks
            chunks = self.create_chunks(text, method="hybrid")

            # Create document object
            doc_obj = {
                "filename": os.path.basename(pdf_file),
                "filepath": pdf_file,
                "doc_type": doc_type,
                "total_length": len(text),
                "word_count": len(text.split()),
                "chunks": chunks,
                "entities": self.extract_legal_entities(text),
                "summary": self._generate_summary(text)
            }

            processed_documents.append(doc_obj)

        logger.info(f"Successfully processed {len(processed_documents)} documents")
        return processed_documents

    def _generate_summary(self, text: str, max_length: int = 300) -> str:
        """
        Generate a simple summary of the document.

        Args:
            text: Document text
            max_length: Maximum summary length

        Returns:
            Document summary
        """
        # Extract first few sentences as summary
        sentences = re.split(r'[.!?]+', text)
        summary_sentences = []

        for sentence in sentences[:3]:  # First 3 sentences
            if len(' '.join(summary_sentences + [sentence.strip()])) < max_length:
                if sentence.strip():
                    summary_sentences.append(sentence.strip())
            else:
                break

        return '. '.join(summary_sentences) + '.' if summary_sentences else "Legal document summary"


# Usage example
if __name__ == "__main__":
    processor = LegalDocumentProcessor()

    # Process documents
    documents = processor.process_documents("Rag Documents")

    # Print summary
    for doc in documents:
        print(f"\nDocument: {doc['filename']}")
        print(f"Type: {doc['doc_type']}")
        print(f"Chunks: {len(doc['chunks'])}")
        print(f"Summary: {doc['summary'][:100]}...")
