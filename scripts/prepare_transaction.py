import pandas as pd
from pathlib import Path
import hashlib

BASE = Path("D:/fraudgraph-ai")

RAW = BASE / "data/raw/transactions.csv"
MAPPING = BASE / "data/processed/card_mapping.csv"
OUTPUT = BASE / "data/processed/transaction_new.csv"


print("=" * 70)
print("REBUILDING TRANSACTION DATA WITH CARD_ID")
print("=" * 70)


# =========================================================
# Load confirmed case-card mapping
# =========================================================

mapping = pd.read_csv(
    MAPPING,
    dtype=str,
    keep_default_na=False
)

fingerprint_map = {}

for _, row in mapping.iterrows():

    customer_id = row["customer_id"].strip()
    fingerprint = row["card_fingerprint"].strip()
    card_id = row["card_id"].strip()

    fingerprint_map[
        (customer_id, fingerprint)
    ] = card_id


print(f"Confirmed mappings: {len(fingerprint_map):,}")


# =========================================================
# Card fingerprint
# =========================================================

def make_fingerprint(row):

    return "|".join([
        str(row["card1"]).strip(),
        str(row["card2"]).strip(),
        str(row["card3"]).strip(),
        str(row["card4"]).strip(),
        str(row["card5"]).strip(),
        str(row["card6"]).strip(),
    ])


# =========================================================
# Fallback card ID
# =========================================================

def make_fallback_card_id(customer_id, fingerprint):

    digest = hashlib.sha1(
        fingerprint.encode("utf-8")
    ).hexdigest()[:10]

    return f"{customer_id}-F{digest}"


# =========================================================
# Input columns
# =========================================================

usecols = [
    "TransactionID",
    "TransactionAmt",
    "ProductCD",

    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",

    "customer_id",
    "risk_score",
    "ts",
    "channel",

    "P_emaildomain",
    "addr1",
]


chunksize = 100000

first_write = True

total = 0
confirmed = 0
fallback = 0


# =========================================================
# Process raw transactions
# =========================================================

for chunk_no, chunk in enumerate(
    pd.read_csv(
        RAW,
        usecols=usecols,
        dtype=str,
        chunksize=chunksize,
        keep_default_na=False
    ),
    start=1
):

    print(f"Processing chunk {chunk_no}...")

    rows = []

    for _, row in chunk.iterrows():

        transaction_id = row["TransactionID"].strip()
        customer_id = row["customer_id"].strip()

        if not transaction_id or not customer_id:
            continue


        # -------------------------------------------------
        # Build card fingerprint
        # -------------------------------------------------

        fingerprint = make_fingerprint(row)

        key = (customer_id, fingerprint)


        # -------------------------------------------------
        # Determine Card ID
        # -------------------------------------------------

        if key in fingerprint_map:

            card_id = fingerprint_map[key]
            confirmed += 1

        else:

            card_id = make_fallback_card_id(
                customer_id,
                fingerprint
            )

            fallback += 1


        # -------------------------------------------------
        # Transaction row
        # -------------------------------------------------

        rows.append({
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "card_id": card_id,
            "transaction_time": row["ts"],
            "amount": row["TransactionAmt"],
            "product_code": row["ProductCD"],
            "channel": row["channel"],
            "risk_score": row["risk_score"],
            "billing_region": row["addr1"],
            "purchaser_email_domain": row["P_emaildomain"],
        })

        total += 1


    output = pd.DataFrame(rows)

    output.to_csv(
        OUTPUT,
        mode="w" if first_write else "a",
        header=first_write,
        index=False
    )

    first_write = False


# =========================================================
# Result
# =========================================================

print()
print("=" * 70)
print("TRANSACTION FILE COMPLETE")
print("=" * 70)

print(f"Total transactions : {total:,}")
print(f"Confirmed Card IDs : {confirmed:,}")
print(f"Fallback Card IDs  : {fallback:,}")

print()
print("Output:")
print(OUTPUT)

print()
print("Columns:")
print([
    "transaction_id",
    "customer_id",
    "card_id",
    "transaction_time",
    "amount",
    "product_code",
    "channel",
    "risk_score",
    "billing_region",
    "purchaser_email_domain"
])

print("=" * 70)