# IP-SAKTI

> **Multilingual RAG Assistant for Ayurveda IPR and Regulatory Guidance**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Vector DB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange)](https://www.trychroma.com/)
[![Status](https://img.shields.io/badge/Status-MVP-yellow)](https://github.com/Hanshal)

IP-SAKTI is a citation-grounded AI assistant that helps users explore intellectual-property and regulatory information related to Ayurveda. It combines a curated multilingual knowledge base, hybrid retrieval, jurisdiction filtering, voice interaction, formulation classification, and access-and-benefit-sharing guidance.

The application runs locally with a FastAPI backend and an accessible AYUSH-inspired web interface.

> **Important:** IP-SAKTI provides general educational information, not legal, medical, or regulatory advice. Always verify current primary sources and consult a qualified professional before making decisions. The web interface is an educational clone and is not an official Government of India service.

---

## ✨ Key Features

- **Citation-grounded answers** with retrieved source names, categories, jurisdictions, and relevance scores
- **Hybrid retrieval** using ChromaDB dense embeddings and in-memory BM25, fused with reciprocal rank fusion
- **Jurisdiction-aware search** across `All`, `India`, and `International`
- **Nine supported languages**: English, Hindi, Marathi, Sanskrit, Bengali, Tamil, Telugu, Kannada, and Gujarati
- **Voice input and audio output**, with Sarvam AI, Groq Whisper, and fallback STT support
- **Ayurvedic formulation classifier** for classical, proprietary, phytopharmaceutical, food supplement, and cosmetic products
- **ABS compliance checklist** covering PIC, MAT, SBB/NBA approval, exports, and IP disclosure
- **Human escalation directory** for IP attorneys, NBA, GI Registry, TKDL, NALSA, and AYUSH support
- **Automatic corpus refresh** when source documents change
- **LLM-free retrieval evaluation** with a reusable question set

---

## 🏗 Architecture

```text
User Browser
   │
   ├── Text question ────────┐
   ├── Recorded voice ───────┼──> FastAPI app.py
   └── Classifier/checklist ─┘          │
                                        ├── Language detection
                                        ├── Jurisdiction filtering
                                        ├── Hybrid RAG retrieval
                                        │      ├── ChromaDB dense search
                                        │      └── BM25 keyword search
                                        ├── LLM answer generation
                                        ├── STT/TTS providers
                                        └── Curated data/ corpus
```

The generated ChromaDB store is local and disposable. It is rebuilt automatically from the version-tracked files in `data/`.

---

## 📁 Project Structure

```text
.
├── app.py                       # FastAPI application and API endpoints
├── root_search.py               # Root data.txt keyword retrieval
├── requirements.txt             # Reproducible Python dependencies
├── start_server.bat             # Windows launcher
├── demo_preflight.py            # End-to-end demo checks
├── .env.example                 # Environment-variable template
├── ayush-clone/                 # Web UI and chat widget
│   ├── index.html
│   ├── script.js
│   ├── chat-widget.js
│   └── CSS assets
├── data/                        # Curated and versioned knowledge corpus
│   ├── config.py
│   ├── rag_loader.py
│   ├── data.txt
│   ├── corpus_version.json
│   └── jurisdiction/language collections
├── evaluation/                  # Retrieval test set and runner
│   ├── Questions.txt
│   └── run_eval.py
└── docs/                        # Project documentation
```

Generated directories such as `.venv/`, `my_db/`, `__pycache__/`, and `server.log` are intentionally excluded from Git.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or newer
- Git
- A modern browser
- Optional API keys for full LLM and voice features

The dependency set was verified on Python 3.14.

### 1. Clone the Repository

```bash
git clone https://github.com/Hanshal/IP-SAKTI.git
cd IP-SAKTI
```

Replace the URL above with the repository's actual GitHub URL if it differs.

### 2. Create a Virtual Environment

#### Windows

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API keys. Never commit this file.

### 4. Start the Application

Use the Windows launcher:

```powershell
.\start_server.bat
```

Or start it directly from any supported platform:

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

Voice recording works on `localhost`/`127.0.0.1` or over HTTPS. Browsers may block microphone access on a network IP served over plain HTTP.

---

## 🔑 Configuration

| Variable | Required | Purpose |
|---|---:|---|
| `GEMINI_API_KEY` | Optional* | Gemini answer generation |
| `GROQ_API_KEY` | Optional* | Groq answer generation and Whisper STT |
| `SARVAM_API_KEY` | Optional | Indic STT and Bulbul TTS |
| `MODEL` | No | LLM model; defaults to `gemini-2.5-flash` |
| `GROQ_STT_MODEL` | No | Groq transcription model; defaults to `whisper-large-v3` |
| `COLLECTION_NAME` | No | ChromaDB collection name; defaults to `my_knowledge` |
| `CHUNK_SIZE` | No | Corpus chunk size; defaults to `500` |
| `TOP_K` | No | Retrieval result count; defaults to `8` |
| `HYBRID_SEARCH` | No | Set to `1` for dense + BM25 or `0` for dense only |
| `PORT` | No | Server port; defaults to `5000` |
| `LLM_BASE_URL` | Optional | Custom OpenAI-compatible endpoint |
| `LLM_API_KEY` | Optional | API key for a custom endpoint |

\* At least one valid LLM key or a configured OpenAI-compatible endpoint is needed for generated answers. Retrieval still works without them, but the application enters demo mode.

---

## 🧠 Retrieval and Corpus

The current corpus is version **2.1.0**, dated **2026-09-14**. It includes:

- Ayurveda overview and herb information
- Indian and international IP statutes
- Patentability and traditional-knowledge guidance
- Drug regulations and labelling requirements
- Formulation classification
- Geographical indications
- Case law
- Access and Benefit Sharing
- International treaties
- Bengali, Gujarati, Kannada, Sanskrit, Tamil, and Telugu materials

`data/corpus_version.json` records corpus metadata. SHA-1 hashes in the generated ChromaDB manifest detect source changes and trigger a rebuild.

To rebuild manually through the API:

```bash
curl -X POST http://127.0.0.1:5000/rebuild
```

---

## 💬 Example API Requests

### Text Query

```bash
curl -X POST http://127.0.0.1:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I patent an Ayurvedic formulation?",
    "jurisdiction": "india"
  }'
```

### Formulation Classifier

```bash
curl -X POST http://127.0.0.1:5000/formulation/classify \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "in_authoritative_text": "no",
      "new_ingredient_or_combination": "yes",
      "standardized_extract": "yes",
      "intended_claims": "treat"
    }
  }'
```

### Health Check

```bash
curl http://127.0.0.1:5000/health
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web application |
| `POST` | `/query` | Text-based RAG query |
| `POST` | `/query-voice` | Voice query with transcription and optional TTS |
| `POST` | `/text-to-speech` | Convert text to speech |
| `GET` | `/stats` | Retrieval-store statistics |
| `POST` | `/rebuild` | Force a corpus rebuild |
| `GET` | `/languages` | Supported language list |
| `GET` | `/corpus-version` | Corpus metadata and document count |
| `GET` | `/health` | Service health and provider status |
| `GET` | `/formulation/questions` | Formulation wizard questions |
| `POST` | `/formulation/classify` | Classify an Ayurvedic formulation |
| `GET` | `/abs/checklist` | ABS compliance checklist |
| `POST` | `/abs/check` | Evaluate completed ABS steps |
| `GET` | `/escalation` | Professional and government escalation contacts |

Interactive API documentation is available at [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs).

---

## 🧪 Evaluation and Preflight

Run retrieval evaluation directly against the local RAG store:

```bash
python evaluation/run_eval.py --local
```

Run it against a live server:

```bash
python evaluation/run_eval.py
```

After starting the server with full LLM configuration, run the demo checks in another terminal:

```bash
python demo_preflight.py
```

The preflight validates health, corpus loading, languages, text answers, sources, confidence, formulation classification, ABS checks, and escalation contacts.

---

## 🌐 Deployment Notes

For a public deployment:

1. Set all required environment variables in the hosting platform.
2. Use HTTPS, especially for microphone-based voice input.
3. Persist the ChromaDB data directory or allow the corpus to rebuild at startup.
4. Protect administrative endpoints such as `/rebuild`.
5. Add authentication, rate limiting, request-size limits, and redacted production logs.
6. Keep API keys server-side and rotate exposed keys immediately.
7. Review corpus freshness and primary legal sources before each public release.

---

## 🔒 Security and Privacy

- `.env` and other secret files must never be committed.
- Use `.env.example` only for placeholder variable names.
- Do not paste private legal, medical, business, or personal information into a public deployment.
- Audio sent to external STT/TTS providers is subject to those providers' policies.
- Review third-party API terms before production use.

---

## 🛠 Troubleshooting

### The application starts in demo mode

Confirm that either `GEMINI_API_KEY` or `GROQ_API_KEY` contains a valid, active key. Also verify that `MODEL` matches an available model.

### A Python package cannot be imported

Activate `.venv`, then reinstall dependencies:

```bash
pip install -r requirements.txt
```

### The microphone is blocked

Open the application through `http://127.0.0.1:5000` or `http://localhost:5000`, grant microphone permission, and retry. Remote HTTP addresses require HTTPS.

### The vector store appears stale

Stop the server, delete the generated `my_db/` directory, and restart the application. It will be recreated from `data/`.

### Port 5000 is already in use

Set another port before starting:

```bash
set PORT=8000
python app.py
```

On Linux or macOS:

```bash
PORT=8000 python app.py
```

---

## 🤝 Contributing

Contributions are welcome. Useful contribution areas include:

- Correcting or expanding sourced legal and regulatory content
- Adding multilingual corpus material with jurisdiction metadata
- Improving retrieval and evaluation coverage
- Strengthening accessibility and responsive UI behavior
- Adding tests, security controls, and deployment documentation

Before contributing, ensure that no secrets, private data, generated databases, or unnecessary large media files are included.

---

## 📄 License

A repository license has not yet been selected. Add an appropriate open-source license before public distribution or reuse.

---

<p align="center">
  <strong>IP-SAKTI — Preserving traditional knowledge through accessible, source-grounded technology.</strong>
</p>
