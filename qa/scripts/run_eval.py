import argparse, uuid
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from qa.src.dataset_loader import load_golden_set
from qa.src.ai_client import MockClient, HTTPClient
from qa.src.evaluator import evaluate, save_run
p=argparse.ArgumentParser(); p.add_argument("--mode",choices=["mock","http"],default="mock"); a=p.parse_args()
root=Path(__file__).parents[2]; cases=load_golden_set(root/"qa/eval/golden_set.csv"); client=MockClient() if a.mode=="mock" else HTTPClient()
run=evaluate(cases,client,"run-"+uuid.uuid4().hex[:12],root,official=a.mode=="http",execution_mode=a.mode); save_run(run,root/"qa/eval/runs"); print(run["run_id"],run["metrics"])
