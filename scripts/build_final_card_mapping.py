import pandas as pd
from collections import defaultdict
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

CLOSED_CASES = BASE / "data/raw/closed_cases_history.csv"
CASE_PACK = BASE / "data/raw/case_pack.csv"
CASE_TXNS = BASE / "data/processed/case_transaction_cards.csv"

OUTPUT = BASE / "data/processed/card_mapping.csv"
AMBIGUOUS = BASE / "data/processed/card_mapping_ambiguous.csv"


print("=" * 70)
print("BUILDING FINAL CARD MAPPING")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load case transaction/card data
# ---------------------------------------------------------

case_txns = pd.read_csv(CASE_TXNS, dtype=str)

print(f"Case transactions loaded: {len(case_txns):,}")


# ---------------------------------------------------------
# 2. Create transaction -> card_id mappings
# ---------------------------------------------------------

txn_to_cards = defaultdict(set)


# ---------------------------------------------------------
# Historical closed cases
# ---------------------------------------------------------

closed = pd.read_csv(
    CLOSED_CASES,
    dtype=str,
    keep_default_na=False
)

for _, row in closed.iterrows():

    card_id = str(row["card_id"]).strip()

    if not card_id:
        continue

    txn_ids = str(row["txn_ids"]).strip()

    if txn_ids:
        for txn_id in txn_ids.split("|"):
            txn_id = txn_id.strip()

            if txn_id:
                txn_to_cards[txn_id].add(card_id)

    # Also include first fraud transaction
    first_txn = str(row["first_fraud_txn_id"]).strip()

    if first_txn:
        txn_to_cards[first_txn].add(card_id)


# ---------------------------------------------------------
# Benchmark case pack
# ---------------------------------------------------------

case_pack = pd.read_csv(
    CASE_PACK,
    dtype=str,
    keep_default_na=False
)

for _, row in case_pack.iterrows():

    txn_id = str(row["flagged_txn_id"]).strip()
    card_id = str(row["card_id"]).strip()

    if txn_id and card_id:
        txn_to_cards[txn_id].add(card_id)


print(f"Transactions with case card information: {len(txn_to_cards):,}")


# ---------------------------------------------------------
# 3. Build fingerprint -> card mapping
# ---------------------------------------------------------

fingerprint_to_cards = defaultdict(set)


for _, row in case_txns.iterrows():

    txn_id = str(row["TransactionID"]).strip()
    customer_id = str(row["customer_id"]).strip()

    if not txn_id or not customer_id:
        continue

    cards_for_txn = txn_to_cards.get(txn_id, set())

    if not cards_for_txn:
        continue

    fingerprint = "|".join([
        str(row.get("card1", "")).strip(),
        str(row.get("card2", "")).strip(),
        str(row.get("card3", "")).strip(),
        str(row.get("card4", "")).strip(),
        str(row.get("card5", "")).strip(),
        str(row.get("card6", "")).strip(),
    ])

    key = (customer_id, fingerprint)

    for card_id in cards_for_txn:
        fingerprint_to_cards[key].add(card_id)


# ---------------------------------------------------------
# 4. Separate confirmed and ambiguous mappings
# ---------------------------------------------------------

confirmed = []
ambiguous = []


for (customer_id, fingerprint), cards in fingerprint_to_cards.items():

    cards = sorted(cards)

    if len(cards) == 1:

        confirmed.append({
            "customer_id": customer_id,
            "card_id": cards[0],
            "card_fingerprint": fingerprint,
            "status": "confirmed"
        })

    else:

        ambiguous.append({
            "customer_id": customer_id,
            "card_fingerprint": fingerprint,
            "candidate_card_ids": "|".join(cards),
            "candidate_count": len(cards),
            "status": "ambiguous"
        })


# ---------------------------------------------------------
# 5. Save results
# ---------------------------------------------------------

confirmed_df = pd.DataFrame(confirmed)

ambiguous_df = pd.DataFrame(ambiguous)


confirmed_df.to_csv(
    OUTPUT,
    index=False
)

ambiguous_df.to_csv(
    AMBIGUOUS,
    index=False
)


# ---------------------------------------------------------
# 6. Print summary
# ---------------------------------------------------------

print()
print("=" * 70)
print("RESULT")
print("=" * 70)

print(f"Confirmed mappings : {len(confirmed_df):,}")
print(f"Ambiguous mappings : {len(ambiguous_df):,}")

print()
print(f"Saved:")
print(f"  {OUTPUT}")
print(f"  {AMBIGUOUS}")

print("=" * 70)