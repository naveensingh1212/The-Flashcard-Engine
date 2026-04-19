# Backend Refactoring - Agent-Based Architecture

## 🏗️ New Architecture Overview

Your backend has been refactored into a **modular agent system** for better scalability, maintainability, and quality:

```
PDF Upload
    ↓
[Parser Agent] → Extract text, metadata, tables, lists, structure
    ↓
[Validator Agent] → Validate PDF text quality
    ↓
[NLP Agent] → Generate cards with category-specific prompts
    ↓
[Validator Agent] → Validate, clean, deduplicate cards
    ↓
Database → Store enriched deck + cards with quality metrics
```

---

## 📦 New Agents Created

### 1. **Parser Agent** (`parser_agent.py`)
**Purpose**: Enhanced PDF extraction with structure preservation

**Features**:
- ✅ Metadata extraction (title, author, pages, dates)
- ✅ Structure preservation (headers, sections, page markers)
- ✅ Table detection and extraction
- ✅ List extraction (bullets, numbered)
- ✅ Intelligent text prioritization
- ✅ Handles complex PDFs better than simple text extraction

**Key Functions**:
- `parse_pdf_enhanced()` - Main parsing function
- `extract_metadata()` - Get PDF metadata
- `preserve_structure()` - Mark headers and sections
- `extract_tables()` - Detect table content
- `extract_lists()` - Extract bullet/numbered lists
- `get_best_text_for_generation()` - Prioritize content for AI

---

### 2. **NLP Agent** (`nlp_agent.py`)
**Purpose**: Advanced card generation with multiple AI models

**Features**:
- ✅ **Category-specific prompts** for each card type:
  - `definition` - Precise definitions and terminology
  - `concept` - Core principles and explanations
  - `example` - Concrete, practical examples
  - `relationship` - Connections between concepts
  - `application` - Real-world use cases
  - `edge_case` - Exceptions and special situations
- ✅ **Multi-model support**:
  - Groq (LLaMA 3 70B) - Fast, free tier available
  - OpenAI (GPT-4 Turbo) - Powerful and detailed
  - Anthropic (Claude 3 Opus) - Creative and nuanced
- ✅ **Automatic fallback** between models if one fails
- ✅ Better temperature tuning (0.3-0.4 for consistency)
- ✅ Chunk-based processing for large PDFs

**Key Functions**:
- `generate_flashcards_advanced()` - Main entry point with model selection
- `generate_cards_with_model()` - Generates using specific model
- Category-specific generators: `_generate_with_groq()`, `_generate_with_openai()`, `_generate_with_anthropic()`

**Environment Variables**:
```env
GROQ_API_KEY=your_key          # Primary (default)
OPENAI_API_KEY=your_key         # Fallback 1
ANTHROPIC_API_KEY=your_key      # Fallback 2
PREFERRED_AI_MODEL=groq         # Which to try first (groq|openai|anthropic)
```

---

### 3. **Validator Agent** (`validator_agent.py`)
**Purpose**: Quality assurance and data validation

**Features**:
- ✅ **Individual card validation**:
  - Required fields check
  - Content length validation (5-500 chars for questions)
  - Type checking and normalization
  - Duplicate detection (82% similarity threshold)
  - Generic question detection and rejection
- ✅ **Batch validation** with detailed reporting
- ✅ **PDF text validation** before generation
- ✅ **Quality metrics**:
  - Success rate percentage
  - Invalid card count
  - Duplicates removed
  - Warnings and errors logged
- ✅ **Card cleaning**:
  - Whitespace normalization
  - Markdown removal
  - Line break standardization
  - Hint truncation

**Key Functions**:
- `validate_cards_batch()` - Validate multiple cards
- `is_valid_card()` - Validate single card
- `remove_duplicates()` - Detect and remove duplicates
- `validate_pdf_text()` - Check PDF extraction quality
- `generate_quality_report()` - Create detailed report

**Validation Rules**:
- Questions: 5-500 characters, must be specific (not generic)
- Answers: 10-2000 characters
- Hints: max 15 words
- Categories: must be one of 6 valid types
- Difficulty: easy, medium, or hard
- No question-answer duplicates (82%+ similarity)

---

## 🔄 Updated Upload Flow

### Request: `POST /decks/upload`
```json
{
  "file": "document.pdf",
  "deck_name": "Optional deck name"
}
```

### Response: Enhanced with metadata and quality metrics
```json
{
  "deck": {
    "id": "uuid",
    "name": "Document Title",
    "total_cards": 42,
    "mastery_counts": {...}
  },
  "cards": [
    {
      "id": "uuid",
      "front": "What is spaced repetition?",
      "back": "A learning technique that schedules reviews...",
      "category": "definition",
      "difficulty": "easy",
      "hint": "Think about review timing",
      ...
    }
  ],
  "metadata": {
    "pdf_title": "Extracted from PDF",
    "pdf_pages": 45,
    "cards_generated": 42,
    "quality_report": {
      "valid_cards": 42,
      "invalid_cards": 0,
      "duplicates_removed": 2,
      "success_rate": 100.0,
      "warnings": []
    }
  }
}
```

---

## 🎯 Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **PDF Parsing** | Basic text extraction | Structure-aware with metadata |
| **Card Generation** | Single model (Groq) | 3 models with auto-fallback |
| **Quality Control** | Minimal validation | Comprehensive QA with metrics |
| **Error Handling** | Basic try-catch | Detailed error reports |
| **Card Variety** | Generic prompts | Category-specific prompts |
| **Duplicates** | Not handled | Automatically removed |
| **Metadata** | None | PDF title, pages, dates |

---

## 📝 Environment Setup

Create a `.env` file in the backend directory:

```env
# Database
DB_PATH=flashcards.db

# API Keys (at least one required)
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Preference (default: groq)
PREFERRED_AI_MODEL=groq

# Server
PORT=10000
```

---

## 🚀 Installation

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn main:app --reload --port 10000
```

---

## 📊 Quality Metrics

Each upload generates a quality report with:
- **Total Processed**: Cards generated by AI
- **Valid Cards**: After validation
- **Invalid Cards**: Rejected due to quality issues
- **Duplicates Removed**: Near-duplicate cards merged
- **Final Count**: Cards saved to database
- **Success Rate**: Percentage of valid cards
- **Warnings**: Specific issues found

---

## 🔧 Advanced Usage

### Switch AI Model for a Request

The system tries models in this order:
1. `PREFERRED_AI_MODEL` (env variable)
2. Alternative models (if first fails)
3. Falls back through: Groq → OpenAI → Anthropic

### Force a Specific Model

Update `PREFERRED_AI_MODEL` in `.env` before upload.

### Monitor Generation Quality

Check the quality_report in the response to see:
- How many cards passed validation
- What validation errors occurred
- Whether duplicates were removed

---

## 🛠️ Future Enhancements

Potential improvements:
1. **Image extraction** from PDFs (OCR support)
2. **Caching** of frequently generated card patterns
3. **User feedback loop** to improve AI prompts
4. **Custom validation rules** per deck
5. **Batch processing** for multiple PDFs
6. **Card difficulty auto-adjustment** based on review history
7. **Export to Anki/Quizlet** format

---

## 📞 Support

If cards aren't generating:
1. Check `.env` has at least one valid API key
2. Verify PDF has readable text (not scanned image)
3. Check quality_report in response for specific issues
4. Try different `PREFERRED_AI_MODEL`
5. Check terminal logs for detailed error messages

