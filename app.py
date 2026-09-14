from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import google.generativeai as genai
import os
import sys
import io
import json
import base64
import re
import tempfile
import speech_recognition as sr
import requests
import requests.adapters
import hashlib

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")



app = Flask(__name__, static_folder="ayush-clone", static_url_path="")

from data.rag_loader import initialize_rag
from data.config import config
from root_search import search_root_data_txt

config.print_status()

llm_client = None
gemini_client = None
if config.gemini_api_key:
    genai.configure(api_key=config.gemini_api_key)
    gemini_client = genai.GenerativeModel(config.model)

# Custom OpenAI-compatible endpoint (local/remote)
custom_base = os.getenv("LLM_BASE_URL", "")
custom_key = os.getenv("LLM_API_KEY", "")
if custom_key and custom_base:
    llm_client = OpenAI(api_key=custom_key, base_url=custom_base)
elif config.groq_api_key:
    llm_client = OpenAI(
        api_key=config.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

print("[INIT] Loading knowledge from data folder...")
rag_store = initialize_rag(data_dir="data", force=False)
print(f"[INIT] RAG store stats: {rag_store.get_stats()}")

# Shared HTTP session with connection pooling (keeps TLS connections to
# Groq/Sarvam alive across requests instead of reconnecting every call).
http = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=1)
http.mount("https://", _adapter)
http.mount("http://", _adapter)

# Small LRU-style cache for repeated (query, jurisdiction) answers.
ANSWER_CACHE: dict = {}
ANSWER_CACHE_MAX = 128


def cached_answer_key(query: str, jurisdiction: str) -> str:
    norm = " ".join(query.lower().split())
    return hashlib.sha1(f"{norm}|{jurisdiction}".encode()).hexdigest()


def get_cached_answer(key: str):
    return ANSWER_CACHE.get(key)


def store_cached_answer(key: str, payload: dict) -> None:
    if len(ANSWER_CACHE) >= ANSWER_CACHE_MAX:
        ANSWER_CACHE.pop(next(iter(ANSWER_CACHE)))
    ANSWER_CACHE[key] = payload

LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "mr": "mr",
    "sa": "sa",
    "bn": "bn",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "gu": "gu",
    "auto": "en",
}

SARVAM_LANG_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "sa": "sa-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "gu": "gu-IN",
    "auto": "en-IN",
}


def transcribe_sarvam(audio_data: bytes, language_code: str = "hi-IN") -> str:
    """Transcribe audio using Sarvam AI Speech-to-Text API."""
    try:
        if not config.sarvam_configured:
            print("[SARVAM STT] API key not configured")
            return ""

        url = "https://api.sarvam.ai/speech-to-text"

        files = {
            "file": ("audio.wav", io.BytesIO(audio_data), "audio/wav"),
        }

        data = {
            "language_code": language_code,
            "model": "saaras:v4",
            "mode": "transcribe",
        }

        headers = {
            "api-subscription-key": config.sarvam_api_key,
        }

        response = http.post(url, files=files, data=data, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            transcript = result.get("transcript", "")
            if transcript:
                print(f"[SARVAM STT] Transcribed: {transcript[:100]}...")
                return transcript
        else:
            print(f"[SARVAM STT] Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[SARVAM STT] Exception: {e}")
    
    return ""


def transcribe_groq(audio_data: bytes, language_code: str = "en") -> str:
    """Transcribe audio using Groq's Whisper STT (same API as the
    ESP32-Groq-Speech-to-Text project, but with the browser mic).

    Groq returns in ~0.3s and supports all major Indic languages.
    """
    try:
        if not config.groq_configured:
            print("[GROQ STT] API key not configured")
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {config.groq_api_key}",
        }

        files = {
            "file": ("audio.wav", io.BytesIO(audio_data), "audio/wav"),
        }

        data = {
            "model": config.groq_stt_model,
            "response_format": "json",
        }
        # Whisper auto-detects when no language is hinted
        if language_code and language_code not in ("", "auto"):
            data["language"] = language_code

        response = http.post(url, files=files, data=data, headers=headers, timeout=30)

        if response.status_code == 200:
            transcript = response.json().get("text", "")
            if transcript:
                print(f"[GROQ STT] Transcribed: {transcript[:100]}...")
                return transcript
        else:
            print(f"[GROQ STT] Error: {response.status_code} - {response.text[:200]}")

    except Exception as e:
        print(f"[GROQ STT] Exception: {e}")

    return ""


def transcribe_audio(audio_data: bytes, input_lang: str = "en") -> str:
    """STT fallback chain: Sarvam (Indic-tuned) -> Groq Whisper -> Google.

    Returns the first successful transcription, or "".
    """
    lang_code = LANG_CODES.get(input_lang, "en")
    sarvam_lang_code = SARVAM_LANG_CODES.get(input_lang, "en-IN")

    if config.sarvam_configured:
        text = transcribe_sarvam(audio_data, sarvam_lang_code)
        if text:
            return text

    if config.groq_configured:
        text = transcribe_groq(audio_data, lang_code if input_lang != "auto" else "")
        if text:
            return text

    # Last resort: free Google Web Speech API via SpeechRecognition
    try:
        recognizer = sr.Recognizer()
        audio_io = io.BytesIO(audio_data)
        with sr.AudioFile(audio_io) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language=lang_code)
    except Exception:
        return ""


def bulbul_tts(text: str, language_code: str = "en-IN") -> str:
    """Generate audio using Sarvam AI Bulbul TTS and return base64-encoded audio."""
    try:
        if not config.sarvam_configured:
            print("[BULBUL TTS] API key not configured")
            return ""

        url = "https://api.sarvam.ai/text-to-speech"

        headers = {
            "api-subscription-key": config.sarvam_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text[:2500],  # Bulbul v3 max is 2500 chars
            "language_code": language_code,
            "model": "bulbul:v3",
        }

        response = http.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            audio_b64 = result.get("audios", [None])[0]
            if audio_b64:
                print(f"[BULBUL TTS] Generated audio for text ({len(text)} chars)")
                return audio_b64
        else:
            print(f"[BULBUL TTS] Error: {response.status_code} - {response.text[:200]}")

    except Exception as e:
        print(f"[BULBUL TTS] Exception: {e}")

    return ""


def gtts_fallback(text: str, lang: str = "en") -> str:
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        return fp.name
    except Exception as e:
        print(f"gTTS error: {e}")
        return None


DISCLAIMER = (
    "Disclaimer: IP-SAKTI provides general information for educational purposes only. "
    "It is not legal advice. Consult a qualified IP attorney or the AYUSH facilitation "
    "centre before making legal or regulatory decisions."
)

TKDL_POINTER = (
    "Prior-art check: search the Traditional Knowledge Digital Library at "
    "https://tkdl.res.in before filing or opposing patents involving Ayurvedic knowledge."
)

ESCALATION_CONTACTS = [
    {
        "name": "Registered Patent Agents & IP Attorneys",
        "detail": "Searchable via the Indian Patent Office agent registry.",
        "url": "https://ipindia.gov.in",
    },
    {
        "name": "National Biodiversity Authority (ABS approvals)",
        "detail": "Prior approval and ABS clarifications for biological resources.",
        "url": "https://nba.india.gov.in",
    },
    {
        "name": "GI Registry, Chennai",
        "detail": "Geographical Indication registration guidance.",
        "url": "https://ipindiaservices.gov.in/GIRPublic/App",
    },
    {
        "name": "CSIR-TKDL Unit",
        "detail": "Traditional-knowledge verification and access agreements.",
        "url": "https://tkdl.res.in",
    },
    {
        "name": "NALSA (free legal aid)",
        "detail": "Free legal services for eligible applicants.",
        "url": "https://nalsa.gov.in",
    },
    {
        "name": "AYUSH Startup / Incubation Centres",
        "detail": "Ministry of AYUSH entrepreneurship programs, AYUSH Park and ARIIA-ranked institutes.",
        "url": "https://ayush.gov.in",
    },
]


def normalize_relevance(distance) -> float:
    """Map a vector distance to a 0..1 relevance score.

    Distances from the default embedding function routinely exceed 1.0,
    so 1-d would go negative. Normalize over a 2.0 distance range instead
    (d=0 -> 1.0, d=1 -> 0.5, d>=2 -> 0.0).
    """
    if distance is None:
        return 0.5
    return round(max(0.0, 1 - distance / 2), 3)


def build_source_lists(metadatas, distances, root_hits, jurisdiction="all"):
    """Build deduplicated source records, split by jurisdiction.

    Each unique (category, source) keeps one record that aggregates every
    jurisdiction its chunks were labelled with, so a file containing both
    India and International chunks appears in both answer-sets.
    """
    sources = []
    index = {}
    if root_hits:
        entry = {
            "category": "Consolidated Knowledge Base",
            "source": "data.txt",
            "source_path": "data.txt",
            "jurisdiction": "General",
            "jurisdictions": ["General"],
            "relevance_score": 1.0,
        }
        sources.append(entry)
        index[("Consolidated Knowledge Base", "data.txt")] = entry
    for meta, dist in zip(metadatas, distances):
        if not meta:
            continue
        key = (meta.get("category", ""), meta.get("source", ""))
        jur = meta.get("jurisdiction", "General")
        rel = normalize_relevance(dist)
        if key not in index:
            entry = {
                "category": key[0] or "Unknown",
                "source": key[1] or "Unknown",
                "source_path": meta.get("source_path", ""),
                "jurisdiction": jur,
                "jurisdictions": [jur],
                "relevance_score": rel,
            }
            sources.append(entry)
            index[key] = entry
        else:
            entry = index[key]
            if jur not in entry["jurisdictions"]:
                entry["jurisdictions"].append(jur)
            # Surface the jurisdiction matching the active filter first
            if jurisdiction in ("india", "international") and jur.lower() == jurisdiction:
                entry["jurisdiction"] = jur
            if rel > entry["relevance_score"]:
                entry["relevance_score"] = rel
    return sources


def split_sources_by_jurisdiction(sources):
    india = [s for s in sources if "India" in s.get("jurisdictions", [])]
    international = [s for s in sources if "International" in s.get("jurisdictions", [])]
    other = [s for s in sources if not (india.__contains__(s) or international.__contains__(s))]
    return india, international, other


SYSTEM_PROMPT = (
    "You are IP-SAKTI, a professional AI assistant for the IP-SAKTI Ayurveda IPR guidance tool. "
    "RULES: "
    "1. Answer using ONLY the provided context. "
    "2. State the jurisdiction (India or International) clearly. "
    "3. If the context does not contain the answer, say: 'I don't have enough information.' "
    "4. Never pretend to be human. "
    "5. FORMAT: respond ONLY as bullet points. Start every line with '- '. "
    "   Each bullet is one short, distinct fact. No prose paragraphs, no headings. "
    "6. Do NOT include reasoning, thinking, analysis, planning, self-correction, drafts, "
    "   step-by-step notes, brackets, bold/italic markup, or meta-commentary. "
    "7. FORBIDDEN phrases (anywhere in output): 'Here is my answer', 'Let me think', "
    "   'First', 'Second', 'Step', 'Based on', 'According to', 'The answer is', "
    "   'Drafting Answer', 'Final Answer', 'I need to', 'I should', 'Note that', "
    "   'Wait', 'Output Generation', 'Self-Correction', 'Check against rules'. "
    "8. Output ONLY the bullet list. Nothing before or after it."
)


def clean_answer(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"```[\s\S]*?```", "", text)

    text = re.sub(r"\n?\s*Source:\s*[^\n]+", "", text, flags=re.IGNORECASE)

    stop_markers = [
        "Rules to Follow", "Wait, I need", "Let me check", "Self-Correction",
        "All good", "Matches all constraints", "Check against rules",
        "Output Generation", "Ready. Output", "Let me ensure",
        "One minor thing", "Note: I will", "Generating.", "Drafting Answer",
        "Final Answer", "Output:", "Answer:", "Drafting:", "Analyzing:",
    ]
    cut = len(text)
    for marker in stop_markers:
        idx = text.find(marker)
        if idx != -1 and idx > 30:
            cut = min(cut, idx)
    text = text[:cut].strip()

    text = re.sub(r"Here's a thinking process.*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Analyze User Input.*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Let me analyze.*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Thinking:.*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Reasoning:.*", "", text, flags=re.IGNORECASE | re.DOTALL)

    lines = text.split("\n")
    bullets = []
    seen = set()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        line = re.sub(r"^[\-\*\u2022\u25E6\u2023]+", "", line).strip()
        line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        line = re.sub(r"^\*\*|\*\*$", "", line).strip()

        if not line or len(line) < 8:
            continue

        drop_prefixes = [
            "drafting answer", "final answer", "answer:", "context:", "question:",
            "rules to follow", "let me", "i need to", "i should", "note that",
            "wait", "self-correction", "all good", "check against", "output generation",
            "ready.", "generating.", "one minor thing", "here's a", "analyze user",
            "thinking:", "reasoning:", "analysis:", "now i",
        ]
        lower_line = line.lower()
        if any(lower_line.startswith(p) for p in drop_prefixes):
            continue

        key = re.sub(r"\s+", " ", lower_line)
        if key not in seen:
            seen.add(key)
            bullets.append("- " + line)

    text = "\n".join(bullets)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if not text or len(re.sub(r"[\s\n]", "", text)) < 20:
        return "I don't have enough information in my knowledge base to answer this question."

    return text


@app.route("/")
def index():
    return send_from_directory("ayush-clone", "index.html")


def generate_rag_answer(user_query: str, jurisdiction: str = "all"):
    """Shared RAG pipeline: retrieve -> build sources -> LLM answer.

    Used by both /query and /query-voice so voice and text get identical
    filtering, confidence bands, and answer formatting. Results are cached
    so repeated questions skip retrieval + LLM entirely.
    """
    cache_key = cached_answer_key(user_query, jurisdiction)
    cached = get_cached_answer(cache_key)
    if cached is not None:
        print(f"[CACHE] Hit for query: {user_query[:60]}...")
        return cached

    # Priority 1: search root data.txt (respects jurisdiction filter)
    root_hits = search_root_data_txt(user_query, top_n=3, jurisdiction=jurisdiction)
    # Priority 2: search data/ folder via RAG store (jurisdiction-filtered)
    results = rag_store.query(user_query, top_k=config.top_k, jurisdiction=jurisdiction)
    retrieved = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # Prepend root data.txt hits (priority)
    if root_hits:
        retrieved = root_hits + retrieved
        distances = [0.0] * len(root_hits) + list(distances)

    max_relevance = max((normalize_relevance(d) for d in distances if d is not None), default=0)

    print(f"[DEBUG] query={user_query}, jurisdiction={jurisdiction}, docs={len(retrieved)}, max_rel={max_relevance:.3f}, demo_mode={config.demo_mode}")

    if not retrieved or (max_relevance < 0.0):
        payload = {
            "answer": "I don't have enough information in my knowledge base to answer this question.",
            "sources": [],
            "confidence": "low",
            "jurisdiction": jurisdiction,
            "disclaimer": DISCLAIMER,
        }
        store_cached_answer(cache_key, payload)
        return payload

    sources = build_source_lists(metadatas, distances, root_hits, jurisdiction=jurisdiction)
    india_sources, intl_sources, _ = split_sources_by_jurisdiction(sources)

    # Confidence bands are calibrated to the normalized 0..1 relevance score
    avg_score = max_relevance
    if avg_score >= 0.45:
        confidence = "high"
    elif avg_score >= 0.25:
        confidence = "medium"
    else:
        confidence = "low"

    if config.demo_mode or (llm_client is None and gemini_client is None):
        payload = {
            "answer": (
                "Demo mode: answer generation requires LLM integration. "
                "Please configure GEMINI_API_KEY or GROQ_API_KEY to enable full responses."
            ),
            "sources": sources,
            "sources_india": india_sources,
            "sources_international": intl_sources,
            "confidence": confidence,
            "jurisdiction": jurisdiction,
            "disclaimer": DISCLAIMER,
            "demo_mode": True,
        }
        return payload

    # No manual language detection — model auto-detects from query
    system_content = SYSTEM_PROMPT
    if jurisdiction and jurisdiction != "all":
        system_content += (
            f"\n9. Focus on {jurisdiction.capitalize()} law and guidance only. "
            "State the jurisdiction explicitly in your bullets."
        )

    context = "\n\n---\n\n".join(retrieved)
    user_prompt = f"### Context:\n{context}\n\n### Question:\n{user_query}"

    # Prefer Gemini if configured
    if gemini_client is not None:
        response = gemini_client.generate_content(
            system_content + "\n\n" + user_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        answer = response.text or ""
    else:
        try:
            response = llm_client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            raw_msg = response.choices[0].message
            answer = getattr(raw_msg, "content", None) or ""
        except Exception as llm_e:
            print(f"[LLM ERROR] {llm_e}")
            answer = f"LLM call failed: {llm_e}"
    print(f"[DEBUG] raw LLM response: {answer[:500]}")
    answer = clean_answer(answer)

    payload = {
        "answer": answer,
        "sources": sources,
        "sources_india": india_sources,
        "sources_international": intl_sources,
        "confidence": confidence,
        "jurisdiction": jurisdiction,
        "disclaimer": DISCLAIMER,
        "tkdl_pointer": TKDL_POINTER,
        "demo_mode": False,
    }
    store_cached_answer(cache_key, payload)
    return payload


@app.route("/query", methods=["POST"])
def query():
    jurisdiction = "all"
    try:
        data = request.json
        user_query = data.get("query", "").strip()
        jurisdiction = data.get("jurisdiction", "all")
        if jurisdiction not in ("all", "india", "international"):
            jurisdiction = "all"
        top_k = data.get("top_k", config.top_k)

        if not user_query:
            return jsonify({"answer": "Please ask a question.", "sources": []})

        return jsonify(generate_rag_answer(user_query, jurisdiction))
    except Exception as e:
        return jsonify({"answer": f"Error: {e}", "sources": [], "confidence": "low", "jurisdiction": jurisdiction, "disclaimer": DISCLAIMER})


@app.route("/query-voice", methods=["POST"])
def query_voice():
    try:
        data = request.json
        input_lang = data.get("inputLanguage", "en")
        output_lang = data.get("outputLanguage", "en")
        audio_b64 = data.get("audioBase64", "")
        jurisdiction = data.get("jurisdiction", "all")
        if jurisdiction not in ("all", "india", "international"):
            jurisdiction = "all"

        if not audio_b64:
            return jsonify({"error": "No audio provided", "success": False})

        audio_data = base64.b64decode(audio_b64)

        # STT fallback chain: Sarvam -> Groq Whisper -> Google
        user_text = transcribe_audio(audio_data, input_lang)

        if not user_text:
            return jsonify({"error": "Could not transcribe audio", "success": False})

        result = generate_rag_answer(user_text, jurisdiction)

        audio_b64_out = None
        try:
            lang_code = SARVAM_LANG_CODES.get(output_lang, "en-IN")
            audio_b64_out = bulbul_tts(result.get("answer", ""), lang_code)
        except Exception:
            audio_b64_out = None

        return jsonify({
            "answer": result.get("answer", ""),
            "user_text": user_text,
            "sources": result.get("sources", []),
            "sources_india": result.get("sources_india", []),
            "sources_international": result.get("sources_international", []),
            "confidence": result.get("confidence", "low"),
            "disclaimer": result.get("disclaimer", DISCLAIMER),
            "tkdl_pointer": result.get("tkdl_pointer"),
            "audio_base64": audio_b64_out,
            "success": True,
            "inputLanguage": input_lang,
            "outputLanguage": output_lang
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    try:
        data = request.json
        text = data.get("text", "")
        language = data.get("language", "en")

        if not text:
            return jsonify({"error": "No text provided", "audio_base64": None})

        lang_code = SARVAM_LANG_CODES.get(language, "en-IN")
        audio_b64 = bulbul_tts(text, lang_code)

        if audio_b64:
            return jsonify({"success": True, "audio_base64": audio_b64, "language": language})
        else:
            return jsonify({"error": "TTS failed", "audio_base64": None})
    except Exception as e:
        return jsonify({"error": str(e), "audio_base64": None})


@app.route("/stats", methods=["GET"])
def stats():
    return jsonify(rag_store.get_stats())


@app.route("/rebuild", methods=["POST"])
def rebuild():
    try:
        rag_store.populate(data_dir="data", force=True)
        return jsonify({"success": True, "stats": rag_store.get_stats()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/languages", methods=["GET"])
def get_languages():
    stt_provider = config.stt_provider
    languages = [
        {"code": code, "name": name, "lang_code": SARVAM_LANG_CODES.get(code, "en-IN")}
        for code, name in [
            ("en", "English"), ("hi", "Hindi"), ("mr", "Marathi"), ("sa", "Sanskrit"),
            ("bn", "Bengali"), ("ta", "Tamil"), ("te", "Telugu"), ("kn", "Kannada"),
            ("gu", "Gujarati"),
        ]
    ]
    return jsonify({
        "stt_provider": stt_provider,
        "languages": languages
    })


@app.route("/corpus-version", methods=["GET"])
def corpus_version():
    version_path = os.path.join("data", "corpus_version.json")
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            version_info = json.load(f)
    except Exception:
        version_info = {"version": "unknown", "date": "unknown", "sources": []}
    version_info["rag_documents"] = rag_store.get_stats().get("total_documents", 0)
    return jsonify(version_info)


@app.route("/escalation", methods=["GET"])
def escalation():
    return jsonify({
        "contacts": ESCALATION_CONTACTS,
        "when_to_escalate": [
            "Patent drafting or filing",
            "Patent opposition or litigation",
            "Benefit-sharing (MAT) contract negotiation",
            "DCGI / FSSAI licensing strategy",
            "GI application drafting",
        ],
        "disclaimer": DISCLAIMER,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "demo_mode": config.demo_mode,
        "rag_documents": rag_store.get_stats().get("total_documents", 0),
        "stt_provider": config.stt_provider,
        "sarvam_stt": config.sarvam_configured,
        "groq_stt": config.groq_configured,
    })


# ============================================================
# Formulation classification wizard (pre-RAG router)
# Mirrors the decision tree in data/formulation_classification
# ============================================================

FORMULATION_QUESTION_STEPS = [
    {
        "id": "in_authoritative_text",
        "question": "Is the formulation listed in an authoritative Ayurvedic text (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, Bhaishajya Ratnavali, or the Ayurvedic Pharmacopoeia of India)?",
        "options": [
            {"value": "yes", "label": "Yes — it is a classical formulation"},
            {"value": "no", "label": "No — it is not in the texts"},
        ],
    },
    {
        "id": "new_ingredient_or_combination",
        "question": "Does the formulation contain a new active ingredient or a new combination of ingredients not found in classical texts?",
        "options": [
            {"value": "yes", "label": "Yes — new ingredient or combination"},
            {"value": "no", "label": "No — based on known ingredients"},
        ],
    },
    {
        "id": "standardized_extract",
        "question": "Are the active ingredients known and standardized (e.g., quantified plant extracts with marker compounds)?",
        "options": [
            {"value": "yes", "label": "Yes — standardized plant extract"},
            {"value": "no", "label": "No — traditional preparation"},
        ],
    },
    {
        "id": "intended_claims",
        "question": "What claims will the product make?",
        "options": [
            {"value": "treat", "label": "Diagnose, treat, cure or prevent disease (medicine)"},
            {"value": "supplement", "label": "Supplement the diet / maintain health (food supplement)"},
            {"value": "beautify", "label": "External application to cleanse or beautify (cosmetic)"},
        ],
    },
]

FORMULATION_CLASSIFICATIONS = {
    "classical": {
        "label": "Classical Ayurvedic Formulation",
        "description": "Included in authoritative Ayurvedic texts. No pre-market approval for safety and efficacy is required; traditional use is the evidence base.",
        "regulatory": "Comply with GMP, Ayurvedic Pharmacopoeia of India (API) standards, and Schedule E(1) labelling.",
        "ip_note": "Not patentable under Section 3(p) of the Patents Act, 1970 as traditional knowledge; novel processes around it may still be patentable.",
        "abs_check": "If biological resources are sourced from India, obtain SBB approval and share benefits per the Biological Diversity Act, 2002.",
    },
    "pam": {
        "label": "Proprietary Ayurvedic Medicine (PAM) / New Drug",
        "description": "A new formulation based on Ayurvedic principles but not in authoritative texts. Requires pre-market approval from the Drugs Controller General of India (DCGI).",
        "regulatory": "Submit safety and efficacy data from animal studies and human clinical trials; follow GMP and pharmacovigilance reporting.",
        "ip_note": "Potentially patentable if novel, inventive and industrially applicable; Sections 3(c) and 3(p) of the Patents Act may still bar claims.",
        "abs_check": "Disclose the source and geographical origin of biological resources (Section 10(4A)); obtain NBA/SBB approval for Indian biological resources.",
    },
    "phytopharmaceutical": {
        "label": "Phytopharmaceutical Drug",
        "description": "A drug derived from plant sources with known, standardized active ingredients (category introduced in 2015).",
        "regulatory": "Pre-market approval from DCGI, standardized extract characterization, clinical trials, and pharmacovigilance.",
        "ip_note": "The standardized extract or its process may be patentable if novel and non-obvious.",
        "abs_check": "ABS compliance under the Biological Diversity Act applies to all plant sourcing; disclose origin in the patent application.",
    },
    "food_supplement": {
        "label": "Food Supplement (Aahar)",
        "description": "Regulated under the Food Safety and Standards Act, 2006. No pre-market approval for safety and efficacy, but disease-treatment claims are prohibited.",
        "regulatory": "FSSAI registration/licence, food standards compliance, and FSSAI labelling rules.",
        "ip_note": "Limited patent protection; brand names and packaging can be protected via trademarks and designs.",
        "abs_check": "ABS obligations still apply when the supplement uses Indian biological resources.",
    },
    "cosmetic": {
        "label": "Cosmetic",
        "description": "External-use products that claim to cleanse, beautify or maintain the skin are regulated as cosmetics.",
        "regulatory": "CDSCO registration, Cosmetics Rules 2020 compliance, and cosmetic labelling standards.",
        "ip_note": "Formulations may be patentable if novel; trademarks, designs and trade secrets offer additional protection.",
        "abs_check": "ABS obligations apply to plant-derived cosmetic ingredients sourced from India.",
    },
}


def classify_formulation(answers: dict) -> dict:
    """Apply the decision tree from data/formulation_classification."""
    in_text = answers.get("in_authoritative_text")
    new_ingredient = answers.get("new_ingredient_or_combination")
    standardized = answers.get("standardized_extract")
    claims = answers.get("intended_claims")

    if in_text == "yes":
        key = "classical"
    elif new_ingredient == "yes":
        key = "pam"
    elif standardized == "yes":
        key = "phytopharmaceutical"
    elif claims == "treat":
        key = "pam"
    elif claims == "supplement":
        key = "food_supplement"
    elif claims == "beautify":
        key = "cosmetic"
    else:
        key = "food_supplement"

    result = {"classification": key, **FORMULATION_CLASSIFICATIONS[key]}

    if in_text == "no" and claims == "treat":
        result["note"] = (
            "A new formulation claiming to treat disease is regulated as a new drug / PAM "
            "and needs DCGI pre-market approval with clinical trial data."
        )
    result["disclaimer"] = DISCLAIMER
    return result


@app.route("/formulation/classify", methods=["POST"])
def formulation_classify():
    try:
        data = request.json or {}
        answers = data.get("answers", {})
        required = {step["id"] for step in FORMULATION_QUESTION_STEPS}
        missing = [q for q in required if q not in answers]
        if missing:
            return jsonify({
                "error": f"Missing answers: {', '.join(missing)}",
                "questions": FORMULATION_QUESTION_STEPS,
                "success": False,
            })
        return jsonify({"success": True, **classify_formulation(answers)})
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


@app.route("/formulation/questions", methods=["GET"])
def formulation_questions():
    return jsonify({"steps": FORMULATION_QUESTION_STEPS})


# ============================================================
# ABS compliance checklist wizard (PIC → MAT → NBA approval)
# ============================================================

ABS_CHECKLIST = [
    {
        "id": "identify_resources",
        "phase": "Preparation",
        "item": "Identify all biological resources (herbs, plant parts, extracts) used in the formulation.",
        "authority": "Internal documentation",
    },
    {
        "id": "origin_india",
        "phase": "Preparation",
        "item": "Determine whether the resources are sourced from within India or imported.",
        "authority": "Internal documentation",
    },
    {
        "id": "sbb_notice",
        "phase": "PIC (Prior Informed Consent)",
        "item": "Indian entities using Indian biological resources for commercial utilization must give prior intimation / obtain approval from the State Biodiversity Board (SBB).",
        "authority": "State Biodiversity Board",
    },
    {
        "id": "nba_approval_foreign",
        "phase": "NBA Approval",
        "item": "Foreign entities or transfer of resources to foreign persons require prior approval of the National Biodiversity Authority (NBA) (Section 3, Biological Diversity Act, 2002).",
        "authority": "National Biodiversity Authority",
    },
    {
        "id": "mat_negotiation",
        "phase": "MAT (Mutually Agreed Terms)",
        "item": "Negotiate mutually agreed terms including benefit-sharing: royalty (typically 3–5% of net profits), upfront and milestone payments, or non-monetary benefits (technology transfer, joint research, capacity building).",
        "authority": "BMC / local communities via SBB",
    },
    {
        "id": "bmc_consultation",
        "phase": "PIC (Prior Informed Consent)",
        "item": "Where local communities hold the associated traditional knowledge, obtain their prior informed consent through the Biodiversity Management Committee (BMC).",
        "authority": "Biodiversity Management Committee",
    },
    {
        "id": "ip_disclosure",
        "phase": "IPR",
        "item": "Patent applications must disclose the source and geographical origin of biological resources (Section 10(4A), Patents Act; Section 6, Biological Diversity Act).",
        "authority": "Indian Patent Office",
    },
    {
        "id": "export_check",
        "phase": "Export",
        "item": "Export of certain biological resources requires NBA approval; verify the EXIM policy for restricted herbs.",
        "authority": "National Biodiversity Authority / DGFT",
    },
    {
        "id": "record_keeping",
        "phase": "Ongoing",
        "item": "Maintain records of all access and benefit-sharing arrangements for audit and reporting.",
        "authority": "NBA / SBB",
    },
]


@app.route("/abs/checklist", methods=["GET"])
def abs_checklist():
    return jsonify({
        "steps": ABS_CHECKLIST,
        "tkdl_pointer": TKDL_POINTER,
        "disclaimer": DISCLAIMER,
    })


@app.route("/abs/check", methods=["POST"])
def abs_check():
    try:
        data = request.json or {}
        completed = set(data.get("completed", []))
        foreign_entity = data.get("foreign_entity", False)
        exports = data.get("exports", False)

        remaining = [step for step in ABS_CHECKLIST if step["id"] not in completed]
        required_ids = {s["id"] for s in ABS_CHECKLIST}
        if foreign_entity:
            required_ids.add("nba_approval_foreign")
        if exports:
            required_ids.add("export_check")

        missing_required = [
            step for step in ABS_CHECKLIST
            if step["id"] in required_ids and step["id"] not in completed
        ]
        pct = round(100 * len(completed & required_ids) / len(required_ids)) if required_ids else 100

        return jsonify({
            "success": True,
            "percent_complete": pct,
            "remaining_steps": remaining,
            "missing_required": missing_required,
            "compliant": len(missing_required) == 0,
            "foreign_entity_required": foreign_entity,
            "export_required": exports,
            "disclaimer": DISCLAIMER,
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


if __name__ == "__main__":
    print(f"[START] IP-SAKTI Ayurveda IPR Assistant running at http://127.0.0.1:5000")
    print(f"[START] Supported languages: Auto-detected (English, Hindi, Marathi, etc.)")
    print(f"[START] Data folder: data/")
    use_debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=use_debug, use_reloader=False, host="0.0.0.0", port=port)
