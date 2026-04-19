"""
NLP Agent - Advanced flashcard generation.
Uses a single optimized prompt to save tokens.
Supports multiple AI models (Groq, OpenAI, Anthropic).
"""
import os
import json
import re
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

print(f"[nlp_agent] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")

DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

class AIModel(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

def create_groq_client():
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        return Groq(api_key=api_key)
    except ImportError:
        raise ImportError("Groq package not installed. Run: pip install groq")

def generate_cards_with_model(text: str, model: AIModel = AIModel.GROQ, max_cards: int = 15) -> list[dict]:
    if model == AIModel.GROQ:
        return _generate_with_groq(text, max_cards)
    elif model == AIModel.OPENAI:
        return _generate_with_openai(text, max_cards)
    elif model == AIModel.ANTHROPIC:
        return _generate_with_anthropic(text, max_cards)
    else:
        return _generate_with_groq(text, max_cards)

def _build_prompt(text: str, max_cards: int) -> str:
    return f"""You are an expert educator creating high-quality flashcards.

MATERIAL:
{text}

Generate exactly {max_cards} flashcards covering ALL these categories:
- definition: "What is X?", "Define X"
- concept: "How does X work?", "Explain the principle of X"
- relationship: "How does X relate to Y?", "What is the difference between X and Y?"
- edge_case: "What happens when X?", "When does X not apply?"
- example: "Show an example of X", "Walk through X step by step"
- application: "How is X applied in real life?"

Mix categories evenly. Make questions specific and testable.

Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
Each object must have exactly these fields:
- "front": question string
- "back": answer string (1-3 sentences)
- "category": one of ["definition", "concept", "relationship", "edge_case", "example", "application"]
- "difficulty": one of ["easy", "medium", "hard"]
- "hint": short hint max 10 words

[{{"front": "What is spaced repetition?", "back": "A learning technique that schedules reviews at increasing intervals to maximize long-term retention.", "category": "definition", "difficulty": "easy", "hint": "Think about timing of reviews"}}]"""

def _generate_with_groq(text: str, max_cards: int = 15) -> list[dict]:
    client = create_groq_client()
    text = text[:12000]  # single chunk, saves tokens
    prompt = _build_prompt(text, max_cards)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=3000,
        )
        raw = response.choices[0].message.content.strip()
        print(f"[nlp_agent] Groq raw response: {raw[:200]}")

        if "```" in raw:
            raw = re.sub(r"```(?:json)?", "", raw).strip()

        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            cards = json.loads(match.group())
            cards = [c for c in cards if all(k in c for k in ["front", "back", "category", "difficulty", "hint"])]
            print(f"[nlp_agent] Got {len(cards)} cards")
            return cards[:max_cards]
        else:
            print(f"[nlp_agent] No JSON array found in response")
            return []

    except Exception as e:
        print(f"[nlp_agent] Groq error: {e}")
        raise

def _generate_with_openai(text: str, max_cards: int = 15) -> list[dict]:
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. pip install openai")

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    text = text[:8000]
    prompt = _build_prompt(text, max_cards)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            cards = json.loads(match.group())
            return cards[:max_cards]
    except Exception as e:
        print(f"[nlp_agent] OpenAI error: {e}")
        raise

    return []

def _generate_with_anthropic(text: str, max_cards: int = 15) -> list[dict]:
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. pip install anthropic")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    text = text[:8000]
    prompt = _build_prompt(text, max_cards)

    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            cards = json.loads(match.group())
            return cards[:max_cards]
    except Exception as e:
        print(f"[nlp_agent] Anthropic error: {e}")
        raise

    return []

def generate_flashcards_advanced(text: str, preferred_model: str = "groq") -> list[dict]:
    if DEMO_MODE:
        print("[nlp_agent] DEMO_MODE enabled - returning sample cards")
        return _generate_demo_cards()

    if preferred_model.lower() == "groq":
        models_to_try = [AIModel.GROQ, AIModel.OPENAI, AIModel.ANTHROPIC]
    elif preferred_model.lower() == "openai":
        models_to_try = [AIModel.OPENAI, AIModel.GROQ, AIModel.ANTHROPIC]
    elif preferred_model.lower() == "anthropic":
        models_to_try = [AIModel.ANTHROPIC, AIModel.OPENAI, AIModel.GROQ]
    else:
        models_to_try = [AIModel.GROQ, AIModel.OPENAI, AIModel.ANTHROPIC]

    for model in models_to_try:
        try:
            cards = generate_cards_with_model(text, model, max_cards=15)
            if cards:
                print(f"[nlp_agent] Generated {len(cards)} cards using {model.value}")
                return cards
        except Exception as e:
            print(f"[nlp_agent] {model.value} failed: {e}. Trying next model...")
            continue

    raise Exception("All AI models failed. Check your API keys in .env and backend logs.")

def _generate_demo_cards() -> list[dict]:
    return [
        {
            "front": "What is a quadratic equation?",
            "back": "An equation of the form ax² + bx + c = 0, where a ≠ 0.",
            "category": "definition",
            "difficulty": "easy",
            "hint": "Contains squared variable"
        },
        {
            "front": "How do you solve a quadratic using the quadratic formula?",
            "back": "Use x = (-b ± √(b² - 4ac)) / 2a.",
            "category": "relationship",
            "difficulty": "medium",
            "hint": "Formula connects equation to solutions"
        },
        {
            "front": "What does the discriminant tell you?",
            "back": "b² - 4ac: >0 two real roots, =0 one real root, <0 complex roots.",
            "category": "concept",
            "difficulty": "medium",
            "hint": "Sign determines root type"
        },
    ]