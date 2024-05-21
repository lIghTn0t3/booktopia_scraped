import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import csv

file_path = r'input_list.csv'

df = pd.read_csv(file_path)

isbn13_list = df['ISBN13']

base_url = "https://www.booktopia.com.au/book/{}.html"


cookies = {
    'domainCustomerSessionGuid': '3F78A7C2-8815-0245-3BCE-C00ED3F0EAE1',
    '_pxvid': '10fe8e4c-16b9-11ef-b0e2-6d64f249e6fd',
    'gaUniqueIdentifier': '204691B8-5E9C-5BC5-D8D3-F9CF8C9F1A14',
    'JSESSIONID': 'SUuZb1eaBMMbg0zRRKCAyn7SL94hWrf8oaVzd-om.10.0.103.97',
    'AWSALB': 'DNtWU4yXoJghzlLBaBDH0EARxO6S6yeeovS9pTZGzs5MVTCuIHZgkSH7rjnyc9AUC/gS4uNSeb4JV005UZeXyD4OFQKuULTyVoR0/yu1DuYUCmN15wA0eIrFBYbg',
    'AWSALBCORS': 'DNtWU4yXoJghzlLBaBDH0EARxO6S6yeeovS9pTZGzs5MVTCuIHZgkSH7rjnyc9AUC/gS4uNSeb4JV005UZeXyD4OFQKuULTyVoR0/yu1DuYUCmN15wA0eIrFBYbg',
    'forterToken': '7ae72df3c65048c9b41241dd8a6906a8_1716222667845_74_UAL9_6',
    'pxcts': '05dd5b54-16c7-11ef-a739-0af61be59656',
    '_px3': '7d6bd235f45cb6742595987f9939e83162c908474ad169ffdcbec3e305e893cd:2650oHX2E7JAyIn5qKBfFcwxUWWIMdcGhUXaf8pMcwFAWqFQkvTnuqsGv27tP1OV8y9w/A631MP2+vjmov034A==:1000:q447aWJc3x+iMNkrU/dO/MeXf6iNqj/etXQ7QSTJ9pdXgmtS+dJhYLZuERaVBz91ntjlCM7hFY7etREUMFiHy2NscnlZsZKNYbIhaj+h52X/WmAbeJXjx9dZKaC7QmU3t+miW5+H/We3S78izVC2a3vmW/66H2EgcAAwljdY2NqCXyCZ7nxDb/JorNssk4jIY2PXewHfYtVWplVXJo0L0BoVoe9/ComKpmPO1jTtyp0=',
    '_pxde': '3c94b70c5f13ef58e722e5153eba2da99188fd2107b9734a0bceca7f99f27da7:eyJ0aW1lc3RhbXAiOjE3MTYyMjI5NjY0NjJ9',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.6',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.booktopia.com.au/',
    'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

# Function to send request and extract book details
def get_book_details(isbn):
    try:
        url = base_url.format(isbn)
        response = requests.get(url, cookies=cookies, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            json_data = json.loads(script_tag.string)
            for item in json_data:
                if '@type' in item and 'Book' in item['@type']:
                    title = item.get('name', 'N/A')
                    authors = ", ".join(author['name'] for author in item.get('author', []))
                    book_format = item.get('workExample', {}).get('bookFormat', 'N/A')
                    publisher = item.get('publisher', {}).get('name', 'N/A')
                    published_date = item.get('workExample', {}).get('datePublished', 'N/A')
                    isbn10 = item.get('workExample', {}).get('isbn', 'N/A')
                    original_price = item.get('offers', [{}])[0].get('price', 'N/A')
                    discounted_price = item.get('offers', [{}])[0].get('price', 'N/A')
                    num_pages = item.get('offers', [{}])[0].get('number_of_pages', 'N/A')
                    return {
                        'Title': title,
                        'Author': authors,
                        'Book Type': book_format,
                        'Publisher': publisher,
                        'Published Date': published_date,
                        'ISBN-10': isbn10,
                        'Original Price': original_price,
                        'Discounted Price': discounted_price,
                        'No. of Pages': num_pages,
                    }
    except Exception as e:
        print(f"Error fetching data for ISBN {isbn}: {e}")
        return {
            'Title': 'N/A',
            'Author': 'N/A',
            'Book Type': 'N/A',
            'Publisher': 'N/A',
            'Published Date': 'N/A',
            'ISBN-10': 'N/A',
            'Original Price': 'N/A',
            'Discounted Price': 'N/A',
            'No. of Pages': 'N/A',
        }

output_file = r'scraped_books.csv'


fieldnames = ['Title', 'Author', 'Book Type', 'Publisher', 'Published Date', 'ISBN-10', 'Original Price', 'Discounted Price', 'No. of Pages']


with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

# Iterate over each ISBN, send a request, and write book details to CSV
for isbn in isbn13_list:
    book_details = get_book_details(isbn)
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(book_details)
    print(f"ISBN: {isbn}, Book Details: {book_details}")
    time.sleep(3) 
