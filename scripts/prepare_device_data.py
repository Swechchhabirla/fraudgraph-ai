import pandas as pd
from pathlib import Path
import hashlib


BASE = Path("D:/fraudgraph-ai")

IDENTITY_FILE = BASE / "data/raw/identity.csv"

DEVICE_FILE = BASE / "data/processed/device_profile.csv"

EDGE_DIR = BASE / "data/processed/edges"
EDGE_FILE = EDGE_DIR / "from_device.csv"

EDGE_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("PREPARING DEVICE PROFILE DATA")
print("=" * 70)


# =========================================================
# 1. Read identity data
# =========================================================

usecols = [
    "TransactionID",
    "DeviceType",
    "DeviceInfo",
]


devices = {}

edges = []

chunksize = 100000


# =========================================================
# 2. Process identity.csv in chunks
# =========================================================

for chunk_number, chunk in enumerate(
    pd.read_csv(
        IDENTITY_FILE,
        usecols=usecols,
        dtype=str,
        chunksize=chunksize,
        keep_default_na=False
    ),
    start=1
):

    print(f"Processing identity chunk {chunk_number}...")

    for _, row in chunk.iterrows():

        transaction_id = row["TransactionID"].strip()
        device_type = row["DeviceType"].strip()
        device_info = row["DeviceInfo"].strip()

        if not transaction_id:
            continue

        # -------------------------------------------------
        # Skip records where there is no device information
        # -------------------------------------------------

        if not device_type and not device_info:
            continue


        # -------------------------------------------------
        # Create deterministic Device ID
        # -------------------------------------------------

        raw_device = f"{device_type}|{device_info}"

        digest = hashlib.sha1(
            raw_device.encode("utf-8")
        ).hexdigest()[:12]

        device_id = f"DEV-{digest}"


        # -------------------------------------------------
        # Device vertex
        # -------------------------------------------------

        if device_id not in devices:

            devices[device_id] = {
                "device_id": device_id,
                "device_type": device_type,
                "device_info": device_info,
            }


        # -------------------------------------------------
        # Transaction -> Device edge
        # -------------------------------------------------

        edges.append({
            "transaction_id": transaction_id,
            "device_id": device_id
        })


# =========================================================
# 3. Save DeviceProfile vertices
# =========================================================

device_df = pd.DataFrame(
    list(devices.values())
)

device_df.to_csv(
    DEVICE_FILE,
    index=False
)


# =========================================================
# 4. Save FROM_DEVICE edges
# =========================================================

edge_df = pd.DataFrame(edges)

edge_df = edge_df.drop_duplicates()

edge_df.to_csv(
    EDGE_FILE,
    index=False
)


# =========================================================
# 5. Summary
# =========================================================

print()
print("=" * 70)
print("DEVICE DATA COMPLETE")
print("=" * 70)

print(f"Device profiles : {len(device_df):,}")
print(f"FROM_DEVICE edges: {len(edge_df):,}")

print()
print("Device file:")
print(DEVICE_FILE)

print()
print("Edge file:")
print(EDGE_FILE)

print()
print("Device columns:")
print(list(device_df.columns))

print()
print("Edge columns:")
print(list(edge_df.columns))

print("=" * 70)