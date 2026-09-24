from pathlib import Path
import csv


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = RAW_DIR / "case_pack.csv"
OUTPUT_FILE = PROCESSED_DIR / "case_pack.csv"


# ============================================================
# HELPER
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 47 - BENCHMARK CASE PACK")
    print("=" * 70)

    cases = 0

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile, open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)

        # ----------------------------------------------------
        # Preserve the benchmark case structure
        # ----------------------------------------------------

        writer.writerow([
            "case_id",
            "opened_at",
            "trigger_type",
            "trigger_text",
            "flagged_txn_id",
            "card_id",
            "customer_id",
            "risk_score"
        ])

        for row in reader:

            case_id = clean(row["case_id"])

            if not case_id:
                continue

            writer.writerow([
                case_id,
                clean(row["opened_at"]),
                clean(row["trigger_type"]),
                clean(row["trigger_text"]),
                clean(row["flagged_txn_id"]),
                clean(row["card_id"]),
                clean(row["customer_id"]),
                clean(row["risk_score"])
            ])

            cases += 1

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 47 COMPLETED")
    print("=" * 70)

    print(f"Benchmark cases: {cases:,}")
    print(f"Output: {OUTPUT_FILE}")

    if cases == 20:
        print()
        print("[OK] Expected 20 benchmark cases found.")
    else:
        print()
        print(
            f"[WARNING] Expected 20 cases, "
            f"but found {cases}."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()