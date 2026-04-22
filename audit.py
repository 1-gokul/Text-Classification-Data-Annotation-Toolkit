"""
audit.py — Quality Audit Module for Data Annotation Toolkit
------------------------------------------------------------
Validates annotation records against:
  1. Valid category rule set (label integrity check)
  2. Classifier predictions (mismatch detection)
  3. Completeness checks (missing fields, empty labels)

Flags issues and saves an escalation-ready audit log.

Usage:
    python audit.py
    python audit.py --annotations tracker/daily_tracker.csv --classified data/classified_products.csv
"""

import csv
import os
import argparse
from datetime import datetime
from collections import Counter


ANNOTATIONS_FILE = "tracker/daily_tracker.csv"
CLASSIFIED_FILE  = "data/classified_products.csv"
AUDIT_LOG_FILE   = "tracker/audit_log.csv"
AUDIT_SUMMARY    = "tracker/audit_summary.txt"

VALID_CATEGORIES = {
    "Office Supplies",
    "Industrial Equipment",
    "Scientific Instruments",
    "Safety & PPE",
    "Electronics",
    "Furniture",
    "Cleaning Supplies",
    "Other",
    "Uncategorized",
}


def load_csv(filepath):
    """Load a CSV file and return list of dicts. Returns [] if file not found."""
    if not os.path.exists(filepath):
        print(f"[WARN] File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_label_integrity(records):
    """
    Check 1: Validate each annotation against the allowed category set.
    Flags records with missing or unrecognized category labels.
    """
    issues = []
    for r in records:
        cat = r.get("annotated_category", "").strip()
        pid = r.get("product_id", "N/A")
        if not cat:
            issues.append({
                "product_id": pid,
                "product_name": r.get("product_name", ""),
                "annotated_category": cat,
                "predicted_category": "",
                "issue_type": "MISSING_LABEL",
                "detail": "Annotated category is empty",
                "severity": "HIGH",
                "timestamp": r.get("timestamp", ""),
            })
        elif cat not in VALID_CATEGORIES:
            issues.append({
                "product_id": pid,
                "product_name": r.get("product_name", ""),
                "annotated_category": cat,
                "predicted_category": "",
                "issue_type": "INVALID_LABEL",
                "detail": f"'{cat}' is not in approved category list",
                "severity": "HIGH",
                "timestamp": r.get("timestamp", ""),
            })
    return issues


def check_classifier_mismatches(annotations, classified):
    """
    Check 2: Compare annotated labels against classifier predictions.
    Flags records where human annotation and rule-based classifier disagree.
    """
    classified_map = {
        r["product_id"]: r.get("predicted_category", "")
        for r in classified
        if "product_id" in r
    }

    issues = []
    for r in annotations:
        pid = r.get("product_id", "")
        annotated = r.get("annotated_category", "").strip()
        predicted = classified_map.get(pid, "")

        if predicted and annotated and annotated != predicted and predicted != "Uncategorized":
            issues.append({
                "product_id": pid,
                "product_name": r.get("product_name", ""),
                "annotated_category": annotated,
                "predicted_category": predicted,
                "issue_type": "CLASSIFIER_MISMATCH",
                "detail": f"Human: '{annotated}' vs Classifier: '{predicted}'",
                "severity": "MEDIUM",
                "timestamp": r.get("timestamp", ""),
            })
    return issues


def check_completeness(records):
    """
    Check 3: Flag records with missing required fields.
    """
    required_fields = ["product_id", "product_name", "annotated_category", "timestamp"]
    issues = []
    for r in records:
        missing = [f for f in required_fields if not r.get(f, "").strip()]
        if missing:
            issues.append({
                "product_id": r.get("product_id", "N/A"),
                "product_name": r.get("product_name", ""),
                "annotated_category": r.get("annotated_category", ""),
                "predicted_category": "",
                "issue_type": "INCOMPLETE_RECORD",
                "detail": f"Missing fields: {', '.join(missing)}",
                "severity": "MEDIUM",
                "timestamp": r.get("timestamp", ""),
            })
    return issues


def save_audit_log(issues, filepath=AUDIT_LOG_FILE):
    """Write all flagged issues to the audit log CSV."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    if not issues:
        print("[PASS] No issues found. All records pass audit.")
        return
    fieldnames = ["product_id", "product_name", "annotated_category",
                  "predicted_category", "issue_type", "detail", "severity", "timestamp"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)
    print(f"[INFO] Audit log saved → {filepath}  ({len(issues)} issues)")


def save_audit_summary(annotations, classified, all_issues, summary_path=AUDIT_SUMMARY):
    """Write a plain-text audit summary for escalation/reporting."""
    os.makedirs(os.path.dirname(summary_path) if os.path.dirname(summary_path) else ".", exist_ok=True)
    severity_counts = Counter(i["severity"] for i in all_issues)
    type_counts = Counter(i["issue_type"] for i in all_issues)
    pass_rate = ((len(annotations) - len(all_issues)) / len(annotations) * 100) if annotations else 0

    lines = [
        "=" * 52,
        "  B2B ANNOTATION PIPELINE — AUDIT SUMMARY",
        f"  Run at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 52,
        f"\n  Records Audited     : {len(annotations)}",
        f"  Classifier Records  : {len(classified)}",
        f"  Total Issues Found  : {len(all_issues)}",
        f"  Audit Pass Rate     : {pass_rate:.1f}%",
        "\n  ── Issues by Type ──",
    ]
    for itype, count in type_counts.most_common():
        lines.append(f"  {itype:<28} {count}")

    lines.append("\n  ── Issues by Severity ──")
    for sev, count in severity_counts.most_common():
        lines.append(f"  {sev:<10} {count}")

    if all_issues:
        lines.append("\n  ⚠ Escalation required. Review audit_log.csv for details.")
    else:
        lines.append("\n  ✓ All records passed. No escalation needed.")

    lines.append("\n" + "=" * 52 + "\n")

    text = "\n".join(lines)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"[INFO] Summary saved → {summary_path}")


def run_audit(annotations_file, classified_file, audit_log, audit_summary):
    print("=== Quality Audit: Data Annotation Toolkit ===\n")

    annotations = load_csv(annotations_file)
    classified  = load_csv(classified_file)

    if not annotations:
        print("[INFO] No annotation records to audit. Run annotator.py first.")
        return

    # Run all checks
    label_issues      = check_label_integrity(annotations)
    mismatch_issues   = check_classifier_mismatches(annotations, classified)
    completeness_issues = check_completeness(annotations)

    all_issues = label_issues + mismatch_issues + completeness_issues

    save_audit_log(all_issues, audit_log)
    save_audit_summary(annotations, classified, all_issues, audit_summary)


def main():
    parser = argparse.ArgumentParser(description="B2B Annotation Quality Audit")
    parser.add_argument("--annotations", default=ANNOTATIONS_FILE, help="Annotated tracker CSV")
    parser.add_argument("--classified",  default=CLASSIFIED_FILE,  help="Classifier output CSV")
    parser.add_argument("--log",         default=AUDIT_LOG_FILE,   help="Audit log output path")
    parser.add_argument("--summary",     default=AUDIT_SUMMARY,    help="Audit summary output path")
    args = parser.parse_args()

    run_audit(args.annotations, args.classified, args.log, args.summary)


if __name__ == "__main__":
    main()
