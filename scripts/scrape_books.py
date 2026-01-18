import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/page-{}.html"

def safe_get(session, url, retries=3, timeout=15):
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(1.0 * attempt)

def scrape_all_books():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    books = []
    visited = set()

    for page in range(1, 51):  # 50 páginas (1000 livros)
        print(f"Scraping página {page}...")
        url = CATALOGUE_URL.format(page)

        try:
            resp = safe_get(session, url)
        except Exception:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".product_pod")
        if not items:
            break

        for item in items:
            rel = item.h3.a["href"]
            book_url = BASE_URL + "catalogue/" + rel.replace("../", "")

            if book_url in visited:
                continue
            visited.add(book_url)

            try:
                detail = safe_get(session, book_url)
            except Exception:
                continue

            dsoup = BeautifulSoup(detail.text, "html.parser")

            title = dsoup.find("h1").text.strip()

            price_text = dsoup.select_one(".price_color").text
            price = float(price_text.replace("£", "").replace("Â", ""))

            availability = dsoup.select_one(".availability").text.strip()
            rating = dsoup.find("p", class_="star-rating")["class"][1]

            breadcrumb = dsoup.select("ul.breadcrumb li a")
            category = breadcrumb[2].text.strip() if len(breadcrumb) > 2 else "Default"

            image_src = dsoup.select_one(".item img")["src"].replace("../", "")
            image_url = BASE_URL + image_src

            books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "category": category,
                "image_url": image_url
            })

            time.sleep(0.3)

    return pd.DataFrame(books)

if __name__ == "__main__":
    df = scrape_all_books()
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/books.csv", index=False)
    print(f"Scraping concluído! {len(df)} livros salvos em data/books.csv")
