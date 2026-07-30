import argparse,json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from qa.src.regression import compare_results
p=argparse.ArgumentParser(); p.add_argument("--baseline",required=True); p.add_argument("--candidate",required=True); a=p.parse_args(); d=Path(__file__).parents[1]/"eval/runs"
b=json.loads((d/(a.baseline+".json")).read_text()); c=json.loads((d/(a.candidate+".json")).read_text()); r=compare_results(b["results"],c["results"]); out=Path(__file__).parents[1]/f"eval/reports/regression_{a.baseline}_vs_{a.candidate}.md"; out.write_text("# Regression\n\n"+json.dumps(r,ensure_ascii=False,indent=2)); print(out)
