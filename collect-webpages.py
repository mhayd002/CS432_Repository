import sys
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

TIMEOUT = 5
MIN_SIZE = 1000

def is_html_large_enough(response):
    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type:
        return False

    return len(response.content) > MIN_SIZE


def extract_links(url):
    links = set()
    try:
        response = requests.get(url, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            parsed = urlparse(link)

            if parsed.scheme in ["http", "https"]:
                links.add(link)

    except requests.RequestException:
        pass

    return links

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 collect-webpages.py <seed_url> [target]")
        sys.exit(1)

    seed = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 500

    collected = set()
    frontier = [seed]

    while len(collected) < target and frontier:
        current = frontier.pop(0)

        try:
            response = requests.get(current, timeout=TIMEOUT, allow_redirects=True)

            final_url = response.url

            if final_url in collected:
                continue

            if is_html_large_enough(response):
                collected.add(final_url)
                print(final_url, flush=True)

                links = extract_links(final_url)
                frontier.extend(links - collected)

        except requests.RequestException:
            continue

        if not frontier and len(collected) < target:
            frontier = list(collected)
            random.shuffle(frontier)
            print(f"\nNeed to collect {target - len(collected)} more URIs...\n")

        time.sleep(0.5)

    print(f"\nCollected {len(collected)} unique URIs")

if __name__ == "__main__":
    main()
