from bs4 import BeautifulSoup
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from config import proxies
import json
from datetime import datetime


def get_article_author(url):

    try:

        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            script_tag = soup.find('script',type="application/ld+json")

            if script_tag:
                data = json.loads(script_tag.string)
                return_data = {
                    'datePublished': None,
                    'author' : None  
                }
                return_data['datePublished'] = data["datePublished"]
                
                if "author" in data.keys():
                    if isinstance(data['author'], list):
                        return_data['author'] = '\n'.join([author["name"] for author in data["author"]])
                    else:
                        return_data['author'] = data['author']['name']


                    return_data['author'] = return_data['author'].replace('&', '\n').replace(' and ', '\n')

                return return_data
                   
        
        else:
            print(f"Request status code {url} : {response.status_code}")
            print(f"Response text {url} : {response.text}")
    except requests.exceptions.HTTPError as http_exp:
        print(f"HTTP exception {url} : {http_exp}")

    except requests.exceptions.RequestException as req_exp:
        print(f"{url} : {req_exp}")



def parse_html(text_html):
    
    
    soup = BeautifulSoup(text_html, 'html.parser')


    elements = soup.find_all('div', attrs={'data-testid':'anchor-inner-wrapper'})

    

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_dict = {}

        for element in elements:
            a_tag = element.find('a', {'data-testid': 'external-anchor'})
            href = None
            if a_tag is not None:
                href = a_tag.get('href')
            else:
                a_tag = element.find('a', {'data-testid': 'internal-link'})
                if a_tag is not None:
                    href = f"https://www.bbc.com{a_tag.get('href')}"
            
            if href is not None and 'articles' in href:    

                h2_tag = element.find('h2', attrs={'data-testid':'card-headline'})
                if h2_tag is not None:
                    future = executor.submit(get_article_author, href)
                    future_dict[future] = (href, h2_tag.get_text(strip=True))
                    
        results = []
        for future in as_completed(future_dict):
            result = future.result()
            href, title = future_dict[future]


            results.append({'url' : href,
                            'title': title,
                            'author': result['author'] if result else None,
                            'datePublished': result['datePublished'] if result else None})

    if results and len(results) > 0:

        filename = f"news/news_bbc_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)

        
        print(f"Save in {filename}")
    else:
        print('Nothing save')


def get_main_page():

    url = "https://www.bbc.com/news"

    try:
        response = requests.get(url, proxies=proxies, timeout=10)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Request status code {response.status_code}")
            print(f"Response text: {response.text}")
    except requests.exceptions.HTTPError as http_exp:
        print(f"HTTP exception: {http_exp}")
    except requests.exceptions.RequestException as req_exp:
        print(f"Other type exception: {req_exp}")





if __name__ == '__main__':
    if not os.path.isdir('news'):
        os.makedirs('news')
    

    html_text = get_main_page()
    if html_text is not None:
        parse_html(html_text)

    

