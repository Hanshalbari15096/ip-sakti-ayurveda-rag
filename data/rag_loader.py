"""RAG data loader for IP-SAKTI Ayurveda IPR Assistant.

Loads knowledge from the data folder, chunks the text, and populates
the ChromaDB vector store with metadata for source attribution.
"""
import os
import re
import json
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
try:
    from .config import config
except ImportError:
    from config import config

# Message digest of every data/*.txt file, written next to the vector store so
# the collection is rebuilt automatically whenever the corpus changes. The
# digest key is the data-file path and the value is its SHA-1 (fast and
# adequate for freshness detection; not a security boundary).
MANIFEST_FILENAME = "corpus_manifest.json"


def compute_corpus_manifest(data_dir: str = "data") -> Dict[str, str]:
    """Map every .txt file under data_dir to a SHA-1 digest."""
    base = Path(data_dir)
    manifest = {}
    if base.exists():
        for txt_path in sorted(base.rglob("*.txt")):
            try:
                manifest[str(txt_path.relative_to(base))] = hashlib.sha1(
                    txt_path.read_bytes()
                ).hexdigest()
            except OSError:
                continue
    return manifest


def load_stored_manifest(persist_dir: str) -> Dict[str, str]:
    path = Path(persist_dir) / MANIFEST_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


FOLDER_CATEGORIES = {
    "ip_statutes": "IP Statute",
    "drug_regulations": "Drug Regulation",
    "formulation_classification": "Formulation Classification",
    "gi_registry": "Geographical Indication",
    "case_law": "Case Law",
    "abs_compliance": "Access & Benefit Sharing",
    "herbs": "Ayurvedic Herb",
    "international_treaties": "International Treaty",
}

TOP_LEVEL_FILES = {
    "ayurveda_overview.txt": "Ayurveda Overview",
    "herbs.txt": "Ayurvedic Herb",
    "data.txt": "Consolidated Knowledge Base",
}

# Files whose content carries explicit JURISDICTION: markers we can parse.
# (Everything is parsed anyway; unknown blocks default to "General".)
JURISDICTION_RE = re.compile(
    r"^\s*(?:jurisdiction|international)\s*[:\-]\s*(india|international)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def detect_jurisdiction(text: str, category: str) -> str:
    """Detect jurisdiction from explicit markers in a chunk of text."""
    match = JURISDICTION_RE.search(text)
    if match:
        return match.group(1).capitalize()
    lowered = text[:400].lower()
    if "jurisdiction: india" in lowered:
        return "India"
    if "jurisdiction: international" in lowered:
        return "International"
    return "General"


def discover_data_files(data_dir: str = "data") -> List[Dict[str, str]]:
    """Discover all .txt data files in the data folder and subfolders."""
    base = Path(data_dir)
    if not base.exists():
        return []

    discovered = []
    for txt_path in base.rglob("*.txt"):
        relative = txt_path.relative_to(base)
        category = "General"
        parts = relative.parts

        if parts[0] in FOLDER_CATEGORIES:
            category = FOLDER_CATEGORIES[parts[0]]
        elif parts[0] in TOP_LEVEL_FILES:
            category = TOP_LEVEL_FILES[parts[0]]

        discovered.append({
            "path": str(txt_path),
            "category": category,
            "filename": txt_path.name,
        })

    return discovered


def chunk_text(text: str, chunk_size: int, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for vector storage."""
    chunks = []
    if not text or not text.strip():
        return chunks

    text = text.strip()
    step = max(1, chunk_size - overlap)
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def load_text_file(file_path: str) -> str:
    """Load a single text file with UTF-8 encoding."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def build_knowledge_base(data_dir: str = "data") -> List[Dict]:
    """Build a list of chunked knowledge base entries with metadata."""
    knowledge = []
    files = discover_data_files(data_dir)

    if not files:
        print(f"[RAG Loader] No data files found in {data_dir}")
        return knowledge

    for file_info in files:
        path = file_info["path"]
        category = file_info["category"]
        try:
            text = load_text_file(path)
        except Exception as e:
            print(f"[RAG Loader] Failed to read {path}: {e}")
            continue

        chunks = chunk_text(text, config.chunk_size, overlap=50)
        for idx, chunk in enumerate(chunks):
            knowledge.append({
                "text": chunk,
                "category": category,
                "source": file_info["filename"],
                "source_path": path,
                "chunk_index": idx,
                "jurisdiction": detect_jurisdiction(chunk, category),
            })

    print(f"[RAG Loader] Loaded {len(knowledge)} chunks from {len(files)} files")
    return knowledge


class RAGStore:
    """Wrapper around ChromaDB collection for the RAG system."""

    def __init__(self, persist_dir: str = "./my_db", collection_name: Optional[str] = None):
        self.persist_dir = persist_dir
        self.collection_name = collection_name or config.collection_name
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_fn,
        )

    def populate(self, data_dir: str = "data", force: bool = False) -> int:
        """Populate the vector store from the data folder.

        Rebuilds when (a) forced, (b) the corpus manifest differs from the
        stored one (any data/*.txt changed, added or removed), or (c) a
        legacy collection predates the jurisdiction metadata field.
        """
        current_manifest = compute_corpus_manifest(data_dir)
        stored_manifest = load_stored_manifest(self.persist_dir)
        manifest_changed = current_manifest != stored_manifest

        needs_rebuild = force
        if not needs_rebuild and manifest_changed:
            print(
                "[RAG Store] Corpus changed "
                f"({len(stored_manifest)}->{len(current_manifest)} files) — rebuilding."
            )
            needs_rebuild = True

        if not needs_rebuild and self.collection.count() > 0:
            # Rebuild automatically when the existing store lacks the
            # jurisdiction metadata field (schema upgrade).
            stats = self.get_stats()
            if not stats.get("jurisdiction_metadata"):
                print("[RAG Store] Existing collection lacks jurisdiction metadata — rebuilding.")
                needs_rebuild = True
            elif stored_manifest:
                print(f"[RAG Store] Collection already has {self.collection.count()} documents (corpus unchanged)")
                return 0
            else:
                print(
                    f"[RAG Store] Collection already has {self.collection.count()} documents "
                    "(no stored manifest; assuming current)"
                )
                self._save_manifest(current_manifest)
                return 0

        if needs_rebuild:
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embed_fn,
            )

        knowledge = build_knowledge_base(data_dir)
        if not knowledge:
            return 0

        documents = [item["text"] for item in knowledge]
        ids = [f"{item['source_path'].replace('/','_').replace('\\','_')}_chunk_{item['chunk_index']}" for item in knowledge]
        metadatas = [
            {
                "category": item["category"],
                "source": item["source"],
                "source_path": item["source_path"],
                "jurisdiction": item["jurisdiction"],
            }
            for item in knowledge
        ]

        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)
        self._save_manifest(current_manifest)
        print(f"[RAG Store] Added {len(documents)} documents to collection")
        return len(documents)

    def _save_manifest(self, manifest: Dict[str, str]) -> None:
        """Persist the corpus manifest next to the vector store."""
        try:
            path = Path(self.persist_dir) / MANIFEST_FILENAME
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        except OSError as e:
            print(f"[RAG Store] Could not write corpus manifest: {e}")

    def query(self, query_text: str, top_k: Optional[int] = None, jurisdiction: str = "all") -> Dict:
        """Query the vector store for relevant chunks.

        jurisdiction: "all" (no filter), "India"/"india", or
        "International"/"international". Chunks labelled "General" (no
        explicit jurisdiction marker) are always included alongside the
        jurisdiction-specific hits, so unknown-jurisdiction content is
        never dropped.
        """
        n = top_k or config.top_k
        if jurisdiction and jurisdiction not in ("all", "", None):
            jur = jurisdiction.strip().capitalize()
            # Prefer the jurisdiction-specific chunks, but always keep
            # "General" chunks (no explicit marker) in the result set.
            where = {"$or": [{"jurisdiction": jur}, {"jurisdiction": "General"}]}
            try:
                result = self.collection.query(
                    query_texts=[query_text],
                    n_results=n,
                    where=where,
                )
                if result.get("documents", [[]])[0]:
                    return result
            except Exception as e:
                print(f"[RAG Store] jurisdiction filter failed ({e}); querying without filter")
        return self.collection.query(query_texts=[query_text], n_results=n)

    def get_stats(self) -> Dict:
        """Return statistics about the vector store."""
        count = self.collection.count()
        categories = set()
        sources = set()
        jurisdictions = set()
        has_jurisdiction_meta = False
        if count > 0:
            peek = self.collection.peek(limit=min(count, 500))
            for meta in peek.get("metadatas", []):
                if meta:
                    categories.add(meta.get("category", "Unknown"))
                    sources.add(meta.get("source", "Unknown"))
                    if "jurisdiction" in meta:
                        has_jurisdiction_meta = True
                        jurisdictions.add(meta.get("jurisdiction", "General"))
        return {
            "total_documents": count,
            "categories": sorted(categories),
            "sources": sorted(sources),
            "jurisdictions": sorted(j for j in jurisdictions if j),
            "jurisdiction_metadata": has_jurisdiction_meta,
        }


def initialize_rag(data_dir: str = "data", force: bool = False) -> RAGStore:
    """Initialize the RAG store and populate it from the data folder."""
    store = RAGStore()
    store.populate(data_dir=data_dir, force=force)
    return store
