from bs4 import BeautifulSoup
import requests
import re
from main import get_stanzas


def gen_web_stanzas():
    web_stanzas = get_stanzas()
    subset_keys = list(web_stanzas.keys())[:5]
    
    for key in subset_keys:
        link = web_stanzas[key][1]
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        pre_tags = soup.find_all('pre')
        for tag in pre_tags:
            lines = tag.text.split('\n')
            for line in lines:
                if re.match(r'^Title (.+)$', line):
                    title = re.search(r'Title (.+)[\(]?', line)
                    print(line)
                    date = re.search(r'[0-9]{8}', line).group()
                    print("Title: " + title + "-" + date)


if __name__ == "__main__":
    gen_web_stanzas()
