from bs4 import BeautifulSoup
import requests
import yaml

def getshowdata(query, subgroup=None, configs=None):
    """
    Sends a query to nyaa.si and parses the result into a list
    query: Search query for nyaa site
    subgroup: Subtitle group, usually within sqaure brackets
    """
    res = requests.get(f'{configs['BASE_URL']}q={query}&s=seeders')
    subgroup = subgroup.lower() if subgroup else None
    soup = BeautifulSoup(res.text, 'html.parser')
    
    data = []
    table = soup.find('table', attrs={'class':configs['TABLE_CLASS']})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        tmp = {}
        cols = row.find_all('td')
        links = row.find_all('a')
        cols = [ele.text.strip() for ele in cols]
        tmp['title'] = links[2].text if 'comments' in links[1].get('class', []) else links[1].text
        tmp['magnet'] = links[3]['href']
        tmp['seeders'] = int(cols[5])
        tmp['date'] = cols[4]

        # Calculate filesize
        t = cols[3].split()
        size = float(t[0])
        convert = t[1] == 'MiB'
        tmp['size'] = size / 1024 if convert else size

        if subgroup and subgroup not in tmp['title'].lower():
            continue
        data.append(tmp)

    return data

