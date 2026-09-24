import pandas as pd
from pathlib import Path

BASE = Path(r"D:\fraudgraph-ai")

INPUT = BASE / "data" / "processed" / "benchmark_case.csv"
OUTPUT_DIR = BASE / "data" / "processed" / "edges"
OUTPUT = OUTPUT_DIR / "flags.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    INPUT,
    dtype={
        "case_id": str,
        "flagged_txn_id": str
    }
)

flags = df[["case_id", "flagged_txn_id"]].copy()

flags.columns = [
    "benchmark_case_id",
    "transaction_id"
]

flags.to_csv(OUTPUT, index=False)

print(f"FLAGS edges: {len(flags)}")
print(f"Saved: {OUTPUT}")
print()
print(flags.head(10).to_string(index=False))