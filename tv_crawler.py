from io import TextIOWrapper
import re
from bs4 import BeautifulSoup
from urllib import parse, request
import requests

# retrieves all links in a given link
def get_links(url:str)->list[str]:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return [parse.urljoin(url, link.get('href')) for link in soup.find_all('a', href=re.compile('.*film/.*'))]

def crawl_n_scrape(url:str, out_file:TextIOWrapper, max_content=100):
    visited = []
    links = get_links(url)
    for link in links:
        print(link, file=out_file)
        # max_content = max_content - 1
        # print(link)
        # print(link)
        
    

def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

# read file into list[str], each elem is a line
def get_roots(file_name: str) -> list[str]:
    with open(file_name, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines if line.strip()]
    # print(lines)
    return lines

if __name__ == '__main__':
    roots = get_roots("roots.txt")

    with open('links.txt', 'w') as fout:
        for link in roots:
            for i in range(10):
                crawl_n_scrape(link+str(i+1), fout)

