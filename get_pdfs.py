
# -*- coding: utf-8 -*-
"""
Ravelry multi-pattern batch downloader:
- Extracts metadata
- Handles modal logic robustly
- Downloads PDFs for free Ravelry patterns
"""

import os
import re
import json
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
CSV_AGGREGATE = DOWNLOAD_DIR / "metadata.csv"

# ---------- Helpers ----------
def slug_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    return path.split("/")[-1] or "pattern"

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def extract_dt_dd_map(soup: BeautifulSoup) -> dict:
    info = {}
    for dt in soup.find_all("dt"):
        label = clean_text(dt.get_text()).lower()
        dd = dt.find_next("dd")
        value = clean_text(dd.get_text(" ", strip=True)) if dd else ""
        if label:
            info[label] = value
    return info

def extract_attributes(soup: BeautifulSoup) -> list:
    attrs = []
    el = soup.find(string=re.compile(r"search patterns with these attributes", re.I))
    if el:
        container = el.parent
        for a in container.find_all("a"):
            txt = clean_text(a.get_text())
            if txt and "search patterns" not in txt.lower():
                attrs.append(txt)
    else:
        for a in soup.select("aside a, .sidebar a"):
            txt = clean_text(a.get_text())
            if txt and len(txt) < 50 and not re.search(r"download|buy|queue|favorites", txt, re.I):
                attrs.append(txt)
    seen, out = set(), []
    for x in attrs:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

def extract_description(soup: BeautifulSoup) -> str:
    candidates = soup.select("div#content, main, .content, .pattern-page, .pattern-notes, .notes")
    text_blocks = []
    for c in candidates:
        for p in c.find_all(["p", "div"]):
            txt = clean_text(p.get_text(" ", strip=True))
            if txt and len(txt) > 80:
                text_blocks.append(txt)
        if text_blocks:
            break
    if not text_blocks:
        for p in soup.find_all("p"):
            txt = clean_text(p.get_text(" ", strip=True))
            if txt and len(txt) > 80:
                text_blocks.append(txt)
    return "\n\n".join(text_blocks[:3])

def extract_title_designer(soup: BeautifulSoup) -> tuple[str, str | None]:
    title = None
    h1 = soup.find("h1")
    if h1:
        title = clean_text(h1.get_text())
    if not title:
        og_title = soup.find("meta", {"property": "og:title"})
        if og_title and og_title.get("content"):
            title = clean_text(og_title["content"])
    designer = None
    if h1 and h1.parent:
        neighborhood_text = clean_text(h1.parent.get_text(" ", strip=True))
        m = re.search(r"\bby\s+([^\n]+)", neighborhood_text, re.I)
        if m:
            designer = clean_text(m.group(1))
    if not designer:
        b = soup.find(string=re.compile(r"^by\s", re.I))
        if b:
            designer = clean_text(re.sub(r"^by\s+", "", b, flags=re.I))
    return title, designer

def extract_og_image(soup: BeautifulSoup) -> str | None:
    m = soup.find("meta", {"property": "og:image"})
    return m.get("content") if m and m.get("content") else None

def availability_hints(soup: BeautifulSoup) -> dict:
    txt = soup.get_text(" ", strip=True).lower()
    return {
        "free_ravelry_download": "free ravelry download" in txt,
        "buy_it_now_present": "buy it now" in txt,
    }

def pick(dtdd: dict, key_variants) -> str | None:
    for kv in key_variants:
        if kv in dtdd:
            return dtdd[kv]
    return None

def extract_metadata(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    dtdd = extract_dt_dd_map(soup)
    title, designer = extract_title_designer(soup)
    desc = extract_description(soup)
    attrs = extract_attributes(soup)
    og_img = extract_og_image(soup)
    avail = availability_hints(soup)

    data = {
        "title": title,
        "url": url,
        "designer": designer,
        "description": desc,
        "cover_image": og_img,
        "craft": pick(dtdd, ["craft"]),
        "category": pick(dtdd, ["category"]),
        "published": pick(dtdd, ["published"]),
        "suggested_yarn": pick(dtdd, ["suggested yarn", "suggested yarns"]),
        "yarn_weight": pick(dtdd, ["yarn weight"]),
        "hook_size": pick(dtdd, ["hook size", "needle size"]),
        "yardage": pick(dtdd, ["yardage"]),
        "sizes_available": pick(dtdd, ["sizes available", "size", "sizes"]),
        "terminology": pick(dtdd, ["crochet terminology", "knitting terminology"]),
        "languages": pick(dtdd, ["languages", "language"]),
        "attributes": attrs,
        "availability": avail,
        "pdf": None,
    }
    for k, v in list(data.items()):
        if isinstance(v, str):
            data[k] = clean_text(v)
    return data

def is_probably_pdf_url(url: str) -> bool:
    return ("ravelrycache.com" in url.lower()) and url.lower().endswith(".pdf")

def append_to_csv(rows: list[dict], csv_path: Path):
    flattened = []
    for row in rows:
        r = dict(row)
        pdf = r.pop("pdf", None)
        if isinstance(pdf, dict):
            for k, v in pdf.items():
                r[f"pdf_{k}"] = v
        flattened.append(r)
    df = pd.DataFrame(flattened)
    if csv_path.exists():
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

# ---------- Per-pattern processing ----------
def process_pattern(context, url: str, delay_between_actions: float = 1.0) -> dict:
    slug = slug_from_url(url)
    meta_path = DOWNLOAD_DIR / f"{slug}.json"

    page = context.new_page()
    pdf_holder = {"url": None, "content_type": None, "size": 0}

    def on_response(resp):
        ct = (resp.headers.get("content-type") or "").lower()
        u = resp.url
        if "application/pdf" in ct or is_probably_pdf_url(u):
            pdf_holder["url"] = u
            pdf_holder["content_type"] = ct
            cl = resp.headers.get("content-length")
            if cl and cl.isdigit():
                pdf_holder["size"] = int(cl)

    page.on("response", on_response)

    # 1) Go to page, extract metadata
    page.goto(url, wait_until="domcontentloaded")
    html = page.content()
    metadata = extract_metadata(html, url)
    time.sleep(delay_between_actions)

    # 2) Click Download button
    selectors = [
        "a:has-text('free Ravelry download')",
        "a:has-text('Download')",
        "button:has-text('Download')",
        "a[href*='/dl/']",
        "a[href*='/download']",
    ]
    clicked = False
    for sel in selectors:
        if page.locator(sel).first.is_visible():
            page.locator(sel).first.click()
            clicked = True
            break
    if not clicked:
        for l in page.locator("a").all():
            href = l.get_attribute("href") or ""
            txt = (l.inner_text() or "").strip().lower()
            if "download" in txt or "/dl/" in href or "/download" in href:
                l.click()
                clicked = True
                break
    time.sleep(delay_between_actions + 1.0)

    # 3) Scrape modal links
    saved_pdf_path = None
    if clicked:
        try:
            modal_html = page.locator("div.modal").inner_html()
            print(f"[DEBUG] Modal HTML for {slug}:\n", modal_html[:500], "...\n")
            links = page.locator("div.modal a").all()
            candidates = []
            for l in links:
                href = l.get_attribute("href") or ""
                if href:
                    candidates.append(href)
            print(f"[DEBUG] Found links in modal: {candidates}")
            for href in candidates:
                if href.endswith(".pdf") or "ravelrycache.com" in href:
                    resp = page.request.get(href)
                    fname = os.path.basename(re.sub(r"\?.*$", "", href)) or f"{slug}.pdf"
                    target_path = DOWNLOAD_DIR / fname
                    with open(target_path, "wb") as f:
                        f.write(resp.body())
                    saved_pdf_path = str(target_path)
                    metadata["pdf"] = {
                        "filename": fname,
                        "path": saved_pdf_path,
                        "url": href,
                        "content_type": pdf_holder["content_type"],
                        "size_bytes": pdf_holder["size"] or os.path.getsize(target_path),
                    }
                    print(f"[INFO] Saved PDF for {slug}: {saved_pdf_path}")
                    break
        except Exception as e:
            print(f"[WARN] Modal scraping failed for {slug}: {e}")

    # 4) Save JSON
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    page.close()
    return metadata

# ---------- Batch runner ----------
def load_urls_from_file(path: str) -> list[str]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            u = line.strip()
            if u and u.startswith("http"):
                out.append(u)
    return out

def run_batch(urls: list[str], headless: bool = False, delay_between_pages: float = 1.5):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        storage_state_path = "ravelry_state.json"
        if os.path.exists(storage_state_path):
            context = browser.new_context(storage_state=storage_state_path)
        else:
            context = browser.new_context()

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Processing: {url}")
            try:
                meta = process_pattern(context, url)
                results.append(meta)
                time.sleep(delay_between_pages)
            except Exception as e:
                print(f"[ERROR] Failed on {url}: {e}")
                time.sleep(delay_between_pages)

        context.storage_state(path=storage_state_path)
        browser.close()

    if results:
        append_to_csv(results, CSV_AGGREGATE)
        print(f"[INFO] Appended {len(results)} rows to {CSV_AGGREGATE}")
    else:
        print("[INFO] No results captured.")

# ---------- CLI ----------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Batch download Ravelry patterns + metadata.")
    ap.add_argument("--list", help="Path to a text file with one pattern URL per line.")
    ap.add_argument("--headless", action="store_true", help="Run Chromium headless.")
    args = ap.parse_args()

    if not args.list or not os.path.exists(args.list):
        print("Provide --list <file> with pattern URLs (one per line).")
        exit(1)

    urls = load_urls_from_file(args.list)
    run_batch(urls=urls, headless=args.headless)
