# 🐰 Snowbunnies — Shipping Document Verification System

An automated, ultra-high-performance pipeline that processes a shipping operations inbox, classifies incoming messages, extracts shipment metadata from complex multi-format attachments (PDF, Word, Excel, Plain Text), and compares Shipping Instructions (SI) against draft Bills of Lading (BL) to catch discrepancies with 100% precision.

🏆 **Final Hackathon Score: 1.0000 (100.0% Perfect Score)**
- **Stage 1 (Classification F1):** `1.000` (100%)
- **Stage 3 (Defect Detection F1):** `1.000` (100%)
- **Reliability (Edge Case Escalation):** `1.000` (20/20 edge cases caught, 0 false alarms)
- **End-to-End Headline Metric:** `46/46` defect emails caught (100%)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the interactive web UI
streamlit run app.py

# 3. (Optional) Run the headless pipeline
python3 pipeline.py

# 4. Verify against official scoreboard
python3 sdoc-hackathon-docker/server/score_cli.py submission_final.json
```

---

## 📂 Project Structure

```
Hackathon/
├── app.py                  # Streamlit web UI (Team Snowbunnies dashboard)
├── pipeline.py             # Automated end-to-end batch processing pipeline
│
├── classification.py       # Stage 1: Email classification engine (5 categories)
├── doc_parser.py           # Document parser (PDF, DOCX, XLSX, TXT)
├── extraction.py           # Stage 2: Multi-line & multi-format field extraction
├── comparison.py           # Stage 3: Normalisation, comparison & escalation logic
├── llm_extraction.py       # AI-enhanced extraction fallback (GPT-4o-mini & Claude Sonnet)
│
├── requirements.txt        # Reproducible Python dependencies
├── submission_final.json   # Evaluated submission output
│
├── sdoc-hackathon-bundle/  # Inbox dataset & attachments
└── sdoc-hackathon-docker/  # Local evaluation server & ground-truth verifier
```

---

## 🏗️ System Architecture & Rubric Mapping

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Email Inbox (520 emails)                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       [Stage 1: classification.py] ── 100% Accuracy (5 Categories)
       ├── SPAM
       ├── INVOICE_QUERY
       ├── SI_REQUEST
       ├── GENERAL
       └── BL_COMPARISON ──────────────────────────────────┐
                                                           ▼
                                  [doc_parser.py: PDF / DOCX / XLSX / TXT]
                                                           │
                                                           ▼
                                         [Stage 2: extraction.py]
                                         ├── 7 Core Shipping Fields
                                         └── Optional LLM Fallback (OpenAI / Claude)
                                                           │
                                                           ▼
                                         [Stage 3: comparison.py]
                                         ├── Normalisation & Cross-Field Checks
                                         └── Human-in-the-Loop Reliability
                                                           │
                               ┌───────────────────────────┴───────────────────────────┐
                               ▼                                                       ▼
                      Decision: OK / MISMATCH                                Decision: NEEDS_REVIEW
                  (46/46 Defects Detected)                                   (20/20 Edge Cases Caught)
                                                                             ├── wrong_doc_type (5/5)
                                                                             ├── missing_attachment (5/5)
                                                                             ├── unreadable (5/5)
                                                                             └── missing_value (5/5)
```

---

## 📊 Scoreboard Results

```text
==============================================================
  SDOC HACKATHON SCORE  —  submission_final.json
  520 emails
==============================================================

STAGE 1 · Email classification
  accuracy      1.000  ████████████████████████
  macro-F1      1.000  ████████████████████████

  per-category  precision / recall / f1
    BL_COMPARISON   1.00 / 1.00 / 1.00
    SI_REQUEST      1.00 / 1.00 / 1.00
    INVOICE_QUERY   1.00 / 1.00 / 1.00
    GENERAL         1.00 / 1.00 / 1.00
    SPAM            1.00 / 1.00 / 1.00

STAGE 3 · BL-vs-SI comparison  (comparable doc emails)
  defect recall     1.000  ████████████████████████
  defect precision  1.000  ████████████████████████
  field-level F1    1.000  ████████████████████████
  exact-match rate  1.000

RELIABILITY · escalate what you can't decide  (diagnostic)
  escalation recall     1.000  ████████████████████████
  escalation precision  1.000  ████████████████████████
  gold NEEDS_REVIEW: 20   flagged: 20
    wrong_doc_type       5/5 escalated
    missing_attachment   5/5 escalated
    unreadable           5/5 escalated
    missing_value        5/5 escalated

END-TO-END · the headline metric
  46/46 defect emails caught end to end
  rate  1.000  ████████████████████████

--------------------------------------------------------------
  FINAL SCORE  1.0000   (w: s1=0.3, s3=0.2, e2e=0.5)
--------------------------------------------------------------
```

---

## 👥 Team

**Team Snowbunnies** — SDOC Hackathon 2026
