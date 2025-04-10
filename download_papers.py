import requests
import feedparser
import time
import os

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser


# Query for CS papers from 2024
BASE_URL = "http://export.arxiv.org/api/query?"
QUERY = "search_query=cat:cs.*+AND+submittedDate:[202401010000+TO+202412312359]"


def download_arxiv_pdf(limit=1000, output_dir="arxiv_pdf"):

    """
    Downloads arXiv papers as pdfs

    Args:
        limit: Maximum amount of papers to download

    """

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


def download_arxiv_md(limit=1000, output_dir="arxiv_md"):

    """
    Downloads arXiv papers in pdf temporarily and converts to markdown

    Args:
        limit: Maximum amount of papers to download

    """

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("markdown_temp", exist_ok=True)

    start = 0
    max_results = min(100, limit)

    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )

    while start < limit:
        url = f"{BASE_URL}{QUERY}&start={start}&max_results={max_results}"
        response = requests.get(url)
        feed = feedparser.parse(response.text)

        if not feed.entries:
            break

        for entry in feed.entries:
            pdf_url = entry.id.replace('abs', 'pdf')
            paper_id = entry.id.split('/')[-1]
            pdf_filepath = f"markdown_temp/{paper_id}.pdf"
            md_filepath = f"{output_dir}/{paper_id}.md"
            print(f"Downloading {pdf_url}")
            
            try:
                if not os.path.exists(pdf_filepath):
                    print(f"Downloading {pdf_filepath}")
                    pdf = requests.get(pdf_url + ".pdf")
                    with open(pdf_filepath, 'wb') as p:
                        p.write(pdf.content)

                    with open(md_filepath, 'w', encoding="utf-8") as m:
                        print(f"Converting {pdf_filepath} to {md_filepath}")
                        rendered = converter(pdf_filepath)
                        text, _, _ = text_from_rendered(rendered)
                        m.write(text)

                    os.remove(pdf_filepath) 
            except:
                os.remove(pdf_filepath) 
                continue


        start += max_results
        time.sleep(3)

    try:
        os.rmdir("markdown_temp")
    except OSError:
        raise OSError("Failed to delete temporary files after execution")

# TODO: Command line arguments
if __name__ == "__main__":
    # download_arxiv_pdf(100)
    download_arxiv_md(10)
    pass
