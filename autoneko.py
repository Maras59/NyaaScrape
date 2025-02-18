import argparse
import cmd
import csv
import yaml
import shlex
from datetime import datetime
from time import sleep

CONFIG_PATH = 'config_dev.yaml'

with open(CONFIG_PATH) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        exit(exc)

class MainCLI(cmd.Cmd):
    prompt = '>> '
    intro = 'Welcome to AutoNeko. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True
    
    def do_add(self, line):
        """
        Adds arguments to the argument parser for a torrent download management system.

Arguments:
-t or --title (required):       Type: str
                                Description: The title of the show. This should be the show title only and does not
                                             need to be the full torrent title, but MUST be present in the torrent title.
    
-s or --subgroup (optional):    Type: str
                                Description: The subgroup, usually within square brackets, responsible for uploading the torrent.
    
-d or --date (optional):        Type: str
                                Description: The date filter to only download episodes uploaded after a specific date.
                                The date must be in YYYY-MM-DD format and is useful for downloading episodes from the latest season.
    
-m or --maxfilesize (optional): Type: str
                                Description: Specifies the maximum file size (in GiB) for the download. 
                                This helps avoid accidental batch downloads of large files. The default can be set in the config.
    
-r or --directory (required):   Type: str
                                Description: The folder in which the torrent will be stored.

-b or --bonus (optional):       Type: str
                                Description: Bonus keywords related to the entry.
                                These help restrict duplicates (e.g., to filter out multiple resolutions of the same episode by adding a keyword like "1080p").
        """
        
        parser = argparse.ArgumentParser()
        
        parser.add_argument('-t', '--title', type=str, required=True, help='Show title, only needs to be show title, does not need to be full torrent title but MUST be present in torrent title')
        parser.add_argument('-s', '--subgroup', type=str, required=False, help='Subgroup, usually within square brackets')
        parser.add_argument('-d', '--date', type=str, required=False, help='Only download episodes uploaded after certain date, useful for only getting episodes for a a latest season, must be in YYYY-MM-DD format')
        parser.add_argument('-m', '--maxfilesize', type=str, required=False, help='Maximum file size (in GiB), useful for avoiding the accidental batch download')
        parser.add_argument('-r', '--directory', type=str, required=True, help='Folder in which torrent will be stored in')
        parser.add_argument('-b', '--bonus', type=str, help='Bonus keywords related to the entry, helps restrict duplicates (Ex. subgroup that uploads same episode in multiple resolutions, can add keyword \"1080p\" to filter out all other resolutions)')

        args = parser.parse_args(shlex.split(line))

        title = args.title.strip()
        subgroup = args.subgroup.strip()
        try:
            # Attempt to convert the string to a datetime object
            date = datetime.strptime(args.date.strip(), '%Y-%m-%d')
        except ValueError:
            # If the format is incorrect, raise an error
            print("Date must be in YYYY-MM-DD format")
            return False
        
        maxfilesize = None
        if args.maxfilesize:
            try:
                print('here1')
                maxfilesize = float(args.maxfilesize)
            except ValueError:
                print("Max file size must be a valid number.")
                return False
        else:
            maxfilesize = conf['FULL_BATCH_THRESHOLD']
        
        directory = conf['BASE_PLEX_PATH'] + args.directory.strip()

        bonus = args.bonus.strip() if args.bonus else 'None'


        print(f"\nVerify the following information:")
        print(f"Title: {args.title}")
        print(f"Subgroup: {args.subgroup}")
        print(f"Date: {args.date}")
        print(f"Max File Size: {maxfilesize} GiB")
        print(f"Directory: {args.directory}")
        print(f"Bonus Keywords: {bonus}")

        # Ask for confirmation (Y/n)
        confirm = input("\nDo you want to proceed? (Y/n): ").strip().lower()

        if confirm in ['y', 'yes']:
            print('Proceeding...')
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M') if not date else date.strftime('%Y-%m-%d %H:%M')
            maxfilesize_str = str(maxfilesize) if maxfilesize else '-1'

            row = [
                title,
                subgroup if subgroup else 'None',
                date_str,
                maxfilesize_str,
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