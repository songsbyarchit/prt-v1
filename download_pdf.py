import os
import pdfkit
from bs4 import BeautifulSoup

# File paths
html_file_path = "empa.html"  # Path to your local HTML file
output_dir = "webpage_pdfs"  # Directory to save PDFs
os.makedirs(output_dir, exist_ok=True)

def get_links_from_html(file_path):
    """Extract links to forum posts from a local HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    # Extract all links
    links = [a['href'] for a in soup.find_all('a', href=True)]
    # Filter forum links only (modify based on specific forum URL structure)
    links = [link for link in links if "/t/" in link]
    # Remove duplicates and return absolute URLs
    links = list(set(links))  # Remove duplicates
    links = [link if link.startswith("http") else f"https://community.endmyopia.org{link}" for link in links]
    return links

def save_as_pdf(url, output_path):
    """Convert a webpage to a PDF."""
    try:
        pdfkit.from_url(url, output_path)
        print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Failed to save {url}: {e}")

def main():
    # Extract links from the local HTML file
    links = get_links_from_html(html_file_path)
    for i, link in enumerate(links):
        output_path = os.path.join(output_dir, f"forum_post_{i+1}.pdf")
        save_as_pdf(link, output_path)

if __name__ == "__main__":
    main()