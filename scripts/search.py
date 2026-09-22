"""Search published notes locally and print a bounded, source-linked result."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

from public_paths import public_note_path

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {"ventas": "sales", "soporte": "support", "memoria": "memory",
           "crear": "create", "aprobaciones": "approvals", "coste": "token",
           "costos": "token", "equipo": "team", "campaña": "campaign",
           "campañas": "campaign", "prospectos": "prospecting", "datos": "data",
           "verificar": "verification", "lanzamiento": "launch", "guia": "guide"}


def tokens(text: str) -> set[str]:
    found = set(re.findall(r"[\w]+", text.lower()))
    return found | {ALIASES[x] for x in found if x in ALIASES}


def search(query: str, kind: str, limit: int, max_chars: int) -> list[dict]:
    catalog = json.loads((ROOT / "knowledge/catalog.json").read_text(encoding="utf-8"))
    terms = tokens(query)
    docs = []
    for item in catalog["documents"]:
        if kind != "all" and item["kind"] != kind:
            continue
        path = public_note_path(ROOT, item["path"], kind=item["kind"])
        body = path.read_text(encoding="utf-8")
        docs.append((item, body, tokens(body)))
    weights = {t: 1 + math.log((1 + len(docs)) / (1 + sum(t in d[2] for d in docs))) for t in terms}
    ranked = []
    for item, body, found in docs:
        matching = terms & found
        if not matching:
            continue
        title = tokens(item["title"] + " " + Path(item["path"]).stem.replace("-", " "))
        score = sum(weights[t] * (4 if t in title else 1) for t in matching)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body)
                      if p.strip() and not p.startswith("---")
                      and not re.fullmatch(r"#{1,6} [^\n]+", p.strip())]
        best = max(paragraphs, key=lambda p: sum(weights[t] for t in terms & tokens(p)), default=body)
        excerpt = best
        if len(best) > max_chars:
            excerpt = best[:max_chars - 1]
            if " " in excerpt:
                excerpt = excerpt.rsplit(" ", 1)[0]
            excerpt = excerpt.rstrip() + "…"
        ranked.append((score, {"path": item["path"], "title": item["title"],
                               "words": item["words"], "excerpt": excerpt}))
    return [x[1] for x in sorted(ranked, key=lambda x: (-x[0], x[1]["path"]))[:limit]]


def main() -> int:
    # Windows consoles/pipes may default to cp1252, which cannot encode the
    # arrows and other Unicode text present in the event notes and JSON.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", nargs="+", help="words or a short question; English or common Spanish task terms")
    p.add_argument("--kind", choices=("canon", "session", "timelines", "all"), default="canon")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--max-chars", type=int, default=900, help="maximum excerpt characters per result")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if not 1 <= args.limit <= 20 or not 80 <= args.max_chars <= 4000:
        p.error("--limit must be 1–20; --max-chars must be 80–4000")
    try:
        results = search(" ".join(args.query), args.kind, args.limit, args.max_chars)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f"Search failed: {exc}\n")
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f"{item['title']}\n{item['path']} ({item['words']} words)\n{item['excerpt']}\n")
        if not results:
            print("No match. Try knowledge/ROUTES.md or --kind all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
