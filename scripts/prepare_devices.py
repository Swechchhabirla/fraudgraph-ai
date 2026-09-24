from pathlib import Path
import csv
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

IDENTITY_FILE = RAW_DIR / "identity.csv"
DEVICE_FILE = PROCESSED_DIR / "device_profile.csv"
FROM_DEVICE_FILE = (
    PROCESSED_DIR / "edges" / "from_device.csv"
)

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
(PROCESSED_DIR / "edges").mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def clean(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def make_device_id(device_type, device_info):

    # Deterministic device identifier.
    # We will use the same value for the vertex and edge.

    device_type = clean(device_type)
    device_info = clean(device_info)

    if not device_type and not device_info:
        return ""

    return f"{device_type}|{device_info}"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 44 - DEVICE PROFILE PREPARATION")
    print("=" * 70)

    if DEVICE_FILE.exists():
        DEVICE_FILE.unlink()

    if FROM_DEVICE_FILE.exists():
        FROM_DEVICE_FILE.unlink()

    devices = {}

    transaction_devices = []

    print()
    print("Reading identity.csv...")

    for chunk in pd.read_csv(
        IDENTITY_FILE,
        usecols=[
            "TransactionID",
            "DeviceType",
            "DeviceInfo"
        ],
        chunksize=50_000,
        low_memory=True
    ):

        for _, row in chunk.iterrows():

            transaction_id = clean(row["TransactionID"])
            device_type = clean(row["DeviceType"])
            device_info = clean(row["DeviceInfo"])

            device_id = make_device_id(
                device_type,
                device_info
            )

            if not transaction_id or not device_id:
                continue

            # Store unique device
            if device_id not in devices:

                devices[device_id] = {
                    "device_type": device_type,
                    "device_info": device_info
                }

            # Store transaction -> device relationship
            transaction_devices.append(
                (
                    transaction_id,
                    device_id
                )
            )

    print()
    print(f"Unique devices: {len(devices):,}")
    print(
        f"Transaction-device relationships: "
        f"{len(transaction_devices):,}"
    )

    # ========================================================
    # DEVICE VERTEX FILE
    # ========================================================

    print()
    print("Writing device_profile.csv...")

    with open(
        DEVICE_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "device_id",
            "device_type",
            "device_info"
        ])

        for device_id, data in devices.items():

            writer.writerow([
                device_id,
                data["device_type"],
                data["device_info"]
            ])

    # ========================================================
    # FROM_DEVICE EDGE FILE
    # ========================================================

    print("Writing from_device.csv...")

    with open(
        FROM_DEVICE_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "from_transaction_id",
            "to_device_id"
        ])

        for transaction_id, device_id in transaction_devices:

            writer.writerow([
                transaction_id,
                device_id
            ])

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 44 COMPLETED")
    print("=" * 70)

    print(f"Device vertices : {len(devices):,}")
    print(
        f"Device edges    : "
        f"{len(transaction_devices):,}"
    )

    print()
    print(f"Vertex file : {DEVICE_FILE}")
    print(f"Edge file   : {FROM_DEVICE_FILE}")

    print("=" * 70)


if __name__ == "__main__":
    main()