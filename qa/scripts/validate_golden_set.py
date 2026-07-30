from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from qa.src.dataset_loader import load_golden_set
path=Path(__file__).parents[1]/"eval/golden_set.csv"
rows=load_golden_set(path); print(f"Valid Golden Set: {len(rows)} cases")
