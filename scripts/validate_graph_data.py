from pathlib import Path
import pandas as pd


BASE = Path("D:/fraudgraph-ai")
DATA = BASE / "data/processed"
EDGES = DATA / "edges"


print("=" * 75)
print("TIGERGRAPH DATA VALIDATION")
print("=" * 75)


# =========================================================
# Expected files
# =========================================================

vertex_files = {
    "Customer": DATA / "customer.csv",
    "Card": DATA / "card.csv",
    "Transaction": DATA / "transaction_new.csv",
    "DeviceProfile": DATA / "device_profile.csv",
    "EmailDomain": DATA / "email_domain.csv",
    "BillingRegion": DATA / "billing_region.csv",
    "ClosedCase": DATA / "closed_case.csv",
}

edge_files = {
    "OWNS": EDGES / "owns.csv",
    "MADE": EDGES / "made.csv",
    "FROM_DEVICE": EDGES / "from_device.csv",
    "PURCHASER_EMAIL": EDGES / "purchaser_email.csv",
    "BILLED_IN": EDGES / "billed_in.csv",
    "INVOLVES": EDGES / "involves.csv",
    "ON_CARD": EDGES / "on_card.csv",
    "CONNECTED_TO": EDGES / "connected_to.csv",
    "NEXT": EDGES / "next.csv",
}


# =========================================================
# Helper
# =========================================================

def inspect_file(name, path):

    print()
    print("-" * 75)
    print(name)
    print("-" * 75)

    if not path.exists():

        print("❌ MISSING")
        print(path)

        return False

    try:

        df = pd.read_csv(
            path,
            dtype=str,
            nrows=5
        )

        total_rows = sum(
            1
            for _ in open(
                path,
                "r",
                encoding="utf-8-sig",
                errors="ignore"
            )
        ) - 1

        print("✅ EXISTS")
        print(f"Rows: {total_rows:,}")
        print(f"Columns: {list(df.columns)}")

        print()
        print(df.head(3).to_string(index=False))

        return True

    except Exception as e:

        print("❌ ERROR")
        print(str(e))

        return False


# =========================================================
# Vertex validation
# =========================================================

print()
print("VERTICES")

vertex_ok = True

for name, path in vertex_files.items():

    if not inspect_file(
        f"VERTEX: {name}",
        path
    ):
        vertex_ok = False


# =========================================================
# Edge validation
# =========================================================

print()
print()
print("EDGES")

edge_ok = True

for name, path in edge_files.items():

    if not inspect_file(
        f"EDGE: {name}",
        path
    ):
        edge_ok = False


# =========================================================
# Final result
# =========================================================

print()
print()
print("=" * 75)
print("VALIDATION RESULT")
print("=" * 75)

if vertex_ok and edge_ok:

    print("✅ ALL EXPECTED FILES EXIST")
    print()
    print("The graph data is ready for the next validation stage.")

else:

    print("❌ SOME FILES ARE MISSING OR INVALID")
    print()
    print("Do NOT import into TigerGraph yet.")


print("=" * 75)