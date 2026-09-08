### Custom RSS full-text scraper for the feeds I like.

from bs4 import BeautifulSoup # dont need javascript rendering
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import random
import requests
import sys
import time
import xml.etree.ElementTree as ET


# Setup cache
cache_dir = Path("cache/")
try:
    cache_dir.mkdir(exist_ok=False)
    print("Created cache dir")
except FileExistsError as e:
    print("Found cache dir")

# Download the feed so it's up to date
rss_url = "https://edmonton.taproot.news/pulse/feed"
filename = "taprootpulse.xml"
filename_out = "taprootpulse-full.xml"
print("Downloading feed "+rss_url)
response = requests.get(rss_url)
print(response.status_code)
with open(filename, "w", encoding="utf-8") as file:
    file.write(response.text)

# Parse the feed for each item...
print("Filling text...")
tree = ET.parse(filename)
root = tree.getroot()
channel = root.find("channel")
for item in channel.findall("item"): #[:2]:
    # Fill this entry with the article's full text content
    item_link = item.findtext("link")

    print(item.findtext("title")+'... ', end='')

    # Check the cache to see if we already downloaded this text
    url_sanitized = item_link.replace('/', '-').replace(':', '-')
    cache_file = cache_dir / url_sanitized
    content = ''
    if cache_file.is_file():
        with open(cache_file, 'r') as file:
            content = file.read()
            print("got from cache")
    else:
        # Get the linked article and extract the full text
        response = requests.get(item_link)
        time.sleep(random.randint(1, 4)) # respect the servers
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        content = str(soup.select_one(".article-body-width"))
        # Update the cache
        with open(cache_file, 'w') as file:
            file.write(content)

    # Put the full text back into the feed XML
    item.find("description").text = content

# Write the full feed out to a new file.
# xml_declaration preserves the <?xml version="1.0" ?> header line
tree.write(filename_out, encoding="utf-8", xml_declaration=True)

print("Written to "+filename_out)

# Serve the feeds locally; the feeds-to-instapaper app won't know the difference
httpd = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
print(f"Serving feeds at http://localhost:8000")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    httpd.server_close()
