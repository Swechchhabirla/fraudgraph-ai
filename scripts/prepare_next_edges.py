import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

TRANSACTIONS = BASE / "data/raw/transactions.csv"
OUTPUT = BASE / "data/processed/edges/next.csv"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("PREPARING NEXT TRANSACTION EDGES")
print("=" * 70)


# We need the card fingerprint because the raw dataset
# does not contain the final TigerGraph card_id.

usecols = [
    "TransactionID",
    "TransactionDT",
    "customer_id",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
]

chunksize = 100000

parts = []


# =========================================================
# 1. Read transactions
# =========================================================

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

    print(f"Reading chunk {chunk_number}...")

    # Convert TransactionDT for sorting
    chunk["TransactionDT_num"] = pd.to_numeric(
        chunk["TransactionDT"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Build raw card fingerprint
    # -----------------------------------------------------

    chunk["card_fingerprint"] = (
        chunk["card1"].astype(str).str.strip()
        + "|" +
        chunk["card2"].astype(str).str.strip()
        + "|" +
        chunk["card3"].astype(str).str.strip()
        + "|" +
        chunk["card4"].astype(str).str.strip()
        + "|" +
        chunk["card5"].astype(str).str.strip()
        + "|" +
        chunk["card6"].astype(str).str.strip()
    )

    parts.append(
        chunk[
            [
                "TransactionID",
                "TransactionDT_num",
                "customer_id",
                "card_fingerprint"
            ]
        ]
    )


# =========================================================
# 2. Combine
# =========================================================

print()
print("Combining transaction data...")

df = pd.concat(
    parts,
    ignore_index=True
)

del parts


print(f"Transactions loaded: {len(df):,}")


# =========================================================
# 3. Sort by customer + card + time
# =========================================================

print("Sorting transactions...")

df = df.sort_values(
    [
        "customer_id",
        "card_fingerprint",
        "TransactionDT_num"
    ]
)


# =========================================================
# 4. Create NEXT relationship
# =========================================================

print("Creating NEXT edges...")


df["next_transaction_id"] = (
    df.groupby(
        [
            "customer_id",
            "card_fingerprint"
        ]
    )["TransactionID"]
    .shift(-1)
)


next_df = df[
    [
        "TransactionID",
        "next_transaction_id"
    ]
].copy()


next_df = next_df.rename(
    columns={
        "TransactionID": "from_transaction_id",
        "next_transaction_id": "to_transaction_id"
    }
)


# Remove final transaction of every card
next_df = next_df[
    next_df["to_transaction_id"].notna()
]


# Remove empty values
next_df = next_df[
    (next_df["from_transaction_id"].astype(str).str.strip() != "") &
    (next_df["to_transaction_id"].astype(str).str.strip() != "")
]


next_df = next_df.drop_duplicates()


# =========================================================
# 5. Save
# =========================================================

next_df.to_csv(
    OUTPUT,
    index=False
)


# =========================================================
# 6. Summary
# =========================================================

print()
print("=" * 70)
print("NEXT EDGES COMPLETE")
print("=" * 70)

print(f"NEXT edges: {len(next_df):,}")

print()
print("Columns:")
print(list(next_df.columns))

print()
print("Sample:")
print(
    next_df.head(10).to_string(index=False)
)

print()
print(f"Saved:")
print(OUTPUT)

print("=" * 70)