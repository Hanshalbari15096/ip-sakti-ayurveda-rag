RUNNING SETUP SUMMARY (2026-09-09)
=====================================
- Removed Groq model from .env (GROQ_API_KEY cleared, GROQ_STT_MODEL not set)
- Disabled broken custom endpoint (LLM_BASE_URL / LLM_API_KEY commented out)
- Disabled invalid Gemini key (GEMINI_API_KEY=) so demo_mode activates
- Kept SARVAM_API_KEY for STT and TTS (bulbul_tts now defined in app.py)
- Fixed missing bulbul_tts() function definition in app.py (line 217)
- App runs in demo mode: RAG retrieval + source citation works; LLM answers show demo message
- To enable full LLM answers: set GEMINI_API_KEY or GROQ_API_KEY in .env
- To run: source .venv/Scripts/activate; python app.py; open http://127.0.0.1:5000
- Data folder (data/) and RAG store (my_db/) are present; rebuild with /rebuild if needed
- .env credentials should NOT be committed (already in .gitignore)
