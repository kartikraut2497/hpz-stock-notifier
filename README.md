# HPZ Stock Notifier

Monitors a [Headphone Zone](https://www.headphonezone.in) product and sends you an email the moment it comes back in stock. Runs every 30 minutes via GitHub Actions — no server needed, completely free.

Currently tracking: **Tangzu Wan'er S.G 2 Red Lion Edition**

---

## Setup

### 1. Fork / clone this repo
Push it to your own GitHub account.

### 2. Add GitHub Secrets
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these three secrets:

| Secret name       | Value                                      |
|-------------------|--------------------------------------------|
| `SENDER_EMAIL`    | Your Gmail address                         |
| `SENDER_PASSWORD` | Your Gmail **App Password** (not your login password) |
| `RECEIVER_EMAIL`  | Email address to receive notifications     |

> **How to generate a Gmail App Password:**
> 1. Enable 2-Step Verification on your Google account
> 2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 3. Create an app password for "Mail"
> 4. Copy the 16-character password into `SENDER_PASSWORD`

### 3. Enable GitHub Actions
Go to the **Actions** tab in your repo and enable workflows if prompted.

That's it. The workflow runs automatically every 30 minutes.

---

## Manual trigger
You can also trigger a check manually anytime:
**Actions → HPZ Stock Notifier → Run workflow**

---

## Tracking a different product
Change `PRODUCT_HANDLE` in `hpz_notifier.py` to the URL slug of any Headphone Zone product.

For example, for `https://www.headphonezone.in/products/moondrop-chu-ii`, the handle is `moondrop-chu-ii`.

---

## Notes
- GitHub Actions cron has ~1 minute of jitter, so checks won't be perfectly on the dot.
- GitHub may pause scheduled workflows on repos with no activity for 60 days. Just push a small commit to re-enable.
