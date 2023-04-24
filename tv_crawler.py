from io import TextIOWrapper
import re
from bs4 import BeautifulSoup
from urllib import parse
import requests
import json

class Site:
    def __init__(self:str, link:str, key_path:str, page:str, info:str):
        self.link = link
        self.key_path = key_path
        self.page = int(page)
        self.info = info

    def __str__(self):
        return 'Link: '+self.link+'\nKey path: '+self.key_path+'\nPage: '+self.page+'\nInfo: '+self.info+'\n'

# retrieves all links in a given link
def get_links(url:str, key_path:str)->list[str]:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return [parse.urljoin(url, link.get('href')) for link in soup.find_all('a', href=re.compile('.*'+key_path+'.*'))]

def get_content(url:str):
    data = {}
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    # title
    for div in soup.find_all('div', {'class':'mvic-desc'}):
        data['Title'] = div.find('h3').get_text(strip=True)
        data['Description'] = div.find('div', {'class':'desc'}).get_text(strip=True)
        for item in div.find('div', {'class':'mvic-info'}).find_all('p'):
            key, value = item.get_text(strip=True).split(':')
            key = key.strip()
            value = value.strip()
            data[key] = value
        data['Link'] = url
    return data
    # return [parse.urljoin(url, link.get('href')) )]

def crawl_n_scrape(site:Site, out_file:TextIOWrapper):
    for i in range(1):
        links = get_links(site.link+str(i+1), site.key_path)
        for link in links:
            # content = get_content(link)
            print(link, file=out_file)
            print("processing: ",link)
        
    

def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

# read file into list[Site]
def get_sites(filename)->list[Site]:
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    sites = []
    site = None
    for line in lines:
        if line.startswith('Link: '):
            link = line.split('Link: ')[1]
            site = Site(link, '', '0', '')
        elif line.startswith('Key path: '):
            site.key_path = line.split('Key path: ')[1]
        elif line.startswith('Page: '):
            site.page = line.split('Page: ')[1]
        elif line.startswith('Info: '):
            site.info = line.split('Info: ')[1]
            sites.append(site)
            print(site)

    return sites


if __name__ == '__main__':
    sites = get_sites("roots.txt")

    with open('links.txt', 'w') as fout:
        for site in sites:
            crawl_n_scrape(site, fout)

