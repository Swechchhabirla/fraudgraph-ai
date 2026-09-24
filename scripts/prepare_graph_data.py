from pathlib import Path
import csv
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

TRANSACTIONS_FILE = RAW_DIR / "transactions.csv"

CARD_FILE = PROCESSED_DIR / "card.csv"
TRANSACTION_FILE = PROCESSED_DIR / "transaction_new.csv"


# ============================================================
# SETTINGS
# ============================================================

CHUNK_SIZE = 50_000


# ============================================================
# HELPER
# ============================================================

def clean(value):
    """Convert pandas missing values to empty strings."""
    if pd.isna(value):
        return ""

    return str(value).strip()


def make_card_key(row):
    """
    Create a deterministic raw-card key.

    IMPORTANT:
    This is an intermediate key.
    We will validate it against closed_cases_history.csv
    before using it as the final TigerGraph card_id.
    """

    parts = [
        clean(row["card1"]),
        clean(row["card2"]),
        clean(row["card3"]),
        clean(row["card4"]),
        clean(row["card5"]),
        clean(row["card6"]),
    ]

    return "|".join(parts)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 41 - CARD + TRANSACTION PREPARATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Remove old files
    # --------------------------------------------------------

    for file_path in [CARD_FILE, TRANSACTION_FILE]:

        if file_path.exists():
            file_path.unlink()

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    usecols = [
        "TransactionID",
        "TransactionDT",
        "TransactionAmt",
        "ProductCD",

        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",

        "customer_id",
        "ts",
        "channel",
        "risk_score",

        "addr1",
        "P_emaildomain",
    ]

    # --------------------------------------------------------
    # Prepare output files
    # --------------------------------------------------------

    card_file = open(
        CARD_FILE,
        "w",
        encoding="utf-8",
        newline=""
    )

    transaction_file = open(
        TRANSACTION_FILE,
        "w",
        encoding="utf-8",
        newline=""
    )

    card_writer = csv.writer(card_file)
    transaction_writer = csv.writer(transaction_file)

    # TigerGraph vertex headers
    card_writer.writerow([
        "card_id",
        "customer_id",
        "card_network",
        "card_type",
    ])

    transaction_writer.writerow([
        "transaction_id",
        "customer_id",
        "card_id",
        "transaction_time",
        "amount",
        "product_code",
        "channel",
        "risk_score",
        "billing_region",
        "purchaser_email_domain",
    ])

    # --------------------------------------------------------
    # Keep unique cards
    # --------------------------------------------------------

    cards = {}

    total_transactions = 0
    chunk_number = 0

    print()
    print("Processing transactions...")
    print()

    # --------------------------------------------------------
    # Process large file in chunks
    # --------------------------------------------------------

    for chunk in pd.read_csv(
        TRANSACTIONS_FILE,
        usecols=usecols,
        chunksize=CHUNK_SIZE,
        low_memory=True
    ):

        chunk_number += 1

        for _, row in chunk.iterrows():

            transaction_id = clean(row["TransactionID"])
            customer_id = clean(row["customer_id"])

            if not transaction_id or not customer_id:
                continue

            # ----------------------------------------------
            # Intermediate card key
            # ----------------------------------------------

            raw_card_key = make_card_key(row)

            # Skip if no card information
            if not raw_card_key.replace("|", ""):
                continue

            # ----------------------------------------------
            # Temporary card ID
            # ----------------------------------------------

            card_id = f"{customer_id}|{raw_card_key}"

            # ----------------------------------------------
            # Store unique card
            # ----------------------------------------------

            if card_id not in cards:

                cards[card_id] = {
                    "customer_id": customer_id,
                    "card_network": clean(row["card4"]),
                    "card_type": clean(row["card6"]),
                }

            # ----------------------------------------------
            # Transaction
            # ----------------------------------------------

            transaction_writer.writerow([
                transaction_id,
                customer_id,
                card_id,
                clean(row["ts"]),
                clean(row["TransactionAmt"]),
                clean(row["ProductCD"]),
                clean(row["channel"]),
                clean(row["risk_score"]),
                clean(row["addr1"]),
                clean(row["P_emaildomain"]),
            ])

            total_transactions += 1

        print(
            f"Chunk {chunk_number:>3} | "
            f"Transactions: {total_transactions:>9,} | "
            f"Cards: {len(cards):>9,}"
        )

    # --------------------------------------------------------
    # Write cards
    # --------------------------------------------------------

    print()
    print("Writing card.csv...")

    for card_id, data in cards.items():

        card_writer.writerow([
            card_id,
            data["customer_id"],
            data["card_network"],
            data["card_type"],
        ])

    card_file.close()
    transaction_file.close()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("STEP 41 COMPLETED")
    print("=" * 70)

    print(f"Transactions : {total_transactions:,}")
    print(f"Cards        : {len(cards):,}")
    print()
    print(f"Card file        : {CARD_FILE}")
    print(f"Transaction file : {TRANSACTION_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()