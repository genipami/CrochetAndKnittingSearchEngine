

# -*- coding: utf-8 -*-
"""
Download PDFs for free Ravelry patterns using `download_url` from enriched metadata.
- Reads JSON files from downloads_api_enriched/
- Checks if free_ravelry_download is True and download_url exists
- Resolves redirects, validates content-type, and falls back to parsing HTML interstitials
- Saves PDFs in ./pdfs with canonical names: {id}.pdf or {permalink}.pdf
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

# -------------------------
# Auth (env vars or defaults)
# -------------------------
CONSUMER_KEY = os.getenv("RAVELRY_CONSUMER_KEY", "15c948c58a84cc81c3cd01df60d40a28")
CONSUMER_SECRET = os.getenv("RAVELRY_CONSUMER_SECRET", "uqlkk_iRsKsluJHDEyJABKcLsutsxupvWjduE38M")
ACCESS_TOKEN = os.getenv("RAVELRY_ACCESS_TOKEN", "6qCZndZUP1cHXUPgpWx1nn7ZNpe5cyz48WJQeygZ")
ACCESS_SECRET = os.getenv("RAVELRY_ACCESS_SECRET", "hkBOYFw9c4fuKoF976XAuFi99Puu5xcAxbCGqXSP")
AUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

# -------------------------
# Paths
# -------------------------
ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"
PDF_DIR = ROOT_DIR / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# Helpers
# -------------------------
PDF_CT_RE = re.compile(r"application/pdf", re.I)

def is_pdf_response(resp: Response) -> bool:
    ct = (resp.headers.get("Content-Type") or "").lower()
    return bool(PDF_CT_RE.search(ct))

def find_pdf_href_in_html(html: str) -> Optional[str]:
    """Find a likely PDF link inside an interstitial HTML page."""
    m = re.search(r'href="\'', html, re.I)
    if m:
        return m.group(1)
    m = re.search(r'src="\'', html, re.I)
    if m:
        return m.group(1)
    return None

def request_with_redirects(session: requests.Session, url: str, method: str = "GET", stream: bool = True, timeout: int = 60) -> Response:
    headers = {
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

def resolve_and_download_pdf(download_url: str, meta: dict, retries: int = 2, pause: float = 0.8) -> Optional[Dict[str, Any]]:
    """
    Resolve the API-provided download_url to a final PDF and save it.
    Save as {id}.pdf or {permalink}.pdf for canonical naming.
    """
    session = requests.Session()
    session.auth = AUTH
    attempt = 0
    last_err: Optional[str] = None

    # Determine canonical filename
    canonical_name = f"{meta.get('id') or meta.get('permalink')}.pdf"
    target_path = PDF_DIR / canonical_name

    while attempt <= retries:
        try:
            head_resp = request_with_redirects(session, download_url, method="HEAD", stream=False)
            final_head_url = str(head_resp.url)
            if is_pdf_response(head_resp):
                download_binary(session, final_head_url, target_path)
                return {
                    "filename": canonical_name,
                    "path": str(target_path),
                    "url": final_head_url,
                    "size_bytes": target_path.stat().st_size,
                }

            get_resp = request_with_redirects(session, download_url, method="GET", stream=True)
            final_get_url = str(get_resp.url)
            if is_pdf_response(get_resp):
                with open(target_path, "wb") as f:
                    for chunk in get_resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return {
                    "filename": canonical_name,
                    "path": str(target_path),
                    "url": final_get_url,
                    "size_bytes": target_path.stat().st_size,
                }

            html_text = get_resp.text
            pdf_href = find_pdf_href_in_html(html_text)
            if pdf_href:
                download_binary(session, pdf_href, target_path)
                return {
                    "filename": canonical_name,
                    "path": str(target_path),
                    "url": pdf_href,
                    "size_bytes": target_path.stat().st_size,
                }

            last_err = f"No PDF link found for {canonical_name} (url: {final_get_url})"
        except Exception as e:
            last_err = f"Error: {e}"

        attempt += 1
        if attempt <= retries:
            print(f"[WARN] Retry {attempt}/{retries} for {canonical_name}. {last_err}")
            time.sleep(pause)

    print(f"[ERROR] Could not download PDF for {canonical_name}: {last_err}")
    return None

# -------------------------
# Main loop
# -------------------------
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
        if isinstance(data.get("pdf"), dict) and data["pdf"].get("path") and pathlib.Path(data["pdf"]["path"]).exists():
            done += 1
            print(f"[{i}/{len(files)}] [SKIP] Already downloaded: {slug}")
            continue
        print(f"[{i}/{len(files)}] [PROCESS] {slug} → resolving and downloading …")
        pdf_info = resolve_and_download_pdf(download_url, data, retries=2, pause=0.8)
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
