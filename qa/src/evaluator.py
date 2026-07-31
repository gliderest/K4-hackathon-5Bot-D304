"""Evaluation orchestration and immutable run storage."""
import csv, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from .scorers import score_case, aggregate_metrics

def save_run(run, directory):
    directory=Path(directory); directory.mkdir(parents=True, exist_ok=True)
    base=directory/run["run_id"]
    if base.with_suffix(".json").exists() or base.with_suffix(".csv").exists(): raise FileExistsError(run["run_id"])
    base.with_suffix(".json").write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding="utf-8")
    rows=run.get("results",[])
    if rows:
        keys=sorted({k for r in rows for k in r})
        with base.with_suffix(".csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    return base

def git_hash(root):
    try: return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    except Exception: return "unknown"

def evaluate(cases, client, run_id, root, official=False, execution_mode="mock"):
    results=[]
    for case in cases:
        try:
            response=client.ask(case["input"], case.get("context",""))
            output=response.get("output",""); citations=response.get("citations",[])
            scored=score_case(case,output,citations)
            results.append({**case,**scored,"actual_output":output,"citations":citations,"latency_ms":response.get("latency_ms"),"http_status":response.get("http_status"),"error":""})
        except Exception as exc:
            results.append({**case,"actual_output":"","citations":[],"latency_ms":None,"http_status":None,"error":str(exc),"pass":False,"critical_fail":False,"failure_reasons":[str(exc)],"manual_review_required":True})
    return {"run_id":run_id,"timestamp":datetime.now(timezone.utc).isoformat(),"official":official,"execution_mode":execution_mode,"commit_hash":git_hash(root),"metrics":aggregate_metrics(results),"results":results}
