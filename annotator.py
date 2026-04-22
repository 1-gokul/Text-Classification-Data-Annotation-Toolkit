"""
annotator.py — Interactive Data Annotation Tool
-------------------------------------------------------
Provides a CLI interface for manually labeling product listings.
Each annotated record is appended to the daily tracker CSV for SLA reporting.

Usage:
    python annotator.py
    python annotator.py --input data/sample_products.csv
"""

import csv
import os
import argparse
from datetime import datetime

TRACKER_FILE = "tracker/daily_tracker.csv"

VALID_CATEGORIES = [
    "Office Supplies",
    "Industrial Equipment",
    "Scientific Instruments",
    "Safety & PPE",
    "Electronics",
    "Furniture",
    "Cleaning Supplies",
    "Other",
]


def load_products(filepath):
    """Load product listings from CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Product file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_already_annotated(tracker_file=TRACKER_FILE):
    """Return set of product_ids already annotated in this tracker."""
    if not os.path.exists(tracker_file):
        return set()
    with open(tracker_file, "r", encoding="utf-8") as f:
        return {row["product_id"] for row in csv.DictReader(f)}


def save_annotation(record, tracker_file=TRACKER_FILE):
    """Append a single annotation record to the daily tracker CSV."""
    os.makedirs(os.path.dirname(tracker_file), exist_ok=True)
    file_exists = os.path.exists(tracker_file)
    fieldnames = ["timestamp", "product_id", "product_name",
                  "annotated_category", "confidence", "annotator_note"]
    with open(tracker_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def prompt_category():
    """Display category menu and return valid user selection."""
    print("\n  Available Categories:")
    for i, cat in enumerate(VALID_CATEGORIES, 1):
        print(f"    [{i}] {cat}")
    while True:
        choice = input("  Enter number or category name (or 'skip' / 'quit'): ").strip()
        if choice.lower() in ("skip", "quit"):
            return choice.lower()
        if choice.isdigit() and 1 <= int(choice) <= len(VALID_CATEGORIES):
            return VALID_CATEGORIES[int(choice) - 1]
        if choice in VALID_CATEGORIES:
            return choice
        print("  [WARN] Invalid selection. Try again.")


def run_annotation_session(products, tracker_file=TRACKER_FILE):
    """Run an interactive annotation session over unannotated products."""
    already_done = get_already_annotated(tracker_file)
    pending = [p for p in products if p.get("product_id") not in already_done]

    print(f"\n=== Data Annotation Tool ===")
    print(f"  Total products : {len(products)}")
    print(f"  Already done   : {len(already_done)}")
    print(f"  Pending        : {len(pending)}")
    print("  Type 'skip' to skip | 'quit' to exit session\n")

    annotated_this_session = 0

    for product in pending:
        print("\n" + "─" * 52)
        print(f"  ID          : {product.get('product_id', 'N/A')}")
        print(f"  Name        : {product.get('product_name', 'N/A')}")
        print(f"  Description : {product.get('description', 'N/A')}")

        choice = prompt_category()

        if choice == "quit":
            print("\n[INFO] Session ended by user.")
            break
        if choice == "skip":
            print("  Skipped.")
            continue

        note = input("  Annotator note (optional, press Enter to skip): ").strip()
        confidence = input("  Confidence? [high / medium / low] (default: high): ").strip() or "high"

        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product_id": product.get("product_id", ""),
            "product_name": product.get("product_name", ""),
            "annotated_category": choice,
            "confidence": confidence,
            "annotator_note": note,
        }

        save_annotation(record, tracker_file)
        annotated_this_session += 1
        print(f"  ✓ Saved. Session total: {annotated_this_session}")

    print(f"\n=== Session Complete ===")
    print(f"  Annotated this session : {annotated_this_session}")
    print(f"  Tracker updated        : {tracker_file}\n")


def main():
    parser = argparse.ArgumentParser(description="Data Annotation Tool")
    parser.add_argument("--input",   default="data/sample_products.csv", help="Product CSV path")
    parser.add_argument("--tracker", default=TRACKER_FILE,               help="Tracker CSV output path")
    args = parser.parse_args()

    products = load_products(args.input)
    run_annotation_session(products, args.tracker)


if __name__ == "__main__":
    main()
