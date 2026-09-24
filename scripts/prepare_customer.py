import pandas as pd
from pathlib import Path

BASE = Path("D:/fraudgraph-ai")

TRANSACTIONS = BASE / "data/raw/transactions.csv"
OUTPUT = BASE / "data/processed/customer.csv"

print("=" * 70)
print("PREPARING CUSTOMER DATA")
print("=" * 70)

customers = set()

usecols = ["customer_id"]
chunksize = 100000

for chunk_number, chunk in enumerate(
    pd.read_csv(
        TRANSACTIONS,
        usecols=usecols,
        dtype=str,
        chunksize=chunksize,
        keep_default_na=False
    ),
    start=1
):

    print(f"Processing chunk {chunk_number}...")

    values = (
        chunk["customer_id"]
        .astype(str)
        .str.strip()
    )

    customers.update(
        value for value in values
        if value
    )


customer_df = pd.DataFrame(
    sorted(customers),
    columns=["customer_id"]
)

customer_df.to_csv(
    OUTPUT,
    index=False
)

print()
print("=" * 70)
print("CUSTOMER DATA COMPLETE")
print("=" * 70)

print(f"Customers: {len(customer_df):,}")
print(f"Saved: {OUTPUT}")

print()
print(customer_df.head(10).to_string(index=False))

print("=" * 70)