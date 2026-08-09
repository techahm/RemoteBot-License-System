#!/usr/bin/env python3

import base64
import datetime
import hashlib
import hmac
import json
import os
import subprocess
import tempfile
import urllib.request


PRODUCT_NAME = "RemoteBot"

# ==========================================================
# GitHub RAW URL
# ==========================================================

LICENSE_URL = (
    "https://raw.githubusercontent.com/techahm/RemoteBot-License-System/main/licenses.json"
)

PUBLIC_KEY_FILE = "public_key.pem"


# ==========================================================
# Download License Database
# ==========================================================

def download_database():

    try:

        request = urllib.request.Request(
            LICENSE_URL,
            headers={
                "User-Agent": "RemoteBot-License"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            content = response.read().decode(
                "utf-8"
            )

        database = json.loads(
            content
        )

        if not isinstance(
            database,
            dict
        ):

            return None

        return database

    except Exception:

        return None


# ==========================================================
# Canonical License Data
# ==========================================================

def canonical_data(record):

    unsigned = {

        "license_id":
            record["license_id"],

        "username":
            record["username"],

        "password_hash":
            record["password_hash"],

        "salt":
            record["salt"],

        "expiry":
            record["expiry"],

        "product":
            record["product"]
    }

    return json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")


# ==========================================================
# Verify Digital Signature
# ==========================================================

def verify_signature(record):

    message_file = None
    signature_file = None

    try:

        # --------------------------------------------------
        # Decode signature
        # --------------------------------------------------

        signature = base64.b64decode(
            record["signature"],
            validate=True
        )

        # --------------------------------------------------
        # Recreate signed data
        # --------------------------------------------------

        message = canonical_data(
            record
        )

        # --------------------------------------------------
        # Temporary message file
        # --------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False
        ) as f:

            f.write(message)

            message_file = f.name

        # --------------------------------------------------
        # Temporary signature file
        # --------------------------------------------------

        signature_file = (
            message_file + ".sig"
        )

        with open(
            signature_file,
            "wb"
        ) as f:

            f.write(signature)

        # --------------------------------------------------
        # OpenSSL verification
        # --------------------------------------------------

        result = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-verify",
                "-pubin",
                "-inkey",
                PUBLIC_KEY_FILE,
                "-rawin",
                "-in",
                message_file,
                "-sigfile",
                signature_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return result.returncode == 0

    except Exception:

        return False

    finally:

        if message_file:

            try:
                os.remove(
                    message_file
                )
            except Exception:
                pass

        if signature_file:

            try:
                os.remove(
                    signature_file
                )
            except Exception:
                pass


# ==========================================================
# Password Verification
# ==========================================================

def verify_password(
    password,
    record
):

    try:

        salt = base64.b64decode(
            record["salt"],
            validate=True
        )

        calculated_hash = (
            hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                200_000
            ).hex()
        )

        return hmac.compare_digest(
            calculated_hash,
            record["password_hash"]
        )

    except Exception:

        return False


# ==========================================================
# Login Verification
# ==========================================================

def verify_login(
    username,
    password
):

    # ------------------------------------------------------
    # Public key check
    # ------------------------------------------------------

    if not os.path.exists(
        PUBLIC_KEY_FILE
    ):

        return False, (
            "public_key.pem not found."
        )

    # ------------------------------------------------------
    # Download database
    # ------------------------------------------------------

    database = download_database()

    if database is None:

        return False, (
            "Cannot connect to license server."
        )

    # ------------------------------------------------------
    # Get licenses
    # ------------------------------------------------------

    licenses = database.get(
        "licenses",
        []
    )

    if not isinstance(
        licenses,
        list
    ):

        return False, (
            "Invalid license database."
        )

    # ------------------------------------------------------
    # Find Username
    # ------------------------------------------------------

    record = None

    for item in licenses:

        if not isinstance(
            item,
            dict
        ):

            continue

        if hmac.compare_digest(
            str(item.get("username", "")),
            username
        ):

            record = item

            break

    if record is None:

        return False, (
            "Username not found."
        )

    # ------------------------------------------------------
    # Product Check
    # ------------------------------------------------------

    if record.get(
        "product"
    ) != PRODUCT_NAME:

        return False, (
            "Invalid product."
        )

    # ------------------------------------------------------
    # Signature Check
    # ------------------------------------------------------

    if not verify_signature(
        record
    ):

        return False, (
            "Invalid license signature."
        )

    # ------------------------------------------------------
    # Password Check
    # ------------------------------------------------------

    if not verify_password(
        password,
        record
    ):

        return False, (
            "Wrong password."
        )

    # ------------------------------------------------------
    # Expiry Check
    # ------------------------------------------------------

    try:

        expiry = datetime.datetime.strptime(
            record["expiry"],
            "%Y-%m-%d"
        ).date()

    except Exception:

        return False, (
            "Invalid expiry date."
        )

    today = datetime.date.today()

    if today > expiry:

        return False, (
            "License expired."
        )

    # ------------------------------------------------------
    # Remaining Days
    # ------------------------------------------------------

    remaining_days = (
        expiry - today
    ).days

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    return True, {

        "license_id":
            record["license_id"],

        "username":
            record["username"],

        "expiry":
            record["expiry"],

        "remaining_days":
            remaining_days
    }


# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    import getpass

    print("""
╔══════════════════════════════════════════╗
║       RemoteBot License Verification     ║
╚══════════════════════════════════════════╝
""")

    username = input(
        "👤 Username: "
    ).strip()

    password = getpass.getpass(
        "🔐 Password: "
    )

    valid, result = verify_login(
        username,
        password
    )

    if valid:

        print("""
╔══════════════════════════════════════════╗
║          ✅ ACCESS GRANTED               ║
╚══════════════════════════════════════════╝
""")

        print(
            "👤 Username :",
            result["username"]
        )

        print(
            "📅 Expiry   :",
            result["expiry"]
        )

        print(
            "⏳ Remaining :",
            result["remaining_days"],
            "days"
        )

    else:

        print("""
╔══════════════════════════════════════════╗
║          ❌ ACCESS DENIED                ║
╚══════════════════════════════════════════╝
""")

        print(
            "Reason:",
            result
        )