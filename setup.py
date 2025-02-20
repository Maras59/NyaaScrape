import csv
from time import sleep
import yaml
import subprocess
import os
from pathlib import Path

CONFIG_PATH = 'configs/config.yaml'
print('Welcome to NyaaScrape')
print('Running setup script...')
sleep(1)

host = None
username = None
password = None
download_path = None

if not os.path.exists(CONFIG_PATH):
    print('Config file does not exist, creating...')
    print('These configs can be changed later in configs/config.yaml')
    Path(CONFIG_PATH).touch()
    sleep(1)

    host = input('qBittorrent host URL [http://localhost:8080]: ')
    host = 'http://localhost:8080' if host is None else host
    while download_path is None:
        download_path = input('Enter torrent download path (for a plex server this is would be the /TV/ directory path, include the trailing slash): ')
    while username is None:
        username = input('qBittorrent Web UI username: ')
    while password is None:
        password = input('qBittorrent Web UI password: ')
    
    print('\nThe following data will be used:')
    print(f'qBit Host: {host}')
    print(f'Download path: {download_path}')
    print(f'Username: {username}')
    print(f'Password: {password}')

    print('\nThis information can be changed directly in configs/config.yaml')
    print('\nProceeding with creation...')

    # Yes this is ugly but i want comments in my yaml file and this has to run without any external libraries
    with open(CONFIG_PATH, "w") as yaml_file:
        yaml_file.write("# qBittorrent host address\n")
        yaml.dump({"qBit_HOST": host}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# Base URL for torrent searches\n")
        yaml.dump({"BASE_URL": "https://nyaa.si/?"}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# Path to the CSV file containing show data\n")
        yaml.dump({"SHOW_CSV_PATH": "showdata/shows.csv"}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# Base file path for downloads\n")
        yaml.dump({"BASE_FILE_PATH": download_path}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# qBittorrent web UI credentials\n")
        yaml.dump({"credentials": {"username": username, "password": password}}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# Default maximum filesize for torrents\n")
        yaml.dump({"FULL_BATCH_THRESHOLD": 1.5}, yaml_file, default_flow_style=False, sort_keys=False)
        yaml_file.write("\n# DO NOT TOUCH - Required class name for parsing torrent table\n")
        yaml.dump({"TABLE_CLASS": "table table-bordered table-hover table-striped torrent-list"}, yaml_file, default_flow_style=False, sort_keys=False)
    sleep(1)

else:
    print(f'Config file already exists at {CONFIG_PATH}!')

csv_header = ["Show Title", "Subgroup", "Last Episode Download Date", "Max Size", "Directory", "Bonus Str"]
with open("showdata/shows.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_header)

print('Running setup scripts...')

# Add to cron
rc = subprocess.call("./.setup.sh")
cwd = os.getcwd()
cron_job = f'0 */12 * * * /bin/bash {cwd}/run_script.sh >> {cwd}/cron.log 2>&1'
os.system(f'(crontab -l; echo "{cron_job}") | crontab -')

print('Setup complete!')
