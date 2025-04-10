import requests
import feedparser
import time
import os
from arxiv2text import arxiv_to_md


# Query for CS papers from 2024
BASE_URL = "http://export.arxiv.org/api/query?"
QUERY = "search_query=cat:cs.*+AND+submittedDate:[202401010000+TO+202412312359]"

# TODO: Some papers have no PDF (https://arxiv.org/abs/2404.13672v1), but this will still download them
def download_arxiv_pdf(limit=1000):

    """
    Downloads arXiv papers as pdf

    Args:
        limit: Maximum amount of papers to download

    """

    output_dir = "arxiv_pdf"
    os.makedirs(output_dir, exist_ok=True)
    start = 0
    max_results = min(100, limit)

    while start < limit:
        url = f"{BASE_URL}{QUERY}&start={start}&max_results={max_results}"
        response = requests.get(url)
        feed = feedparser.parse(response.text)

        if not feed.entries:
            break

        for entry in feed.entries:
            pdf_url = entry.id.replace('abs', 'pdf')
            paper_id = entry.id.split('/')[-1]
            filename = f"{output_dir}/{paper_id}.pdf"
            if not os.path.exists(filename):
                print(f"Downloading {filename}")
                pdf = requests.get(pdf_url + ".pdf")
                with open(filename, 'wb') as f:
                    f.write(pdf.content)
                time.sleep(1)

        start += max_results
        time.sleep(3)

# TODO: https://github.com/VikParuchuri/marker might be better than arxiv2text for this
def download_arxiv_md(limit=1000):

    """
    Downloads arXiv papers in markdown

    Args:
        limit: Maximum amount of papers to download

    """

    output_dir = "arxiv_md"
    os.makedirs(output_dir, exist_ok=True)
    start = 0
    max_results = min(100, limit)

    while start < limit:
        url = f"{BASE_URL}{QUERY}&start={start}&max_results={max_results}"
        response = requests.get(url)
        feed = feedparser.parse(response.text)

        if not feed.entries:
            break

        for entry in feed.entries:
            pdf_url = entry.id.replace('abs', 'pdf')
            print(f"Downloading {pdf_url}")
            
            try:    # Exception will be thrown if there is not a valid pdf
                arxiv_to_md(pdf_url, output_dir)
            except:
                continue
            time.sleep(1)

        start += max_results
        time.sleep(3)


if __name__ == "__main__":
    # download_arxiv_pdf()
    # download_arxiv_md()
    pass
