#!/usr/bin/env python
# coding: utf-8
"""
get_twitter_cookies.py
-----------------------
Extracts Twitter session cookies from your existing Chrome or Edge browser
(where you're already logged into Twitter). No login needed.

IMPORTANT: Close Chrome/Edge completely before running this.

Run once (or when cookies expire):
    python tools/get_twitter_cookies.py
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

COOKIE_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "twitter_cookies.json")

LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")

BROWSER_PROFILES = [
    # (channel, user_data_dir, label)
    ("chrome", os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data"), "Chrome"),
    ("msedge", os.path.join(LOCALAPPDATA, "Microsoft", "Edge", "User Data"),  "Edge"),
]


async def extract_cookies():
    browser_found = False

    async with async_playwright() as p:
        for channel, user_data_dir, label in BROWSER_PROFILES:
            if not os.path.exists(user_data_dir):
                continue

            print(f"[INFO] Found {label} profile at: {user_data_dir}")
            print(f"[INFO] Opening {label} with your existing session ...")
            print(f"[INFO] Make sure {label} is fully closed before running this.\n")

            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    channel=channel,
                    headless=False,
                    args=["--no-first-run", "--no-default-browser-check"],
                )
            except Exception as e:
                print(f"[WARN] Could not open {label}: {e}")
                print(f"[WARN] Make sure {label} is fully closed and try again.\n")
                continue

            browser_found = True
            page = await context.new_page()

            # Navigate to Twitter to ensure cookies are loaded
            print("[INFO] Opening Twitter ...")
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            current_url = page.url
            if "login" in current_url or "flow" in current_url:
                print("[WARN] Twitter is showing the login page — you're not logged in on this browser.")
                print("[WARN] Log into Twitter in this browser first, then re-run this script.")
                await context.close()
                sys.exit(1)

            print(f"[INFO] Logged in — URL: {current_url}")

            # Extract cookies
            cookies = await context.cookies(["https://x.com", "https://twitter.com"])
            twitter_cookies = {c["name"]: c["value"] for c in cookies}

            os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
            with open(COOKIE_PATH, "w") as f:
                json.dump(twitter_cookies, f, indent=2)

            print(f"\n[DONE] Saved {len(twitter_cookies)} cookies → {os.path.abspath(COOKIE_PATH)}")
            await context.close()
            return

    if not browser_found:
        print("[ERROR] No Chrome or Edge installation found.")
        print("        Install Chrome or Edge and log into Twitter, then re-run.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(extract_cookies())
