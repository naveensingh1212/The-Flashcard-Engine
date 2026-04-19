"""
Validation Agent - Quality assurance and error handling.
Validates cards, detects duplicates, ensures proper formatting.
"""
import re
from typing import Optional, Tuple
from difflib import SequenceMatcher

class ValidationResult:
    def __init__(self):
        self.valid_cards = []
        self.invalid_cards = []
        self.duplicates_removed = 0
        self.errors = []
        self.warnings = []

def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity between two strings (0-1)."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def is_valid_card(card: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate a single card structure and content.
    Returns (is_valid, error_message)
    """
    required_fields = ["front", "back", "category", "difficulty", "hint"]
    
    # Check required fields
    for field in required_fields:
        if field not in card:
            return False, f"Missing required field: {field}"
    
    # Validate field types
    if not isinstance(card["front"], str) or not card["front"].strip():
        return False, "Front (question) cannot be empty"
    
    if not isinstance(card["back"], str) or not card["back"].strip():
        return False, "Back (answer) cannot be empty"
    
    # Front and back should be different
    if card["front"].strip().lower() == card["back"].strip().lower():
        return False, "Front and back are identical"
    
    # Validate category
    valid_categories = ["definition", "concept", "example", "relationship", "application", "edge_case"]
    if card["category"] not in valid_categories:
        return False, f"Invalid category: {card['category']}"
    
    # Validate difficulty
    valid_difficulties = ["easy", "medium", "hard"]
    if card["difficulty"] not in valid_difficulties:
        return False, f"Invalid difficulty: {card['difficulty']}"
    
    # Validate hint
    if not isinstance(card["hint"], str):
        card["hint"] = str(card["hint"])
    
    hint_words = len(card["hint"].split())
    if hint_words > 15:
        return False, f"Hint too long ({hint_words} words, max 15)"
    
    # Content length checks
    if len(card["front"]) < 5:
        return False, "Question too short (min 5 chars)"
    
    if len(card["front"]) > 500:
        return False, "Question too long (max 500 chars)"
    
    if len(card["back"]) < 10:
        return False, "Answer too short (min 10 chars)"
    
    if len(card["back"]) > 2000:
        return False, "Answer too long (max 2000 chars)"
    
    # Check for low-quality patterns (generic questions)
    generic_patterns = [
        r"^what is (this|it|the)?$",
        r"^why$",
        r"^how$",
        r"^who",
    ]
    front_lower = card["front"].lower().strip()
    for pattern in generic_patterns:
        if re.match(pattern, front_lower):
            return False, f"Question too generic: '{card['front']}'"
    
    return True, None

def clean_card(card: dict) -> dict:
    """
    Clean and normalize card fields.
    """
    cleaned = {
        "front": card.get("front", "").strip(),
        "back": card.get("back", "").strip(),
        "category": card.get("category", "concept").lower(),
        "difficulty": card.get("difficulty", "medium").lower(),
        "hint": card.get("hint", "").strip()[:150],  # Limit hint length
    }
    
    # Remove extra whitespace and normalize
    cleaned["front"] = re.sub(r'\s+', ' ', cleaned["front"])
    cleaned["back"] = re.sub(r'\s+', ' ', cleaned["back"])
    cleaned["hint"] = re.sub(r'\s+', ' ', cleaned["hint"])
    
    # Remove markdown formatting if present
    cleaned["front"] = re.sub(r'\*\*|__|\*|_|`', '', cleaned["front"])
    cleaned["back"] = re.sub(r'\n\n+', '\n', cleaned["back"])  # Normalize line breaks
    
    return cleaned

def remove_duplicates(cards: list[dict], similarity_threshold: float = 0.85) -> Tuple[list[dict], int]:
    """
    Remove duplicate or near-duplicate cards.
    Returns (deduplicated_cards, count_removed)
    """
    if not cards:
        return [], 0
    
    deduplicated = []
    removed_count = 0
    
    for card in cards:
        is_duplicate = False
        
        for existing in deduplicated:
            # Check similarity of front (questions)
            front_similarity = similarity_ratio(card["front"], existing["front"])
            
            # Check similarity of back (answers)
            back_similarity = similarity_ratio(card["back"], existing["back"])
            
            # If both questions and answers are very similar, it's a duplicate
            avg_similarity = (front_similarity + back_similarity) / 2
            
            if avg_similarity > similarity_threshold:
                is_duplicate = True
                removed_count += 1
                break
        
        if not is_duplicate:
            deduplicated.append(card)
    
    return deduplicated, removed_count

def validate_cards_batch(cards: list[dict], remove_dupes: bool = True) -> ValidationResult:
    """
    Validate a batch of cards.
    Returns ValidationResult with valid cards and error info.
    """
    result = ValidationResult()
    
    if not cards:
        result.errors.append("No cards provided")
        return result
    
    # First pass: clean and validate individual cards
    cleaned_cards = []
    for i, card in enumerate(cards):
        try:
            cleaned = clean_card(card)
            is_valid, error = is_valid_card(cleaned)
            
            if is_valid:
                cleaned_cards.append(cleaned)
            else:
                result.invalid_cards.append({
                    "index": i,
                    "card": card,
                    "error": error
                })
                result.warnings.append(f"Card {i+1}: {error}")
        
        except Exception as e:
            result.invalid_cards.append({
                "index": i,
                "card": card,
                "error": str(e)
            })
            result.errors.append(f"Card {i+1} processing failed: {e}")
    
    # Second pass: remove duplicates if requested
    if remove_dupes and cleaned_cards:
        deduplicated, removed = remove_duplicates(cleaned_cards, similarity_threshold=0.82)
        result.duplicates_removed = removed
        result.valid_cards = deduplicated
    else:
        result.valid_cards = cleaned_cards
    
    return result

def validate_pdf_text(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate extracted PDF text quality.
    Returns (is_valid, error_message)
    """
    if not text or not isinstance(text, str):
        return False, "Text is empty or invalid"
    
    text_stripped = text.strip()
    
    if len(text_stripped) < 100:
        return False, "Text too short (less than 100 characters)"
    
    if len(text_stripped) > 500000:
        return False, "Text too long (more than 500k characters)"
    
    # Check if text has some meaningful content (not just symbols)
    words = text_stripped.split()
    if len(words) < 20:
        return False, "Not enough words extracted"
    
    # Check for language (basic heuristic)
    letter_count = sum(1 for c in text_stripped if c.isalpha())
    if letter_count / len(text_stripped) < 0.3:
        return False, "Text appears to be mostly non-alphabetic (possibly scanned image)"
    
    return True, None

def generate_quality_report(result: ValidationResult) -> dict:
    """
    Generate a quality report from validation result.
    """
    total_processed = len(result.valid_cards) + len(result.invalid_cards)
    valid_count = len(result.valid_cards)
    
    return {
        "total_processed": total_processed,
        "valid_cards": valid_count,
        "invalid_cards": len(result.invalid_cards),
        "duplicates_removed": result.duplicates_removed,
        "final_count": len(result.valid_cards),
        "success_rate": round((valid_count / total_processed * 100), 1) if total_processed > 0 else 0,
        "warnings": result.warnings[:10],  # Top 10 warnings
        "errors": result.errors,
    }
