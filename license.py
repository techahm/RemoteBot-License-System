#!/usr/bin/env python3

import base64
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request


PRODUCT_NAME = "RemoteBot"

# ==========================================================
# এখানে আপনার GitHub RAW licenses.json URL বসাবেন
# ==========================================================

LICENSE_URL = (
    "https://github.com/techahm/RemoteBot-License-System/blob/main/license_5vAdDkMgfUGAmUtGjVdrnO2-.json"
)

PUBLIC_KEY_FILE = "public_key.pem"


def download_database():

    try:
        req = urllib.request.Request(
            LICENSE_URL,
            headers={
                "User-Agent": "RemoteBot-License"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:

        return None


def verify_signature(payload):

    try:

        signature = base64.b64decode(
            payload["signature"],
            validate=True
        )

        unsigned = {
            "license_id": payload["license_id"],
            "username": payload["username"],
            "password_hash": payload["password_hash"],
            "salt": payload["salt"],
            "expiry": payload["expiry"],
            "product": payload["product"]
        }

        message = json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")

        with tempfile.NamedTemporaryFile(
            delete=False
        ) as f:

            f.write(message)
            msg_file = f.name

        sig_file = msg_file + ".sig"

        with open(
            sig_file,
            "wb"
        ) as f:

            f.write(signature)

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
                msg_file,
                "-sigfile",
                sig_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        os.remove(msg_file)
        os.remove(sig_file)

        return result.returncode == 0

    except Exception:

        return False


def verify_login(username, password):

    if not os.path.exists(
        PUBLIC_KEY_FILE
    ):
        return False, "public_key.pem not found."

    database = download_database()

    if database is None:
        return False, "Cannot connect to license server."

    licenses = database.get(
        "licenses",
        []
    )

    record = None

    for item in licenses:

        if item.get("username") == username:

            record = item
            break

    if record is None:

        return False, "Username not found."

    if record.get("product") != PRODUCT_NAME:

        return False, "Invalid product."

    # ------------------------------------------------------
    # Verify cryptographic signature FIRST
    # ------------------------------------------------------

    if not verify_signature(record):

        return False, "Invalid license signature."

    # ------------------------------------------------------
    # Password verification
    # ------------------------------------------------------

    try:

        salt = base64.b64decode(
            record["salt"]
        )

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        ).hex()

    except Exception:

        return False, "Invalid password data."

    if not secrets_compare(
        calculated,
        record["password_hash"]
    ):

        return False, "Wrong password."

    # ------------------------------------------------------
    # Expiry
    # ------------------------------------------------------

    try:

        expiry = datetime.datetime.strptime(
            record["expiry"],
            "%Y-%m-%d"
        )

    except Exception:

        return False, "Invalid expiry date."

    if datetime.datetime.now() > expiry:

        return False, "License expired."

    remaining = (
        expiry - datetime.datetime.now()
    ).days

    return True, {
        "license_id": record["license_id"],
        "username": record["username"],
        "expiry": record["expiry"],
        "remaining_days": remaining
    }


def secrets_compare(a, b):

    if len(a) != len(b):
        return False

    result = 0

    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y

    return result == 0


if __name__ == "__main__":

    print("""
╔══════════════════════════════════════════╗
║       RemoteBot Login Verification       ║
╚══════════════════════════════════════════╝
""")

    username = input(
        "👤 Username: "
    ).strip()

    import getpass

    password = getpass.getpass(
        "🔐 Password: "
    )

    valid, result = verify_login(
        username,
        password
    )

    if valid:

        print("\n✅ LOGIN SUCCESSFUL")

        print(
            "👤 Username:",
            result["username"]
        )

        print(
            "📅 Expiry:",
            result["expiry"]
        )

        print(
            "⏳ Remaining:",
            result["remaining_days"],
            "days"
        )

    else:

        print("\n❌ ACCESS DENIED")
        print("Reason:", result)