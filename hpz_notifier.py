"""
Headphone Zone Stock Notifier
Monitors a Headphone Zone product and sends an email when it comes back in stock.
Designed to run as a GitHub Actions job — reads credentials from environment variables.
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

PRODUCT_HANDLE = "headphone-zone-x-tangzu-waner-sg-edition-red"

# Read from GitHub Actions secrets (set these in your repo settings)
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


def check_availability(product: dict) -> tuple[bool, list[dict]]:
    available_variants = [
        v for v in product["variants"]
        if v.get("available") is True
    ]
    return bool(available_variants), available_variants


def format_variant_list(variants: list[dict]) -> str:
    return "\n".join(
        f"  • {v.get('title', 'Default')}  —  ₹{v.get('price', 'N/A')}"
        for v in variants
    )


def send_email(product_title: str, variants: list[dict]):
    subject = f"✅ Back in Stock: {product_title}"
    body = f"""\
Good news! The following product is now available on Headphone Zone:

{product_title}
{PRODUCT_URL}

Available variants:
{format_variant_list(variants)}

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
    log.info("Checking stock for: %s", PRODUCT_HANDLE)

    product = fetch_product()
    title   = product.get("title", PRODUCT_HANDLE)
    in_stock, available_variants = check_availability(product)

    if in_stock:
        log.info("✅ IN STOCK — %s", title)
        for v in available_variants:
            log.info("  Variant: %s | Price: ₹%s", v.get("title"), v.get("price"))
        send_email(title, available_variants)
    else:
        log.info("❌ Out of stock — %s. No email sent.", title)


if __name__ == "__main__":
    main()
