import pytest
from pathlib import Path
from qa.src.dataset_loader import load_golden_set, validate_cases

def test_loads_required_columns():
    cases = load_golden_set(Path(__file__).parents[1] / "eval/golden_set.csv")
    assert len(cases) >= 20

def test_duplicate_case_id_is_rejected(tmp_path):
    p = tmp_path / "cases.csv"
    header = "case_id,category,risk_class,source,source_reference,input,context,expected_behavior,expected_citation,must_ask_clarification,must_refuse,severity,notes\n"
    p.write_text(header + "a,happy_path,source_truth,sample,,,,,,,,,\na,happy_path,source_truth,sample,,,,,,,,,\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_golden_set(p)

def test_invalid_category_is_rejected(tmp_path):
    p = tmp_path / "cases.csv"
    header = "case_id,category,risk_class,source,source_reference,input,context,expected_behavior,expected_citation,must_ask_clarification,must_refuse,severity,notes\n"
    p.write_text(header + "a,bad,source_truth,sample,,,,,,,,,\n")
    with pytest.raises(ValueError, match="category"):
        load_golden_set(p)
