import os
import requests
from urllib.parse import urlparse
import os
import requests
from urllib.parse import urlparse
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

class URLHandler:
    def __init__(self, base_directory):
        self.base_directory = base_directory

    def validate_url(self, url):
        try:
            response = requests.head(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            return False
        return False

    def download_html(self, url):
        if not self.validate_url(url):
            return "Invalid URL"

        # Extract the domain from the URL
        domain = urlparse(url).netloc

        # Extract the path from the URL and create a directory structure
        url_path = urlsplit(url).path
        if url_path == "":
            url_path = "/"

        # Create the directory for the website data
        website_directory = os.path.join(self.base_directory, "websites", domain, url_path[1:])
        os.makedirs(website_directory, exist_ok=True)

        # Create a valid filename from the URL
        filename = "index.html" if url_path == "/" else os.path.basename(url_path) + ".html"

        # Download the HTML content and save it as a text file
        response = requests.get(url)
        if response.status_code == 200:
            # with open(os.path.join(website_directory, filename), "w", encoding="utf-8") as file:
            #     file.write(response.text)

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract and save text content
            text_content = soup.get_text()
            text_filename = "text.txt"
            with open(os.path.join(website_directory, text_filename), "w", encoding="utf-8") as text_file:
                text_file.write(text_content)

            return "HTML content and text extracted and saved successfully."

        return "Failed to download HTML content."
