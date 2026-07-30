from qa.src.scorers import score_case, aggregate_metrics

def test_hallucination_is_critical_fail():
    result = score_case({"risk_class":"source_truth", "expected_citation":"doc.pdf (Tr.3)", "must_refuse":"false"}, "Chắc chắn đáp án là X.", [])
    assert result["pass"] is False
    assert "critical" in " ".join(result["failure_reasons"]).lower()

def test_empty_output_fails_and_needs_no_manual_guess():
    result = score_case({"risk_class":"happy_path", "expected_citation":"", "must_refuse":"false"}, "", [])
    assert result["pass"] is False
    assert result["manual_review_required"] is True

def test_pass_rate_is_computed():
    assert aggregate_metrics([{"pass": True}, {"pass": False}])["pass_rate"] == 0.5
