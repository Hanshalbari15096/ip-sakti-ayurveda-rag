# IP-SAKTI YouTube Video — Visual Assets, Slides & Image Prompts (YT_resources)

A comprehensive breakdown of all graphics, slides, overlays, diagrams, and AI image prompts needed to produce the IP-SAKTI video.

---

## 1. Video Thumbnail

* **Asset Type**: 16:9 YouTube Thumbnail (1920x1080)
* **Visual Composition**:
  * **Left 50%**: Ancient Sanskrit Ayurvedic palm-leaf manuscript with turmeric and medicinal herbs, warm golden lighting.
  * **Right 50%**: Modern dark-mode glowing AI cybersecurity/legal shield dashboard with neural network nodes.
  * **Center / Overlay**: High-contrast bold text with subtle glowing drop-shadow: `"AI SHIELD FOR AYURVEDA"` and sub-badge `"SIH 2026 | IP-SAKTI"`.
* **AI Image Generation Prompt (Midjourney / Flux / DALL-E 3)**:
  > `YouTube thumbnail 16:9, dramatic split screen. Left side shows an ancient Indian Ayurveda palm-leaf manuscript on aged parchment with raw turmeric root and sacred herbs under warm sacred temple light. Right side shows a futuristic glowing holographic AI shield interface with neon cyan and saffron data nodes, neural connections, and legal compliance graphs. Highly detailed, cinematic lighting, 8k resolution, photorealistic, sharp contrast, vibrant modern tech aesthetics --ar 16:9 --style raw`

---

## 2. Segment 1: [0:00 - 0:30] Hook — Biopiracy Defense

### Asset 1.1: Vintage Newspaper Clipping — US Turmeric Patent Dispute
* **Asset Type**: High-resolution historical graphic / mock news clipping
* **Visual Content**: Headline: *"US Patent Office Revokes Turmeric Patent After India Proves Ancient Prior Art"*, yellowed 1995 newspaper texture, archival stamp.
* **AI Generation Prompt**:
  > `Vintage 1990s newspaper front-page clipping headline 'US Patent Office Cancels Turmeric Patent in Landmark Battle with India', aged yellowed paper texture, historical journalism photograph of turmeric root in laboratory, bold black letterpress typography, archival document style --ar 16:9`

### Asset 1.2: Vintage Newspaper Clipping — Neem Patent Revocation
* **Asset Type**: Mock news clipping / editorial visual
* **Visual Content**: Headline: *"European Patent Office Overturns Neem Tree Patent — 10-Year Victory Against Biopiracy"*.
* **AI Generation Prompt**:
  > `Macro close-up shot of an international intellectual property legal document with a heavy red 'PATENT REVOKED' rubber stamp over botanical drawings of the Neem plant (Azadirachta indica), legal seal of EPO and Indian Patent Office, documentary evidence style, dramatic side lighting --ar 16:9`

### Asset 1.3: Animated Stat Card Overlay
* **Asset Type**: Transparent Motion Graphic / Lower Third
* **Text / Content**:
  * Large Stat: `2,000+`
  * Subtext: `Documented Biopiracy Attempts on Traditional Indian Knowledge Worldwide`
  * Highlight badge: `Threat: High`

---

## 3. Segment 2: [0:30 - 1:15] The Problem — Regulatory Maze

### Asset 2.1: Rapid-Flash Legal Statute Cards (Canva / PPT / Graphics)
* **Asset Type**: 8 Kinetic Typography / Glassmorphism Badge Overlays (Transparent PNG / 1920x1080)
* **Content List for Cards**:
  1. `Patents Act, 1970 — Section 3(p) & 3(d)` (Red Tag: Non-Patentable Traditional Knowledge)
  2. `Biological Diversity Act, 2002` (SBB / NBA Clearances)
  3. `Geographical Indications (GI) of Goods Act, 1999`
  4. `TRIPS Agreement — Article 27.3(b)` (WTO Standards)
  5. `Nagoya Protocol on Access & Benefit Sharing (ABS)`
  6. `WIPO GRATK Treaty 2024` (Mandatory Genetic Resource Disclosure)
  7. `Drugs & Cosmetics Act, 1940 (Schedule E(1) & GMP)`
  8. `FSSAI Ayurveda Aahar Regulations, 2022`

### Asset 2.2: The 3 Core Pain Points Slide
* **Asset Type**: Slide / Full-Screen Graphic
* **Header**: `The Ayurveda Innovation Barrier`
* **Layout**: 3 Columns with warning icons:
  * **Column 1 (Practitioners)**: `Legal Blindspot` — Lack awareness of Section 3(p) TK exclusions; risk rejection.
  * **Column 2 (Startups)**: `Classification Dilemma` — Cannot determine if formula is Classical, PAM, or Phytopharmaceutical.
  * **Column 3 (MSMEs & Exporters)**: `ABS Non-Compliance` — Shipments seized & licenses denied under Nagoya Protocol / NBA rules.
* **AI Generation Prompt (Background Concept)**:
  > `A clean dark-blue minimalist legal tech infographic background with subtle geometric nodes, glassmorphic card containers, saffron and white accent lines, professional enterprise UI aesthetic --ar 16:9`

---

## 4. Segment 3: [1:15 - 2:00] Solution Overview & Architecture

### Asset 3.1: IP-SAKTI System Architecture Diagram
* **Asset Type**: High-Resolution Vector Diagram (From Slide 3 of Presentation)
* **Visual Flow**:
  1. **User Layer**: Voice / Text Input (9 Indic Languages + English) → Sarvam AI STT & Groq Whisper.
  2. **Orchestration / API Layer**: FastAPI Gateway + Jurisdiction Router (`India` vs `International`).
  3. **Retrieval Engine**: Hybrid Dense Vector Search (ChromaDB + MiniLM-L12-v2) + In-Memory BM25 Keyword Search fused via Reciprocal Rank Fusion (RRF).
  4. **Corpus Base**: Statutory Acts, Drug Rules, Case Law, AYUSH Formularies, TKDL Indices.
  5. **Generation & Verification**: Gemini 2.5 Flash / Groq LLM + Source Attribution + Confidence Scorer + TKDL Guardrails.
  6. **Output Layer**: Citation-grounded Bullets + Bulbul Indic TTS Audio Readout.

### Asset 3.2: 6 Core Feature Icon Cards (Lower-Third / Grid)
* **Asset Type**: 6 Glassmorphic Feature Badges (Icons + 1-Line Description)
  * 🌐 **1. Jurisdiction Toggle**: Zero cross-jurisdiction hallucination (India vs International).
  * 🗣️ **2. 9 Indic Languages**: Voice-In and Voice-Out (Hindi, Marathi, Sanskrit, Tamil, etc.).
  * 📜 **3. Citation Grounding**: Every bullet backed by exact statute/case metadata.
  * 🧪 **4. Formulation Classifier**: 4-step decision tree for Classical / PAM / Phytopharm / Cosmetic.
  * 📋 **5. ABS Compliance Wizard**: Step-by-step PIC → MAT → NBA approval tracker.
  * 👥 **6. Human Escalation**: 1-click links to registered patent agents, NBA, and NALSA.

### Asset 3.3: Technology Stack Banner
* **Asset Type**: Horizontal Tech Logo Strip
* **Logos / Badges**: `FastAPI` | `ChromaDB` | `Sentence-Transformers` | `Google Gemini` | `Groq Cloud` | `Sarvam AI`

---

## 5. Segment 4: [2:00 - 4:30] Live Demo Visual Assets

### Asset 4.1: Browser Screen Setup (1920x1080 @ 125% Zoom)
* **Screen 1**: Portal Homepage (`http://127.0.0.1:5000`) with AYUSH Ministry theme and chat trigger.
* **Screen 2**: Text Query & Citation Result with split panels (`India Sources` vs `International Sources`).
* **Screen 3**: Voice Dialog Overlay showing interactive waveform and Hindi speech recognition.
* **Screen 4**: Formulation Wizard Interactive Modal (4 Steps).
* **Screen 5**: ABS Compliance Checklist with live dynamic percentage progress bar.
* **Screen 6**: Human Escalation Modal with direct links to `ipindia.gov.in`, `nba.india.gov.in`, etc.
* **Screen 7**: REST API JSON Endpoints (`/health`, `/stats`, `/corpus-version`, `/languages`).

---

## 6. Segment 5: [4:30 - 5:15] Impact & Feasibility Slide

### Asset 6.1: Feasibility & Viability Slide (Slide 4 in SIH Format)
* **Asset Type**: 2-Column Pitch Slide
* **Left Column (Technical Feasibility)**:
  * Zero research risk — mature stack (FastAPI, ChromaDB, Gemini/Groq).
  * 100% open government legal corpus (Patent Act, BD Act, API, TKDL public records).
  * Runs on lightweight cloud ($30/mo, zero dedicated GPU overhead).
  * Production ready in 6–8 weeks with 2–3 developers.
* **Right Column (Ecosystem Impact)**:
  * 50,000+ AYUSH startups, researchers & MSMEs empowered.
  * Prevents biopiracy via instant TKDL prior-art checks.
  * Solves export compliance under Nagoya Protocol / ABS guidelines.
  * Preserves and democratizes Sanskrit/vernacular heritage.

---

## 7. Segment 6: [5:15 - 5:30] Roadmap & Closing End Card

### Asset 7.1: 3-Stage Development Roadmap Infographic
* **Asset Type**: Horizontal 3-Phase Stepper Graphic
  * 🟢 **Stage 1 (Completed / MVP)**: Multilingual RAG Assistant + Citation Retrieval + Hybrid Search + Voice I/O.
  * 🟡 **Stage 2 (Next 3 Months)**: Knowledge Graph integration for Multi-hop Ayurvedic formulation reasoning & TKDL API sync.
  * 🔵 **Stage 3 (Production Scale)**: Direct integration into National AYUSH Portal & e-filing Patent Examiner toolset.

### Asset 7.2: Video End Card / Outro Slide
* **Asset Type**: 16:9 Video End Screen (1920x1080)
* **Content Layout**:
  * **Title**: `IP-SAKTI: AI Shield for Ayurveda`
  * **Team**: `Team VedaVanguard`
  * **SIH Problem Statement**: `SIH26045`
  * **Theme**: `Healthcare & Traditional Knowledge`
  * **GitHub / Contact**: Repo link + Ministry of AYUSH acknowledgement
* **AI Image Generation Prompt (Outro Background)**:
  > `Modern Indian national digital emblem style background, subtle saffron and deep navy blue gradients, clean tech typography placeholder space, glowing traditional lotus and neural network fusion motif, elegant and professional hackathon closing screen --ar 16:9`

---

## Quick Reference Summary Table

| Segment | Timing | Key Visual Asset | Format |
|---|---|---|---|
| **1. Hook** | 0:00 - 0:30 | Turmeric & Neem Patent News Clippings | Mock Images + Stat Overlay |
| **2. Problem** | 0:30 - 1:15 | 8 Legal Acts Flash Badges & 3 Pain Points Slide | Slide / Kinetic Badges |
| **3. Solution** | 1:15 - 2:00 | Architecture Diagram + 6 Feature Icons | Diagram + Logo Strip |
| **4. Live Demo**| 2:00 - 4:30 | Live Screen Capture (Webcam PiP bottom-right) | 1080p Screen Recording |
| **5. Impact** | 4:30 - 5:15 | Feasibility & Impact 2-Column Matrix | High-contrast Pitch Slide |
| **6. Closing** | 5:15 - 5:30 | 3-Stage Roadmap + End Card (Team VedaVanguard) | Stepper Graphic + End Screen |
| **Thumbnail** | - | Split Screen: Palm-leaf Manuscript vs AI Shield | 1920x1080 YouTube Banner |
