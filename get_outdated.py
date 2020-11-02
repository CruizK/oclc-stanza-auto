import re

config_file = "config.txt"


def get_outdated_stanzas():
    with open(config_file, "r") as f:
        lines = f.readlines()
    
    line_count = 0
    #print(lines)
    for line in lines:
        if re.match(r'^(Title|T) (.+)$', line, flags=re.I):
            search = re.search(r'^(?:Title|T) ((?:(?! \(updated).)*) \(updated (\d{8})\)', line, flags=re.I)

            if search is None:
                search = re.search(r'^(?:Title|T) (.+)$', line, flags=re.I)
            
            if search is None:
                print("Could not find title: " + line)
            else:
                print(search.group(1).strip())

        line_count += 1




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