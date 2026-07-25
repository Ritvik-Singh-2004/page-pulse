from collections import Counter
import time
from re import compile
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx2
from bs4 import BeautifulSoup
import re

app = FastAPI(title="Page Pulse API")

# Serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in ["http", "https"] and parsed.netloc)



def extract_top_keywords(text: str, top_n: int = 5):
    # Standard NLP stop words
    stop_words = {
        "the", "and", "is", "in", "it", "to", "of", "for", "on", "with", 
        "a", "an", "this", "that", "you", "we", "are", "by", "as", "be", 
        "or", "your", "not", "can", "from", "at", "all", "has", "have"
    }
    
    # Tokenization: Extract words containing only alphabets (min 3 letters)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Stop-word removal
    meaningful_words = [word for word in words if word not in stop_words]
    
    # Frequency distribution
    keyword_freq = Counter(meaningful_words).most_common(top_n)
    
    # Return as a simple dictionary
    return {word: count for word, count in keyword_freq}

def parse_html_content(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"(?i)^description$")})
    meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else "N/A"

    h1_count = len(soup.find_all("h1"))
    images = soup.find_all("img")
    missing_alt_count = sum(1 for img in images if not img.get("alt"))

    # Extract visible text for our NLP pipeline
    text = soup.get_text(separator=" ", strip=True)
    word_count = len(text.split())
    
    # 🌟 NEW: Run the text through our NLP keyword extractor
    top_keywords = extract_top_keywords(text)

    return {
        "title": title,
        "meta_description": meta_description,
        "h1_count": h1_count,
        "missing_alt_images_count": missing_alt_count,
        "word_count": word_count,
        "top_keywords": top_keywords,  # Add this to the payload
    }


@app.get("/api/audit")
async def audit_url(url: str = Query(..., description="Target URL to audit")):
    if not url.startswith(("http://", "https://")):
        url="http://" + url  # Default to http if scheme is missing

    if not is_valid_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format. Please include http:// or https://",
        )

    start_time = time.time()

    headers = {
        "User-Agent": "Mozilla/5.0 (PagePulse Audit Tool; +https://digitalheroesco.com)"
    }

    try:
        async with httpx2.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response_time_ms = round((time.time() - start_time) * 1000, 2)

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Target URL returned non-HTML response type: {content_type}",
                )

            parsed_data = parse_html_content(response.text)

            return {
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "metrics": parsed_data,
            }

    except httpx2.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request timed out while trying to reach the target URL.",
        )
    except httpx2.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to the provided URL: {str(exc)}",
        )