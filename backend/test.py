import re, time, io, os
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor

try:
    from pdfminer.high_level import extract_text
except Exception as e:
    print(f"{str(e)} -> Cannot import `pdfminer`!")

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

BASE = "https://docs.legis.wisconsin.gov"
TOC_URL = "https://docs.legis.wisconsin.gov/statutes/prefaces/toc"
HEADERS = {"User-Agent": "wi-statutes-scraper/0.1 (contact: you@example.com)"}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def http_get(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp

def grab_doc_links(soup):
    links = soup.find_all("a", href=lambda h: h and h.startswith("/document/statutes/ch."))
    results = []
    for a in links:
        href = a.get("href")
        href = href.replace("/document", "/statutes").replace("ch.%20", "")
        full_url = urljoin(BASE, href)
        title = a.get_text(strip=True)
        if full_url.lower().endswith(".pdf") and results:
            title = results[-1]["title"]
        results.append({"title": title, "url": full_url})
    return results

def clean_html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img", "source", "form", "iframe"]):
        tag.decompose()
    for tag in soup.find_all(["nav", "header", "footer", "aside"]):
        tag.decompose()

    for tag in soup.find_all(class_=True):
        classes = tag.get("class", [])
        if any(c.startswith("qshead") or c.startswith("qstoc_entry") for c in classes):
            tag.decompose()

    for a in soup.find_all("a"):
        a.unwrap()

    main = soup.find("main") or soup.find(id="content") or soup.body or soup
    raw = main.get_text(separator="\n")

    lines = [ln.strip() for ln in raw.splitlines()]
    out = []
    for ln in lines:
        if ln:
            out.append(ln)
        elif out and out[-1] != "":
            out.append("")

    start_idx = 0
    chapter_re = re.compile(r"^CHAPTER\s+\d+[A-Za-z]*$")
    section_re = re.compile(r"^\d+\.\d+")
    for i, ln in enumerate(out):
        if chapter_re.match(ln) or section_re.match(ln):
            start_idx = i
            break
    out = out[start_idx:]
    return "\n".join(out).strip()

def process_html_document(title, url, html, save_dir=None):
    pass

def pdf_bytes_to_text(pdf_bytes):
    try:
        return extract_text(io.BytesIO(pdf_bytes)).strip()
    except Exception:
        return None

def scrape_one(title, url, save_dir=None, throttle=0.5):
    print(f"Scraping: {title} -> {url}")
    r = http_get(url)
    text = None
    ct = r.headers.get("Content-Type", "").lower()

    if url.lower().endswith(".pdf") or "application/pdf" in ct:
        text = pdf_bytes_to_text(r.content)
    else:
        text = clean_html_to_text(r.text)

    if text is None or not text.strip():
        text = ""

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        safe = title or urlparse(url).path.rsplit("/", 1)[-1]
        safe = "".join(c for c in safe if c.isalnum() or c in (" ", ".", "_", "-")).strip()
        if not safe:
            safe = "chapter"
        path = os.path.join(save_dir, f"{safe}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    time.sleep(throttle)
    return {"title": title, "url": url, "text": text}

if __name__ == "__main__":
    resp = requests.get(TOC_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    chapters = grab_doc_links(soup)
    
    with ThreadPoolExecutor(max_workers=5) as tp:
        futures = [tp.submit(scrape_one, item["title"], item["url"], "wi_statutes_txt") for item in chapters]

    results = [f.result() for f in futures]