"""
NLP Agent - Advanced flashcard generation with category-specific prompts.
Uses specialized prompts for each card category to improve quality.
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

class CardCategory(Enum):
    DEFINITION = "definition"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    EDGE_CASE = "edge_case"
    EXAMPLE = "example"        
    APPLICATION = "application"

CATEGORY_PROMPTS = {
    "definition": """Extract precise definitions and explanations of key terms.
        - Questions: "What is X?", "Define X", "Explain X"
        - Answers: Clear, concise definitions (1-2 sentences)
        - Include any etymology or related terms if relevant
        - Difficulty: Usually easy to medium""",
    
    "concept": """Explain core concepts and principles.
        - Questions: "Explain the concept of X", "How does X work?", "What is the principle of X?"
        - Answers: Detailed but concise explanation (2-3 sentences)
        - Include why it matters
        - Difficulty: Medium""",
    
    "relationship": """Explore connections between concepts and practical applications.
        - Questions: "How does X relate to Y?", "What is the difference between X and Y?", "How are X and Y connected?", "How is X used in practice?", "Give an example of X"
        - Answers: Clearly articulate relationships, differences, and real-world applications (2-3 sentences)
        - Highlight similarities, differences, and concrete examples
        - Difficulty: Medium to hard""",
    
    "edge_case": """Handle exceptions, edge cases, and special situations.
        - Questions: "What happens when X?", "What are edge cases for X?", "When does X fail or not apply?", "What is an exception to X?"
        - Answers: Specific edge cases and exceptions with explanations
        - Include why the case matters
        - Difficulty: Hard""",
    
    "example": """Create worked examples and step-by-step solutions.
        - Questions: "Show an example of X", "Walk through X step by step"
        - Answers: Concrete step-by-step worked examples
        - Difficulty: Medium to hard""",

    "application": """Real-world applications and use cases.
        - Questions: "How is X applied in real life?", "Give a real-world use of X"
        - Answers: Practical applications with context
        - Difficulty: Medium""",
}

def create_groq_client():
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        return Groq(api_key=api_key)
    except ImportError:
        raise ImportError("Groq package not installed. Run: pip install groq")

def create_openai_client():
    try:
        import openai
        return openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except ImportError:
        return None

def generate_cards_with_model(text: str, model: AIModel = AIModel.GROQ, max_cards: int = 15) -> list[dict]:
    if model == AIModel.GROQ:
        return _generate_with_groq(text, max_cards)
    elif model == AIModel.OPENAI:
        return _generate_with_openai(text, max_cards)
    elif model == AIModel.ANTHROPIC:
        return _generate_with_anthropic(text, max_cards)
    else:
        return _generate_with_groq(text, max_cards)

def _generate_with_groq(text: str, max_cards: int = 15) -> list[dict]:
    client = create_groq_client()
    
    max_chars = 12000
    chunks = [text[i:i+max_chars] for i in range(0, min(len(text), 60000), max_chars)]
    
    all_cards = []
    
    for chunk_idx, chunk in enumerate(chunks):
        categories_for_chunk = list(CardCategory.__members__.values())
        
        for category in categories_for_chunk:
            category_name = category.value
            category_prompt = CATEGORY_PROMPTS.get(category_name, "")
            
            prompt = f"""You are an expert educator creating high-quality flashcards.

MATERIAL:
{chunk}

CATEGORY: {category_name.upper()}
{category_prompt}

Generate exactly {max(3, max_cards // 4)} cards for this category. Ensure variety in question styles and difficulty levels.

Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
Each object must have exactly these fields:
- "front": the question string
- "back": the answer string
- "category": "{category_name}"
- "difficulty": one of ["easy", "medium", "hard"]
- "hint": a short hint string (max 10 words)

Example format:
[{{"front": "What is spaced repetition?", "back": "A learning technique...", "category": "{category_name}", "difficulty": "easy", "hint": "Think about timing"}}]"""
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=2048,
                )
                raw = response.choices[0].message.content.strip()
                print(f"[nlp_agent] Groq raw response for {category_name}: {raw[:200]}")
                
                if "```" in raw:
                    raw = re.sub(r"```(?:json)?", "", raw).strip()
                
                match = re.search(r'\[.*\]', raw, re.DOTALL)
                if match:
                    cards = json.loads(match.group())
                    cards = [c for c in cards if all(k in c for k in ["front", "back", "category", "difficulty", "hint"])]
                    all_cards.extend(cards)
                    print(f"[nlp_agent] Got {len(cards)} cards for {category_name}")
                else:
                    print(f"[nlp_agent] No JSON array found in response for {category_name}")
            
            except Exception as e:
                print(f"[nlp_agent] Groq error for {category_name}: {e}")
                continue
    
    return all_cards[:max_cards]

def _generate_with_openai(text: str, max_cards: int = 15) -> list[dict]:
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. pip install openai")
    
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if not client.api_key:
        raise ValueError("OpenAI API key not set.")
    
    max_chars = 8000
    chunks = [text[i:i+max_chars] for i in range(0, min(len(text), 40000), max_chars)]
    all_cards = []
    
    for chunk in chunks:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"""Create {max_cards} high-quality flashcards from this text:

{chunk}

Return ONLY a valid JSON array with fields: front, back, category, difficulty, hint.
Categories: definition, concept, relationship, edge_case"""
                }],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            if "```" in raw:
                raw = re.sub(r"```(?:json)?", "", raw).strip()
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                cards = json.loads(match.group())
                all_cards.extend(cards)
        except Exception as e:
            print(f"[nlp_agent] OpenAI error: {e}")
            continue
    
    return all_cards[:max_cards]

def _generate_with_anthropic(text: str, max_cards: int = 15) -> list[dict]:
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. pip install anthropic")
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    max_chars = 8000
    chunks = [text[i:i+max_chars] for i in range(0, min(len(text), 40000), max_chars)]
    all_cards = []
    
    for chunk in chunks:
        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": f"""Create {max_cards} high-quality flashcards from this text:

{chunk}

Return ONLY a valid JSON array with fields: front, back, category, difficulty, hint.
Categories: definition, concept, relationship, edge_case"""
                }]
            )
            raw = response.content[0].text.strip()
            if "```" in raw:
                raw = re.sub(r"```(?:json)?", "", raw).strip()
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                cards = json.loads(match.group())
                all_cards.extend(cards)
        except Exception as e:
            print(f"[nlp_agent] Anthropic error: {e}")
            continue
    
    return all_cards[:max_cards]

def generate_flashcards_advanced(text: str, preferred_model: str = "groq") -> list[dict]:
    if DEMO_MODE:
        print("[nlp_agent] DEMO_MODE enabled - returning sample cards")
        return _generate_demo_cards()
    
    models_to_try = []
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