"""RAG data loader for IP-SAKTI Ayurveda IPR Assistant.

Loads knowledge from the data folder, chunks the text, and populates
the ChromaDB vector store with metadata for source attribution.
"""
import os
import re
import json
import math
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
try:
    from .config import config
except ImportError:
    from config import config

# --- Hybrid (dense + BM25) support -------------------------------------------
#
# Chroma 1.5.9's sparse-collection path is unusable on this platform (the
# chroma_bm25.json config schema is not shipped in the wheel, so any sparse
# collection creation fails in the Rust backend). Hybrid retrieval therefore
# scores the corpus with an in-memory classic BM25 over the same chunked
# documents and RRF-fuses that ranking with the dense ANN. Same two-rank-list
# design the sparse collection would have used, zero extra dependencies, and
# fast enough for a ~350-chunk corpus (sub-millisecond per query).
RRF_K = 60
BM25_CANDIDATES_MULT = 3   # sparse pool = top_k * this (bounded recall boost)
BM25_SYNTH_DIST_SCALE = 1.05  # distance for a BM25-only hit (just below worst dense)

_ALNUM_RE = re.compile(r"[a-zA-Zऀ-ॿ]+|\d+", re.UNICODE)


def _bm25_tokens(text: str) -> List[str]:
    """Lower-cased alnum tokens (Latin + Devanagari + digits), length >= 2."""
    return [t.lower() for t in _ALNUM_RE.findall(text) if len(t) >= 2]


def chunk_id(source_path: str, chunk_index: int) -> str:
    """Document id format shared by dense collection and BM25 index."""
    return f"{source_path.replace('/', '_').replace('\\\\', '_')}_chunk_{chunk_index}"


class InMemoryBM25:
    """Classic BM25 (Robertson/Sparck-Jones) over a fixed corpus.

    Precomputes per-document term frequencies, lengths, and IDF so each query
    is a single sweep scoring every document. Items carry (id, text, meta);
    jurisdiction filtering mirrors the dense collection's where-clause.
    """

    def __init__(self, items: List[tuple], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.ids = [it[0] for it in items]
        self.texts = [it[1] for it in items]
        self.metas = [it[2] for it in items]
        try:
            self.jurs = [it[3] for it in items]
        except IndexError:
            self.jurs = ["General"] * len(items)

        df: Dict[str, int] = {}
        self.docs: List[Dict[str, int]] = []
        self.doc_len: List[int] = []
        for _, text, *_ in items:
            toks = _bm25_tokens(text)
            self.doc_len.append(len(toks))
            tf: Dict[str, int] = {}
            for tok in toks:
                tf[tok] = tf.get(tok, 0) + 1
            self.docs.append(tf)
            for tok in tf:
                df[tok] = df.get(tok, 0) + 1
        self.df = df
        n = len(self.docs)
        self.n = n
        self.avgdl = (sum(self.doc_len) / n) if n else 1.0

    def score(self, query: str, jurisdiction: str = "all") -> Dict[str, float]:
        """Return {doc_id: bm25_score} for all docs matching the jurisdiction."""
        q_toks = set(_bm25_tokens(query))
        if not q_toks:
            return {}
        if jurisdiction and jurisdiction not in ("all", "", None):
            jur = jurisdiction.strip().capitalize()
        else:
            jur = "all"
        k1, b, n = self.k1, self.b, self.n
        avgdl = self.avgdl or 1.0
        out: Dict[str, float] = {}
        for di, tf in enumerate(self.docs):
            if jur != "all" and self.jurs[di] not in (jur, "General"):
                continue
            dl = self.doc_len[di] or 1
            s = 0.0
            for tok in q_toks:
                f = tf.get(tok, 0)
                if not f:
                    continue
                freq = self.df.get(tok, 0)
                idf = math.log(1.0 + (n - freq + 0.5) / (freq + 0.5))
                s += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
            if s > 0:
                out[self.ids[di]] = s
        return out

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
        # In-memory corpus + BM25 index for hybrid retrieval (see module note).
        # Built eagerly during populate() when possible, else lazily on first
        # hybrid query from the same chunking pipeline.
        self._corpus: Optional[List[Dict]] = None
        self._bm25: Optional[InMemoryBM25] = None

    def _ensure_bm25(self, data_dir: str = "data") -> InMemoryBM25:
        """Return the BM25 index, building it lazily from the data folder."""
        if self._bm25 is not None:
            return self._bm25
        kb = self._corpus if self._corpus is not None else build_knowledge_base(data_dir)
        items = [
            (chunk_id(k["source_path"], k["chunk_index"]), k["text"],
             {kk: k[kk] for kk in ("category", "source", "source_path", "jurisdiction")},
             k.get("jurisdiction", "General"))
            for k in kb
        ]
        self._bm25 = InMemoryBM25(items)
        return self._bm25

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
        ids = [chunk_id(item["source_path"], item["chunk_index"]) for item in knowledge]
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
        # Refresh hybrid cache from the corpus actually stored (rebuild can
        # change chunk counts), so the BM25 index and dense ids stay aligned.
        self._corpus = knowledge
        self._bm25 = None
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

        With hybrid search enabled (config.hybrid_search), the dense ANN
        ranking is RRF-fused with an in-memory BM25 ranking. The returned
        documents/metadatas/distances keep the same shape as a plain Chroma
        result so callers (app.py) are unaffected.
        """
        n = top_k or config.top_k
        dense = self._dense_query(query_text, n, jurisdiction)
        if not config.hybrid_search:
            return dense
        try:
            return self._hybrid_query(dense, query_text, n, jurisdiction)
        except Exception as e:
            print(f"[RAG Store] Hybrid query failed ({e}); returning dense results")
            return dense

    def _dense_query(self, query_text: str, n: int, jurisdiction: str) -> Dict:
        """Dense ANN query (identical to pre-hybrid behaviour)."""
        # Query always returns ids; "ids" is not a valid include item here.
        include = ["documents", "metadatas", "distances"]
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
                    include=include,
                )
                if result.get("documents", [[]])[0]:
                    return result
            except Exception as e:
                print(f"[RAG Store] jurisdiction filter failed ({e}); querying without filter")
        return self.collection.query(query_texts=[query_text], n_results=n, include=include)

    def _hybrid_query(self, dense: Dict, query_text: str, n: int, jurisdiction: str) -> Dict:
        """RRF-fuse dense ANN + in-memory BM25, preserving dense distance semantics.

        Fused documents keep their native dense distance when they came from
        the dense top-k (so confidence-band calibration in app.py is
        unchanged). Documents rescued by BM25 only get a synthesized distance
        just below the worst dense hit.
        """
        dense_ids = dense.get("ids", [[]])[0]
        dense_docs = dense.get("documents", [[]])[0]
        dense_metas = dense.get("metadatas", [[]])[0]
        dense_dists = dense.get("distances", [[]])[0]

        bm25 = self._ensure_bm25()
        bm25_scores = bm25.score(query_text, jurisdiction=jurisdiction)

        dense_rank = {doc_id: rank for rank, doc_id in enumerate(dense_ids)}
        bm25_ordered = sorted(
            bm25_scores, key=bm25_scores.get, reverse=True
        )[: max(n * BM25_CANDIDATES_MULT, 10)]
        bm25_rank = {doc_id: rank for rank, doc_id in enumerate(bm25_ordered)}

        rrf: Dict[str, float] = {}
        for doc_id, rank in dense_rank.items():
            rrf[doc_id] = rrf.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        for doc_id, rank in bm25_rank.items():
            rrf[doc_id] = rrf.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)

        if not rrf:
            return dense

        # Fused order; dense rank breaks ties so identical sets keep dense order.
        order = sorted(
            rrf, key=lambda doc_id: (-rrf[doc_id], dense_rank.get(doc_id, float("inf")))
        )[:n]

        dense_idx = {doc_id: i for i, doc_id in enumerate(dense_ids)}
        synth_dist = (max(dense_dists) * BM25_SYNTH_DIST_SCALE) if dense_dists else 1.0

        docs_out, metas_out, dists_out = [], [], []
        for doc_id in order:
            if doc_id in dense_idx:
                i = dense_idx[doc_id]
                docs_out.append(dense_docs[i])
                metas_out.append(dense_metas[i])
                dists_out.append(dense_dists[i])
            else:
                docs_out.append(bm25.texts[bm25.ids.index(doc_id)])
                metas_out.append(bm25.metas[bm25.ids.index(doc_id)])
                dists_out.append(synth_dist)

        return {
            "ids": [order],
            "documents": [docs_out],
            "metadatas": [metas_out],
            "distances": [dists_out],
        }

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
