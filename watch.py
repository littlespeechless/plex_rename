import argparse
import json
import logging
import os.path
from logging.handlers import RotatingFileHandler

import rename


def add_watch(source, destination, show_name, season, watch_db):
    """
    Add a new watch
    Args:
        source: Source of the watch
        destination: Destination of the watch
        show_name: Show name
        season: Season number
        watch_db: Watch database
    """
    if source in watch_db:
        print("Watch already exists")
        logger.error(f"Watch already exists")
        exit(1)
    if not os.path.exists(source):
        print("Source does not exist")
        logger.error(f"Source does not exist")
        exit(1)
    if not os.path.exists(destination):
        # process no destination found case
        print("Destination does not exist")
        logger.error(f"Watch Add Destination does not exist")
        print("Starting Rename process")
        print("Please enter the plex library root path")
        plex_root = input()
        if plex_root[0] == "~":
            plex_root = os.path.expanduser(plex_root)
        # plex_root = os.path.abspath(plex_root)
        show_name, show_folder_name = rename.get_show_info(show_name=show_name)
        # create the destination folder
        working_dir = os.path.join(plex_root, show_folder_name, season)
        print(f"Creating destination folder {working_dir}")
        logger.info(f"Creating destination folder {working_dir}")
        if not os.path.exists(working_dir):
            os.makedirs(working_dir, exist_ok=True)
        # reformat the files and move them to the destination
        rename.reformat_files_for_watch(source, working_dir, show_name, season, logger)
        watch_db[source] = {"dest": working_dir, "show_name": show_name, "season": season}
        print(f"Watch {source} added successfully, with destination {working_dir}, "
              f"show_name {show_name}, season {season}")
    else:
        watch_db[source] = {"dest": destination, "show_name": show_name, "season": season}
        print(f"Watch {source} added successfully, with destination {destination}, "
              f"show folder {show_name}, season {season}")


def main():
    """
    Main function for the watch module.
    Args:
        -add : Add a new watch
        -src : Source of the watch
        -dest : Destination of the watch
        -show-names : Show names of the files
        -list : List all watches
        -remove : Remove a watch
        -update : Update a watch
    """
    parser = argparse.ArgumentParser(description='Watch utility for managing Plex libraries.')
    parser.add_argument('-add', action='store_true', help='Add a new watch')
    parser.add_argument('-src', type=str, help='Source of the watch')
    parser.add_argument('-dest', type=str, help='Destination of the watch')
    parser.add_argument('-show-name', type=str, help='show folder name')
    parser.add_argument('-season', type=str, help='Season number')
    parser.add_argument('-list', action='store_true', help='List all watches')
    parser.add_argument('-remove', action='store_true', help='Remove a watch')
    parser.add_argument('-update', action='store_true', help='Update a watch')
    parser.add_argument("-refresh", action='store_true', help='Perform a refresh and '
                                                              'add new episodes to the library')

    args = parser.parse_args()

    watch_db_path = "./watch.json"
    if not os.path.exists(watch_db_path):
        print("Creating watch database")
        watch_db = {}
        with open(watch_db_path, 'w') as f:
            json.dump(watch_db, f, indent=4)
    else:
        with open(watch_db_path, 'r') as f:
            watch_db = json.load(f)

    # Example usage of parsed arguments
    if args.add:
        # if cmd is watch.py -add -src <src> -dest <dest> -show-names <show-names>
        if args.src and args.dest and args.show_name and args.season:
            # process the arguments with non-interative mode
            print(
                f"Adding a new watch with source {args.src}, destination {args.dest}, "
                f"show-name {args.show_name}, season {args.season}")
            logger.info(f"Adding a new watch with source {args.src}, destination {args.dest}, "
                        f"show-names {args.show_name}, season {args.season}")
            source = args.src
            destination = args.dest
            show_name = args.show_name
            season = args.season
        else:
            # process the arguments with interactive mode
            print("Please enter the source path")
            source = input()
            print("Please enter the destination path")
            destination = input()
            print("Show Name  i.e Show Name")
            show_name = input()
            print("Please enter the season str")
            season = input()
        if source[0] == "~":
            source = os.path.expanduser(source)
        if destination[0] == "~":
            destination = os.path.expanduser(destination)
        add_watch(source, destination, show_name, season, watch_db)

    elif args.list:
        print(f"Listing all watches, {len(watch_db)} total watches\n")
        print("-" * 50)
        for key, value in watch_db.items():
            # pretty print the watch database
            print(f"Show Name: {value['show_name']}")
            print(f"\tSeason: {value['season']}\n"
                  f"\tWatch Source: {key}\n"
                  f"\tPlex Destination: {value['dest']}\n"
                  )
            print("-" * 50)

    elif args.remove:
        if args.src:
            source = args.src
        else:
            print("Please enter the source path")
            source = input()
        if source in watch_db:
            del watch_db[source]
            print(f"Watch {source} removed successfully")
        else:
            print(f"Watch {source} not found")
    elif args.update:
        if args.src:
            source = args.src
        else:
            print("Please enter the source path")
            source = input()
        if source in watch_db:
            print("Please enter the destination path")
            destination = input()
            print("Show Name folder i.e Show Name")
            show_name = input()
            print("Please enter the season str, i.e Season 01, Specials, Extras")
            season = input()
            watch_db[source] = {"dest": destination, "show_name": show_name, "season": season}
            print(f"Watch {source} updated successfully, with destination {destination}, "
                  f"show_name {show_name}, season {season}")
        else:
            print(f"Watch {source} not found")
    elif args.refresh:
        print("Refreshing the library")
        logger.info(f"Refreshing all {len(watch_db)} watches")
        for key, value in watch_db.items():
            print(f"Refreshing {key}")
            logger.info(f"Refreshing {key}")
            rename.reformat_files_for_watch(key, value['dest'], value['show_name'], value['season'], logger)

    # save the watch database
    if args.add or args.remove or args.update:
        with open(watch_db_path, 'w') as f:
            json.dump(watch_db, f, indent=4)


if __name__ == '__main__':
    # # add logger
    # logging.basicConfig(level=logging.INFO,
    #                     filename='watch.log',
    #                     filemode='a',
    #                     format='%(asctime)s - %(levelname)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    # Configure logging with RotatingFileHandler
    logger = logging.getLogger('watch_logger')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('watch.log', maxBytes=10 * 1024 * 1024, backupCount=2)  # 5 MB file size
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
