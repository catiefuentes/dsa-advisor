import json
from pathlib import Path
from typing import List, Dict

# Buckets (edit if your program rules change)
REQUIRED_SET = {"CIS 512", "CIS 600", "MAT 646", "MAT 616", "DSA 688"}
PLUS_OPTIONS = {"PSM 601", "PSM 602"}  # one of these must satisfy PLUS

class Advisor:
    def __init__(self, catalog_path: str = "data/course_catalog.json"):
        catalog_list = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
        # Quick lookup by course code
        self.catalog: Dict[str, Dict] = {c["code"]: c for c in catalog_list}

    def _credits(self, codes: List[str]) -> int:
        return sum(self.catalog[c]["credits"] for c in codes if c in self.catalog)

    def audit(self, completed: List[str]) -> Dict:
        completed_set = set(completed)

        # Required
        required_done = sorted(list(REQUIRED_SET & completed_set))
        required_missing = sorted(list(REQUIRED_SET - completed_set))

        # PLUS requirement
        plus_done_all = sorted(list(PLUS_OPTIONS & completed_set))
        has_plus = len(plus_done_all) >= 1
        plus_done = plus_done_all[:1]  # count at most one toward PLUS
        plus_missing = [] if has_plus else sorted(list(PLUS_OPTIONS))
        used_for_plus = plus_done[0] if has_plus else None

        # Electives: anything else in catalog not already counted as required/PLUS
        electives_taken: List[str] = []
        for c in completed_set:
            if c not in self.catalog:
                continue
            if c in REQUIRED_SET:
                continue
            if c in PLUS_OPTIONS and c == used_for_plus:
                continue
            electives_taken.append(c)

        # Credits
        required_credits = self._credits(required_done)
        if used_for_plus:
            required_credits += self.catalog[used_for_plus]["credits"]
        elective_credits = self._credits(electives_taken)
        total_credits = required_credits + elective_credits

        return {
            "required_done": required_done,
            "required_missing": required_missing,
            "plus_done": plus_done,
            "plus_missing": plus_missing,
            "electives_taken": electives_taken,
            "required_credits": required_credits,
            "elective_credits": elective_credits,
            "total_credits": total_credits,
            "needs": {
                "required_remaining_cr": max(0, 18 - required_credits),
                "electives_remaining_cr": max(0, 12 - elective_credits),
                "program_remaining_cr": max(0, 30 - total_credits),
            },
        }

    def suggest_next(self, completed: List[str],
                     interest_tags: List[str],
                     top_k: int = 6) -> List[Dict]:
        completed_set = set(completed)
        suggestions: List[Dict] = []

        # Priority 1 — missing required
        for code in (REQUIRED_SET - completed_set):
            if code in self.catalog:
                suggestions.append({"priority": 1, **self.catalog[code]})

        # Priority 1 — missing PLUS
        if len(PLUS_OPTIONS & completed_set) == 0:
            for code in ["PSM 601", "PSM 602"]:
                if code in self.catalog:
                    suggestions.append({"priority": 1, **self.catalog[code]})

        # Priority 2/3 — electives ranked by interest tag overlap
        interest_set = set(t.strip().lower() for t in interest_tags if t.strip())
        for c in self.catalog.values():
            code = c["code"]
            if code in completed_set or code in REQUIRED_SET or code in PLUS_OPTIONS:
                continue
            tags = set(map(str.lower, c.get("tags", [])))
            match = len(interest_set & tags)
            priority = 2 if match > 0 else 3
            suggestions.append({"priority": priority, "match": match, **c})

        # Rank: priority, then match desc, then title
        suggestions.sort(key=lambda x: (x["priority"], -x.get("match", 0), x["title"]))

        # De-dup & trim
        out, seen = [], set()
        for s in suggestions:
            if s["code"] in seen:
                continue
            out.append(s)
            seen.add(s["code"])
            if len(out) >= top_k:
                break
        return out
