from flask import Flask, render_template, request
from advise_logic import Advisor
from rag import MiniRAG

app = Flask(__name__)
advisor = Advisor()
rag = MiniRAG()

# Load catalog codes for checkboxes
from pathlib import Path
import json
CATALOG = json.loads(Path("data/course_catalog.json").read_text(encoding="utf-8"))
CODES = [c["code"] for c in CATALOG]

@app.route("/")
def index():
    return render_template("index.html", codes=CODES)

@app.route("/advise", methods=["POST"])
def advise():
    completed = request.form.getlist("completed")
    interests = request.form.get("interests", "").lower().split(",")
    interests = [t.strip() for t in interests if t.strip()]
    question = request.form.get("question", "")

    audit = advisor.audit(completed)
    suggestions = advisor.suggest_next(completed, interests)

    rag_answer = None
    if question.strip():
        rag_answer = rag.answer(question)

    return render_template(
        "result.html",
        completed=completed,
        interests=interests,
        audit=audit,
        suggestions=suggestions,
        rag_answer=rag_answer
    )

if __name__ == "__main__":
    app.run(debug=True, port=5050)
