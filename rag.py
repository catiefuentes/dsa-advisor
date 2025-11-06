import os
import json
from pathlib import Path
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Optional: lightly polish with OpenAI after retrieval.
# Leave False to run fully local. Flip to True *and* set OPENAI_API_KEY to use.
USE_OPENAI = False and bool(os.getenv("OPENAI_API_KEY"))

if USE_OPENAI:
    from openai import OpenAI
    oai_client = OpenAI()


class MiniRAG:
    def __init__(self, data_dir: str = "data"):
        self.docs: List[str] = []
        self.sources: List[str] = []

        # Load program rules (markdown blob)
        rules_path = Path(data_dir, "program_rules.md")
        rules_text = rules_path.read_text(encoding="utf-8")
        self.docs.append(rules_text)
        self.sources.append("program_rules.md")

        # Load course catalog and add each course as a separate doc
        catalog = json.loads(Path(data_dir, "course_catalog.json")
                            .read_text(encoding="utf-8"))
        for c in catalog:
            blob = (
                f"{c['code']} — {c['title']} ({c['credits']} cr)\n"
                f"{c['desc']}\n"
                f"Tags: {', '.join(c.get('tags', []))}"
            )
            self.docs.append(blob)
            self.sources.append(c["code"])

        # Build TF-IDF index
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.docs)

    def retrieve(self, query: str, k: int = 4) -> List[Dict]:
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix)[0]
        idxs = sims.argsort()[::-1][:k]
        out: List[Dict] = []
        for i in idxs:
            out.append({
                "source": self.sources[i],
                "score": float(sims[i]),
                "text": self.docs[i],
            })
        return out

    def answer(self, query: str) -> Dict:
        ctx = self.retrieve(query, k=5)
        joined = "\n\n---\n\n".join(x["text"] for x in ctx)

        if USE_OPENAI:
            prompt = (
                "You are an academic advisor. Answer clearly using ONLY the info "
                "in the context.\n\n"
                f"Context:\n{joined}\n\n"
                f"Question: {query}\n\nAnswer:"
            )
            resp = oai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            text = resp.choices[0].message.content
        else:
            # Local heuristic: list the first line from each top doc
            lines = []
            for d in ctx:
                first_line = d["text"].split("\n")[0]
                lines.append(f"- {first_line}")
            text = "\n".join(lines) + \
                   "\n\n(Enable OpenAI in rag.py for polished answers.)"

        return {"answer": text, "context": ctx}
