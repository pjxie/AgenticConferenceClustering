import requests
import feedparser
import time
import os

base_url = "http://export.arxiv.org/api/query?"
query = "search_query=cat:cs.*+AND+submittedDate:[202401010000+TO+202412312359]"
max_results = 1000
start = 0

os.makedirs("arxiv_2024_cs", exist_ok=True)

while True:
    url = f"{base_url}{query}&start={start}&max_results={max_results}"
    response = requests.get(url)
    feed = feedparser.parse(response.text)

    if not feed.entries:
        break

    for entry in feed.entries:
        pdf_url = entry.id.replace('abs', 'pdf')
        paper_id = entry.id.split('/')[-1]
        filename = f"arxiv_2024_cs/{paper_id}.pdf"
        if not os.path.exists(filename):
            print(f"Downloading {filename}")
            pdf = requests.get(pdf_url + ".pdf")
            with open(filename, 'wb') as f:
                f.write(pdf.content)
            time.sleep(1)

    start += max_results
    time.sleep(3)


