from bs4 import BeautifulSoup
from main import get_stanzas
from datetime import datetime
from multiprocessing import Pool
import requests
import re
import os.path
import json

json_file = "complete_stanzas.json"


def check_file():
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
            for d in data:
                try:
                    d['last_updated'] = datetime.fromisoformat(data['last_updated'])
                except:
                    pass
            return data
    else:
        with open(json_file, "w") as f:
            data = {}
            json.dump(data, f, indent=4)
            return data

def get_not_updated(stanza_data):
    not_updated_subset = []
    for key in stanza_data:
        if 'last_updated' not in stanza_data[key]:
            not_updated_subset.append(key)
    return not_updated_subset



def gen_web_stanzas():
    web_stanzas = get_stanzas()
    all_links = [web_stanzas[key][1] for key in web_stanzas]
    stanza_data = check_file()

    links = get_not_updated(stanza_data)[:2]
    #link = "https://help.oclc.org/Library_Management/EZproxy/Database_stanzas/ASTM_Compass"
    link = "https://help.oclc.org/Library_Management/EZproxy/Database_stanzas/Gale_InfoTrac"
    page_data = parsePage(link, stanza_data)
    with open(json_file, "w") as f:
        stanza_data.update(page_data)
        json.dump(stanza_data, f, indent=4)
    """
    with Pool(2) as p:
        while(len(links) > 0):
            results = [p.apply_async(parsePage, args=(i,)) for i in links]
            arr = [result.get() for result in results]
            for i in arr:
                if i['link'] in stanza_data:
                    stanza_data[i['link']].update(i)
            
            with open(json_file, "w") as f:
                json.dump(stanza_data, f, indent=4)

            links = get_not_updated(stanza_data)[:2]
"""

def parsePage(link, stanza_data):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    pre_tags = soup.find_all('pre')
    
    total_stanzas = {}

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
                    total_stanzas[title] = {
                        'title': title,
                        'last_updated': str(last_updated),
                        'stanza_text': stanza_text
                    }
                else:
                    print("Stanza without title")
                stanza_text = ""
                continue
            if re.match(r'^Title (.+)$', line):
                print(line)

                # NOTE: Certain updates seem to be structured as Title blahblah (OCLC Include File updated xxxxxxxx)
                search = re.search(r'^Title ((?:(?! \(updated).)*) \(updated (\d{8})\)', line)  # Wow so beautiful

                if search == None: # Make the assumption that it has no (updated) format ex: Title 123Library
                    search = re.search(r'^Title (.+)$', line)
                title = search.group(1).strip()

                last_updated = ""
                main_stanza_text = tag.text
                try:
                    last_updated = datetime.strptime(search.group(2), "%Y%m%d")
                except:
                    last_updated = "No Data"
            stanza_text += line + "\n"
    return total_stanzas
        


if __name__ == "__main__":
    gen_web_stanzas()
