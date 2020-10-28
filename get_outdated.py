import re
import datetime
from main import get_stanzas

conf_file = "config.txt"

with open(conf_file, "r") as f:
    lines = f.readlines()

titles_n_dates= []

for line in lines:
    if re.match(r'^Title .+ \(updated .+\)$', line):
        title = re.search(r'Title (.*) \(', line).group(1)
        date = re.search(r'[0-9]{8}', line).group()
        try:
            last_updated = datetime.datetime.strptime(date, "%Y%m%d")
        except:
            print("Fix this date: " + title)
        
        if date and title:
            titles_n_dates.append((title, last_updated))

stanzas = get_stanzas()

for thing in titles_n_dates:
    this_date = thing[1]
    their_date = stanzas[thing[0]][0]

    if this_date < their_date:
        print("?")