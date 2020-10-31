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
            for d in data:
                try:
                    d['last_updated'] = datetime.fromisoformat(data['last_updated'])
                except:
                    pass
            return data
    else:
        with open(json_file, "w") as f:
            web_stanzas = get_stanzas()
            links = {web_stanzas[key][1]: {'web_title': key}
                     for key in web_stanzas}
            json.dump(links, f, indent=4)
            return links


def gen_web_stanzas():
    stanza_data = check_file()

    not_updated_subset = []
    for key in stanza_data:
        if 'last_updated' not in stanza_data[key]:
            not_updated_subset.append(key)

    
    with Pool(5) as p:
        results = [p.apply_async(parsePage, args=(i,)) for i in not_updated_subset[:5]]
        arr = [result.get() for result in results]
        for i in arr:
            if i['link'] in stanza_data:
                stanza_data[i['link']].update(i)
        
        with open(json_file, "w") as f:
            json.dump(stanza_data, f, indent=4)


def parsePage(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    pre_tags = soup.find_all('pre')
    
    main_stanza_text = ""
    other_text = []
    last_updated = ""
    title = ""

    for tag in pre_tags:
        lines = tag.text.split('\n')
        is_title_tag = False
        for line in lines:
            if re.match(r'^Title (.+)$', line):
                is_title_tag = True
                print(line)
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
        if is_title_tag == False:
            other_text.append(str(tag.text))

    return {
        'title': title,
        'last_updated': str(last_updated),
        'main_stanza_text': main_stanza_text,
        'other_text': other_text,
        'link': link
    }


if __name__ == "__main__":
    gen_web_stanzas()
