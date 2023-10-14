import requests
from bs4 import BeautifulSoup


propublica_base_url = "https://projects.propublica.org/nonprofits/organizations/"


def get_xml_url_from_ein(ein):
    """Returns most recent URL for 990 XML form

    Args:
        string (ein): company's UID

    Returns:
        string: most recent URL for 990 XML form
    """
    propublica_url = propublica_base_url + str(ein)
    page = requests.get(propublica_url)
    soup = BeautifulSoup(page.content, "html.parser")

    xml_buttons = soup.find_all(lambda x: x.name == "a" and x.text == "XML")

    if xml_buttons:
        urls = ["https://projects.propublica.org" +
                e.get("href") for e in xml_buttons]
    else:
        return -1

    return urls[0]
