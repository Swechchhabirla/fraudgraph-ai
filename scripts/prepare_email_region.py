import pandas as pd
from pathlib import Path


BASE = Path("D:/fraudgraph-ai")

TRANSACTIONS = BASE / "data/raw/transactions.csv"

EMAIL_FILE = BASE / "data/processed/email_domain.csv"
REGION_FILE = BASE / "data/processed/billing_region.csv"

EDGE_DIR = BASE / "data/processed/edges"

EMAIL_EDGE_FILE = EDGE_DIR / "purchaser_email.csv"
REGION_EDGE_FILE = EDGE_DIR / "billed_in.csv"

EDGE_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("PREPARING EMAIL DOMAIN AND BILLING REGION DATA")
print("=" * 70)


# =========================================================
# Storage
# =========================================================

email_domains = set()
regions = set()

email_edges = []
region_edges = []


# =========================================================
# Process transactions in chunks
# =========================================================

usecols = [
    "TransactionID",
    "P_emaildomain",
    "addr1",
]

chunksize = 100000


for chunk_number, chunk in enumerate(
    pd.read_csv(
        TRANSACTIONS,
        usecols=usecols,
        dtype=str,
        chunksize=chunksize,
        keep_default_na=False
    ),
    start=1
):

    print(f"Processing chunk {chunk_number}...")

    for _, row in chunk.iterrows():

        transaction_id = row["TransactionID"].strip()

        if not transaction_id:
            continue


        # =================================================
        # Email domain
        # =================================================

        email_domain = row["P_emaildomain"].strip()

        if email_domain:

            email_domains.add(email_domain)

            email_edges.append({
                "transaction_id": transaction_id,
                "domain": email_domain
            })


        # =================================================
        # Billing region
        # =================================================

        region = row["addr1"].strip()

        if region:

            region_id = f"REG-{region}"

            regions.add(
                region_id
            )

            region_edges.append({
                "transaction_id": transaction_id,
                "region_id": region_id
            })


# =========================================================
# EmailDomain vertices
# =========================================================

email_df = pd.DataFrame({
    "domain": sorted(email_domains)
})

email_df.to_csv(
    EMAIL_FILE,
    index=False
)


# =========================================================
# BillingRegion vertices
# =========================================================

region_df = pd.DataFrame({
    "region_id": sorted(regions)
})

region_df.to_csv(
    REGION_FILE,
    index=False
)


# =========================================================
# PURCHASER_EMAIL edges
# =========================================================

email_edge_df = pd.DataFrame(
    email_edges
).drop_duplicates()

email_edge_df.to_csv(
    EMAIL_EDGE_FILE,
    index=False
)


# =========================================================
# BILLED_IN edges
# =========================================================

region_edge_df = pd.DataFrame(
    region_edges
).drop_duplicates()

region_edge_df.to_csv(
    REGION_EDGE_FILE,
    index=False
)


# =========================================================
# Summary
# =========================================================

print()
print("=" * 70)
print("EMAIL + REGION DATA COMPLETE")
print("=" * 70)

print(f"Email domains       : {len(email_df):,}")
print(f"PURCHASER_EMAIL edges: {len(email_edge_df):,}")

print(f"Billing regions     : {len(region_df):,}")
print(f"BILLED_IN edges     : {len(region_edge_df):,}")

print()
print("Created files:")

print(EMAIL_FILE)
print(REGION_FILE)
print(EMAIL_EDGE_FILE)
print(REGION_EDGE_FILE)

print()
print("Email columns:")
print(list(email_df.columns))

print()
print("Region columns:")
print(list(region_df.columns))

print()
print("Email edge columns:")
print(list(email_edge_df.columns))

print()
print("Region edge columns:")
print(list(region_edge_df.columns))

print("=" * 70)