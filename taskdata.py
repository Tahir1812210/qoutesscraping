import json
from typing import List
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from qoute import Qoute  # Importing the correct Qoute class


def main() -> None:
    url = "https://api.breakingbadquotes.xyz/v1/quotes/"
    quotes = fetch_quotes_and_author(url)
    save_items_to_json(quotes, "quotes_and_author.json")


def fetch_quotes_and_author(base_url: str) -> List[Qoute]:
    quotes_and_author: List[Qoute] = []

    while True:
        url = f"{base_url}"
        html = get_html(url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        item_boxes = soup.find_all(
            "div", class_="quote"
        )  # Assuming quotes are in a div with class "quote"
        if not item_boxes:
            break
        quotes_and_author.extend(
            [extract_quote_data(item_box) for item_box in item_boxes]
        )
    return quotes_and_author


def save_items_to_json(quotes: List[Qoute], filename: str) -> None:
    json_str = json.dumps([quote.__dict__ for quote in quotes], indent=4)
    with open(filename, "w") as f:
        f.write(json_str)


def extract_quote_data(quote_box) -> Qoute:
    # Assuming the structure is <span class="cm-property"> for both quote and author
    quote = quote_box.find_all("span", class_="cm-property")[
        0
    ].text.strip()  # First span is the quote
    author = quote_box.find_all("span", class_="cm-property")[
        1
    ].text.strip()  # Second span is the author
    return Qoute(quote, author)


def get_html(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


if __name__ == "__main__":
    main()
