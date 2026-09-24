from pathlib import Path
import csv
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

CLOSED_CASES_FILE = RAW_DIR / "closed_cases_history.csv"
CASE_PACK_FILE = RAW_DIR / "case_pack.csv"
CASE_TXN_FILE = PROCESSED_DIR / "case_transaction_cards.csv"

OUTPUT_FILE = PROCESSED_DIR / "card_case_reference.csv"


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def main():

    print("=" * 70)
    print("STEP 52 - BUILD CARD REFERENCE")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Read case card IDs
    # --------------------------------------------------------

    case_cards = defaultdict(set)

    with open(
        CLOSED_CASES_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            customer_id = clean(row["customer_id"])
            card_id = clean(row["card_id"])

            if customer_id and card_id:
                case_cards[customer_id].add(card_id)

    # --------------------------------------------------------
    # 2. Read benchmark card IDs
    # --------------------------------------------------------

    with open(
        CASE_PACK_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            customer_id = clean(row["customer_id"])
            card_id = clean(row["card_id"])

            if customer_id and card_id:
                case_cards[customer_id].add(card_id)

    # --------------------------------------------------------
    # 3. Read transaction/card combinations
    # --------------------------------------------------------

    transaction_rows = []

    with open(
        CASE_TXN_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            transaction_rows.append(row)

    # --------------------------------------------------------
    # 4. Build reference records
    # --------------------------------------------------------

    output_rows = []

    for row in transaction_rows:

        customer_id = clean(row["customer_id"])

        possible_cards = sorted(
            case_cards.get(customer_id, set())
        )

        # We intentionally DO NOT guess K1/K2.
        #
        # A customer can have multiple cards.
        # The source data shown so far does not establish
        # which raw card fingerprint maps to which K number.

        output_rows.append({
            "TransactionID": clean(row["TransactionID"]),
            "customer_id": customer_id,
            "card1": clean(row["card1"]),
            "card2": clean(row["card2"]),
            "card3": clean(row["card3"]),
            "card4": clean(row["card4"]),
            "card5": clean(row["card5"]),
            "card6": clean(row["card6"]),
            "case_card_ids": "|".join(possible_cards),
        })

    # --------------------------------------------------------
    # 5. Write reference file
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        fieldnames = [
            "TransactionID",
            "customer_id",
            "card1",
            "card2",
            "card3",
            "card4",
            "card5",
            "card6",
            "case_card_ids",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print()
    print(f"Case-related transactions : {len(output_rows):,}")
    print(f"Output                     : {OUTPUT_FILE}")

    print()
    print("IMPORTANT:")
    print("No K1/K2/K3 mapping was guessed.")
    print("The source card IDs remain authoritative.")

    print()
    print("=" * 70)
    print("STEP 52 COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()