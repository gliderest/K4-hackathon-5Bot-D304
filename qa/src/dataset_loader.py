"""Load and validate Golden Set rows before any evaluation run."""
import csv
from pathlib import Path

REQUIRED_COLUMNS = ["case_id","category","risk_class","source","source_reference","input","context","expected_behavior","expected_citation","must_ask_clarification","must_refuse","severity","notes"]
VALID_CATEGORIES = {"happy_path","source_truth","ambiguous_or_missing_context","out_of_scope","domain_specific_error","edge_case"}
VALID_RISKS = {"source_truth","ambiguous_or_missing_context","out_of_scope","domain_specific_error"}

def validate_cases(rows):
    missing = set(REQUIRED_COLUMNS) - set(rows[0].keys() if rows else [])
    if missing: raise ValueError(f"missing required columns: {sorted(missing)}")
    ids = [r["case_id"] for r in rows]
    if len(ids) != len(set(ids)): raise ValueError("duplicate case_id")
    for row in rows:
        if row["category"] not in VALID_CATEGORIES: raise ValueError(f"invalid category: {row['category']}")
        if row["risk_class"] not in VALID_RISKS: raise ValueError(f"invalid risk_class: {row['risk_class']}")
    return rows

def load_golden_set(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return validate_cases(list(csv.DictReader(f)))
