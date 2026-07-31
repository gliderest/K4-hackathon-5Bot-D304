import pytest
from qa.src.evaluator import save_run
from qa.src.evaluator import evaluate

def test_run_is_not_overwritten(tmp_path):
    save_run({"run_id":"run-1"}, tmp_path)
    with pytest.raises(FileExistsError):
        save_run({"run_id":"run-1"}, tmp_path)

def test_timeout_or_client_error_keeps_case_as_failure(tmp_path):
    class TimeoutClient:
        def ask(self, *_):
            raise TimeoutError("request timed out")
    run = evaluate([{"case_id":"T1","input":"x","context":""}], TimeoutClient(), "run-timeout", tmp_path, execution_mode="http")
    assert run["results"][0]["pass"] is False
    assert "timed out" in run["results"][0]["error"]
