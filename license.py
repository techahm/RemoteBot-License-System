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
# GitHub RAW DATABASE URL
# ==========================================================

LICENSE_URL = (
    "https://raw.githubusercontent.com/"
    "techahm/RemoteBot-License-System/main/licenses.json"
)

# ==========================================================
# Public Key
# ==========================================================

PUBLIC_KEY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "public_key.pem"
)


# ==========================================================
# Download licenses.json
# ==========================================================

def download_database():

    try:

        request = urllib.request.Request(
            LICENSE_URL,
            headers={
                "User-Agent": "RemoteBot-License-System"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            data = response.read().decode("utf-8")

        database = json.loads(data)

        if not isinstance(database, dict):
            return None

        if "licenses" not in database:
            return None

        if not isinstance(database["licenses"], list):
            return None

        return database

    except Exception as e:

        print(
            f"\n⚠️ License server error: {e}"
        )

        return None


# ==========================================================
# Constant-time string comparison
# ==========================================================

def secrets_compare(a, b):

    if not isinstance(a, str):
        return False

    if not isinstance(b, str):
        return False

    if len(a) != len(b):
        return False

    result = 0

    for x, y in zip(
        a.encode("utf-8"),
        b.encode("utf-8")
    ):

        result |= x ^ y

    return result == 0


# ==========================================================
# Verify RSA Signature
# ==========================================================

def verify_signature(payload):

    msg_file = None
    sig_file = None

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

        # Temporary message file
        with tempfile.NamedTemporaryFile(
            delete=False
        ) as f:

            f.write(message)
            msg_file = f.name

        # Temporary signature file
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

        return result.returncode == 0

    except Exception:

        return False

    finally:

        # Cleanup temporary files
        if msg_file:

            try:
                os.remove(msg_file)
            except Exception:
                pass

        if sig_file:

            try:
                os.remove(sig_file)
            except Exception:
                pass


# ==========================================================
# Verify Username + Password
# ==========================================================

def verify_login(username, password):

    # ------------------------------------------------------
    # Check public key
    # ------------------------------------------------------

    if not os.path.exists(
        PUBLIC_KEY_FILE
    ):

        return (
            False,
            "public_key.pem not found."
        )

    # ------------------------------------------------------
    # Download database
    # ------------------------------------------------------

    database = download_database()

    if database is None:

        return (
            False,
            "Cannot connect to license server."
        )

    licenses = database.get(
        "licenses",
        []
    )

    # ------------------------------------------------------
    # Find username
    # ------------------------------------------------------

    record = None

    for item in licenses:

        if item.get("username") == username:

            record = item
            break

    if record is None:

        return (
            False,
            "Username not found."
        )

    # ------------------------------------------------------
    # Product check
    # ------------------------------------------------------

    if record.get("product") != PRODUCT_NAME:

        return (
            False,
            "Invalid product."
        )

    # ------------------------------------------------------
    # Signature check
    # ------------------------------------------------------

    if not verify_signature(record):

        return (
            False,
            "Invalid license signature."
        )

    # ------------------------------------------------------
    # Password check
    # ------------------------------------------------------

    try:

        salt = base64.b64decode(
            record["salt"]
        )

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        ).hex()

    except Exception:

        return (
            False,
            "Invalid password data."
        )

    if not secrets_compare(
        calculated_hash,
        record.get("password_hash", "")
    ):

        return (
            False,
            "Wrong password."
        )

    # ------------------------------------------------------
    # Expiry check
    # ------------------------------------------------------

    try:

        expiry = datetime.datetime.strptime(
            record["expiry"],
            "%Y-%m-%d"
        )

    except Exception:

        return (
            False,
            "Invalid expiry date."
        )

    # ------------------------------------------------------
    # Expired?
    # ------------------------------------------------------

    now = datetime.datetime.now()

    if now.date() > expiry.date():

        return (
            False,
            "License expired."
        )

    # ------------------------------------------------------
    # Remaining days
    # ------------------------------------------------------

    remaining_days = (
        expiry.date() - now.date()
    ).days

    # ------------------------------------------------------
    # Login successful
    # ------------------------------------------------------

    return True, {

        "license_id":
            record.get("license_id", ""),

        "username":
            record.get("username", ""),

        "expiry":
            record.get("expiry", ""),

        "remaining_days":
            remaining_days

    }


# ==========================================================
# Login Screen
# ==========================================================

def check_license():

    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[1m"
    X = "\033[0m"

    print(
        f"""
{Y}{B}
╔══════════════════════════════════════════╗
║             RemoteBot Login              ║
╚══════════════════════════════════════════╝
{X}
"""
    )

    # ------------------------------------------------------
    # Username
    # ------------------------------------------------------

    username = input(
        f"{Y}👤 Username: {X}"
    ).strip()

    if not username:

        print(
            f"{R}❌ Username required.{X}"
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Password
    # ------------------------------------------------------

    import getpass

    password = getpass.getpass(
        f"{Y}🔐 Password: {X}"
    )

    if not password:

        print(
            f"{R}❌ Password required.{X}"
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Verify
    # ------------------------------------------------------

    print(
        f"\n{Y}⏳ Verifying account...{X}"
    )

    valid, result = verify_login(
        username,
        password
    )

    # ------------------------------------------------------
    # Access denied
    # ------------------------------------------------------

    if not valid:

        print(
            f"""
{R}{B}
╔══════════════════════════════════════════╗
║             ❌ ACCESS DENIED             ║
╠══════════════════════════════════════════╣
║  {str(result):<38} ║
╚══════════════════════════════════════════╝
{X}
"""
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Access granted
    # ------------------------------------------------------

    print(
        f"""
{G}{B}
╔══════════════════════════════════════════╗
║             ✅ ACCESS GRANTED            ║
╠══════════════════════════════════════════╣
║  👤 User: {result["username"]:<29} ║
║  📅 Expiry: {result["expiry"]:<27} ║
║  ⏳ Days: {result["remaining_days"]:<29} ║
╚══════════════════════════════════════════╝
{X}
"""
    )

    return True


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":

    check_license()
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
