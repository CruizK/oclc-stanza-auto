import re
import os.path
import json
from datetime import datetime

config_file = "config.txt"
stanza_file = "complete_stanzas.json"

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
    #print(lines)
    total = 0
    titles_found = 0
    for line in lines:
        if re.match(r'^(Title|T) (.+)$', line, flags=re.I):
            last_updated = ""
            title = ""
            search = re.search(r'^(?:Title|T) ((?:(?! \(updated).)*) \(updated (\d{8})\)', line, flags=re.I)

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
                    titles_found += 1
                    print(str(found['last_updated']) +  "-"   + str(last_updated))
                else:
                    print("Could not find title: " + title)
            total += 1
        line_count += 1
    print("Total: " + str(total) + " | Found out of total: " + str(titles_found))




def parseStanza(stanza):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    pre_tags = soup.find_all('pre')
    
    total_stanzas = {
        'ERROR': []
    }

    stanza_text = ""
    last_updated = ""
    title = ""
    for tag in pre_tags:
        lines = tag.text.split('\n')[1:]
        if "IncludeFile" in tag.text:
            continue
        for line in lines:
            # If it's A title line, then read in the title and date and save it
            if line == "" and stanza_text != "":
                if title in total_stanzas:
                    total_stanzas[title]['stanza_text'] += stanza_text
                elif title != "":
                    # If last_updated was not found in the stanza text fallback to the web one we scraped
                    if last_updated == "":
                        last_updated = stanza_updated
                    total_stanzas[title] = {
                        'title': title,
                        'last_updated': str(last_updated),
                        'stanza_text': stanza_text,
                        'link': link
                    }
                else:
                    print("COULD NOT PARSE THE TITLE: LOGGING TO ERROR JSON")
                    total_stanzas['ERROR'].append({
                        'link': link, 
                        'stanza_text': stanza_text, 
                        'last_updated': str(last_updated),
                        'tag_text': tag.text,
                        'msg': "Could not parse a Title xxxxxx from this tag_text"
                    })
                stanza_text = ""
                last_updated = ""
                continue
            if re.match(r'^Title (.+)$', line, flags=re.I):
                print(line)

                # NOTE: Certain updates seem to be structured as Title blahblah (OCLC Include File updated xxxxxxxx)
                search = re.search(r'^Title ((?:(?! \(updated).)*) \(updated (\d{8})\)', line, flags=re.I)  # Wow so beautiful

                if search == None: # Make the assumption that it has no (updated) format ex: Title 123Library
                    search = re.search(r'^Title (.+)$', line, flags=re.I)
                title = search.group(1).strip()

                last_updated = ""
                main_stanza_text = tag.text
                try:
                    last_updated = datetime.strptime(search.group(2), "%Y%m%d")
                except:
                    last_updated = ""
            stanza_text += line + "\n"
    return total_stanzas
        


if __name__ == "__main__":
    get_outdated_stanzas()