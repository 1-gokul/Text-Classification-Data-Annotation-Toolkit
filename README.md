# Text Classification & Data Annotation Toolkit

A Python-based ML data pipeline for **classifying, annotating, auditing, and tracking** Business-to-Business (B2B) product catalog data. Built to simulate real-world data operations for large-scale product classification tasks across industrial, scientific, office, and safety product categories.

---

## Overview

This project addresses four core challenges in B2B data annotation workflows:

| Challenge | Module |
|-----------|--------|
| Classify product listings using configurable rule sets | `classify.py` |
| Manually annotate products through a guided CLI session | `annotator.py` |
| Track daily annotation progress and SLA compliance | `tracker.py` |
| Audit label quality and flag classification mismatches | `audit.py` |

---

## Project Structure

```
text-classification-annotation-toolkit/
├── classify.py             # Rule-based product classifier
├── annotator.py            # Interactive CLI annotation tool
├── tracker.py              # Daily progress tracker & report generator
├── audit.py                # Quality audit & escalation logger
├── requirements.txt        # No external dependencies (stdlib only)
│
├── rules/
│   └── classification_rules.json   # Configurable keyword rule sets
│
├── data/
│   └── sample_products.csv         # Sample B2B product listings
│
└── tracker/                        # Auto-created at runtime
    ├── daily_tracker.csv
    ├── progress_report.txt
    ├── audit_log.csv
    └── audit_summary.txt
```

---

## Setup

Python 3.8+ required. No external packages needed.

```bash
git clone https://github.com/<your-username>/text-classification-annotation-toolkit.git
cd text-classification-annotation-toolkit
```

---

## Usage

### Step 1 — Classify Products

Applies keyword-based rule sets to auto-classify all products in the dataset.

```bash
python classify.py
# Output: data/classified_products.csv
```

Custom paths:
```bash
python classify.py --input data/sample_products.csv --output data/classified_products.csv --rules rules/classification_rules.json
```

### Step 2 — Annotate Products

Interactive CLI session to manually label each product. Annotated records are logged to the daily tracker.

```bash
python annotator.py
# Output: tracker/daily_tracker.csv
```

### Step 3 — Track Progress

Generates a daily breakdown report with SLA compliance status.

```bash
python tracker.py
# Output: tracker/progress_report.txt
```

Set a custom daily target:
```bash
python tracker.py --target 15
```

### Step 4 — Run Quality Audit

Validates all annotation records for label integrity, completeness, and classifier mismatches. Produces an escalation-ready audit log.

```bash
python audit.py
# Output: tracker/audit_log.csv, tracker/audit_summary.txt
```
Deploying on hugging face!
---

## Product Categories

Products are classified into 8 categories based on configurable keyword rule sets:

- Office Supplies
- Industrial Equipment
- Scientific Instruments
- Safety & PPE
- Electronics
- Furniture
- Cleaning Supplies
- Other / Uncategorized

To add or modify classification rules, edit `rules/classification_rules.json`.

---

## Key Features

- **Rule Set Management** — JSON-based category rules, easy to extend and version-control
- **Annotation Tracking** — Daily tracker CSV with timestamps, confidence levels, and annotator notes
- **SLA Reporting** — Per-day task counts with pass/miss status against configurable targets
- **3-Layer Quality Audit** — Label integrity, completeness checks, and classifier-vs-human mismatch detection
- **Escalation Logging** — Flagged issues written to `audit_log.csv` with severity levels (HIGH / MEDIUM)
- **Zero Dependencies** — Pure Python standard library

---

## Example Classifier Output

```
[INFO] Loaded 7 category rule sets from 'rules/classification_rules.json'
[DONE] 20 products classified.
       Uncategorized: 0
       Output saved → data/classified_products.csv

--- Classification Summary ---
  Industrial Equipment         ████ (4)
  Scientific Instruments       ████ (4)
  Safety & PPE                 ███ (3)
  Electronics                  ███ (3)
  Office Supplies              ██ (2)
  Furniture                    ██ (2)
  Cleaning Supplies            ██ (2)
```

---

## Skills Demonstrated

- Natural language and text data annotation
- Rule set design and management for multi-class classification
- Data quality auditing and inconsistency detection
- Task tracking and SLA-aligned progress reporting
- Python-based data pipeline development (stdlib only)
