from bs4 import BeautifulSoup
import requests
import re
from main import get_stanzas
from datetime import datetime
from multiprocessing import Pool
import os.path
import json 

json_file = "complete_stanzas.json"

def check_file():
  if os.path.exists(json_file):
    with open(json_file, "r") as f:
      data = json.load(f)
      #for d in data:
      #  data[d][0] = datetime.fromisoformat(data[d][0])
    return data
  else:
    return None

def cube(x):
  return x**3

def gen_web_stanzas():
    web_stanzas = get_stanzas()
    links = [web_stanzas[key][1] for key in web_stanzas] # lol
    subset_links = links[5:10]
    stanzas = check_file()
    with Pool(10) as p:
      results = [p.apply_async(parsePage, args=(i,)) for i in subset_links]
      arr = [result.get() for result in results]
      with open(json_file, 'w') as f:
        json.dump(arr, f, indent=4)
    """
    for key in subset_keys:
        link = web_stanzas[key][1]
        try:
          parsePage(link)
        except:
          print("Error getting site")
"""


def parsePage(link):
  page = requests.get(link)
  soup = BeautifulSoup(page.text, 'html.parser')
  pre_tags = soup.find_all('pre')
  for tag in pre_tags:
      lines = tag.text.split('\n')
      for line in lines:
          if re.match(r'^Title (.+)$', line):
              print(line)
              search = re.search(r'^Title ((?:(?! \(updated).)*) \(updated (\d{8})\)', line) # Wow so beautiful
              title = search.group(1).strip() 
              last_updated = datetime.strptime(search.group(2), "%Y%m%d")
              return {
                'title': title,
                'last_updated': str(last_updated),
                'stanza_text': tag.text
              }


if __name__ == "__main__":
    gen_web_stanzas()
