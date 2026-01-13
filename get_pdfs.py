
# -*- coding: utf-8 -*-
"""
Download PDFs for free Ravelry patterns using `download_url` from enriched metadata.

- Reads JSON files from downloads_api_enriched/
- Checks if free_ravelry_download is True and download_url exists
- Resolves redirects, validates content-type, and falls back to parsing HTML interstitials
- Saves PDFs in ./pdfs (same level as downloads_api_enriched)
- Updates the JSON with PDF info
"""

import os
import re
import json
import time
import pathlib
from typing import Optional, Dict, Any, Tuple

import requests
from requests_oauthlib import OAuth1
from requests import Response

# -----------------------------
# Auth (env vars or defaults)
# -----------------------------
CONSUMER_KEY    = os.getenv("RAVELRY_CONSUMER_KEY",    "15c948c58a84cc81c3cd01df60d40a28")
CONSUMER_SECRET = os.getenv("RAVELRY_CONSUMER_SECRET", "uqlkk_iRsKsluJHDEyJABKcLsutsxupvWjduE38M")
ACCESS_TOKEN    = os.getenv("RAVELRY_ACCESS_TOKEN",    "6qCZndZUP1cHXUPgpWx1nn7ZNpe5cyz48WJQeygZ")
ACCESS_SECRET   = os.getenv("RAVELRY_ACCESS_SECRET",   "hkBOYFw9c4fuKoF976XAuFi99Puu5xcAxbCGqXSP")

AUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

# -----------------------------
# Paths (pdfs folder sibling to downloads_api_enriched)
# -----------------------------
ROOT_DIR       = pathlib.Path(".").resolve()
METADATA_DIR   = ROOT_DIR / "downloads_api_enriched"
PDF_DIR        = ROOT_DIR / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Helpers
# -----------------------------
PDF_CT_RE = re.compile(r"application/pdf", re.I)

def is_pdf_response(resp: Response) -> bool:
    ct = (resp.headers.get("Content-Type") or "").lower()
    return bool(PDF_CT_RE.search(ct))

def safe_pdf_filename_from_url(url: str, slug: str) -> str:
    # Strip query and fragment
    base = url.split("?")[0].split("#")[0]
    name = os.path.basename(base) or f"{slug}.pdf"
    # Force .pdf extension if missing
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    return name

def find_pdf_href_in_html(html: str) -> Optional[str]:
    """
    Find a likely PDF link inside an interstitial HTML page.
    Look for ravelrycache.com URLs or any href/src ending with .pdf
    """
    # Common case: ravelrycache.com direct cache link
    m = re.search(r'href=["\'](https?://[^"\']*ravelrycache\.com[^return m.group(1)]')

    # Fallback: any .pdf href
    m = re.search(r'href=["\'](https?://[^"\']*')
    if m:
        return m.group(1)

    # Fallback: any .pdf src (rare)
    m = re.search(r'src="\'["\']', html, re.I)
    if m:
        return m.group(1)

    return None

def request_with_redirects(session: requests.Session, url: str, method: str = "GET", stream: bool = True, timeout: int = 60) -> Response:
    headers = {
        # Hint the server that we expect a PDF
        "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (metadata-downloader; +https://www.ravelry.com/)",
    }
    if method == "HEAD":
        resp = session.head(url, allow_redirects=True, headers=headers, timeout=timeout)
    else:
        resp = session.get(url, allow_redirects=True, headers=headers, stream=stream, timeout=timeout)
    resp.raise_for_status()
    return resp

def download_binary(session: requests.Session, final_url: str, target_path: pathlib.Path, timeout: int = 120) -> None:
    headers = {
        "Accept": "application/pdf,*/*;q=0.1",
        "User-Agent": "Mozilla/5.0 (metadata-downloader; +https://www.ravelry.com/)",
    }
    with session.get(final_url, stream=True, headers=headers, timeout=timeout) as r:
        r.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def resolve_and_download_pdf(download_url: str, slug: str, retries: int = 2, pause: float = 0.8) -> Optional[Dict[str, Any]]:
    """
    Try to resolve the API-provided download_url to a final PDF and save it.
    Strategy:
      1) HEAD (follow redirects) -> if Content-Type=pdf, use that URL.
      2) GET (stream) -> if pdf, save; if HTML, parse for .pdf link and download that.
      3) Retries for transient failures.
    """
    session = requests.Session()
    session.auth = AUTH

    attempt = 0
    last_err: Optional[str] = None

    while attempt <= retries:
        try:
            # 1) HEAD: quick metadata & redirect resolution
            head_resp = request_with_redirects(session, download_url, method="HEAD", stream=False)
            final_head_url = str(head_resp.url)

            if is_pdf_response(head_resp):
                fname = safe_pdf_filename_from_url(final_head_url, slug)
                target_path = PDF_DIR / fname
                download_binary(session, final_head_url, target_path)
                return {
                    "filename": fname,
                    "path": str(target_path),
                    "url": final_head_url,
                    "size_bytes": target_path.stat().st_size,
                }

            # 2) GET: either pdf or HTML interstitial that contains the real pdf link
            get_resp = request_with_redirects(session, download_url, method="GET", stream=True)
            final_get_url = str(get_resp.url)

            if is_pdf_response(get_resp):
                fname = safe_pdf_filename_from_url(final_get_url, slug)
                target_path = PDF_DIR / fname
                # We already have the response; stream it to disk
                with open(target_path, "wb") as f:
                    for chunk in get_resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return {
                    "filename": fname,
                    "path": str(target_path),
                    "url": final_get_url,
                    "size_bytes": target_path.stat().st_size,
                }

            # If HTML, parse for the pdf link inside the page
            html_text = ""
            try:
                # If stream=True, content might be chunked; read text safely
                html_text = get_resp.text
            except Exception:
                # Fall back to a non-stream re-fetch to get text cleanly
                get_resp_close = session.get(final_get_url, allow_redirects=True, timeout=60)
                get_resp_close.raise_for_status()
                html_text = get_resp_close.text

            pdf_href = find_pdf_href_in_html(html_text)
            if pdf_href:
                # Download from the discovered pdf link
                fname = safe_pdf_filename_from_url(pdf_href, slug)
                target_path = PDF_DIR / fname
                download_binary(session, pdf_href, target_path)
                return {
                    "filename": fname,
                    "path": str(target_path),
                    "url": pdf_href,
                    "size_bytes": target_path.stat().st_size,
                }

            last_err = f"HTML interstitial did not contain a .pdf link for {slug} (url: {final_get_url})"

        except requests.HTTPError as e:
            last_err = f"HTTP error: {e}"
        except requests.RequestException as e:
            last_err = f"Request exception: {e}"
        except Exception as e:
            last_err = f"Unexpected error: {e}"

        attempt += 1
        if attempt <= retries:
            print(f"[WARN] Attempt {attempt}/{retries} failed for {slug}. {last_err}. Retrying in {pause}s …")
            time.sleep(pause)

    print(f"[ERROR] Could not download PDF for {slug}: {last_err}")
    return None

# -----------------------------
# Main loop
# -----------------------------
def process_metadata_files() -> Tuple[int, int, int]:
    files = sorted(METADATA_DIR.glob("*.json"))
    print(f"[INFO] Found {len(files)} metadata files in {METADATA_DIR}.")

    done = 0
    skipped = 0
    failed = 0

    for i, file in enumerate(files, start=1):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = file.stem
        free = bool(data.get("free_ravelry_download"))
        download_url = data.get("download_url")

        if not free or not download_url:
            skipped += 1
            print(f"[{i}/{len(files)}] [SKIP] Not free or missing download_url: {slug}")
            continue

        # Skip if already downloaded
        if isinstance(data.get("pdf"), dict) and data["pdf"].get("path") and pathlib.Path(data["pdf"]["path"]).exists():
            done += 1
            print(f"[{i}/{len(files)}] [SKIP] Already downloaded: {slug}")
            continue

        print(f"[{i}/{len(files)}] [PROCESS] {slug} → resolving and downloading …")
        pdf_info = resolve_and_download_pdf(download_url, slug, retries=2, pause=0.8)
        if pdf_info:
            data["pdf"] = pdf_info
            with open(file, "w", encoding="utf-8") as fw:
                json.dump(data, fw, ensure_ascii=False, indent=2)
            print(f"[INFO] Saved PDF and updated metadata for {slug}")
            done += 1
        else:
            failed += 1
            print(f"[WARN] Download failed for {slug}")

    print(f"[SUMMARY] Done: {done}, Skipped: {skipped}, Failed: {failed}")
    return done, skipped, failed

if __name__ == "__main__":
    process_metadata_files()
