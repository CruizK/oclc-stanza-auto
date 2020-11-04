import re
import os.path
import json
from datetime import datetime

config_file = "config.txt"
stanza_file = "complete_stanzas.json"
outdated_txt = "outdated.txt"
not_found_txt = "notFound.txt"

def read_stazas():
    if os.path.exists(stanza_file):
        with open(stanza_file, "r") as f:
            data = json.load(f)
            for key in data:
                try:
                    data[key]['last_updated'] = datetime.strptime(data[key]['last_updated'][:10], "%Y-%m-%d")
                except:
                    print("Could not parse date")
            return data
    else:
        print("No local stanza file at: " + stanza_file)


def get_outdated_stanzas():
    data = read_stazas()

    with open(config_file, "r") as f:
        lines = f.readlines()
    
    line_count = 0
    not_found = []
    outdated = []
    #print(lines)
    total = 0
    titles_found = 0
    for line in lines:
        if re.match(r'^(Title|T) (.+)$', line, flags=re.I):
            last_updated = ""
            title = ""
            #Title ((?:(?! \(updated).)*) \((?:updated)?\s?(\d{8})\)
            #Title EIVillage (updated 20150603)
            search = re.search(r'^(?:Title|T) ((?:(?! \(updated).)*) \(updated (\d+)\)', line, flags=re.I)

            if search == None:
                search = re.search(r'^(?:Title|T) (.+)$', line, flags=re.I)
            else:
                try:
                    last_updated = datetime.strptime(search.group(2), "%Y%m%d")
                except:
                    print("Could not parse date on line: " + str(line_count))
                    last_updated = ""
            
            title = search.group(1).strip()


            if search == None:
                print("Could not find title on line: " + str(line_count))
            else:      
                if title in data:
                    found = data[title]
                    if last_updated == "":
                        txt = "Update title: " + title + " | Old Date: No Data | New Date " + str(found['last_updated'])
                        outdated.append(txt)
                    elif last_updated < found['last_updated']:
                        txt = "Update title: " + title + " | Old Date: " + str(last_updated) + " | New Date " + str(found['last_updated'])
                        outdated.append(txt)
                    titles_found += 1
                else:
                    print("Could not find date: " + title)
                    txt = "Could not find title on line: " + line.replace('\n', '').replace('\r', '') + " : " + str(line_count)
                    not_found.append(txt)
            total += 1
        line_count += 1
    print("Total: " + str(total) + " | Found out of total: " + str(titles_found))
    with open(not_found_txt, "w") as f:
        f.write("\n".join(not_found))
    with open(outdated_txt, "w") as f:
        f.write("\n".join(outdated))



if __name__ == "__main__":
    get_outdated_stanzas()