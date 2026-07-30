"""Make the repository root importable when pytest is launched from any directory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))
