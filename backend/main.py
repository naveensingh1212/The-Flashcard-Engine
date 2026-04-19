import os
import uuid
import shutil
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from parser_agent import parse_pdf_enhanced, get_best_text_for_generation
from nlp_agent import generate_flashcards_advanced
from validator_agent import validate_cards_batch, validate_pdf_text, generate_quality_report
from database import (
    init_db, insert_deck, get_all_decks, get_deck_by_id, delete_deck,
    insert_cards, get_cards_for_deck, get_card_by_id, update_card,get_deck_by_source_file
)
from sm2 import apply_sm2

load_dotenv()
init_db()

app = FastAPI(title="Flashcard Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    card_id: str
    quality: int  # 0-5

# ── Helpers ───────────────────────────────────────────────────────────────────

def enrich_deck(deck: dict) -> dict:
    """Add card stats to a deck dict."""
    cards = get_cards_for_deck(deck["id"])
    now = datetime.utcnow().isoformat()
    mastery_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    due_count = 0
    for c in cards:
        mastery_counts[c["mastery"]] = mastery_counts.get(c["mastery"], 0) + 1
        if c["due_date"] <= now:
            due_count += 1
    total = len(cards)
    return {
        **deck,
        "total_cards": total,
        "due_count": due_count,
        "mastery_counts": mastery_counts,
        "mastery_percent": round((mastery_counts[3] / total) * 100) if total else 0,
    }

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decks/upload")
async def upload_pdf(file: UploadFile = File(...), deck_name: Optional[str] = None):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Save to temp file (parser needs a path, not bytes)
    suffix = f"_{file.filename}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # ── STEP 1: Parse PDF with enhanced parser agent ──
        parsed_pdf = parse_pdf_enhanced(tmp_path)
        
        # Validate extracted text
        is_text_valid, text_error = validate_pdf_text(parsed_pdf["text"])
        if not is_text_valid:
            raise HTTPException(400, f"PDF parsing failed: {text_error}")
        
        # Get best text for generation (prioritize structure)
        best_text = get_best_text_for_generation(parsed_pdf)
        
    except Exception as e:
        raise HTTPException(500, f"PDF parsing failed: {e}")
    finally:
        os.remove(tmp_path)

    try:
        # ── STEP 2: Generate cards with NLP agent ──
        # Try to use preferred model from env, fallback to groq
        preferred_model = os.environ.get("PREFERRED_AI_MODEL", "groq")
        cards_data = generate_flashcards_advanced(best_text, preferred_model=preferred_model)
        
    except Exception as e:
        raise HTTPException(500, f"Card generation failed: {e}")

    if not cards_data:
        raise HTTPException(500, "Could not generate any cards from this PDF")

    try:
        # ── STEP 3: Validate cards with validator agent ──
        validation_result = validate_cards_batch(cards_data, remove_dupes=True)
        validated_cards = validation_result.valid_cards
        quality_report = generate_quality_report(validation_result)
        
        if not validated_cards:
            raise HTTPException(500, f"Card validation failed: {validation_result.errors}")
        
        print(f"[upload] Quality Report: {quality_report}")
        
    except Exception as e:
        raise HTTPException(500, f"Card validation failed: {e}")

    # ── STEP 4: Save to database ──
    now = datetime.utcnow().isoformat()
    deck_id = str(uuid.uuid4())
    name = deck_name or file.filename.replace(".pdf", "").replace("_", " ").title()

    # Include metadata in deck
    deck = {
        "id": deck_id,
        "name": name,
        "source_file": file.filename,
        "created_at": now,
        "pdf_metadata": parsed_pdf["metadata"],
        "generation_model": preferred_model,
    }
    # ── Duplicate check ──
    if get_deck_by_source_file(file.filename):
        raise HTTPException(
            400, f"A deck from '{file.filename}' already exists. Delete it first."
        )

    insert_deck(deck)

    # Prepare cards with SM-2 scheduling
    cards = []
    for cd in validated_cards:
        card = {
            "id": str(uuid.uuid4()),
            "deck_id": deck_id,
            "front": cd["front"],
            "back": cd["back"],
            "category": cd["category"],
            "difficulty": cd["difficulty"],
            "hint": cd["hint"],
            "repetitions": 0,
            "interval_days": 1,
            "ease_factor": 2.5,
            "due_date": now,
            "last_reviewed": None,
            "mastery": 0,
        }
        cards.append(card)

    insert_cards(cards)

    return {
        "deck": enrich_deck(deck),
        "cards": cards,
        "metadata": {
            "pdf_title": parsed_pdf["metadata"]["title"],
            "pdf_pages": parsed_pdf["metadata"]["total_pages"],
            "cards_generated": len(validated_cards),
            "quality_report": quality_report,
        }
    }


@app.get("/decks")
def list_decks():
    decks = [enrich_deck(d) for d in get_all_decks()]
    return {"decks": decks}


@app.get("/decks/{deck_id}")
def get_deck(deck_id: str):
    deck = get_deck_by_id(deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    cards = get_cards_for_deck(deck_id)
    return {"deck": enrich_deck(deck), "cards": cards}


@app.delete("/decks/{deck_id}")
def remove_deck(deck_id: str):
    if not get_deck_by_id(deck_id):
        raise HTTPException(404, "Deck not found")
    delete_deck(deck_id)
    return {"message": "Deck deleted"}


@app.get("/decks/{deck_id}/study")
def get_study_session(deck_id: str, limit: int = 20):
    """Returns cards due for review, prioritised by urgency."""
    if not get_deck_by_id(deck_id):
        raise HTTPException(404, "Deck not found")

    cards = get_cards_for_deck(deck_id)
    now = datetime.utcnow().isoformat()

    due = sorted(
        [c for c in cards if c["due_date"] <= now],
        key=lambda c: c["due_date"]   # most overdue first
    )
    new_cards = [c for c in cards if c["mastery"] == 0 and c not in due]

    queue = (due + new_cards)[:limit]
    return {
        "cards": queue,
        "total_due": len(due),
        "total_new": len(new_cards),
        "total_cards": len(cards),
    }


@app.post("/cards/review")
def review_card(req: ReviewRequest):
    """Submit review result → SM-2 reschedules the card."""
    card = get_card_by_id(req.card_id)
    if not card:
        raise HTTPException(404, "Card not found")

    updated = apply_sm2(dict(card), req.quality)
    update_card(updated)
    return {"card": updated}


@app.get("/decks/{deck_id}/stats")
def deck_stats(deck_id: str):
    if not get_deck_by_id(deck_id):
        raise HTTPException(404, "Deck not found")

    cards = get_cards_for_deck(deck_id)
    now = datetime.utcnow().isoformat()

    mastery_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    category_counts: dict = {}
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    due_count = 0

    for c in cards:
        mastery_counts[c["mastery"]] = mastery_counts.get(c["mastery"], 0) + 1
        cat = c.get("category", "concept")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        diff = c.get("difficulty", "medium")
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        if c["due_date"] <= now:
            due_count += 1

    total = len(cards)
    return {
        "deck_id": deck_id,
        "total_cards": total,
        "mastery_counts": mastery_counts,
        "mastery_percent": round((mastery_counts[3] / total) * 100) if total else 0,
        "category_counts": category_counts,
        "difficulty_counts": difficulty_counts,
        "due_count": due_count,
    }