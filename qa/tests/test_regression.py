from qa.src.regression import compare_results

def test_detects_pass_to_fail():
    report = compare_results([{"case_id":"a","pass":True}], [{"case_id":"a","pass":False}])
    assert report["regressed_cases"] == ["a"]

def test_detects_improvement():
    report = compare_results([{"case_id":"a","pass":False}], [{"case_id":"a","pass":True}])
    assert report["improved_cases"] == ["a"]
