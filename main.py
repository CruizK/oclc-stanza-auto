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

def load_config_stanzas():
    conf_file = "config.txt"

    with open(conf_file, "r") as f:
        lines = f.readlines()

    current_stanzas = []

    for line in lines:
        if re.match(r'^Title .+ \(updated .+\)$', line):
            title = re.search(r'Title (.+) \(', line).group(1).strip()
            date = re.search(r'[0-9]{8}', line).group()
            try:
                last_updated = datetime.strptime(date, "%Y%m%d")
            except:
                print("Fix this date: " + title)

            if date and title:
                #print(title)
                current_stanzas.append((title, last_updated))
            else:
                print("This doesn't have title or date")

    return current_stanzas



def run():
    print("TEST")
    current_stanzas = load_config_stanzas()
    new_stanzas = get_stanzas()

    #for s in new_stanzas.keys():
        #print("WEB STANZA " + s + "-" + str(len(s)))

    ct = 0
    for stanza in current_stanzas:
        stanza_name = stanza[0]
        stanza_date = stanza[1]
        
        

        if stanza_name not in current_stanzas:
            ct += 1
            print("NAME NOT IN WEB TITLES: " + stanza_name)
      
    print(ct)



if __name__ == "__main__":
    run()