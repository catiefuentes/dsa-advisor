# DSA Advisor – Degree Audit + Course Planning + RAG Assistant

This application helps students in the **M.S. in Data Science & Analytics program at Buffalo State** determine:

1. **Which courses they have already completed**
2. **What degree requirements remain**
3. **Which courses are recommended next**
4. **Answers to program questions** using a small **RAG (Retrieval-Augmented Generation)** knowledge base

The tool provides a **clear degree audit**, identifies **missing required courses**, **PLUS requirement completion**, and **elective credit progress**, then suggests next courses based on **interests** (e.g., *ml, databases, viz, gis, governance*).

---

## 🧠 Features

| Feature | Description |
|--------|-------------|
| Degree Audit | Checks progress toward 30-credit requirement (Required + PLUS + Electives) |
| Course Recommendations | Suggests required/PLUS first, then electives prioritized by interest tags |
| RAG Search | Lets you ask questions (“What do I still need to graduate?”) using program documents |
| Fully Local | Works with TF-IDF retrieval only (no external API required) |
| Optional LLM | Can optionally use OpenAI API to improve answer quality |

---

## 🗂 Project Structure

dsa_advisor/
├─ app.py # Flask web server
├─ advise_logic.py # Degree audit + course recommendation logic
├─ rag.py # Lightweight RAG system (TF-IDF retrieval)
├─ requirements.txt
├─ data/
│ ├─ program_rules.md # Program outline / guidance text
│ └─ course_catalog.json # List of courses, credits, categories, tags
└─ templates/
├─ base.html
├─ index.html # Input form for completed courses + interests
└─ result.html # Degree audit + recommendations + RAG output

---

## 🚀 Running the App

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
export FLASK_APP=app:app
flask run --port 5050