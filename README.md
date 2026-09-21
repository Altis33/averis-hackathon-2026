# 🐰 Snowbunnies — Shipping Document Verification System

An automated pipeline that reads a shipping operations inbox and, for each email, classifies it, extracts shipment data from attached documents, and compares Shipping Instructions (SI) against draft Bills of Lading (BL) to catch discrepancies before the draft is finalised.

**Final Score: 82% end-to-end accuracy**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the web UI
streamlit run app.py

# 3. (Optional) Run the headless pipeline
python3 pipeline.py
```

---

## 📂 Project Structure

```
Hackathon/
├── app.py                  # Streamlit web UI (main entry point)
├── pipeline.py             # Headless end-to-end pipeline (generates submission JSON)
│
├── classification.py       # Stage 1: Email classification (5 categories)
├── doc_parser.py           # Document parser (PDF, DOCX, XLSX, TXT)
├── extraction.py           # Stage 2: Field extraction (7 shipping fields)
├── comparison.py           # Stage 3: SI vs BL comparison & escalation logic
├── llm_extraction.py       # AI-enhanced extraction (OpenAI GPT / Anthropic Claude)
│
├── requirements.txt        # Python dependencies
├── submission_final.json   # Generated submission output
│
├── sdoc-hackathon-bundle/  # Dataset (emails + attachments)
│   ├── inbox/              # Email JSON records
│   ├── attachments/        # SI and BL documents (txt, pdf, docx, xlsx)
│   ├── loader.py           # Provided data loader
│   └── sample_submission.json
│
└── sdoc-hackathon-docker/  # Scoring server (provided by organisers)
    └── server/
        └── score_cli.py    # Local scoring tool
```

---

## 🏗️ Architecture

The system is split into four independent, modular engines:

| Module | Role | Rubric Criteria |
|---|---|---|
| `classification.py` | Routes emails into BL_COMPARISON, SI_REQUEST, INVOICE_QUERY, GENERAL, SPAM | Stage 1 (30%) |
| `doc_parser.py` | Reads PDF, Word, Excel, and plain-text attachments | Advanced Stage |
| `extraction.py` | Extracts 7 shipping fields using relaxed regex patterns | Stage 2 |
| `comparison.py` | Normalises values and compares SI vs BL, with escalation logic | Stage 3 (20%) + End-to-End (50%) |
| `llm_extraction.py` | Optional GPT / Claude fallback for fields regex cannot extract | Technology Integration |

---

## 🤖 AI / LLM Integration

The system uses a **hybrid approach**:
- **Primary engine**: Fast, deterministic regex-based extraction (zero cost, milliseconds)
- **Fallback layer**: OpenAI GPT-4o-mini or Anthropic Claude Sonnet fills in fields the regex engine missed

Toggle the AI layer on/off in the web UI sidebar under **⚙️ AI Model Settings**.

---

## 📊 Evaluation

```bash
# Score the submission against ground truth
python3 sdoc-hackathon-docker/server/score_cli.py submission_final.json
```

| Metric | Score |
|---|---|
| Classification accuracy | 90.2% |
| Defect recall | 97.8% |
| Defect precision | 81.8% |
| Escalation recall | 75.0% (15/20 edge cases caught) |
| **Final score** | **82.02%** |

---

## 👥 Team

**Snowbunnies** — SDOC Hackathon 2026
