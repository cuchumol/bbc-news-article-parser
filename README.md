This script automatically parses the BBC News main page and saves a list of articles (URL, title, author, publication date) into an Excel file.

- Fetches HTML from the BBC News main page
- Extracts article links and headlines
- Loads each article to retrieve author and publication date (via JSON-LD)
- Saves results as an Excel file (`.xlsx`) in the `news/` folder
- Uses multithreading for faster processing

## Installation
Clone the repository:
   
 git clone https://github.com/cuchumol/bbc-news-scraper.git
 cd bbc-news-scraper
 python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
 pip install -r requirements.txt

## Usaege

python bbc_scraper.py
