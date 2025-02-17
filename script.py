from datetime import datetime
from noapi import getshowdata
import csv
import yaml

with open('config.yaml') as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        exit(exc)

with open('shows.csv', 'r') as read_obj:
    r = csv.reader(read_obj)
    show_list = list(r)[1:]

magnet_links = []
for show in show_list:
    latest_date = datetime.strptime(show[2], "%Y-%m-%d %H:%M")
    threshold = conf['FULL_BATCH_THRESHOLD'] if float(show[3]) < 0.0 else float(show[3])

    torrent_list = getshowdata(show[0], show[1], configs=conf)

    for torrent in torrent_list:
        if torrent['date'] > latest_date and torrent['size'] < threshold:
            show[2] = torrent['date'].strftime("%Y-%m-%d %H:%M")
            magnet_links.append(torrent['magnet'])
    
print(magnet_links)
