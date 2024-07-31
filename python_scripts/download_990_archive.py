import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urlparse
import zipfile


def get_links():
    current_year = datetime.now().year
    years_back = 3
    start_year = current_year - years_back
    url = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    collapsible_items = soup.select(".collapsible-item-body")

    zip_links = []
    csv_links = []
    for item in collapsible_items:
        zip_links.extend([link["href"] for link in item.select("a[href$='.zip']")])
        csv_links.extend([link["href"] for link in item.select("a[href$='.csv']")])

    return (
        [link for link in zip_links if int(link.split("/")[-2]) >= start_year],
        [link for link in csv_links if int(link.split("/")[-2]) >= start_year],
    )


def save_files(zip_links, csv_links):
    years = set([link.split("/")[-2] for link in zip_links + csv_links])

    for year in years:
        os.makedirs(f"990_xml_archive/{year}", exist_ok=True)

    for link in csv_links:
        year = link.split("/")[-2]
        filename = os.path.basename(urlparse(link).path)
        csv_path = f"indexes/{filename}"

        if os.path.exists(csv_path):
            print(f"CSV file already exists, skipping: {csv_path}")
            continue

        response = requests.get(link)
        if response.status_code == 200:
            with open(csv_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded CSV: {filename}")
        else:
            print(f"Failed to download CSV: {filename}")

    for link in zip_links:
        year = link.split("/")[-2]
        filename = os.path.basename(urlparse(link).path)
        extract_dir = f"990_xml_archive/{year}/{filename[:-4]}"

        if os.path.exists(extract_dir):
            print(f"Directory already exists, skipping: {extract_dir}")
            continue

        zip_path = f"990_xml_archive/{year}/{filename}"

        response = requests.get(link)
        if response.status_code == 200:
            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            os.remove(zip_path)
            print(f"Downloaded and extracted: {filename}")
        else:
            print(f"Failed to download: {filename}")


if __name__ == "__main__":
    zip_links, csv_links = get_links()
    save_files(zip_links, csv_links)
