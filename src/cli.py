import cmd
import csv
import yaml
import re
from datetime import datetime
from time import sleep

CONFIG_PATH = '../configs/config.yaml'

with open(CONFIG_PATH) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        exit(exc)

class MainCLI(cmd.Cmd):
    prompt = '>> '
    intro = 'Welcome to NyaaScrape. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True
    
    def do_addtorrent(self, line):
        """
        Adds new torrent to daily torrent harvest. All data is scraped from nyaa.si. 
        Will prompt for the following information:
        Title [Required]:               Torrent title, does not need to be the full torrent title, the title of the show is usually all that is needed
        Subgroup [Required]:            Subtitle group, usually contained within square brackets at the beginning of the torrent title
        Date [Optional]:                Only download episodes after a certain date. Useful for only obtaining later seasons
        Max File Size(GiB) [Optional]:  Maximum allowed file size. Useful for avoiding batch downloads
        Directory [Required]:           Folder to store show files in, base path is in config.yaml
        Keywords [Optional]:            Additional keywords, useful for when subgroups upload multiple versions of the same episode
        """

        title = ""
        while not title.strip():
            title = input("Title (required): ").strip()
        subgroup = ""
        while not subgroup.strip():
            subgroup = input("Subgroup (required): ").strip()
        date = ""
        while not date or not re.match(r"\d{4}-\d{2}-\d{2}", date):
            date = input("Enter the date (YYYY-MM-DD): ").strip()
            if not re.match(r"\d{4}-\d{2}-\d{2}", date):
                print("Invalid date format. Please enter the date in YYYY-MM-DD format")
        date = datetime.strptime(date, "%Y-%m-%d")
        
        maxfilesize = None
        maxfilesize = input(f"Enter max file size [{conf['FULL_BATCH_THRESHOLD']}]: ").strip()
        if maxfilesize:
            try:
                maxfilesize = float(maxfilesize)
            except ValueError:
                print(f"Max file size must be a valid number, defaulting to {conf['FULL_BATCH_THRESHOLD']}")
        else:
            maxfilesize = conf['FULL_BATCH_THRESHOLD']
        
        directory = ""
        while not directory.strip():
            directory = input("Directory (required, NO LEADING SLASH): ").strip()
        directory = conf['BASE_FILE_PATH'] + directory

        bonus = input("Bonus (optional): ").strip()

        print(f"\nVerify the following information:")
        print(f"Title: {title}")
        print(f"Subgroup: {subgroup}")
        print(f"Date: {date}")
        print(f"Max File Size: {maxfilesize} GiB")
        print(f"Directory: {directory}")
        print(f"Bonus Keywords: {bonus}")

        # Ask for confirmation (Y/n)
        confirm = input("\nDo you want to proceed? (Y/n): ").strip().lower()

        if confirm in ['y', 'yes']:
            print('Proceeding...')
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M') if not date else date.strftime('%Y-%m-%d %H:%M')
            maxfilesize = str(maxfilesize)

            row = [
                title,
                subgroup if subgroup else 'None',
                date_str,
                maxfilesize,
                directory,
                bonus
            ]

            try:
                with open(conf['SHOW_CSV_PATH'], mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)
                print(f"Succsefully updated show data.")
            except Exception as e:
                print(f"Failed to write show data: {e}")

            return False
        else:
            print("Entry not added.")
            sleep(1)
            return False

if __name__ == '__main__':
    MainCLI().cmdloop()