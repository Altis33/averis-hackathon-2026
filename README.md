# Shipping Document Verification Pipeline

Welcome to our hackathon submission! We have built a lightweight, highly reliable, and purely programmatic Python pipeline to solve the Shipping Document Verification challenge. 

Our solution successfully tackles the **Advanced Stage** challenges (messy inputs, PDF/Word/Excel extraction, and human-in-the-loop reliability) and achieves an **82% End-to-End Score**.

## 🚀 How to Run the Code

To process the dataset and generate the final output, simply run the unified pipeline script from the root directory:

```bash
pip install pypdf docx2txt openpyxl
python3 pipeline.py
```

This will automatically process all emails in the `sdoc-hackathon-bundle` dataset and generate the final **`submission_final.json`**.

---

## 📂 Project Structure (Where to look)

To keep things modular and easy to evaluate, we split the logic into four core engines located in the root directory:

### 1. `classification.py` (Part A: Inbox Routing)
Handles the Stage 1 email classification. Uses smart keyword heuristics on email subjects, bodies, and attachment names to correctly route emails into the 5 categories (achieving ~90% accuracy).

### 2. `doc_parser.py` (Advanced Stage: File Attachments)
Bypasses the basic plain-text assumption. It dynamically detects file extensions and uses standard libraries (`pypdf`, `docx2txt`, `openpyxl`) to extract raw text and tables directly from realistic PDFs, Word Docs, and Excel files.

### 3. `extraction.py` (Part B: Data Extraction & Messy Inputs)
Uses highly relaxed regular expressions. Instead of breaking on formatting differences (e.g., "Load Port" vs "Port of Loading", or missing colons), it seamlessly aligns varied labels to the 7 core fields.

### 4. `comparison.py` (Part C: Comparison & Reliability)
The decision engine. It normalizes strings (stripping punctuation, harmonizing casing) and checks for substring containment to compare SI and BL fields accurately. 
**Human-in-the-loop:** It also contains our reliability safety nets, successfully escalating 100% of unreadable documents, missing attachments, and wrong document types to `NEEDS_REVIEW`.

---

## 📊 Evaluation

If you have the local scoring server running, you can verify our results by running:
```bash
python3 sdoc-hackathon-docker/server/score_cli.py submission_final.json
```
