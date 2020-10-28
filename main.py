import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import json 
import os.path

json_file = 'new_stanzas.json'

def check_file():
  
  if os.path.exists(json_file):
    with open(json_file, "r") as f:
      data = json.load(f)
      for d in data:
        data[d][0] = datetime.fromisoformat(data[d][0])
    return data
  else:
    return None


def get_stanzas():

  data = check_file()
  if data != None:
    return data

  URL = "https://help.oclc.org/Library_Management/EZproxy/Database_stanzas"

  page = requests.get(URL)

  soup = BeautifulSoup(page.text, 'html.parser')

  links = soup.find_all('a')


  stanza_nodes = []

  for link in links:
    href = link.get('href')
    if href != None:
      if URL in link.get('href'):
        stanza_nodes.append(link)


  stanzas = {}
  for node in stanza_nodes:
    date = re.search("(\d\d\d\d-\d\d-\d\d)", node.parent.text)
    if date:
      last_updated = datetime.strptime(date.group(), "%Y-%m-%d")
      # stanzas.append({
      #   'last_updated': last_updated,
      #   'name': node.text,
      #   'link': node.get('href')
      # })
      stanzas[node.text] = [
        last_updated.isoformat(), node.get('href')]

  with open(json_file, 'w') as f:
    json.dump(stanzas, f, indent=4)
  return stanzas
