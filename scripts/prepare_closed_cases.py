import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

INPUT = BASE / "data/raw/closed_cases_history.csv"
OUTPUT = BASE / "data/processed/closed_case.csv"


print("=" * 70)
print("PREPARING CLOSED CASE DATA")
print("=" * 70)


# =========================================================
# Read historical cases
# =========================================================

df = pd.read_csv(
    INPUT,
    dtype=str,
    keep_default_na=False
)


# =========================================================
# Convert numeric fields
# =========================================================

def to_int(value):
    try:
        return int(float(value))
    except:
        return 0


def to_float(value):
    try:
        return float(value)
    except:
        return 0.0


df["n_txns"] = df["n_txns"].apply(to_int)
df["exposure_usd"] = df["exposure_usd"].apply(to_float)


# =========================================================
# Convert report_filed to TRUE/FALSE
# =========================================================

df["report_filed"] = (
    df["report_filed"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({
        "true": True,
        "1": True,
        "yes": True,
        "false": False,
        "0": False,
        "no": False
    })
    .fillna(False)
)


# =========================================================
# Select TigerGraph attributes
# =========================================================

columns = [
    "case_id",
    "customer_id",
    "card_id",
    "opened_at",
    "closed_at",
    "outcome",
    "pattern",
    "first_fraud_txn_id",
    "n_txns",
    "exposure_usd",
    "actions_taken",
    "report_filed",
    "analyst_notes",
]


case_df = df[columns].copy()


# =========================================================
# Save
# =========================================================

case_df.to_csv(
    OUTPUT,
    index=False
)


# =========================================================
# Summary
# =========================================================

print()
print("=" * 70)
print("CLOSED CASE DATA COMPLETE")
print("=" * 70)

print(f"Closed cases: {len(case_df):,}")

print()
print("Columns:")
print(list(case_df.columns))

print()
print("Sample:")
print(
    case_df.head(5).to_string(index=False)
)

print()
print(f"Saved:")
print(OUTPUT)

print("=" * 70)