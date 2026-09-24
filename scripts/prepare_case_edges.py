import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

INPUT = BASE / "data/raw/closed_cases_history.csv"

EDGE_DIR = BASE / "data/processed/edges"
EDGE_DIR.mkdir(parents=True, exist_ok=True)

INVOLVES_FILE = EDGE_DIR / "involves.csv"
ON_CARD_FILE = EDGE_DIR / "on_card.csv"
CONNECTED_FILE = EDGE_DIR / "connected_to.csv"


print("=" * 70)
print("PREPARING CLOSED CASE EDGES")
print("=" * 70)


df = pd.read_csv(
    INPUT,
    dtype=str,
    keep_default_na=False
)


# =========================================================
# INVOLVES
# ClosedCase -> Transaction
# =========================================================

involves_rows = []


for _, row in df.iterrows():

    case_id = row["case_id"].strip()

    txn_ids = row["txn_ids"].strip()

    if not case_id or not txn_ids:
        continue

    for txn_id in txn_ids.split("|"):

        txn_id = txn_id.strip()

        if txn_id:
            involves_rows.append({
                "case_id": case_id,
                "transaction_id": txn_id
            })


involves = pd.DataFrame(
    involves_rows
).drop_duplicates()


involves.to_csv(
    INVOLVES_FILE,
    index=False
)


# =========================================================
# ON_CARD
# ClosedCase -> Card
# =========================================================

on_card = df[
    ["case_id", "card_id"]
].copy()

on_card = on_card[
    (on_card["case_id"].str.strip() != "") &
    (on_card["card_id"].str.strip() != "")
]

on_card = on_card.drop_duplicates()

on_card.to_csv(
    ON_CARD_FILE,
    index=False
)


# =========================================================
# CONNECTED_TO
# ClosedCase -> connected Card
# =========================================================

connected_rows = []


for _, row in df.iterrows():

    case_id = row["case_id"].strip()

    connected_cards = row["connected_card_ids"].strip()

    if not case_id or not connected_cards:
        continue

    for card_id in connected_cards.split("|"):

        card_id = card_id.strip()

        if card_id:
            connected_rows.append({
                "case_id": case_id,
                "card_id": card_id
            })


connected = pd.DataFrame(
    connected_rows
).drop_duplicates()


connected.to_csv(
    CONNECTED_FILE,
    index=False
)


# =========================================================
# Summary
# =========================================================

print()
print("=" * 70)
print("CASE EDGES COMPLETE")
print("=" * 70)

print(f"INVOLVES edges    : {len(involves):,}")
print(f"ON_CARD edges     : {len(on_card):,}")
print(f"CONNECTED_TO edges: {len(connected):,}")

print()
print("Files:")

print(INVOLVES_FILE)
print(ON_CARD_FILE)
print(CONNECTED_FILE)

print()
print("INVOLVES columns:")
print(list(involves.columns))

print()
print("ON_CARD columns:")
print(list(on_card.columns))

print()
print("CONNECTED_TO columns:")
print(list(connected.columns))

print("=" * 70)