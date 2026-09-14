"""Keyword search over the root consolidated knowledge file (data.txt).

The root data.txt uses a lightweight block format:

    <topic title>
    Jurisdiction: India
    fact line one.
    fact line two.
    <blank line>
    <next topic title>
    ...

Blocks are separated by blank lines. The first line is the topic title and,
when present, the second line names the jurisdiction.
"""
import re
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).resolve().parent / "data" / "data.txt"

STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "for", "to", "and", "or",
    "is", "are", "was", "were", "what", "which", "who", "how", "why", "when",
    "does", "do", "did", "can", "could", "should", "would", "with", "about",
    "related", "involving", "any", "me", "my", "please", "tell", "give",
    "benefits", "benefit",
}

_BLOCKS = None  # type: Optional[List[Dict]]  # lazily loaded


def _tokenize(text: str) -> List[str]:
    """Lower-cased word tokens (>=3 chars, ASCII + Devanagari), stopwords removed."""
    return [t for t in re.findall(r"[a-zA-Zऀ-ॿ]{3,}", text.lower()) if t not in STOPWORDS]


def _load_blocks() -> List[Dict[str, str]]:
    """Parse data.txt into a list of {title, jurisdiction, text} blocks."""
    if not DATA_FILE.exists():
        return []
    text = DATA_FILE.read_text(encoding="utf-8", errors="ignore")

    blocks = []
    for raw in re.split(r"\n\s*\n", text):
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if not lines:
            continue
        title = lines[0]
        jurisdiction = "General"
        body_start = 1
        if len(lines) > 1 and lines[1].lower().startswith("jurisdiction:"):
            jurisdiction = lines[1].split(":", 1)[1].strip() or "General"
            body_start = 2
        body = "\n".join(lines[body_start:])
        blocks.append(
            {
                "title": title,
                "jurisdiction": jurisdiction,
                "text": "\n".join([title, body]).strip(),
            }
        )
    return blocks


def _blocks() -> List[Dict[str, str]]:
    global _BLOCKS
    if _BLOCKS is None:
        _BLOCKS = _load_blocks()
    return _BLOCKS


def _jurisdiction_matches(block_jurisdiction: str, jurisdiction: str) -> bool:
    if not jurisdiction or jurisdiction in ("all", "", None):
        return True
    return (
        block_jurisdiction.lower() == jurisdiction.lower()
        or block_jurisdiction == "General"
    )


def search_root_data_txt(
    query: str, top_n: int = None, jurisdiction: str = "all"
) -> List[str]:
    """Return up to top_n matching block texts for a keyword query.

    Scoring: keyword overlap with the block title counts 3x, overlap with
    the body counts 1x. Blocks whose jurisdiction matches the requested
    filter (or are 'General') are eligible.
    """
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return []

    scored = []
    for block in _blocks():
        if not _jurisdiction_matches(block["jurisdiction"], jurisdiction):
            continue
        title_tokens = set(_tokenize(block["title"]))
        body_tokens = set(_tokenize(block["text"]))
        score = 3 * len(q_tokens & title_tokens) + len(q_tokens & body_tokens)
        if score > 0:
            scored.append((score, block))

    scored.sort(key=lambda pair: -pair[0])
    return [block["text"] for _, block in scored[:top_n]]


def reload_root_data() -> None:
    """Force a re-read of data.txt (used after corpus updates)."""
    global _BLOCKS
    _BLOCKS = None