import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

CARD_FILE = BASE / "data/processed/card.csv"
CLOSED_CASES = BASE / "data/raw/closed_cases_history.csv"
CASE_PACK = BASE / "data/raw/case_pack.csv"

OUTPUT = BASE / "data/processed/card.csv"


print("=" * 70)
print("FIXING CASE CARD VERTICES")
print("=" * 70)


# =========================================================
# 1. Load existing cards
# =========================================================

cards = pd.read_csv(
    CARD_FILE,
    dtype=str,
    keep_default_na=False
)

print(f"Existing cards: {len(cards):,}")


# =========================================================
# 2. Collect authoritative case cards
# =========================================================

case_cards = []


# Historical closed cases
closed = pd.read_csv(
    CLOSED_CASES,
    dtype=str,
    keep_default_na=False
)

for _, row in closed.iterrows():

    card_id = row["card_id"].strip()
    customer_id = row["customer_id"].strip()

    if card_id and customer_id:

        case_cards.append({
            "card_id": card_id,
            "customer_id": customer_id,
            "card_network": "",
            "card_type": ""
        })


# Benchmark case pack
case_pack = pd.read_csv(
    CASE_PACK,
    dtype=str,
    keep_default_na=False
)

for _, row in case_pack.iterrows():

    card_id = row["card_id"].strip()
    customer_id = row["customer_id"].strip()

    if card_id and customer_id:

        case_cards.append({
            "card_id": card_id,
            "customer_id": customer_id,
            "card_network": "",
            "card_type": ""
        })


# =========================================================
# 3. Create DataFrame
# =========================================================

case_card_df = pd.DataFrame(case_cards)

case_card_df = case_card_df.drop_duplicates(
    subset=["card_id"]
)


print(
    f"Unique case cards found: {len(case_card_df):,}"
)


# =========================================================
# 4. Find missing case cards
# =========================================================

existing_ids = set(
    cards["card_id"]
    .astype(str)
    .str.strip()
)

case_ids = set(
    case_card_df["card_id"]
    .astype(str)
    .str.strip()
)

missing_ids = case_ids - existing_ids


print(
    f"Missing case cards: {len(missing_ids):,}"
)


# =========================================================
# 5. Add missing cards
# =========================================================

if missing_ids:

    missing_cards = case_card_df[
        case_card_df["card_id"].isin(missing_ids)
    ].copy()

    cards = pd.concat(
        [
            cards,
            missing_cards
        ],
        ignore_index=True
    )


# =========================================================
# 6. Remove duplicate Card IDs
# =========================================================

cards = cards.drop_duplicates(
    subset=["card_id"],
    keep="first"
)


# =========================================================
# 7. Save
# =========================================================

cards.to_csv(
    OUTPUT,
    index=False
)


print()
print("=" * 70)
print("CASE CARD FIX COMPLETE")
print("=" * 70)

print(f"Final cards: {len(cards):,}")
print(f"Cards added: {len(missing_ids):,}")

print()
print(f"Saved:")
print(OUTPUT)

print("=" * 70)