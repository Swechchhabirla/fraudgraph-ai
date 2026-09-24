from pathlib import Path
import csv
from collections import defaultdict


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

CLOSED_CASES = RAW_DIR / "closed_cases_history.csv"
CASE_PACK = RAW_DIR / "case_pack.csv"
CASE_TXNS = PROCESSED_DIR / "case_transaction_cards.csv"

OUTPUT_MAPPING = PROCESSED_DIR / "card_mapping.csv"
OUTPUT_AMBIGUOUS = PROCESSED_DIR / "card_mapping_ambiguous.csv"


# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    value = str(value).strip()

    if value.lower() in ("nan", "none"):
        return ""

    return value


def fingerprint(row):
    """
    Raw card identity from the original Vesta card fields.
    """

    return "|".join([
        clean(row["card1"]),
        clean(row["card2"]),
        clean(row["card3"]),
        clean(row["card4"]),
        clean(row["card5"]),
        clean(row["card6"]),
    ])


def split_txns(value):
    value = clean(value)

    if not value:
        return []

    return [
        x.strip()
        for x in value.split("|")
        if x.strip()
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 56 - INFER CARD MAPPING")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Build transaction -> case card mapping
    # --------------------------------------------------------

    txn_to_cards = defaultdict(set)

    with open(
        CLOSED_CASES,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            card_id = clean(row["card_id"])

            if not card_id:
                continue

            txn_ids = set()

            first_txn = clean(
                row["first_fraud_txn_id"]
            )

            if first_txn:
                txn_ids.add(first_txn)

            for txn_id in split_txns(
                row["txn_ids"]
            ):
                txn_ids.add(txn_id)

            for txn_id in txn_ids:
                txn_to_cards[txn_id].add(card_id)

    # --------------------------------------------------------
    # 2. Read raw card fingerprint for those transactions
    # --------------------------------------------------------

    fingerprint_to_cards = defaultdict(set)
    card_to_fingerprints = defaultdict(set)

    rows_read = 0
    matched_txns = 0

    with open(
        CASE_TXNS,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            rows_read += 1

            txn_id = clean(
                row["TransactionID"]
            )

            if txn_id not in txn_to_cards:
                continue

            fp = fingerprint(row)

            if not fp:
                continue

            matched_txns += 1

            for card_id in txn_to_cards[txn_id]:

                fingerprint_to_cards[fp].add(card_id)
                card_to_fingerprints[card_id].add(fp)

    # --------------------------------------------------------
    # 3. Determine unambiguous mappings
    # --------------------------------------------------------

    mappings = []
    ambiguous = []

    for card_id in sorted(card_to_fingerprints):

        fingerprints = card_to_fingerprints[
            card_id
        ]

        if len(fingerprints) == 1:

            fp = next(iter(fingerprints))

            associated_cards = (
                fingerprint_to_cards[fp]
            )

            if len(associated_cards) == 1:

                mappings.append({
                    "card_id": card_id,
                    "card_fingerprint": fp,
                    "status": "confirmed",
                })

            else:

                ambiguous.append({
                    "card_id": card_id,
                    "card_fingerprints": " || ".join(
                        sorted(fingerprints)
                    ),
                    "reason": (
                        "Same fingerprint is associated "
                        "with multiple case card IDs"
                    ),
                })

        else:

            ambiguous.append({
                "card_id": card_id,
                "card_fingerprints": " || ".join(
                    sorted(fingerprints)
                ),
                "reason": (
                    "Card ID is associated with "
                    "multiple raw fingerprints"
                ),
            })

    # --------------------------------------------------------
    # 4. Write confirmed mapping
    # --------------------------------------------------------

    with open(
        OUTPUT_MAPPING,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "card_id",
                "card_fingerprint",
                "status",
            ]
        )

        writer.writeheader()
        writer.writerows(mappings)

    # --------------------------------------------------------
    # 5. Write ambiguous mapping
    # --------------------------------------------------------

    with open(
        OUTPUT_AMBIGUOUS,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "card_id",
                "card_fingerprints",
                "reason",
            ]
        )

        writer.writeheader()
        writer.writerows(ambiguous)

    # --------------------------------------------------------
    # 6. Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"Case transaction rows read : {rows_read:,}")
    print(f"Matched transaction rows   : {matched_txns:,}")
    print(f"Confirmed card mappings    : {len(mappings):,}")
    print(f"Ambiguous card mappings    : {len(ambiguous):,}")

    print()
    print(f"Confirmed mapping file:")
    print(OUTPUT_MAPPING)

    print()
    print(f"Ambiguous mapping file:")
    print(OUTPUT_AMBIGUOUS)

    print()
    print("=" * 70)

    if ambiguous:
        print(
            "WARNING: Some Card IDs have ambiguous mappings."
        )
    else:
        print(
            "ALL CASE CARD IDS HAVE UNAMBIGUOUS MAPPINGS."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()