"""
tracker.py — Daily Annotation Progress Tracker
-----------------------------------------------
Reads the annotation tracker CSV and generates a structured daily
progress report showing task volume, completion rate, and SLA status.

Usage:
    python tracker.py
    python tracker.py --tracker tracker/daily_tracker.csv --target 10
"""

import csv
import os
import argparse
from datetime import datetime, date
from collections import defaultdict, Counter


TRACKER_FILE  = "tracker/daily_tracker.csv"
REPORT_FILE   = "tracker/progress_report.txt"
DEFAULT_TARGET = 10  # Daily annotation target (tasks/day)


def load_tracker(filepath=TRACKER_FILE):
    """Load all annotation records from tracker CSV."""
    if not os.path.exists(filepath):
        print(f"[WARN] Tracker file not found: {filepath}")
        print("       Run annotator.py first to generate annotation records.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_daily_stats(records):
    """Group records by date and compute per-day statistics."""
    daily = defaultdict(list)
    for r in records:
        day = r.get("timestamp", "")[:10]  # YYYY-MM-DD
        daily[day].append(r)
    return daily


def compute_category_distribution(records):
    """Return a Counter of annotated categories."""
    return Counter(r.get("annotated_category", "Unknown") for r in records)


def compute_confidence_breakdown(records):
    """Return a Counter of confidence levels."""
    return Counter(r.get("confidence", "unknown") for r in records)


def generate_report(records, daily_target=DEFAULT_TARGET, report_path=REPORT_FILE):
    """Generate and save a structured progress report."""
    os.makedirs(os.path.dirname(report_path) if os.path.dirname(report_path) else ".", exist_ok=True)

    total = len(records)
    daily = compute_daily_stats(records)
    category_dist = compute_category_distribution(records)
    confidence_dist = compute_confidence_breakdown(records)

    lines = []
    lines.append("=" * 58)
    lines.append("  DATA ANNOTATION TOOLKIT — PROGRESS REPORT")
    lines.append(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 58)
    lines.append(f"\n  Total Annotations : {total}")
    lines.append(f"  Daily Target      : {daily_target} tasks/day")
    lines.append(f"  Active Days       : {len(daily)}")

    # Daily breakdown
    lines.append("\n  ── Daily Breakdown ──")
    for day in sorted(daily.keys()):
        count = len(daily[day])
        sla = "✓ MET" if count >= daily_target else "✗ MISSED"
        bar = "█" * min(count, 30)
        lines.append(f"  {day}  {bar:<30} {count:>3} tasks  [{sla}]")

    # Category distribution
    lines.append("\n  ── Category Distribution ──")
    for cat, count in category_dist.most_common():
        pct = (count / total * 100) if total else 0
        lines.append(f"  {cat:<28} {count:>3}  ({pct:.1f}%)")

    # Confidence breakdown
    lines.append("\n  ── Confidence Breakdown ──")
    for level, count in confidence_dist.most_common():
        lines.append(f"  {level:<10} {count}")

    lines.append("\n" + "=" * 58 + "\n")

    report_text = "\n".join(lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)
    print(f"[INFO] Report saved → {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Annotation Progress Tracker")
    parser.add_argument("--tracker", default=TRACKER_FILE,  help="Tracker CSV path")
    parser.add_argument("--report",  default=REPORT_FILE,   help="Report output path")
    parser.add_argument("--target",  default=DEFAULT_TARGET, type=int, help="Daily task target")
    args = parser.parse_args()

    records = load_tracker(args.tracker)
    if records:
        generate_report(records, daily_target=args.target, report_path=args.report)
    else:
        print("[INFO] No records to report. Annotate some products first.")


if __name__ == "__main__":
    main()
