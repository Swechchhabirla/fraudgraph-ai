import pandas as pd
from pathlib import Path

BASE = Path("D:/fraudgraph-ai")
DATA = BASE / "data/processed"
EDGES = DATA / "edges"

print("=" * 75)
print("FOREIGN KEY / EDGE REFERENCE VALIDATION")
print("=" * 75)


def load_ids(file, column):
    df = pd.read_csv(
        file,
        dtype=str,
        usecols=[column],
        keep_default_na=False
    )

    return set(
        df[column]
        .astype(str)
        .str.strip()
    )


def check_edge(name, file, source_col, source_file, source_id_col,
               target_col, target_file, target_id_col):

    print()
    print(f"Checking {name}...")

    source_ids = load_ids(
        source_file,
        source_id_col
    )

    target_ids = load_ids(
        target_file,
        target_id_col
    )

    edge_df = pd.read_csv(
        file,
        dtype=str,
        usecols=[source_col, target_col],
        keep_default_na=False
    )

    source_values = set(
        edge_df[source_col]
        .astype(str)
        .str.strip()
    )

    target_values = set(
        edge_df[target_col]
        .astype(str)
        .str.strip()
    )

    missing_source = source_values - source_ids
    missing_target = target_values - target_ids

    print(f"Edges: {len(edge_df):,}")
    print(f"Missing source vertices: {len(missing_source):,}")
    print(f"Missing target vertices: {len(missing_target):,}")

    if missing_source:
        print("Sample missing sources:")
        print(list(missing_source)[:10])

    if missing_target:
        print("Sample missing targets:")
        print(list(missing_target)[:10])

    if not missing_source and not missing_target:
        print("✅ PASS")
        return True

    print("❌ FAIL")
    return False


results = []


# =========================================================
# OWNS
# Customer -> Card
# =========================================================

results.append(
    check_edge(
        "OWNS",
        EDGES / "owns.csv",
        "customer_id",
        DATA / "customer.csv",
        "customer_id",
        "card_id",
        DATA / "card.csv",
        "card_id"
    )
)


# =========================================================
# MADE
# Card -> Transaction
# =========================================================

results.append(
    check_edge(
        "MADE",
        EDGES / "made.csv",
        "card_id",
        DATA / "card.csv",
        "card_id",
        "transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id"
    )
)


# =========================================================
# FROM_DEVICE
# Transaction -> DeviceProfile
# =========================================================

results.append(
    check_edge(
        "FROM_DEVICE",
        EDGES / "from_device.csv",
        "transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id",
        "device_id",
        DATA / "device_profile.csv",
        "device_id"
    )
)


# =========================================================
# PURCHASER_EMAIL
# =========================================================

results.append(
    check_edge(
        "PURCHASER_EMAIL",
        EDGES / "purchaser_email.csv",
        "transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id",
        "domain",
        DATA / "email_domain.csv",
        "domain"
    )
)


# =========================================================
# BILLED_IN
# =========================================================

results.append(
    check_edge(
        "BILLED_IN",
        EDGES / "billed_in.csv",
        "transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id",
        "region_id",
        DATA / "billing_region.csv",
        "region_id"
    )
)


# =========================================================
# INVOLVES
# =========================================================

results.append(
    check_edge(
        "INVOLVES",
        EDGES / "involves.csv",
        "case_id",
        DATA / "closed_case.csv",
        "case_id",
        "transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id"
    )
)


# =========================================================
# ON_CARD
# =========================================================

results.append(
    check_edge(
        "ON_CARD",
        EDGES / "on_card.csv",
        "case_id",
        DATA / "closed_case.csv",
        "case_id",
        "card_id",
        DATA / "card.csv",
        "card_id"
    )
)


# =========================================================
# CONNECTED_TO
# =========================================================

results.append(
    check_edge(
        "CONNECTED_TO",
        EDGES / "connected_to.csv",
        "case_id",
        DATA / "closed_case.csv",
        "case_id",
        "card_id",
        DATA / "card.csv",
        "card_id"
    )
)


# =========================================================
# NEXT
# =========================================================

results.append(
    check_edge(
        "NEXT",
        EDGES / "next.csv",
        "from_transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id",
        "to_transaction_id",
        DATA / "transaction_new.csv",
        "transaction_id"
    )
)


# =========================================================
# FINAL
# =========================================================

print()
print("=" * 75)
print("FINAL RESULT")
print("=" * 75)

passed = sum(results)
total = len(results)

print(f"Passed: {passed}/{total}")

if passed == total:
    print()
    print("✅ ALL EDGE REFERENCES ARE VALID")
    print("The data is ready for TigerGraph import.")

else:
    print()
    print("❌ SOME EDGE REFERENCES ARE INVALID")
    print("DO NOT import into TigerGraph yet.")

print("=" * 75)