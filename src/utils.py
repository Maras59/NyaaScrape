
import csv
import datetime

from bs4 import BeautifulSoup
import requests
from datetime import datetime
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import NewConnectionError
import logging
logger = logging.getLogger(__name__)

def getshowdata(query,subgroup=None,configs=None,keywords=None):
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
        tmp['magnet'] = links[3].attrs['href'] if 'magnet' in links[3].attrs['href'] else links[4].attrs['href']
        tmp['seeders'] = int(cols[5])

        # convert from string format to datetime format
        dtime = datetime.strptime(cols[4], "%Y-%m-%d %H:%M")
        tmp['date'] = dtime

        # Calculate filesize
        t = cols[3].split()
        size = float(t[0])
        convert = t[1] == 'MiB'
        tmp['size'] = size / 1024 if convert else size

        if subgroup and subgroup not in tmp['title'].lower():
            continue
        if keywords and keywords.lower() not in tmp['title'].lower():
            continue

        data.append(tmp)

    return data

def harvest_magnet_links(conf):
    with open(conf['SHOW_CSV_PATH'], 'r') as read_obj:
        r = csv.reader(read_obj)
        show_list = list(r)

    magnet_links = []
    for i, show in enumerate(show_list):
        if i == 0: continue

        latest_date = datetime.strptime(show[2], "%Y-%m-%d %H:%M")
        threshold = conf['FULL_BATCH_THRESHOLD'] if float(show[3]) < 0.0 else float(show[3])

        kw = show[5] if show[5] != 'None' else None
        torrent_list = getshowdata(show[0], show[1], configs=conf, keywords=kw)

        for torrent in torrent_list:
            if torrent['date'] > latest_date and torrent['size'] < threshold:
                if torrent['date'] > datetime.strptime(show_list[i][2], "%Y-%m-%d %H:%M"):
                    show_list[i][2] = torrent['date'].strftime("%Y-%m-%d %H:%M")
                magnet_links.append((torrent['magnet'], show[4], torrent['title']))
        
    with open(conf['SHOW_CSV_PATH'], 'w') as file:
        writer = csv.writer(file)
        writer.writerows(show_list)

    return magnet_links

def start_qBit(magnet_links, conf):
    # start qBit session
    auth = conf['credentials']
    headers = {'Referer': conf['qBit_HOST']}
    
    # Perform login request
    try:
        res = requests.post(f'{conf["qBit_HOST"]}/api/v2/auth/login', headers=headers, data=auth)
    except requests.exceptions.Timeout:
        logger.critical('Request to qBittorrent timed out on login')
        raise SystemExit('Request to qBittorrent timed out on login')
    except requests.exceptions.TooManyRedirects:
        logger.error('Too many redirects. Is qBit_HOST correct?')
        raise SystemExit('Too many redirects. Is qBit_HOST correct?')
    except ConnectionError as e:
        if isinstance(e.args[0], MaxRetryError):
            max_retry_error = e.args[0]
            if isinstance(max_retry_error.reason, NewConnectionError):
                logger.error('Failed to establish connection to qBittorrent. Is it running?')
                raise SystemExit('Failed to establish connection to qBittorrent. Is it running?')
            raise
        raise
    except requests.exceptions.RequestException as e:
        logger.error(e)
        raise SystemExit(f'CATASTROPHIC ERROR ON qBIT LOGIN: {e}')

    if res.status_code != 200:
        logger.error(f'Login to qBittorrent failed. Status code: {res.status_code}, Response: {res.text}')
        exit(f'Login to qBittorrent failed. Status code: {res.status_code}, Response: {res.text}')

    cookies = res.cookies
    if 'SID' not in cookies:
        logger.error('No session cookie found while logging into to qBittorrent!')
        exit('No session cookie found while logging into to qBittorrent!')
    headers['Cookie'] = f'SID={cookies['SID']}' # Attach session ID from cookies

    failed = []
    shows_processed = set()
    for magnet_link in magnet_links:
        payload = {
            'urls': magnet_link[0],
            'savepath': magnet_link[1]
        }
        res = requests.post(f'{conf["qBit_HOST"]}/api/v2/torrents/add', headers=headers, data=payload)
        if res.status_code != 200:
            failed.append(magnet_link[2])
        else:
            shows_processed.add(magnet_link[2])

    logger.info(f'Processed magnet links for the following shows: {list(shows_processed)}')
    if failed:
        logger.error(f'Failed to add the following torrents: {failed}')

    res_logout = requests.post(f'{conf["qBit_HOST"]}/api/v2/auth/logout', headers=headers)
    if res_logout.status_code != 200:
        logger.error(f'Failed to logout. Status code: {res_logout.status_code}, Response: {res_logout.text}')
    else:
        logger.info(f'Script run successfully! Processed {len(magnet_links)} magnet links')
        