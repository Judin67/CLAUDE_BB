#!/usr/bin/env python
# coding: utf-8
"""
fetch_twitter_mentions.py
--------------------------
Scrapes tweets from trader profiles using Playwright + saved Edge cookies.
Navigates to each trader's Twitter page as a real browser would.

Usage:
    from tools.fetch_twitter_mentions import fetch_mentions
    from datetime import date

    df = fetch_mentions(["krisVerma88", "TheShortSniper"], date.today())
    # Returns DataFrame[trader, ticker]

Prerequisites:
    Run tools/get_twitter_cookies.py once to save session cookies.
"""

import asyncio
import json
import os
import re
from datetime import date, datetime, timezone

import pandas as pd
import pytz
from playwright.async_api import async_playwright

COOKIE_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "twitter_cookies.json")
CASHTAG_RE  = re.compile(r'\$([A-Z]{1,5})\b')
ET          = pytz.timezone("America/New_York")

SKIP_TICKERS = {"I", "A", "AI", "IT", "GO", "BE", "AM", "ON", "BY", "AT", "OR", "IN", "IS"}


def _load_cookies() -> list:
    """Load cookies and convert to Playwright format."""
    if not os.path.exists(COOKIE_PATH):
        raise FileNotFoundError(
            f"Cookie file not found: {COOKIE_PATH}\n"
            "Run first:  python tools/get_twitter_cookies.py"
        )
    with open(COOKIE_PATH) as f:
        raw = json.load(f)

    # Convert {name: value} dict → Playwright cookie list
    cookies = []
    for name, value in raw.items():
        cookies.append({
            "name":   name,
            "value":  str(value),
            "domain": ".x.com",
            "path":   "/",
        })
    return cookies


async def _scrape_trader(page, handle: str, target_date: date) -> list[str]:
    """Navigate to a trader's profile and extract cashtags from today's tweets."""
    url = f"https://x.com/{handle}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Check if we hit a login wall or 404
        current = page.url
        if "login" in current or "flow" in current:
            raise PermissionError("Cookies expired — re-run tools/get_twitter_cookies.py")

        not_found = page.locator('[data-testid="error-detail"]')
        if await not_found.count() > 0:
            raise ValueError(f"Account @{handle} not found or suspended")

        # Scroll to load more tweets (one scroll is usually enough for same-day)
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(2000)

        # Extract all tweet articles
        articles = await page.query_selector_all('article[data-testid="tweet"]')
        seen    = set()
        tickers = []

        for article in articles:
            # Get timestamp from <time datetime="..."> (ISO 8601 UTC)
            time_el = await article.query_selector("time[datetime]")
            if not time_el:
                continue
            dt_str = await time_el.get_attribute("datetime")
            try:
                dt_utc = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                dt_et  = dt_utc.astimezone(ET)
            except Exception:
                continue

            if dt_et.date() != target_date:
                continue

            # Get tweet text
            text_el = await article.query_selector('[data-testid="tweetText"]')
            if not text_el:
                continue
            text = await text_el.inner_text()

            for t in CASHTAG_RE.findall(text.upper()):
                if t not in SKIP_TICKERS and t not in seen:
                    seen.add(t)
                    tickers.append(t)

        return tickers

    except PermissionError:
        raise
    except Exception as e:
        raise RuntimeError(str(e))


async def _fetch_async(traders: list[str], target_date: date) -> pd.DataFrame:
    cookies = _load_cookies()
    rows    = []

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(os.path.dirname(__file__), "..", ".tmp", "pw_profile"),
            headless=True,
            args=["--no-sandbox"],
        )
        # Inject saved cookies
        await context.add_cookies(cookies)
        page = await context.new_page()

        for handle in traders:
            print(f"[INFO] Scraping @{handle} ...", end=" ", flush=True)
            try:
                tickers = await _scrape_trader(page, handle, target_date)
                if tickers:
                    print(f"{len(tickers)} ticker(s): {tickers}")
                    for t in tickers:
                        rows.append({"trader": handle, "ticker": t})
                else:
                    print(f"no mentions for {target_date}")
            except PermissionError as e:
                print(f"AUTH ERROR — {e}")
                raise
            except Exception as e:
                print(f"WARN — {e}")

        await context.close()

    if not rows:
        return pd.DataFrame(columns=["trader", "ticker"])
    return pd.DataFrame(rows)


def fetch_mentions(traders: list[str], target_date: date = None) -> pd.DataFrame:
    """
    Scrape cashtag mentions from Twitter trader profiles.

    Args:
        traders     : list of Twitter handles (without @)
        target_date : date to filter tweets (default: today)

    Returns:
        pd.DataFrame[trader, ticker] — one row per unique (trader, ticker) pair.
    """
    if target_date is None:
        target_date = date.today()
    return asyncio.run(_fetch_async(traders, target_date))


if __name__ == "__main__":
    df = fetch_mentions(["krisVerma88"], date.today())
    print(df)
