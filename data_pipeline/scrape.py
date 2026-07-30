import requests
from bs4 import BeautifulSoup
import csv
import os
import time

BASE_URL = "http://books.toscrape.com/"
CATEGORIES = ["Nonfiction", "Romance", "Sequential Art"]
OUTPUT_PATH = os.path.join("data_pipeline", "data", "raw", "books_raw.csv")


def get_category_links():
    # category URLs have a random numeric id in them (e.g. romance_8)
    # so easier to just grab them from the sidebar instead of hardcoding
    resp = requests.get(BASE_URL)
    resp.encoding = "utf-8"  # force correct decoding, site sometimes gets mis-detected as ISO-8859-1
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = {}
    for a in soup.select("div.side_categories ul li ul li a"):
        name = a.text.strip()
        if name in CATEGORIES:
            links[name] = BASE_URL + a["href"]

    return links


def scrape_category(name, url):
    books = []
    next_url = url

    while next_url:
        resp = requests.get(next_url)
        resp.encoding = "utf-8"  # same fix as above, applied per page
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for article in soup.select("article.product_pod"):
            title = article.h3.a["title"].strip()
            price = article.select_one("p.price_color").text.strip()

            # rating is stored as a css class like "star-rating Three"
            rating_class = article.select_one("p.star-rating")["class"]
            star_rating = [c for c in rating_class if c != "star-rating"][0]

            availability = article.select_one("p.instock.availability").text.strip()

            books.append({
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": name
            })

        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_url = next_url.rsplit("/", 1)[0] + "/" + next_btn["href"]
        else:
            next_url = None

        time.sleep(0.5)

    return books


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    category_links = get_category_links()
    print("Categories found:", category_links)

    all_books = []
    for name, url in category_links.items():
        books = scrape_category(name, url)
        print(f"{name}: {len(books)} books")
        all_books.extend(books)

    print("Total books:", len(all_books))

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "star_rating", "availability", "category"])
        writer.writeheader()
        writer.writerows(all_books)

    print("Saved to", OUTPUT_PATH)


if __name__ == "__main__":
    main()