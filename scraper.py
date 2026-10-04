import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

PRICE_PATTERN = re.compile(r"[\$€£¥MAD]?\s*\d[\d\s,.']*(?:\.\d{1,2})?")


def _meta(soup, *names):
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find(
            "meta", attrs={"name": name}
        )
        if tag and tag.get("content", "").strip():
            return tag["content"].strip()
    return ""


def _find_price(soup):
    for selector in [
        "[itemprop='price']",
        ".price",
        ".product-price",
        "#price",
        "[class*='price']",
        "[id*='price']",
    ]:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(" ", strip=True)
            m = PRICE_PATTERN.search(text)
            if m:
                return m.group().strip()
    return ""


def scrape_url(url: str) -> list[dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # --- Try Schema.org Product markup first ---
    products = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(tag.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") in ("Product", "product"):
                    name = item.get("name", "")
                    image = item.get("image", "")
                    if isinstance(image, list):
                        image = image[0]
                    offers = item.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0]
                    price = str(offers.get("price", "")) + " " + offers.get("priceCurrency", "")
                    sku = item.get("sku", "")
                    desc = item.get("description", "")
                    products.append({
                        "name": name,
                        "price": price.strip(),
                        "image": image,
                        "sku": sku,
                        "description": desc,
                        "url": url,
                    })
        except Exception:
            continue

    if products:
        return products

    # --- Fallback: Open Graph + page-level extraction ---
    name = (
        _meta(soup, "og:title")
        or (soup.find("h1") and soup.find("h1").get_text(strip=True))
        or soup.title.string.strip() if soup.title else ""
    )
    image = _meta(soup, "og:image")
    price = _meta(soup, "product:price:amount", "og:price:amount") or _find_price(soup)
    currency = _meta(soup, "product:price:currency", "og:price:currency")
    desc = _meta(soup, "og:description", "description")

    if price and currency:
        price = f"{price} {currency}"

    return [{
        "name": name,
        "price": price,
        "image": image,
        "sku": "",
        "description": desc,
        "url": url,
    }]
