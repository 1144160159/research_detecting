#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download papers by DOI from IEEE Xplore using authenticated session cookies.
Requires proxy at 127.0.0.1:10808 for institutional IP access.
"""

import json
import os
import re
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urljoin

PAPER_DIR = Path(__file__).parent / "paper"
DOIS_FILE = Path(__file__).parent / "paper_dois.json"
REMAINING_FILE = Path(__file__).parent / "remaining_dois.json"
LOG_FILE = Path(__file__).parent / "download_log.txt"
FAILED_FILE = Path(__file__).parent / "failed_dois.json"

# ============================================================
# Proxy configuration
# ============================================================
PROXY = {
    "http": "http://127.0.0.1:10808",
    "https": "http://127.0.0.1:10808",
}

# ============================================================
# IEEE Xplore session cookies (from browser)
# ============================================================
IEEE_COOKIES = {
    # Session auth (refreshed 2026-06-10)
    "xpluserinfo": "eyJpc0luc3QiOiJ0cnVlIiwiaW5zdE5hbWUiOiJQRVMgVW5pdmVyc2l0eSBCZW5nYWx1cnUiLCJwcm9kdWN0cyI6Ik1JVFA6MTk0MzoyMDI0fFdJTEVZX0RBVEFfQ1lCRVJTRUM6MjAxMzoyMDI0fEFTUFA6MjAxMDoyMDI2fE5PS0lBIEJFTEwgTEFCUzoyMDEwOjIwMjZ8UE9QQUxMOjIwMTA6MjAyNnxWREU6MjAxMDoyMDI2fFdJTEVZQUk6MTg3MjoyMDI2fE1BTk5JTkc6MTg3MjoyMDI2fERFR1JVWVRFUjoxODcyOjIwMjZ8ZUxlYXJuaW5nUGFja2FnZSNFRFBMSUJSQVJZOjIwMDQ6MjAyMXxlTGVhcm5pbmdQYWNrYWdlI0VEUEZST05UTElTVDoyMDIyOjIwMjV8In0=",
    "WLSESSION": "1610838538.47873.0000",
    "ERIGHTS": "hFbRyJs6ml0OBK6NRAn0NFx2F37LIPk6DC-18x2dAgpFx2BUv4g0XazdpYRIPs4Qx3Dx3DHz25evx2FJq1Y39qo5x2FeWdvAx3Dx3D-xxSjPuM2fUIr39FKIZ7DE4wx3Dx3D-UVhlBx2FP29HQDntaSxx2dV2wx3Dx3D",
    "JSESSIONID": "87BBEC99B1D648F32E92599C112B2BC0",
    # CloudFront CDN access
    "CloudFront-Key-Pair-Id": "KBLQQ1K30MUFK",
    "CloudFront-Policy": "eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vaWVlZXhwbG9yZS5pZWVlLm9yZy9tZWRpYXN0b3JlL0lFRUUvY29udGVudC9tZWRpYS84ODU4LzExNDM0NTc1LzExMjY0Mjk0LyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3ODA5NzUxNTZ9LCJJcEFkZHJlc3MiOnsiQVdTOlNvdXJjZUlwIjoiMmEwOTpiYWMxOjMxYzA6ODo6M2QwOjIifX19XX0_",
    "CloudFront-Signature": "QzvUgWkRz3xp1tv4H~h7F2yWXS4hIa~H~1i8jKD18s4eJ8hjp2BpQ2BszHHBn4xPbQF0fHkeBtdscmugxeWHS6P0lI4Fv4xGZMz2gz9ng2sXALgbENjGH-k~UfARPKpvvfDAopfUfpZJGyc0CKvnZaFu7eG-RM~4ZTzjcenkCgeXDvdqsiPL6qJEwNQaC4ntrTz~jU8xu2bn2nTGEyPiIjvbisIHXqPgWyH1ajinBmQxgW2~gn34BoBlQAIVNPdGOru-8yHP82H0ulUXMaJC5v~fltgEpEKgMD24WIPmeFRKhRMfOFwI3EnbZYLuqk4yn6NMnEFQPsX3PKtrJ4KeeA__",
    # Server/traffic cookies
    "TS016349ac": "01f15fc87c585edf175bab11d0bec19cd49575f3c1ee415f72d49a24a898d02c4c60ad21cc4e8097246ce71959e21f7a5ce673dcad",
    "TSaf720a17029": "0807dc117eab2800be82fcb1ed7e048cd8eb6ca7f0d91b1726955dce40632f4d41aafe4670ce3f1bc01451f2618fef8a",
    "TS8b476361027": "0807dc117eab20007a589e62ccf26847732fd5aaee997286939eb21d0ac0acbece0295eebace8fe108f59e360c1130002cc026dc64b9ec8d453e6d25c4b33625c2aa682668dd694bf88e6d63600b6c6f2c5d35450ff3cb5da4b77d27e575b942",
    "AWSALBAPP-0": "AAAAAAAAAAAmJV/Gj9hBfLQdAHSyeAoN0oBQ9oUQMNXZr/8nKSv8MXKAE4iOXv4hbUK2wG+R3v1cIrhXO61qvoa+UiWkZmh6CjATPQIMCaBvYmPU0YSzhnszfJ+1LZkin729AA88RPnyH2d7dRnbZO65gyWaSj4ejZtrEjwW7/dw1+2Hyt4TPYYqZl+qeSz3D6xT+MuDbcKaANEcdUx1PQ==",
    "seqId": "66460",
    # IP list
    "ipList": '"2a09:bac1:31c0:8::3cf:57,2a09:bac1:31c0:8::3d0:2,2a09:bac1:31c0:8::245:c8,2a09:bac1:31c0:8::17:318,2a09:bac1:31c0:8::247:131,2a09:bac1:31c0:8::3cf:21,2a09:bac1:31c0:8::17:368,2a09:bac1:31c0:8::17:260,2a09:bac1:31c0:8::246:1e,2a09:bac1:31c0:8::498:54,2a09:bac1:31c0:8::245:89,2a09:bac1:31c0:8::3cf:1d,2a09:bac1:31c0:8::17:229,2a09:bac1:31c0:8::247:62,2a09:bac1:31c0:8::17:234,2a09:bac1:31c0:8::246:c9,2a09:bac1:1480:240::1d:10d,2a09:bac1:7681:6c40::c7:12,2a09:bac1:1480:240::311:5f,2a09:bac1:7681:6c40::c7:16,2a09:bac1:7681:6c40::c7:17,2a09:bac1:7681:6c40::c7:9,2a09:bac1:1480:240::312:86,2a09:bac1:1480:240::2ac:4a,2a09:bac1:7681:6c40::c7:10,2a09:bac1:7681:6c40::c7:c,2a09:bac1:7681:6c40::c7:15,2a09:bac1:7681:6c40::c7:13,2a09:bac1:1480:240::312:92,2a09:bac1:7681:6c40::c7:f,2a09:bac1:1480:240::311:b0,2a09:bac1:7681:6c40::c7:d"',
    # Additional tracking
    "_zitok": "59447b3d06cd69c2c6cb1780969856",
    "fp": "34c2c7c62446d6d93019afa89a938bf4",
}

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def is_pdf_content(content, content_type=""):
    """Check if response content is a valid PDF."""
    if not content or len(content) < 1024:
        return False
    if "application/pdf" in content_type:
        return True
    if b"%PDF" in content[:1024]:
        return True
    return False


def sanitize_filename(doi, arnumber=None):
    """Convert DOI to a safe filename."""
    safe_doi = doi.replace("/", "_").replace("\\", "_").replace(":", "_")
    if arnumber:
        return f"{arnumber}_{safe_doi}"
    return safe_doi


def create_session():
    """Create a requests Session with IEEE cookies and proxy."""
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    session.proxies.update(PROXY)
    # Set cookies for IEEE domains
    for key, value in IEEE_COOKIES.items():
        if value and value != "_remove_":
            session.cookies.set(key, value, domain=".ieee.org")
            session.cookies.set(key, value, domain="ieeexplore.ieee.org")
    return session


def resolve_doi(session, doi):
    """Resolve DOI to get the IEEE Xplore arnumber (article number). Retries on failure."""
    doi_url = f"https://doi.org/{doi}"
    last_error = None
    for attempt in range(3):
        try:
            r = session.get(doi_url, timeout=30, allow_redirects=True)
            final_url = r.url
            m = re.search(r'/document/(\d+)', final_url)
            if m:
                return m.group(1), final_url
            m = re.search(r'arnumber=(\d+)', final_url)
            if m:
                return m.group(1), final_url
            return None, final_url
        except Exception as e:
            last_error = e
            if attempt < 2:
                time.sleep(2)  # wait before retry
    return None, None


def try_download_via_stampPDF(session, arnumber):
    """
    Download PDF via IEEE stampPDF/getPDF.jsp.
    This is the primary method - returns PDF directly when authenticated.
    """
    pdf_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={arnumber}&ref="
    for attempt in range(3):
        try:
            r = session.get(pdf_url, timeout=30, allow_redirects=True)
            content_type = r.headers.get("content-type", "")
            if r.status_code == 200 and is_pdf_content(r.content, content_type):
                return r.content
            # If we got HTML instead of PDF, might be auth issue - no point retrying
            if "text/html" in content_type:
                return None
        except Exception:
            if attempt < 2:
                time.sleep(1)
    return None


def try_download_via_stamp(session, arnumber):
    """
    Download PDF via IEEE stamp/stamp.jsp.
    This endpoint typically returns an HTML page that loads the PDF via JS.
    """
    stamp_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={arnumber}"
    try:
        r = session.get(stamp_url, timeout=30, allow_redirects=True)
        content_type = r.headers.get("content-type", "")
        if r.status_code == 200 and is_pdf_content(r.content, content_type):
            return r.content
    except Exception:
        pass
    return None


def try_download_via_document_page(session, arnumber):
    """Parse the document page to find PDF download link."""
    doc_url = f"https://ieeexplore.ieee.org/document/{arnumber}/"
    try:
        r = session.get(doc_url, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            return None
        html = r.text

        # Find PDF/stamp links
        pdf_links = set()
        for pattern in [
            r'(/stampPDF/getPDF\.jsp[^"\'\s]*)',
            r'(/stamp/stamp\.jsp[^"\'\s]*)',
            r'"([^"]*stampPDF[^"]*)"',
            r'downloadPdfUrl\s*[=:]\s*"([^"]+)"',
            r'pdfUrl\s*[=:]\s*"([^"]+)"',
        ]:
            for match in re.findall(pattern, html, re.IGNORECASE):
                if match.startswith("/"):
                    match = urljoin(doc_url, match)
                elif not match.startswith("http"):
                    match = urljoin(doc_url, match)
                pdf_links.add(match)

        for pdf_url in list(pdf_links)[:5]:
            try:
                r2 = session.get(pdf_url, timeout=30, allow_redirects=True)
                if r2.status_code == 200 and is_pdf_content(r2.content, r2.headers.get("content-type", "")):
                    return r2.content
            except Exception:
                continue
    except Exception:
        pass
    return None


def is_already_downloaded(doi):
    """Check if a paper is already downloaded (by checking paper directory for matching PDF)."""
    safe_name = sanitize_filename(doi)
    # Check for files matching the DOI pattern
    doi_part = doi.replace("/", "_").replace(chr(92), "_").replace(":", "_")
    for pdf in PAPER_DIR.glob("*.pdf"):
        if doi_part in pdf.stem and pdf.stat().st_size > 10240:
            return True
    return False


def download_paper(session, doi):
    """Download a single paper by DOI."""
    safe_name = sanitize_filename(doi)

    # Skip if already downloaded (check paper directory)
    if is_already_downloaded(doi):
        return "already_exists"

    # Remove old placeholder
    placeholder = PAPER_DIR / f"{safe_name}.need_manual.txt"
    if placeholder.exists():
        placeholder.unlink()

    # Step 1: Resolve DOI to get arnumber
    arnumber, final_url = resolve_doi(session, doi)

    if arnumber:
        # Update filename with arnumber
        new_name = sanitize_filename(doi, arnumber)
        output_path = PAPER_DIR / f"{new_name}.pdf"

        # Remove old file with just DOI name
        old_path = PAPER_DIR / f"{safe_name}.pdf"
        if old_path.exists() and old_path != output_path:
            old_path.unlink()

        # Step 2a: Try stampPDF/getPDF.jsp (primary method)
        content = try_download_via_stampPDF(session, arnumber)
        if content:
            output_path.write_bytes(content)
            return f"OK ({len(content)} bytes)"

        # Step 2b: Try stamp/stamp.jsp
        content = try_download_via_stamp(session, arnumber)
        if content:
            output_path.write_bytes(content)
            return f"OK via stamp.jsp ({len(content)} bytes)"

        # Step 2c: Parse document page
        content = try_download_via_document_page(session, arnumber)
        if content:
            output_path.write_bytes(content)
            return f"OK via page ({len(content)} bytes)"

        # arnumber resolved but all download methods failed
        reason = "download_blocked"
    elif final_url is None:
        reason = "doi_network_error"
    else:
        reason = f"no_arnumber ({final_url[:60]})"

    # Failed
    note_path = PAPER_DIR / f"{safe_name}.need_manual.txt"
    note_path.write_text(
        f"DOI: {doi}\n"
        f"arnumber: {arnumber}\n"
        f"Reason: {reason}\n"
        f"Please visit https://doi.org/{doi} manually\n",
        encoding="utf-8"
    )
    return f"FAIL ({reason})"


def main():
    PAPER_DIR.mkdir(parents=True, exist_ok=True)

    # Clean up old .need_manual.txt files
    for f in PAPER_DIR.glob("*.need_manual.txt"):
        f.unlink()

    # Use remaining_dois.json if available (resume mode), otherwise full list
    doi_file = REMAINING_FILE if REMAINING_FILE.exists() else DOIS_FILE
    with open(doi_file, "r", encoding="utf-8") as f:
        dois = json.load(f)

    # Also filter out already-downloaded papers
    remaining = [d for d in dois if not is_already_downloaded(d)]
    skipped = len(dois) - len(remaining)

    print(f"Total in list: {len(dois)}, Already downloaded: {skipped}, To download: {len(remaining)}")
    print(f"Output directory: {PAPER_DIR}")
    print(f"Using proxy: {PROXY['https']}")
    print(f"Cookie xpluserinfo present: {bool(IEEE_COOKIES.get('xpluserinfo'))}")
    print("-" * 60)

    session = create_session()

    results = {"success": 0, "already_exists": 0, "failed": 0}
    failed_dois = []
    log_lines = []

    for i, doi in enumerate(remaining, 1):
        print(f"[{i}/{len(remaining)}] {doi} ... ", end="", flush=True)

        try:
            status = download_paper(session, doi)
        except Exception as e:
            status = f"error: {e}"

        print(status)
        log_lines.append(f"{doi}\t{status}")

        if status == "already_exists":
            results["already_exists"] += 1
        elif status.startswith("FAIL"):
            results["failed"] += 1
            failed_dois.append(doi)
        else:
            results["success"] += 1

        # Delay every 5 papers to avoid rate limiting
        if i % 5 == 0:
            time.sleep(1)

    # Save log and failed list
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    if failed_dois:
        with open(FAILED_FILE, "w", encoding="utf-8") as f:
            json.dump(failed_dois, f, ensure_ascii=False, indent=2)
        with open(REMAINING_FILE, "w", encoding="utf-8") as f:
            json.dump(failed_dois, f, ensure_ascii=False, indent=2)

    print("-" * 60)
    print(f"Done! Success: {results['success']}, Already exists: {results['already_exists']}, Failed: {results['failed']}")
    print(f"Papers saved to: {PAPER_DIR}")
    if failed_dois:
        print(f"{len(failed_dois)} failed DOIs saved to {FAILED_FILE} and {REMAINING_FILE}")


if __name__ == "__main__":
    main()
