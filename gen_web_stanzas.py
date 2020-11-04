from bs4 import BeautifulSoup
from main import get_stanzas
from datetime import datetime
from multiprocessing import Pool
import requests
import re
import os.path
import json

json_file = "complete_stanzas.json"
error_json_file = "errors.json"


def check_file():
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
            for d in data:
                try:
                    d['last_updated'] = datetime.fromisoformat(
                        data['last_updated'])
                except:
                    pass
            return data
    else:
        with open(json_file, "w") as f:
            data = {}
            json.dump(data, f, indent=4)
            return data


def check_error_file():
    if os.path.exists(error_json_file):
        with open(error_json_file, "r") as f:
            data = json.load(f)
            return data
    else:
        with open(error_json_file, "w") as f:
            data = {}
            json.dump(data, f, indent=4)
            return data


def get_not_updated(web_stanzas, stanza_data):
    not_updated_subset = []

    for stanza in web_stanzas:
        should_update = True
        link = web_stanzas[stanza][1]
        for key in stanza_data:
            if stanza_data[key]['link'] == link:
                #print("Not updated link: " + link)
                should_update = False
                break
        if should_update == True:
            print(stanza)
            not_updated_subset.append(web_stanzas[stanza])
    #print(not_updated_subset)
    return not_updated_subset


"""
    links = get_not_updated(stanza_data)[:2]
    # link = "https://help.oclc.org/Library_Management/EZproxy/Database_stanzas/ASTM_Compass"
    link = "https://help.oclc.org/Library_Management/EZproxy/Database_stanzas/Gale_InfoTrac"
    page_data = parsePage(link, stanza_data)
    with open(json_file, "w") as f:
        stanza_data.update(page_data)
        json.dump(stanza_data, f, indent=4)
"""


def gen_web_stanzas():
    web_stanzas = get_stanzas()

    stanza_data = check_file()
    error_data = check_error_file()

    links = get_not_updated(web_stanzas, stanza_data)
    # print(links)
    with Pool(10) as p:
        results = [p.apply_async(parsePage, args=(i[1],i[0])) for i in links]
        stanza_arr = [result.get() for result in results]
        for stanza in stanza_arr:
            if len(stanza['ERROR']) > 0:
                error_data[stanza['ERROR'][0]['link']] = stanza['ERROR']
                with open(error_json_file, "w") as f:
                    json.dump(error_data, f, indent=4)
            del stanza['ERROR']
            stanza_data.update(stanza)
        with open(json_file, "w") as f:
            json.dump(stanza_data, f, indent=4)

        # links = get_not_updated(all_links, stanza_data)[:5]

def parsePage(link, stanza_updated):
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
        if lines[len(lines)-1] != '':
            lines.append('')
        for line in lines:
            # If it's A title line, then read in the title and date and save it
            if line == "" and stanza_text != "":
                if title in total_stanzas:
                    print("IN TOTAL STAZAS: " + title)
                    total_stanzas[title]['stanza_text'] += stanza_text
                elif title != "":
                    print("WRITING STAZA " + title)
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
                #print(line)

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
    gen_web_stanzas()
