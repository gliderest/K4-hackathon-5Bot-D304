qa-install:
	python -m pip install -r qa/requirements.txt
qa-validate:
	python qa/scripts/validate_golden_set.py
qa-test:
	pytest -q qa/tests
qa-eval:
	python qa/scripts/run_eval.py --mode mock
qa-report:
	python qa/scripts/generate_report.py --run-id $(RUN_ID)
qa-compare:
	python qa/scripts/compare_runs.py --baseline $(BASELINE) --candidate $(CANDIDATE)
