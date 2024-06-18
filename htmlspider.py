import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse, unquote
import hashlib

# Set the base URL and headers
base_url = 'http://siduanquan.com'  # Replace with the actual base URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Create a session
session = requests.Session()
session.headers.update(headers)

def get_html(url):
    """Fetch the HTML content of a given URL"""
    try:
        response = session.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Ensure correct encoding
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_html(content, filepath, url):
    """Save HTML content to a file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"<!-- Original URL: {url} -->\n")
        file.write(content)

def find_links(html, current_url):
    """Find all the links on a given HTML page"""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Resolve relative URLs
        full_url = urljoin(current_url, href)
        # Ensure the link is within the same domain
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links

def generate_filename(url):
    """Generate a valid filename from the URL"""
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path.strip('/'))
    if not path:
        path = 'index'
    else:
        path = path.replace('/', '_')
    # Limit filename length to avoid errors
    if len(path) > 150:
        path = path[:150]
    # Append a hash to ensure uniqueness
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    filename = f"{path}_{url_hash}.html"
    return os.path.join('downloaded_pages', filename)

def main():
    visited = set()
    to_visit = {base_url}
    
    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        
        print(f"Visiting: {current_url}")
        html = get_html(current_url)
        if html:
            filepath = generate_filename(current_url)
            save_html(html, filepath, current_url)
            visited.add(current_url)
            
            new_links = find_links(html, current_url)
            to_visit.update(new_links - visited)
        
        time.sleep(1)  # Be polite and avoid bombarding the server

if __name__ == '__main__':
    main()
