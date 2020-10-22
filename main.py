import requests
import re
import datetime
from bs4 import BeautifulSoup

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


stanzas = []
for node in stanza_nodes:
  date = re.search("(\d\d\d\d-\d\d-\d\d)", node.parent.text)
  if date:
    last_updated = datetime.datetime.strptime(date.group(), "%Y-%m-%d")
    stanzas.append({
      'last_updated': last_updated,
      'name': node.text,
      'link': node.get('href')
    })

#print(stanzas)

test_stanza = stanzas[0]

req = requests.get(test_stanza['link'])
soup = BeautifulSoup(req.text, 'html.parser')

code = soup.find_all('pre')

print(code)

#print(links)