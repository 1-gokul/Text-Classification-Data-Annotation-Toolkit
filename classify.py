"""
classify.py — B2B Product Classification Pipeline
---------------------------------------------------
Loads product listings from CSV, applies rule-based classification
using a configurable JSON rule set, and outputs labelled results.

Usage:
    python classify.py
    python classify.py --input data/sample_products.csv --output data/classified_products.csv
"""

import json
import csv
import os
import argparse
from datetime import datetime


def load_rules(rules_path="rules/classification_rules.json"):
    """Load classification rule sets from JSON config."""
    if not os.path.exists(rules_path):
        raise FileNotFoundError(f"Rule set not found: {rules_path}")
    with open(rules_path, "r") as f:
        rules = json.load(f)
    print(f"[INFO] Loaded {len(rules)} category rule sets from '{rules_path}'")
    return rules


def classify_product(product_name, description, rules):
    """
    Apply keyword-based rule set to classify a single product.
    Returns the matched category or 'Uncategorized' if no rule matches.
    """
    text = (product_name + " " + description).lower()
    matched_categories = []

    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword.lower() in text:
                matched_categories.append(category)
                break  # One match per category is sufficient

    if not matched_categories:
        return "Uncategorized"
    # Return first match (priority follows JSON key order)
    return matched_categories[0]


def classify_dataset(input_csv, output_csv, rules):
    """
    Classify all products in input_csv and write labelled results to output_csv.
    Returns list of result dicts.
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    results = []
    uncategorized_count = 0

    with open(input_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = classify_product(
                row.get("product_name", ""),
                row.get("description", ""),
                rules
            )
            row["predicted_category"] = label
            row["classified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(row)
            if label == "Uncategorized":
                uncategorized_count += 1

    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else ".", exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[DONE] {len(results)} products classified.")
    print(f"       Uncategorized: {uncategorized_count}")
    print(f"       Output saved → {output_csv}")
    return results


def print_summary(results):
    """Print a category distribution summary to console."""
    from collections import Counter
    counts = Counter(r["predicted_category"] for r in results)
    print("\n--- Classification Summary ---")
    for category, count in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {category:<28} {bar} ({count})")
    print()


def main():
    parser = argparse.ArgumentParser(description="Text Classifier")
    parser.add_argument("--input",  default="data/sample_products.csv",     help="Input CSV path")
    parser.add_argument("--output", default="data/classified_products.csv", help="Output CSV path")
    parser.add_argument("--rules",  default="rules/classification_rules.json", help="Rule set JSON path")
    args = parser.parse_args()

    rules = load_rules(args.rules)
    results = classify_dataset(args.input, args.output, rules)
    print_summary(results)


if __name__ == "__main__":
    main()
