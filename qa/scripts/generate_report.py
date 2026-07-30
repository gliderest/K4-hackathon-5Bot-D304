import argparse,json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
p=argparse.ArgumentParser(); p.add_argument("--run-id",required=True); a=p.parse_args(); q=Path(__file__).parents[1]; run=json.loads((q/"eval/runs"/(a.run_id+".json")).read_text()); m=run["metrics"]; fails=[r for r in run["results"] if not r.get("pass")]; lines=[f"# Evaluation {a.run_id}","",f"Official: `{run['official']}`; mode: `{run['execution_mode']}`",f"\nPass rate: **{m['pass_rate']:.1%}** ({m['passed']}/{m['total']})",f"Critical Fail: **{m['critical_fail_count']}**","","## Failures"]+[f"- {r['case_id']}: {'; '.join(r.get('failure_reasons',[]))}" for r in fails]; out=q/"eval/reports"/(a.run_id+"_summary.md"); out.write_text("\n".join(lines),encoding="utf-8"); print(out)
