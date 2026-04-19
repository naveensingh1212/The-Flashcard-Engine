# 🃏 The Flashcard Engine

An AI-powered flashcard generator that transforms any PDF into smart study cards using spaced repetition learning.

**Live Demo:** https://the-flashcard-engine-dusky.vercel.app  
**Backend API:** https://flashcard-engine-backend-lz8a.onrender.com

---

## 🚀 What It Does

Upload any PDF → AI reads it → generates categorized flashcards → study with spaced repetition

- 📄 **PDF Upload** → extracts and parses text intelligently
- 🤖 **AI Generation** → Groq LLaMA 3.3 creates flashcards across 6 categories
- 🧠 **SM-2 Algorithm** → schedules reviews based on how well you remember
- 📊 **Progress Tracking** → mastery levels, due cards, water cube visualization
- 🗂️ **4 Card Categories** → Key Concepts, Definitions, Relationships, Edge Cases

---

## 🏗️ Tech Stack

### Frontend
- React + Vite
- Custom CSS animations
- Deployed on **Vercel**

### Backend
- FastAPI (Python)
- SQLite database
- PyMuPDF for PDF parsing
- Groq API (LLaMA 3.3 70B) for card generation
- SM-2 spaced repetition algorithm
- Deployed on **Render** (Docker)

---

## 🧠 How It Works
PDF Upload
↓
Parser Agent (PyMuPDF)
→ extracts text, headers, tables, lists
↓
NLP Agent (Groq LLaMA 3.3)
→ generates 15 flashcards across 6 categories
↓
Validator Agent
→ removes duplicates, checks quality
↓
Database (SQLite)
→ stores cards with SM-2 scheduling
↓
Frontend
→ study session with spaced repetition

---

## 📁 Project Structure
The Flashcard Engine/
├── backend/
│   ├── main.py              # FastAPI routes
│   ├── parser_agent.py      # PDF text extraction
│   ├── nlp_agent.py         # AI card generation
│   ├── validator_agent.py   # Card quality checks
│   ├── database.py          # SQLite operations
│   ├── sm2.py               # Spaced repetition algorithm
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
├── src/
│   ├── pages/
│   │   ├── Home.jsx     # Main dashboard
│   │   └── Study.jsx    # Study session
│   ├── components/
│   │   ├── NavBar.jsx
│   │   ├── SectionCard.jsx
│   │   ├── MiniCard.jsx
│   │   ├── UploadModal.jsx
│   │   ├── WorkedExamplesPage.jsx
│   │   └── WaterCube.jsx
│   └── api/
│       └── client.js    # API calls
└── package.json

---

## 🔧 Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
# Create .env file with:
# GROQ_API_KEY=your_key_here
uvicorn main:app --reload --port 10000
```

### Frontend
```bash
cd frontend
npm install
# Create .env file with:
# VITE_API_URL=http://localhost:10000
npm run dev
```

---

## 🎯 Card Categories

| Category | Description |
|----------|-------------|
| 🧠 Key Concepts | Core principles and how things work |
| 📖 Definitions | What terms mean |
| 🔗 Relationships | How concepts connect |
| ⚡ Edge Cases | Exceptions and special situations |
| 💡 Examples | Worked step-by-step solutions |
| 🌍 Applications | Real-world use cases |

---

## 📈 SM-2 Spaced Repetition

Cards are scheduled using the SM-2 algorithm:
- **Again** → review tomorrow
- **Hard** → review in 1-2 days  
- **Good** → review in 3-5 days
- **Easy** → review in 7+ days

Mastery levels: 🌱 New → 📚 Learning → 🔄 Reviewing → ⭐ Mastered

---

## ⚡ Key Design Decisions

- **SQLite over PostgreSQL** → zero config, perfect for MVP
- **Groq over OpenAI** → faster inference, generous free tier
- **Single prompt generation** → saves tokens, one API call per upload
- **Docker on Render** → avoids dependency issues (PyMuPDF, tiktoken)
- **SM-2 algorithm** → proven spaced repetition, better than random review

---

## 🔮 Future Improvements

- PostgreSQL for persistent storage across deployments
- User authentication and personal decks
- Image/diagram support in PDFs
- Mobile app
- Export cards to Anki format
- Collaborative decks

---

## 👨‍💻 Built By

Naveen Singh 
