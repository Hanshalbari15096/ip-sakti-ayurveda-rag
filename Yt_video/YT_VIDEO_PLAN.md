YT VIDEO PLAN: IP-SAKTI Ayurveda IPR Assistant (SIH 2026)
==========================================================

Target: 5-6 min video | SIH 2026 submission + YouTube portfolio piece
Goal: Impress judges/viewers with problem clarity, working demo, and technical depth


THUMBNAIL IDEA
--------------
- Split screen: ancient Ayurveda manuscript on left, glowing AI chat interface on right
- Text overlay: "AI Protects India's Ayurveda Knowledge"
- Use Ashoka emblem or AYUSH logo vibe (stylized, not actual govt logos)


VIDEO STRUCTURE (5:30 total)
================================

[0:00 - 0:30] HOOK (30 sec)
----------------------------
Open with a SHOCK FACT — grab attention in 5 seconds:

  "The US Patent Office once granted a patent on turmeric wound healing —
   knowledge every Indian grandmother already knew. India spent crores and
   years to revoke it. 2000+ such attempts are still happening worldwide.
   We built IP-SAKTI — an AI shield against biopiracy."

Overlay: newspaper clippings of turmeric/neem patent cases
Quick cut to IP-SAKTI logo


[0:30 - 1:15] THE PROBLEM (45 sec)
------------------------------------
Fast, visual — use text overlays, not just talking:

  "Protecting Ayurvedic innovation means navigating:"
  - Flash on screen one by one (1-2 sec each):
    Patents Act Section 3(p) | Biological Diversity Act | GI Registry |
    TRIPS | Nagoya Protocol | WIPO GRATK Treaty 2024 | Drug regulations
  "...all at once. In 22+ languages. With zero guidance tools available."

  "Practitioners don't know their IP rights.
   Startups can't classify their formulations.
   MSMEs lose export markets from ABS non-compliance.
   No tool exists to help them. Until now."


[1:15 - 2:00] SOLUTION OVERVIEW (45 sec)
-----------------------------------------
Show architecture diagram on screen while narrating:

  "IP-SAKTI is a multilingual, RAG-based AI assistant for Ayurveda IPR."

  Flash 6 features (icon + one-liner each):
  1. Jurisdiction toggle — India vs International, never conflated
  2. 9 Indian languages — voice in, voice out (Sarvam AI + Groq Whisper)
  3. Source-cited answers — every bullet traces to a statute or treaty
  4. Formulation Classifier — Classical / PAM / Phytopharm / Cosmetic
  5. ABS Compliance Checklist — PIC -> MAT -> NBA step-by-step
  6. Human escalation — connects to real IP attorneys when AI isn't enough

  Tech stack flash (3 sec):
  FastAPI | ChromaDB | MiniLM-L12-v2 | Gemini/Groq | Sarvam AI


[2:00 - 4:30] LIVE DEMO (2 min 30 sec) — THE MONEY SHOT
---------------------------------------------------------
Screen recording + webcam overlay. Move fast, no dead air.

Demo 1: Landing page + chat widget (15 sec)
  - Open http://127.0.0.1:5000 — show AYUSH-styled interface
  - Click chat toggle — point out jurisdiction dropdown, tool buttons, disclaimer

Demo 2: Text query — India (30 sec)
  - Jurisdiction: India
  - Type: "How do I patent an Ayurvedic formulation?"
  - Show response: bullet points, source citations, confidence badge
  - Narrate: "It cites Section 3(p), points to TKDL — all grounded in real statutes"

Demo 3: Voice query — Hindi (30 sec) — BIG WOW MOMENT
  - Click mic, speak: "आयुर्वेदिक दवा का पेटेंट कैसे करें?"
  - Show transcription + answer + audio playback
  - Narrate: "Speak Hindi in, get Hindi answer read back. Works for 9 languages."

Demo 4: Formulation Classifier (30 sec)
  - Click "Formulation Classifier"
  - Speed through 4 questions:
    Not in authoritative text -> New ingredient -> Standardized -> Treats disease
  - Show result: "Proprietary Ayurvedic Medicine" + regulatory path + ABS check

Demo 5: ABS Checklist + Escalation (25 sec)
  - Click ABS Checklist — show step-by-step PIC -> MAT -> NBA, progress %
  - Click Escalate — show contacts: Patent Agents, NBA, GI Registry, NALSA, TKDL
  - "When AI isn't enough, we connect you to real experts"

Demo 6: API (20 sec)
  - Flash /health, /stats, /corpus-version in browser tabs
  - "Full REST API — embed in any government portal"


[4:30 - 5:15] IMPACT & FEASIBILITY (45 sec)
---------------------------------------------
Rapid-fire, text on screen:

  WHY IT WORKS:
  - Zero research risk — mature stack, no GPU needed
  - 100% open/government corpus — no licensing issues
  - Runs on $30/month cloud
  - 2-3 devs, production-ready in 6-8 weeks

  WHO BENEFITS:
  - 50K+ AYUSH practitioners, startups, MSMEs
  - Prevents biopiracy via automated TKDL checks
  - Enables Nagoya Protocol / ABS export compliance
  - Bridges language barrier — Sanskrit to Gujarati


[5:15 - 5:30] CLOSING (15 sec)
-------------------------------
  Show 3-stage roadmap as graphic (3 sec):
    Stage 1: RAG MVP [DONE]  ->  Stage 2: Knowledge Graph  ->  Stage 3: Production

  Closing line (deliver to camera):
  "India's traditional knowledge is priceless. IP-SAKTI ensures it stays
   protected, accessible, and never stolen again."

  End card: Team VedaVanguard | SIH 2026 | Problem ID 26045


=====================================
RECORDING TIPS
=====================================

1. SCREEN RECORDING:
   - OBS Studio (free) — screen + webcam picture-in-picture
   - 1920x1080, 6000kbps
   - Record audio separately if possible

2. BEFORE RECORDING THE DEMO:
   - .env must have valid GEMINI_API_KEY or GROQ_API_KEY (not demo mode)
   - Start server: python app.py
   - Test ALL queries beforehand — know exactly what comes back
   - Clear browser cache, close notifications
   - Zoom browser to 125% for readability

3. EDITING:
   - CapCut (free) or DaVinci Resolve
   - Speed up typing/loading — zero dead air in a 5-min video
   - Lower-third section titles
   - Subtle background music (YouTube Audio Library, royalty-free)
   - Text overlays for stats (2000+ patents, $6M, 50K+ users)

4. TALKING STYLE:
   - Fast but clear — 5 min means no fluff
   - "We built" not "I built"
   - Confident, not salesy
   - Camera during non-demo, screen during demo


=====================================
DEMO PREPARATION CHECKLIST
=====================================

[ ] Server starts without errors (python app.py)
[ ] /health returns status:ok, demo_mode:false
[ ] Text query works (India + International)
[ ] Voice input records and transcribes
[ ] Formulation classifier completes all 4 steps
[ ] ABS checklist shows progress
[ ] Escalation shows all 6 contacts
[ ] /stats, /corpus-version, /languages work

Get free API key before recording:
  Gemini: https://aistudio.google.com/
  Groq:   https://console.groq.com/
