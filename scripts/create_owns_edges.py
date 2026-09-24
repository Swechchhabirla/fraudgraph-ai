from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent

CARD_FILE = BASE_DIR / "data" / "processed" / "card.csv"
EDGE_DIR = BASE_DIR / "data" / "processed" / "edges"
OWNS_FILE = EDGE_DIR / "owns.csv"

EDGE_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("STEP 42 - CREATE OWNS EDGES")
print("=" * 70)

seen = set()
count = 0

with open(
    CARD_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as infile, open(
    OWNS_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    # TigerGraph edge format
    writer.writerow([
        "from_customer_id",
        "to_card_id"
    ])

    for row in reader:

        customer_id = row["customer_id"].strip()
        card_id = row["card_id"].strip()

        if not customer_id or not card_id:
            continue

        key = (customer_id, card_id)

        if key in seen:
            continue

        seen.add(key)

        writer.writerow([
            customer_id,
            card_id
        ])

        count += 1

print()
print(f"OWNS edges created: {count:,}")
print(f"Output: {OWNS_FILE}")

print()
print("=" * 70)
print("STEP 42 COMPLETED")
print("=" * 70)