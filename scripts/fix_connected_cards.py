import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

CARD_FILE = BASE / "data/processed/card.csv"
CLOSED_CASES = BASE / "data/raw/closed_cases_history.csv"

OUTPUT = BASE / "data/processed/card.csv"


print("=" * 70)
print("FIXING CONNECTED CARD VERTICES")
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
# 2. Load historical cases
# =========================================================

cases = pd.read_csv(
    CLOSED_CASES,
    dtype=str,
    keep_default_na=False
)


# =========================================================
# 3. Extract every connected card
# =========================================================

connected_cards = []

for _, row in cases.iterrows():

    customer_id = row["customer_id"].strip()

    connected = row["connected_card_ids"].strip()

    if not connected:
        continue

    for card_id in connected.split("|"):

        card_id = card_id.strip()

        if card_id:

            connected_cards.append({
                "card_id": card_id,
                "customer_id": customer_id,
                "card_network": "",
                "card_type": ""
            })


connected_df = pd.DataFrame(
    connected_cards
).drop_duplicates(
    subset=["card_id"]
)


print(
    f"Connected cards found: {len(connected_df):,}"
)


# =========================================================
# 4. Find missing cards
# =========================================================

existing_ids = set(
    cards["card_id"]
    .astype(str)
    .str.strip()
)

connected_ids = set(
    connected_df["card_id"]
    .astype(str)
    .str.strip()
)

missing_ids = connected_ids - existing_ids


print(
    f"Missing connected cards: {len(missing_ids):,}"
)


# =========================================================
# 5. Add missing cards
# =========================================================

if missing_ids:

    missing_cards = connected_df[
        connected_df["card_id"].isin(missing_ids)
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
print("CONNECTED CARD FIX COMPLETE")
print("=" * 70)

print(f"Cards added: {len(missing_ids):,}")
print(f"Final cards: {len(cards):,}")

print()
print(f"Saved:")
print(OUTPUT)

print("=" * 70)