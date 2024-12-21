# Importing additional libraries
import json  # To handle JSON operations
import os  # To handle file and directory paths
from typing import List
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


class Item:
    def __init__(
        self, title: str, price: float, image: str, discounted_price: float
    ) -> None:
        self.title = title
        self.price = price
        self.discounted_price = discounted_price
        self.image = image

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "discounted_price": self.discounted_price,
            "image": self.image,
        }


def main() -> None:
    # Base URLs for different categories
    categories = [
        {
            "name": "WWE T-Shirts",
            "first_page": "https://www.wrestlingstore.pk/products/wwe-t-shirts.phps",
            "other_pages": "https://www.wrestlingstore.pk/products/wwe-t-shirts/",
        },
        {
            "name": "AEW T-Shirts",
            "first_page": "https://www.wrestlingstore.pk/products/aew-t-shirts.phps",
            "other_pages": "https://www.wrestlingstore.pk/products/aew-t-shirts/",
        },
        {
            "name": "WWE Legends T-Shirts",
            "first_page": "https://www.wrestlingstore.pk/products/wwe-legends-t-shirt.phps",
            "other_pages": "https://www.wrestlingstore.pk/products/wwe-legends-t-shirt/",
        },
    ]

    all_items = []  # List to store all scraped items

    # Iterate through each category
    for category in categories:
        page_number = 1  # Start with the first page
        print(f"Scraping category: {category['name']}")

        while True:
            # Construct the appropriate URL based on the page number
            if page_number == 1:
                url = category["first_page"]
            else:
                url = f"{category['other_pages']}{page_number}"

            print(f"Scraping page {page_number}: {url}")
            html = get_html(url)

            # If the page fails to load, stop the scraping process
            if not html:
                print(f"Page {page_number} could not be loaded. Stopping scraping.")
                break

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            items = extract_items_from_html(soup)

            # If no items are found on the page, stop the scraping process
            if not items:
                print(f"No items found on page {page_number}. Stopping scraping.")
                break

            # Add the items from the current page to the master list
            all_items.extend(items)
            page_number += 1

    # Log the total number of items scraped
    print(f"Scraped a total of {len(all_items)} items across all categories.")

    # Save the scraped data to a JSON file
    save_to_json(all_items)

    save_to_sql_server(all_items)


def get_html(url: str) -> str:
    """Fetch HTML content from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


# def extract_items_from_html(soup: BeautifulSoup) -> List[Item]:
#     """Extract items from a BeautifulSoup object."""
#     item_boxes = soup.find_all(class_="item-box")
#     items = []

#     for item in item_boxes:
#         title = item.find("div", class_="item-txt-cnt").find_all("a")[0].text.strip()
#         price = parse_price(item.find("div", class_="item-price").get_text(strip=True))
#         discounted_price = (
#             parse_price(item.find("s").get_text(strip=True)) if item.find("s") else 0.0
#         )
#         image = item.find("img")["src"]

#         items.append(Item(title, price, image, discounted_price))

#     return items


def extract_items_from_html(soup: BeautifulSoup) -> List[Item]:
    item_boxes = soup.find_all(class_="item-box")
    items = []

    for item in item_boxes:
        title = item.find("div", class_="item-txt-cnt").find_all("a")[0].text.strip()

        price_element = item.find("div", class_="item-price")
        price = (
            parse_price(price_element.get_text(strip=True)) if price_element else 0.0
        )

        discounted_element = item.find("s")
        discounted_price = (
            parse_price(discounted_element.get_text(strip=True))
            if discounted_element
            else 0.0
        )

        image = item.find("img")["src"]
        items.append(Item(title, price, image, discounted_price))

    return items


def parse_price(price_str: str) -> float:
    """Parse a price string into a float."""
    price_str = price_str.replace("Rs.", "").replace(",", "").strip()
    try:
        return float(price_str)
    except ValueError:
        return 0.0


def save_to_json(items: List[Item]) -> None:
    """
    Save the list of items to a JSON file in the specified directory.
    """
    # Define the directory and filename
    directory = r"D:\FutureMission\Projects\WebScraping\scrapeddata"
    filename = os.path.join(directory, "scraped_data.json")

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Load existing data if the file exists
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Convert existing data to a dictionary for easier merging
    existing_items = {item["title"]: item for item in existing_data}

    # Add or update items in the existing data
    for item in items:
        existing_items[item.title] = item.to_dict()

    # Write the merged data to the JSON file
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(
            list(existing_items.values()), json_file, indent=4, ensure_ascii=False
        )

    print(f"Scraped data saved to {filename}")


def save_to_sql_server(items: List[Item]) -> None:
    """
    Save the list of items to a SQL Server database using Windows Authentication.
    """
    import pyodbc  # Ensure pyodbc is installed

    # Define your SQL Server connection details
    server = "TAHIR-PC"
    database = "DataScrap"

    # Create a connection string for Windows Authentication
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )

    try:
        # Establish a connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Clear existing data in the table
        cursor.execute("TRUNCATE TABLE ScrapedItems")
        conn.commit()
        print("Existing data in ScrapedItems table cleared.")

        # Prepare bulk insert query
        bulk_insert_query = """
            INSERT INTO ScrapedItems (Title, Price, DiscountedPrice, Image)
            VALUES (?, ?, ?, ?)
        """

        # Perform bulk insert
        data_to_insert = [
            (item.title, item.price, item.discounted_price, item.image)
            for item in items
        ]
        cursor.executemany(bulk_insert_query, data_to_insert)

        # Commit the transaction
        conn.commit()
        print("Scraped data successfully saved to SQL Server.")

    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
