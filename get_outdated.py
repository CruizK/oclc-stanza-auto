import re
import datetime
from main import get_stanzas

conf_file = "config.txt"

with open(conf_file, "r") as f:
    lines = f.readlines()

current_stanzas = []

for line in lines:
    if re.match(r'^Title .+ \(updated .+\)$', line):
        title = re.search(r'Title (.+) \(', line).group(1).strip()
        date = re.search(r'[0-9]{8}', line).group()
        try:
            last_updated = datetime.datetime.strptime(date, "%Y%m%d")
        except:
            print("Fix this date: " + title)

        if date and title:
            #print(title)
            current_stanzas.append((title, last_updated))
        else:
            print("This doesn't have title or date")


new_stanzas = get_stanzas()

for s in new_stanzas.keys():
    print("WEB STANZA " + s + "-" + str(len(s)))


for stanza in current_stanzas:
    stanza_name = stanza[0]
    stanza_date = stanza[1]
    
    found = False
    for key in new_stanzas.keys():
        if stanza_name in key or key in stanza_name:
            found = True
            break

    if found != True:    
        print("NOT ON WEBSITE: " + stanza_name + "-" + str(len(stanza_name)))
