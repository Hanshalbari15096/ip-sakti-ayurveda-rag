 # IP-SAKTI YouTube Video — Full Production Script (Balanced 5:15 Edition)
# Duration: ~5:15 | Target Word Count: ~775 words (~140 wpm + live demo pacing)
# ==============================================================================

## PRE-PRODUCTION CHECKLIST
1. Verify API keys in `.env` (`GEMINI_API_KEY`, `SARVAM_API_KEY`).
2. Start server: `./.venv/Scripts/python.exe app.py` (Confirm `http://127.0.0.1:5000/health` -> `demo_mode: false`).
3. Browser: Zoom to 125%, clean light theme, tabs pre-opened for APIs and presentation.
4. OBS Studio: 1920x1080, 30fps, 6000kbps, Screen + Webcam PiP (bottom-right, 25%).
5. Have `Actual Presentation.pdf` or slide PNG ready for the architecture segment.

---

## SHOT-BY-SHOT SCRIPT

### [0:00 - 0:35] HOOK: The Biopiracy Threat (35 sec | ~85 words)
**Camera**: Direct to camera (Webcam face) -> Quick cuts to archival patent clippings

**NARRATION (Confident, engaging)**:
> "In 1995, the US Patent Office granted a patent on turmeric for wound healing — something documented in ancient Indian texts for thousands of years. India spent crores and years in legal battles to revoke it. The Neem tree patent battle lasted a full decade.
> 
> Even today, over two thousand attempts to patent traditional Indian knowledge have been documented worldwide.
> 
> To protect our heritage, we built **IP-SAKTI** — an AI-powered multilingual shield against biopiracy and a regulatory guide for Ayurvedic innovation."

**VISUALS**:
- **0:00 - 0:08**: Direct eye contact on camera.
- **0:08 - 0:18**: Split-screen flash of vintage Turmeric & Neem patent revocation newspaper clippings.
- **0:18 - 0:26**: Animated motion card: `2,000+ Biopiracy Attempts Documented Worldwide`.
- **0:26 - 0:35**: Cut to IP-SAKTI logo & portal landing page.

---

### [0:35 - 1:20] THE PROBLEM: The Regulatory Maze (45 sec | ~120 words)
**Camera**: Webcam PiP + Kinetic Statute Overlays & 3-Column Problem Slide

**NARRATION**:
> "Bringing an Ayurvedic formulation to market today is a legal minefield. Innovators must navigate the Patents Act, the Biological Diversity Act, the Nagoya Protocol, Drugs and Cosmetics rules, and international treaties — all at once.
> 
> Most practitioners don't know that traditional remedies are strictly non-patentable under Section 3(p). Startups waste months struggling to figure out whether their product is a Classical formulation, a Proprietary medicine, or a Phytopharmaceutical requiring clinical trials. And MSMEs risk export seizures because they missed mandatory Access and Benefit Sharing clearances.
> 
> There has never been an intelligent, accessible guidance tool for them — until now."
 
**VISUALS**:
- Flash statute cards: `Patents Act Section 3(p)`, `Biological Diversity Act 2002`, `Nagoya Protocol ABS`, `WIPO GRATK 2024`.
- 3-column breakdown:
  - **Practitioners**: *Legal Blindspot on Section 3(p)*
  - **Startups**: *Formulation Classification Confusion*
  - **Exporters**: *ABS Non-Compliance & Seizure Risks*

---

### [1:20 - 2:05] SOLUTION & ARCHITECTURE (45 sec | ~130 words)
**Camera**: Full Slide / Architecture Diagram (from Slide 3 of Presentation)

**NARRATION**:
> "IP-SAKTI is a multilingual RAG-based AI assistant specifically engineered for Ayurveda intellectual property and regulatory compliance.
> 
> Here is how the system works. A user submits a query via text or voice in any of 9 Indian languages. Our hybrid retrieval engine combines dense vector search using MiniLM embeddings with sparse BM25 keyword search, fused via Reciprocal Rank Fusion.
> 
> It retrieves verified clauses from our curated statutory corpus — including Indian acts, case law, AYUSH formularies, and TKDL indices.
> 
> The context passes to Gemini with strict jurisdiction filtering — separating India from International rules — ensuring every single response is grounded in real statutory citations with zero legal hallucination."

**VISUALS**:
- Trace the architecture flow:
  `Voice/Text (9 Languages) → Sarvam STT → Hybrid RRF (ChromaDB + BM25) → Gemini 2.5 Flash → Cited Output + Bulbul TTS`.
- Lower-third tech badges: `FastAPI | ChromaDB | Gemini 2.5 Flash | Groq | Sarvam AI`.

---

### [2:05 - 4:20] LIVE DEMO (2 min 15 sec | ~260 words + UI actions)
**Camera**: Screen Recording (1080p @ 125% zoom) + Webcam PiP bottom-right

#### 1. Portal Overview (15 sec)
**Action**: Show `http://127.0.0.1:5000`, open chat widget.
**NARRATION**:
> "Let's see it in action. Here is the AYUSH-styled portal. Opening the chat widget reveals our jurisdiction toggle, safety disclaimers, and dedicated compliance tools."

#### 2. India Legal Query & Citation Grounding (30 sec)
**Action**: Set Jurisdiction to `India`. Type: *"How do I patent an Ayurvedic formulation?"*
**NARRATION**:
> "Let's ask how to patent an Ayurvedic formulation under Indian law.
> 
> Notice how the answer is structured: it immediately cites Section 3(p) of the Patents Act, clarifying that traditional knowledge cannot be patented. It highlights TKDL prior art search requirements and novel extraction methods. Every point is backed by verifiable source citations with exact relevance scores."

#### 3. Multilingual Voice I/O in Hindi (35 sec) — *WOW MOMENT*
**Action**: Click mic (🎤) → Select `Hindi` → Speak: *"आयुर्वेदिक दवा का पेटेंट कैसे करें?"* → Send.
**NARRATION**:
> "Now let's test voice in Hindi. Sarvam AI transcribes our speech in real time, the retrieval engine pulls the Hindi-relevant legal context, and Gemini generates the answer. And listen to this..."
*(Pause 4 seconds while the Hindi audio response plays clearly).*
> "...it reads the complete legal guidance back in natural Hindi. With support for 9 Indian languages, IP-SAKTI breaks the English-only barrier for grassroots practitioners."

#### 4. Formulation Classifier Decision Tree (30 sec)
**Action**: Click *Formulation Classifier* → Walk through the 4 steps:
1. `Not in authoritative text` → No
2. `New ingredient` → Yes
3. `Standardized extract` → Yes
4. `Treats disease` → View Result
**NARRATION**:
> "Next is the Formulation Classifier. This 4-step wizard translates complex Drug & Cosmetics rules into a simple decision tree.
> 
> For our inputs, it correctly classifies the product as Proprietary Ayurvedic Medicine, outlines DCGI approval requirements, and automatically flags mandatory biological resource disclosure rules."

#### 5. ABS Checklist & Human Escalation (25 sec)
**Action**: Open *ABS Checklist* → Check 2 items → Click *Check Compliance* → Switch to *Escalate to Human*.
**NARRATION**:
> "For exporters, the ABS Wizard tracks Prior Informed Consent and State Biodiversity Board approvals step by step.
> 
> And because legal safety comes first, when an issue requires formal representation, the Escalate tool connects users directly to registered patent attorneys, the National Biodiversity Authority, and NALSA free legal aid."

---

### [4:20 - 4:55] IMPACT & FEASIBILITY (35 sec | ~110 words)
**Camera**: Direct to Camera (Face) + Dynamic Metric Cards

**NARRATION**:
> "IP-SAKTI is built for immediate real-world deployment.
> 
> Technically, it carries zero research risk — leveraging a mature, production-tested stack that runs on lightweight cloud infrastructure for under $30 a month with no expensive GPU requirements.
> 
> Economically and socially, it empowers over 50,000 AYUSH startups, researchers, and traditional healers across India. It prevents biopiracy before filing, ensures export compliance under global biodiversity treaties, and preserves India's sovereign traditional knowledge in the digital era."

**VISUALS**:
- Display 4 key metrics:
  - ⚡ `Zero GPU Overhead | <$30/mo Cloud`
  - 🏛️ `100% Open Statutory & TKDL Datasets`
  - 👥 `50,000+ AYUSH Innovators & MSMEs`
  - 🌐 `9 Vernacular Languages Supported`

---

### [4:55 - 5:20] ROADMAP & CONCLUSION (25 sec | ~70 words)
**Camera**: Direct to Camera (Face) → End Screen

**NARRATION (Strong, memorable closing)**:
> "Our working MVP is live today. Our next phase introduces Knowledge Graph multi-hop reasoning and direct integration into the National AYUSH Portal and patent office systems.
> 
> India's traditional knowledge is priceless. IP-SAKTI ensures it stays protected, accessible, and legally defended.
> 
> Thank you."

**VISUALS**:
- **0:00 - 0:12**: 3-Stage Development Stepper:
  - `Stage 1: Multilingual RAG MVP [Completed]`
  - `Stage 2: Knowledge Graph & TKDL API [Next 3 Months]`
  - `Stage 3: National AYUSH Portal Integration [Production]`
- **0:12 - 0:25**: Video Outro End Card:
  - `Project: IP-SAKTI (AI Shield for Ayurveda)`
  - `Team: VedaVanguard | SIH 2026 | Problem ID: SIH26045`
  - `GitHub: [Repository Link]`

---

## TIMING & WORD BUDGET RECAP
| Section | Timestamp | Word Count | Focus |
|---|---|---|---|
| **1. Hook** | 0:00 - 0:35 | ~85 words | Turmeric/Neem biopiracy cases & IP-SAKTI intro |
| **2. Problem** | 0:35 - 1:20 | ~120 words | Section 3(p), classification, and ABS export risks |
| **3. Architecture** | 1:20 - 2:05 | ~130 words | Hybrid RRF, ChromaDB, Gemini, and guardrails |
| **4. Live Demo** | 2:05 - 4:20 | ~260 words | Text query, Hindi voice I/O, classifier, ABS, escalation |
| **5. Impact** | 4:20 - 4:55 | ~110 words | $30/mo cost, zero GPU, 50k MSMEs empowered |
| **6. Closing** | 4:55 - 5:20 | ~70 words | Roadmap, heritage protection, end card |
| **Total** | **5:20** | **~775 words** | **Perfect ~140 wpm natural speaking pace** |
