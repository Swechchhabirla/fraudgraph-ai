import pandas as pd
from pathlib import Path

BASE = Path("D:/fraudgraph-ai")

CARD_FILE = BASE / "data/processed/card.csv"
TRANSACTION_FILE = BASE / "data/processed/transaction_new.csv"

EDGE_DIR = BASE / "data/processed/edges"

OWNS_FILE = EDGE_DIR / "owns.csv"
MADE_FILE = EDGE_DIR / "made.csv"

EDGE_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("PREPARING CORE GRAPH EDGES")
print("=" * 70)


# =========================================================
# 1. OWNS
# =========================================================

print()
print("Creating OWNS edges...")

cards = pd.read_csv(
    CARD_FILE,
    dtype=str,
    keep_default_na=False
)

owns = cards[
    ["customer_id", "card_id"]
].drop_duplicates()

owns.to_csv(
    OWNS_FILE,
    index=False
)

print(f"OWNS edges: {len(owns):,}")
print(f"Saved: {OWNS_FILE}")


# =========================================================
# 2. MADE
# =========================================================

print()
print("Creating MADE edges...")


# IMPORTANT:
# transaction_new.csv currently does NOT contain card_id.
# Therefore we rebuild the relationship from the original
# transaction data using the same card mapping logic.


MAPPING_FILE = BASE / "data/processed/card_mapping.csv"
RAW_TRANSACTION_FILE = BASE / "data/raw/transactions.csv"


mapping = pd.read_csv(
    MAPPING_FILE,
    dtype=str,
    keep_default_na=False
)


# fingerprint -> card_id
fingerprint_map = {}

for _, row in mapping.iterrows():

    customer_id = row["customer_id"].strip()
    fingerprint = row["card_fingerprint"].strip()
    card_id = row["card_id"].strip()

    fingerprint_map[
        (customer_id, fingerprint)
    ] = card_id


# ---------------------------------------------------------
# Function to create fingerprint
# ---------------------------------------------------------

def make_fingerprint(row):

    return "|".join([
        str(row["card1"]).strip(),
        str(row["card2"]).strip(),
        str(row["card3"]).strip(),
        str(row["card4"]).strip(),
        str(row["card5"]).strip(),
        str(row["card6"]).strip(),
    ])


# ---------------------------------------------------------
# IMPORTANT:
# Use the already-created card.csv to build fallback IDs.
# This guarantees MADE uses exactly the same Card IDs.
# ---------------------------------------------------------

card_lookup = {}

for _, row in cards.iterrows():

    customer_id = row["customer_id"].strip()
    card_id = row["card_id"].strip()

    # Case cards are already in mapping.
    # Fallback cards will be identified later.


# ---------------------------------------------------------
# Process raw transactions in chunks
# ---------------------------------------------------------

usecols = [
    "TransactionID",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "customer_id",
]

chunksize = 100000

first_write = True
total_edges = 0

for chunk_number, chunk in enumerate(
    pd.read_csv(
        RAW_TRANSACTION_FILE,
        usecols=usecols,
        dtype=str,
        chunksize=chunksize,
        keep_default_na=False
    ),
    start=1
):

    print(f"Processing chunk {chunk_number}...")

    made_rows = []

    for _, row in chunk.iterrows():

        transaction_id = row["TransactionID"].strip()
        customer_id = row["customer_id"].strip()

        if not transaction_id or not customer_id:
            continue

        fingerprint = make_fingerprint(row)

        key = (customer_id, fingerprint)

        # -------------------------------------------------
        # Confirmed case-card mapping
        # -------------------------------------------------

        if key in fingerprint_map:

            card_id = fingerprint_map[key]

        else:

            # Same deterministic fallback algorithm used
            # in prepare_card.py
            import hashlib

            digest = hashlib.sha1(
                fingerprint.encode("utf-8")
            ).hexdigest()[:10]

            card_id = f"{customer_id}-F{digest}"

        made_rows.append({
            "card_id": card_id,
            "transaction_id": transaction_id
        })

    if made_rows:

        made_df = pd.DataFrame(made_rows)

        made_df.to_csv(
            MADE_FILE,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )

        first_write = False

        total_edges += len(made_df)


print()
print("=" * 70)
print("CORE EDGES COMPLETE")
print("=" * 70)

print(f"OWNS edges: {len(owns):,}")
print(f"MADE edges: {total_edges:,}")

print()
print(f"OWNS: {OWNS_FILE}")
print(f"MADE: {MADE_FILE}")