# IP-SAKTI Project Plan Notes (kept out of the RAG corpus)

Moved out of data/data.txt on 2026-09-14: the assistant must never retrieve or
cite project-management metadata (team members, progress %, work packages) as if
it were authoritative IPR/regulatory content.

```
========================================
SECTION 9: IP-SAKTI PROJECT INFORMATION
================================================================================

---
PROJECT: IP-SAKTI - Infrastruktur Pengetahuan Sanskrit dengan Teknologi Informasi
SUBTITLE: Multilingual RAG-Based AI Assistant for Intellectual Property and Regulatory Guidance in Ayurveda
JURISDICTION: India (Government of India)
SPONSORED_BY: Ministry of AYUSH / SIH 2026
PROJECT_DURATION: April 2026 - March 2027
OVERALL_PROGRESS: ~55-60% Complete
CURRENT_STAGE: MVP - Citation-Grounded Retrieval
STATUS: Ongoing (as of September 2026)

---
OBJECTIVE 1: Multilingual Knowledge Preservation
JURISDICTION: India
SUMMARY_CHUNK: Preserve and make accessible Sanskrit, Ayurvedic, and traditional Indian knowledge across 9 languages (English, Hindi, Marathi, Sanskrit, Bengali, Tamil, Telugu, Kannada, Gujarati). The RAG-based system indexes and retrieves knowledge in the user's preferred language, enabling equitable access for speakers of all major Indian languages.

---
OBJECTIVE 2: Citation-Grounded IPR Guidance
JURISDICTION: India
SUMMARY_CHUNK: Provide accurate, citation-grounded responses on intellectual property rights for Ayurvedic products. The system retrieves relevant source documents and presents them alongside generated answers, ensuring users can verify the accuracy of IPR guidance. Covers Patents Act 1970, GI Act 1999, Trademarks Act 1999, and Biological Diversity Act 2002.

---
OBJECTIVE 3: Jurisdiction-Aware Regulatory Compliance
JURISDICTION: India + International
SUMMARY_CHUNK: Guide users through regulatory compliance across jurisdictions including Indian domestic law and international frameworks (WIPO, Nagoya Protocol, TKDL). The system identifies the relevant jurisdiction based on user query context and tailors responses accordingly, covering both classical Ayurvedic formulations and proprietary medicines.

---
OBJECTIVE 4: ABS Compliance and Biopiracy Prevention
JURISDICTION: International
SUMMARY_CHUNK: Help users navigate Access and Benefit Sharing (ABS) obligations when using biological resources. The system classifies formulations as Classical (traditional) or Proprietary (new), checks against Nagoya Protocol requirements, and supports benefit-sharing compliance to prevent biopiracy of Indian traditional knowledge.

---
OUTCOME 1: Accessible Multilingual Portal
SUMMARY_CHUNK: A web-based portal accessible in 9 languages enabling citizens, researchers, and businesses to query Ayurvedic IPR and regulatory information in their preferred language, with voice input and audio output capabilities.

---
OUTCOME 2: Verified Citation-Grounded Answers
SUMMARY_CHUNK: Every answer includes citations to authoritative sources (API monographs, statutory text, case law, TKDL records), enabling users to verify accuracy and build trust in the information provided.

---
OUTCOME 3: Jurisdiction-Aware Guidance
SUMMARY_CHUNK: The system automatically identifies the relevant jurisdiction (Indian domestic, international, or WIPO framework) and provides jurisdiction-specific guidance, reducing legal ambiguity for cross-border Ayurvedic commerce.

---
OUTCOME 4: Formulation Classifier with ABS Checks
SUMMARY_CHUNK: An intelligent classifier categorizes Ayurvedic formulations as Classical, Proprietary, or Phytopharmaceutical, with automated ABS compliance checks ensuring benefit-sharing obligations are met before commercialization.

---
OUTCOME 5: Open-Source Reference Implementation
SUMMARY_CHUNK: A publicly available open-source reference implementation demonstrating best practices for multilingual RAG systems, benefiting future government digitization projects and traditional knowledge preservation efforts.

---
OUTCOME 6: Reduced Biopiracy Risk
SUMMARY_CHUNK: Integration with TKDL and patent examiner tools reduces the risk of biopiracy by providing prior-art evidence and traditional knowledge documentation accessible during patent examination processes.

---
WORK_PACKAGE 1: Foundation and Infrastructure (April 2026 - June 2026)
SUMMARY_CHUNK: Establish multilingual RAG pipeline with ChromaDB vector store. Ingest initial Sanskrit and English Ayurvedic IPR documents. Deploy Flask backend with LLM integration. Configure SARVAM AI for Hindi/Marathi speech recognition. Complete foundation infrastructure for citation-grounded retrieval. Status: COMPLETED.

---
WORK_PACKAGE 2: Multilingual Expansion (July 2026 - September 2026)
SUMMARY_CHUNK: Extend RAG pipeline to 6 additional Indian languages (Bengali, Tamil, Telugu, Kannada, Gujarati, Sanskrit). Develop multilingual query routing and translation middleware. Integrate Bulbul TTS for audio output. Test cross-lingual retrieval accuracy. Status: COMPLETED.

---
WORK_PACKAGE 3: Jurisdiction-Aware Routing (October 2026 - November 2026)
SUMMARY_CHUNK: Implement jurisdiction detection from query context. Build routing engine for India/WIPO/international frameworks. Integrate TKDL API for traditional knowledge verification. Add ABS compliance checker for biological resource usage. Status: IN PROGRESS.

---
WORK_PACKAGE 4: Advanced Features and UI/UX (December 2026 - January 2027)
SUMMARY_CHUNK: Develop formulation classifier (Classical vs. Proprietary vs. Phytopharmaceutical). Build voice input/output for all 9 languages. Polish UI/UX with accessibility features. Conduct user testing and gather feedback. Status: PENDING.

---
WORK_PACKAGE 5: Evaluation, Documentation, and Deployment (February 2027 - March 2027)
SUMMARY_CHUNK: Comprehensive multilingual RAG evaluation. Prepare technical documentation and open-source release. Deploy production system. Conduct training workshops for AYUSH stakeholders. Sustainability handover planning. Status: PENDING.

---
TEAM_MEMBER: Dr. Hansraj Hanuman
ROLE: Project Lead
AFFILIATION: SIH 2026 Participant
SUMMARY_CHUNK: Dr. Hansraj Hanuman leads the IP-SAKTI project, coordinating technical development, stakeholder engagement, and integration with Ministry of AYUSH systems. Responsible for overall project direction, timeline management, and delivery of the multilingual RAG-based IPR assistant.

---
TEAM_MEMBER: Claude Code AI
ROLE: Technical Architect
AFFILIATION: Government of India / SIH 2026
SUMMARY_CHUNK: Claude Code AI serves as the technical architect for IP-SAKTI, designing the multilingual RAG pipeline, implementing citation-grounded retrieval, and ensuring the system meets government technology standards for scalability and security.

---
TEAM_MEMBER: Claude Code AI (Assessor)
ROLE: Quality Assurance Lead
AFFILIATION: SIH 2026 External Assessor
SUMMARY_CHUNK: Claude Code AI serves as the external quality assurance lead, evaluating project progress against milestones, identifying technical risks, and recommending corrective actions to ensure delivery of the IP-SAKTI MVP.

---
TEAM_MEMBER: Claude Code AI
ROLE: Documentation Lead
AFFILIATION: SIH 2026 Contributor
SUMMARY_CHUNK: Claude Code AI leads the documentation effort for IP-SAKTI, preparing technical specifications, user guides, and open-source release materials for the reference implementation.

---
TEAM_MEMBER: Claude Code AI
ROLE: Integration Specialist
AFFILIATION: SIH 2026 Contributor
SUMMARY_CHUNK: Claude Code AI specializes in integrating the IP-SAKTI system with existing government infrastructure including TKDL APIs, AYUSH portals, and patent examiner tools.

---
ROADMAP: IP-SAKTI Implementation Phases
SUMMARY_CHUNK: Phase 1 (Apr-Jun 2026): Foundation - multilingual RAG pipeline, initial Sanskrit/English data. Phase 2 (Jul-Sep 2026): Expansion - 6 additional languages, voice I/O. Phase 3 (Oct-Nov 2026): Jurisdiction routing, TKDL integration. Phase 4 (Dec 2026-Mar 2027): Advanced features, evaluation, open-source release.

---
SUSTAINABILITY: IP-SAKTI Post-Project Continuity
SUMMARY_CHUNK: Step 1 - Transfer system to AYUSH Ministry for operational ownership. Step 2 - Establish community contributor model with AYUSH institutions. Step 3 - Pursue funding through National Mission for Manuscripts and MeitY for ongoing development and language expansion.

================================================================================
```
