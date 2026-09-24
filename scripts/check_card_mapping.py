from pathlib import Path
import csv
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


TRANSACTIONS_FILE = RAW_DIR / "transactions.csv"
CLOSED_CASES_FILE = RAW_DIR / "closed_cases_history.csv"
CASE_PACK_FILE = RAW_DIR / "case_pack.csv"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 51 - CARD ID CONSISTENCY CHECK")
    print("=" * 70)

    # --------------------------------------------------------
    # Historical card IDs
    # --------------------------------------------------------

    historical_cards = set()

    with open(
        CLOSED_CASES_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            card_id = str(row["card_id"]).strip()

            if card_id:
                historical_cards.add(card_id)

    # --------------------------------------------------------
    # Benchmark card IDs
    # --------------------------------------------------------

    benchmark_cards = set()

    with open(
        CASE_PACK_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            card_id = str(row["card_id"]).strip()

            if card_id:
                benchmark_cards.add(card_id)

    all_case_cards = historical_cards | benchmark_cards

    print()
    print(f"Historical case cards : {len(historical_cards):,}")
    print(f"Benchmark case cards  : {len(benchmark_cards):,}")
    print(f"Unique case cards     : {len(all_case_cards):,}")

    print()
    print("Example case card IDs:")

    for card_id in sorted(all_case_cards)[:20]:
        print(" ", card_id)

    # --------------------------------------------------------
    # Transaction IDs that matter to cases
    # --------------------------------------------------------

    transaction_ids = set()

    with open(
        CLOSED_CASES_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            values = [
                row["first_fraud_txn_id"],
                row["txn_ids"],
            ]

            for value in values:

                if not value:
                    continue

                for txn_id in value.replace("|", ",").split(","):

                    txn_id = txn_id.strip()

                    if txn_id:
                        transaction_ids.add(txn_id)

    with open(
        CASE_PACK_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            txn_id = str(
                row["flagged_txn_id"]
            ).strip()

            if txn_id:
                transaction_ids.add(txn_id)

    print()
    print(
        f"Case-related transaction IDs: "
        f"{len(transaction_ids):,}"
    )

    # --------------------------------------------------------
    # Find those transactions in the large file
    # --------------------------------------------------------

    print()
    print("Searching transactions.csv...")
    print("This may take a little while.")

    usecols = [
        "TransactionID",
        "customer_id",
        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",
    ]

    matches = []

    for chunk in pd.read_csv(
        TRANSACTIONS_FILE,
        usecols=usecols,
        chunksize=50_000,
        low_memory=True
    ):

        chunk["TransactionID"] = (
            chunk["TransactionID"]
            .astype(str)
            .str.strip()
        )

        found = chunk[
            chunk["TransactionID"].isin(transaction_ids)
        ]

        if not found.empty:

            for _, row in found.iterrows():

                matches.append({
                    "TransactionID": str(
                        row["TransactionID"]
                    ),
                    "customer_id": str(
                        row["customer_id"]
                    ),
                    "card1": str(row["card1"]),
                    "card2": str(row["card2"]),
                    "card3": str(row["card3"]),
                    "card4": str(row["card4"]),
                    "card5": str(row["card5"]),
                    "card6": str(row["card6"]),
                })

    # --------------------------------------------------------
    # Print matches
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("CASE TRANSACTION CARD DATA")
    print("=" * 70)

    print(
        f"Transactions found: "
        f"{len(matches):,}"
    )

    for row in matches[:20]:

        print()
        print(
            f"TransactionID : {row['TransactionID']}"
        )
        print(
            f"Customer      : {row['customer_id']}"
        )
        print(
            f"card1         : {row['card1']}"
        )
        print(
            f"card2         : {row['card2']}"
        )
        print(
            f"card3         : {row['card3']}"
        )
        print(
            f"card4         : {row['card4']}"
        )
        print(
            f"card5         : {row['card5']}"
        )
        print(
            f"card6         : {row['card6']}"
        )

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    output = PROCESSED_DIR / "case_transaction_cards.csv"

    with open(
        output,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "TransactionID",
                "customer_id",
                "card1",
                "card2",
                "card3",
                "card4",
                "card5",
                "card6",
            ]
        )

        writer.writeheader()
        writer.writerows(matches)

    print()
    print(f"Saved: {output}")

    print()
    print("=" * 70)
    print("STEP 51 COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()