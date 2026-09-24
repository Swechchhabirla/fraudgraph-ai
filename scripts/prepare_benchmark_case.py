import pandas as pd
from pathlib import Path

BASE = Path(r"D:\fraudgraph-ai")

INPUT = BASE / "data" / "raw" / "case_pack.csv"
OUTPUT_DIR = BASE / "data" / "processed"
OUTPUT = OUTPUT_DIR / "benchmark_case.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

columns = [
    "case_id",
    "opened_at",
    "trigger_type",
    "trigger_text",
    "flagged_txn_id",
    "card_id",
    "customer_id",
    "risk_score",
]

df = pd.read_csv(INPUT, usecols=columns)

# Convert IDs to strings
for col in ["case_id", "flagged_txn_id", "card_id", "customer_id"]:
    df[col] = df[col].fillna("").astype(str)

# Convert timestamps to TigerGraph-friendly format
df["opened_at"] = pd.to_datetime(
    df["opened_at"],
    errors="coerce"
).dt.strftime("%Y-%m-%d %H:%M:%S")

# Keep risk_score numeric
df["risk_score"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce"
)

df.to_csv(OUTPUT, index=False)

print(f"Benchmark cases: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Saved: {OUTPUT}")
print()
print(df.head(5).to_string(index=False))