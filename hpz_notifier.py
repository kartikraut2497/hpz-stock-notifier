"""
Headphone Zone Stock Notifier
Monitors a specific variant of a Headphone Zone product and sends an email when
it comes back in stock. Runs as a GitHub Actions job.
"""

import requests
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────

PRODUCT_HANDLE   = "tangzu-waner-s-g-2-red-lion-edition"
TARGET_VARIANT   = "Type-C"   # exact variant title to watch (case-sensitive)

SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECEIVER_EMAIL  = os.environ["RECEIVER_EMAIL"]

# ─────────────────────────────────────────────

PRODUCT_URL = f"https://www.headphonezone.in/products/{PRODUCT_HANDLE}"
API_URL     = f"https://www.headphonezone.in/products/{PRODUCT_HANDLE}.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def fetch_product() -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (hpz-stock-notifier)"}
    resp = requests.get(API_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()["product"]


def is_variant_available(v: dict) -> bool:
    avail  = v.get("available")
    qty    = v.get("inventory_quantity", 0)
    policy = v.get("inventory_policy", "")
    return avail is True or (isinstance(qty, int) and qty > 0) or policy == "continue"


def check_target_variant(product: dict) -> tuple[bool, dict | None]:
    """
    Logs all variants for visibility, then returns whether the
    TARGET_VARIANT specifically is available.
    """
    log.info("── Variant breakdown ──────────────────────────")
    target = None
    for v in product["variants"]:
        title  = v.get("title", "Default")
        avail  = v.get("available")
        qty    = v.get("inventory_quantity", "N/A")
        policy = v.get("inventory_policy", "N/A")
        marker = " ← watching this" if title == TARGET_VARIANT else ""
        log.info(
            "  %s | available=%s | qty=%s | policy=%s%s",
            title, avail, qty, policy, marker,
        )
        if title == TARGET_VARIANT:
            target = v
    log.info("───────────────────────────────────────────────")

    if target is None:
        log.warning(
            "Variant '%s' not found in product. "
            "Check the exact title in the logs above.", TARGET_VARIANT
        )
        return False, None

    return is_variant_available(target), target


def send_email(product_title: str, variant: dict):
    subject = f"✅ Back in Stock: {product_title} — {TARGET_VARIANT}"
    body = f"""\
Good news! The variant you're watching is now available on Headphone Zone:

Product : {product_title}
Variant : {variant.get('title')}
Price   : ₹{variant.get('price')}
Link    : {PRODUCT_URL}

Head over and grab it before it sells out again!
"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

    log.info("Notification email sent to %s", RECEIVER_EMAIL)


def main():
    log.info("Watching variant '%s' of: %s", TARGET_VARIANT, PRODUCT_HANDLE)

    product  = fetch_product()
    title    = product.get("title", PRODUCT_HANDLE)
    in_stock, variant = check_target_variant(product)

    if in_stock:
        log.info("✅ IN STOCK — %s | %s | ₹%s", title, variant.get("title"), variant.get("price"))
        send_email(title, variant)
    else:
        log.info("❌ Out of stock — %s [%s]. No email sent.", title, TARGET_VARIANT)


if __name__ == "__main__":
    main()
