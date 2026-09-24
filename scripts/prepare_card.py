import pandas as pd
from pathlib import Path
import hashlib


BASE = Path("D:/fraudgraph-ai")

TRANSACTIONS = BASE / "data/raw/transactions.csv"
MAPPING = BASE / "data/processed/card_mapping.csv"

OUTPUT = BASE / "data/processed/card.csv"


print("=" * 70)
print("PREPARING CARD DATA")
print("=" * 70)


# ---------------------------------------------------------
# Load confirmed case-card mappings
# ---------------------------------------------------------

mapping = pd.read_csv(
    MAPPING,
    dtype=str,
    keep_default_na=False
)

print(f"Confirmed mappings loaded: {len(mapping):,}")


# fingerprint -> card_id
fingerprint_map = {}

for _, row in mapping.iterrows():

    customer_id = row["customer_id"].strip()
    fingerprint = row["card_fingerprint"].strip()
    card_id = row["card_id"].strip()

    key = (customer_id, fingerprint)

    fingerprint_map[key] = card_id


# ---------------------------------------------------------
# Read transactions in chunks
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

cards = {}


def make_fingerprint(row):
    return "|".join([
        str(row.get("card1", "")).strip(),
        str(row.get("card2", "")).strip(),
        str(row.get("card3", "")).strip(),
        str(row.get("card4", "")).strip(),
        str(row.get("card5", "")).strip(),
        str(row.get("card6", "")).strip(),
    ])


def make_fallback_card_id(customer_id, fingerprint):

    digest = hashlib.sha1(
        fingerprint.encode("utf-8")
    ).hexdigest()[:10]

    return f"{customer_id}-F{digest}"


# ---------------------------------------------------------
# Process transactions
# ---------------------------------------------------------

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

    for _, row in chunk.iterrows():

        customer_id = row["customer_id"].strip()

        if not customer_id:
            continue

        fingerprint = make_fingerprint(row)

        key = (customer_id, fingerprint)

        # Use authoritative case mapping if available
        if key in fingerprint_map:

            card_id = fingerprint_map[key]

        else:

            # Deterministic ID for cards not present in case history
            card_id = make_fallback_card_id(
                customer_id,
                fingerprint
            )

        if card_id not in cards:

            cards[card_id] = {
                "card_id": card_id,
                "customer_id": customer_id,
                "card_network": row["card4"],
                "card_type": row["card6"],
            }


# ---------------------------------------------------------
# Create DataFrame
# ---------------------------------------------------------

card_df = pd.DataFrame(
    list(cards.values())
)


# ---------------------------------------------------------
# Remove completely empty values
# ---------------------------------------------------------

card_df = card_df.fillna("")


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

card_df.to_csv(
    OUTPUT,
    index=False
)


print()
print("=" * 70)
print("CARD DATA COMPLETE")
print("=" * 70)

print(f"Cards created: {len(card_df):,}")

print()
print("Output:")
print(OUTPUT)

print()
print("Columns:")
print(list(card_df.columns))

print("=" * 70)