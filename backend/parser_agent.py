"""
Parser Agent - Enhanced PDF extraction with structure preservation.
Extracts: text, metadata, tables, lists, and preserves document structure.
"""
import fitz
import re
from typing import TypedDict

class PDFMetadata(TypedDict):
    title: str
    author: str
    total_pages: int
    creation_date: str
    subject: str

class ParsedPDF(TypedDict):
    text: str
    metadata: PDFMetadata
    structure: str  # Simplified structure markers
    tables: list[str]
    lists: list[str]
    headers: list[str]

def extract_metadata(pdf_path: str) -> PDFMetadata:
    """Extract PDF metadata (title, author, etc)."""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata or {}
    
    return {
        "title": metadata.get("title", "Unknown"),
        "author": metadata.get("author", "Unknown"),
        "total_pages": doc.page_count,
        "creation_date": str(metadata.get("creationDate", "Unknown")),
        "subject": metadata.get("subject", ""),
    }

def preserve_structure(text: str) -> str:
    """Add structure markers to text for better understanding."""
    # Mark potential headers (short lines in caps)
    lines = text.split('\n')
    marked = []
    
    for line in lines:
        stripped = line.strip()
        # Detect headers: short lines (< 80 chars), mostly uppercase or numbered
        if (0 < len(stripped) < 80 and 
            (stripped.isupper() or re.match(r'^\d+\.|^[A-Z]', stripped))):
            marked.append(f"[HEADER] {stripped}")
        elif stripped and len(stripped) > 200:
            # Long paragraphs
            marked.append(f"[BODY] {stripped}")
        elif stripped:
            marked.append(stripped)
    
    return '\n'.join(marked)

def extract_tables(text: str) -> list[str]:
    """Extract likely table content from text."""
    # Look for aligned columns (multiple spaces between words)
    tables = []
    lines = text.split('\n')
    potential_table_lines = []
    
    for line in lines:
        # If line has 3+ columns of text separated by 2+ spaces
        if re.search(r'\S+\s{2,}\S+\s{2,}\S+', line):
            potential_table_lines.append(line)
        elif potential_table_lines and line.strip() == '':
            if len(potential_table_lines) > 2:
                tables.append('\n'.join(potential_table_lines))
            potential_table_lines = []
    
    return tables

def extract_lists(text: str) -> list[str]:
    """Extract bulleted/numbered lists from text."""
    lists = []
    lines = text.split('\n')
    current_list = []
    
    for line in lines:
        # Detect list items (bullet, number, dash)
        if re.match(r'^[\s]*([-•*]|\d+\.)\s+\S', line):
            current_list.append(line.strip())
        elif current_list and line.strip():
            # Continue if it's a continuation
            if line.startswith('  ') or line.startswith('\t'):
                current_list.append(line.strip())
            else:
                # List ended
                if len(current_list) > 1:
                    lists.append('\n'.join(current_list))
                current_list = []
        elif current_list and not line.strip():
            continue  # Empty line in list
    
    if current_list:
        lists.append('\n'.join(current_list))
    
    return lists

def extract_headers(text: str) -> list[str]:
    """Extract document headers/sections."""
    headers = []
    lines = text.split('\n')
    
    for line in lines:
        stripped = line.strip()
        # Headers are short, often capitalized or numbered sections
        if (0 < len(stripped) < 100 and 
            re.match(r'^(Chapter|Section|Part|\d+\.)\s+', stripped, re.I)):
            headers.append(stripped)
    
    return headers

def parse_pdf_enhanced(pdf_path: str) -> ParsedPDF:
    """
    Enhanced PDF parsing that preserves structure and extracts components.
    Returns structured data with metadata, text, and components.
    """
    doc = fitz.open(pdf_path)
    all_text = ""
    
    # Extract text page by page with page markers
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        all_text += f"\n[PAGE {page_num}]\n{text}\n"
    
    doc.close()
    
    # Extract components
    metadata = extract_metadata(pdf_path)
    structure = preserve_structure(all_text)
    tables = extract_tables(all_text)
    lists = extract_lists(all_text)
    headers = extract_headers(all_text)
    
    return {
        "text": all_text,
        "metadata": metadata,
        "structure": structure,
        "tables": tables,
        "lists": lists,
        "headers": headers,
    }

def get_best_text_for_generation(parsed: ParsedPDF) -> str:
    """
    Determine best text to send to card generator.
    Prioritize: structure > headers > lists > raw text
    """
    text_sources = []
    
    # Add headers first (high signal)
    if parsed["headers"]:
        text_sources.append("Headers:\n" + "\n".join(parsed["headers"]))
    
    # Add extracted lists (structured content)
    if parsed["lists"]:
        text_sources.append("\nKey Lists:\n" + "\n".join(parsed["lists"][:3]))  # Top 3
    
    # Add tables (if any)
    if parsed["tables"]:
        text_sources.append("\nTables:\n" + "\n".join(parsed["tables"][:2]))  # Top 2
    
    # Add structured text
    text_sources.append("\nContent:\n" + parsed["structure"][:15000])  # Limit size
    
    return "\n\n".join(text_sources)
