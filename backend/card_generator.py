import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def generate_flashcards(text: str) -> list[dict]:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    max_chars = 12000
    chunks = [text[i:i+max_chars] for i in range(0, min(len(text), 60000), max_chars)]

    all_cards = []

    for chunk in chunks:
        prompt = f"""You are an expert educator. Create high-quality flashcards from the study material below.

MATERIAL:
{chunk}

Rules:
- Cover key concepts, definitions, relationships, examples, edge cases
- Questions must be specific and testable (not vague like "What is this about?")
- Answers should be concise but complete (1-3 sentences)
- Include worked examples if they appear in the material
- Ask "why" and "how" questions, not just "what"

Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
Each object must have exactly these fields:
- "front": the question string
- "back": the answer string  
- "category": one of ["definition", "concept", "example", "relationship", "application"]
- "difficulty": one of ["easy", "medium", "hard"]
- "hint": a short hint string (max 10 words)

Generate 8-15 cards. Example:
[{{"front": "What is spaced repetition?", "back": "A learning technique that schedules reviews at increasing intervals to maximize retention.", "category": "definition", "difficulty": "easy", "hint": "Think about timing of reviews"}}]"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            raw = response.choices[0].message.content.strip()

            if "```" in raw:
                raw = re.sub(r"```(?:json)?", "", raw).strip()

            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                cards = json.loads(match.group())
                all_cards.extend(cards)

        except Exception as e:
            print(f"[card_generator] Error on chunk: {e}")
            continue

    return all_cards