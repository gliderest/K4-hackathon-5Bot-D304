"""Compare two stored result sets by stable case_id."""
from collections import defaultdict
def compare_results(baseline,candidate):
    b={r["case_id"]:r for r in baseline}; c={r["case_id"]:r for r in candidate}
    reg=[k for k in c if k in b and b[k].get("pass") and not c[k].get("pass")]
    imp=[k for k in c if k in b and not b[k].get("pass") and c[k].get("pass")]
    return {"regressed_cases":sorted(reg),"improved_cases":sorted(imp),"unchanged_failures":sorted(k for k in c if k in b and not b[k].get("pass") and not c[k].get("pass")),"new_critical_failures":sorted(k for k in c if c[k].get("critical_fail") and not b.get(k,{}).get("critical_fail"))}
