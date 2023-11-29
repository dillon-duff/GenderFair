import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit

def search_website_for_keyword(url, keyword, visited_pages=set(), max_depth=3, current_depth=0):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            page_text = soup.get_text()

            if keyword.lower() in page_text.lower():
                print(f"Keyword '{keyword}' found on {url}")

            visited_pages.add(url)

            if current_depth < max_depth:
                links = soup.find_all('a', href=True)

                for link in links:
                    absolute_url = urljoin(url, link['href'])

                    if urlsplit(absolute_url).netloc == urlsplit(url).netloc:
                        if absolute_url not in visited_pages:
                            visited_pages.add(absolute_url)
                            search_website_for_keyword(absolute_url, keyword, visited_pages, max_depth, current_depth + 1)
        else:
            print(f"Failed to retrieve content from {url} (HTTP status code {response.status_code})")
    except Exception as e:
        print(f"An error occurred while searching {url}: {str(e)}")

if __name__ == "__main__":
    nonprofit_url = "https://www.stjude.org/"
    keyword_to_search = "parental leave"
    max_depth = 6

    search_website_for_keyword(nonprofit_url, keyword_to_search, max_depth=max_depth)

