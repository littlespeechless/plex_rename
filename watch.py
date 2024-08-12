import argparse
import json
import logging
import os.path
import pathlib
from logging.handlers import RotatingFileHandler

import rename
import qbittorrentapi as qbit


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
        logging.error(f"Watch already exists")
        exit(1)
    if not os.path.exists(source):
        print("Source does not exist")
        logging.error(f"Source does not exist")
        exit(1)
    if not os.path.exists(destination):
        # process no destination found case
        print("Destination does not exist")
        logging.error(f"Watch Add Destination does not exist")
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
        logging.info(f"Creating destination folder {working_dir}")
        if not os.path.exists(working_dir):
            os.makedirs(working_dir, exist_ok=True)
        # reformat the files and move them to the destination
        rename.reformat_files_for_watch(source, working_dir, show_name, season)
        watch_db[source.rstrip("/")] = {"dest": working_dir, "show_name": show_name, "season": season}
        print(f"Watch {source} added successfully, with destination {working_dir}, "
              f"show_name {show_name}, season {season}")
    else:
        watch_db[source.rstrip("/")] = {"dest": destination, "show_name": show_name, "season": season}
        print(f"Watch {source} added successfully, with destination {destination}, "
              f"show folder {show_name}, season {season}")


def get_qbittorrent_info():
    """
    Initialize the qBittorrent client
    Returns:
        qbt_client: qBittorrent client
    """
    # read from .evn file
    conn_info = {
    }
    if not os.path.exists('.env'):
        print("Error: .env file not found")
        logging.error(".env file not found")
        return None
    with open('.env', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            if key == 'QBITTORRENT_HOST':
                conn_info['host'] = value
            elif key == 'QBITTORRENT_PORT':
                conn_info['port'] = value
            elif key == 'QBITTORRENT_USER':
                conn_info['username'] = value
            elif key == 'QBITTORRENT_PASS':
                conn_info['password'] = value
    # Initialize the client
    qbt_client = qbit.Client(**conn_info)
    # the Client will automatically acquire/maintain a logged-in state
    # in line with any request. therefore, this is not strictly necessary;
    # however, you may want to test the provided login credentials.
    try:
        qbt_client.auth_log_in()
    except qbit.LoginFailed as e:
        print(e)
        logging.error(e)
        return None
    # list all currently downloading torrents
    torrents = qbt_client.torrents_info(status_filter='downloading')
    # now we can return all downloaded torrents save path to watch, such that
    # we avoid rename and move the epsiodes that are still downloading
    download_path = {}
    for torrent in torrents:
        save_path: str = torrent['save_path']
        save_path = save_path.rstrip("/")
        download_path[save_path] = True
    # log out
    qbt_client.auth_log_out()
    return download_path


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
                                                              'add new episodes to the library. '
                                                              'User must create .evn file with qBittorrent client info.'
                                                              'The .env file should contain the following'
                                                              ' QBITTORRENT_HOST=<host>, '
                                                              'QBITTORRENT_PORT=<port>, '
                                                              'QBITTORRENT_USER=<username>, '
                                                              'QBITTORRENT_PASS=<password>')
    parser.add_argument('-fix-source', action='store_true', help='Fix the source path of the watch')


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
            logging.info(f"Adding a new watch with source {args.src}, destination {args.dest}, "
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
            source = source.rstrip("/")
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
            source = source.rstrip("/")
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
        print("Refreshing the library... Getting the list of currently downloading torrents")
        logging.info(f"Getting the list of currently downloading torrents...")
        download_path = get_qbittorrent_info()
        if download_path is None:
            print("Error while getting the list of currently downloading torrents")
            logging.error("Error while getting the list of currently downloading torrents")
            exit(1)
        # print download_path
        logging.info(f"Got {len(download_path)} torrents ...")
        for key in download_path:
            logging.info(f"Torrents downloading at {key}")
        # get all the watch sources
        logging.info(f"Refreshing all {len(watch_db)} watches")
        for key, value in watch_db.items():
            print(f"Refreshing {key}")
            logging.info(f"Refreshing {key}")
            if key in download_path:
                print(f"Skipping {key} as it is still downloading")
                logging.info(f"Skipping {key} as it is still downloading")
                continue
            rename.reformat_files_for_watch(key, value['dest'], value['show_name'], value['season'])
    elif args.fix_source:
        print("Fixing the source path of the watch")
        logging.info("Fixing the source path of the watch")
        new_watch_db = {}
        for key, value in watch_db.items():
            new_source = key.rstrip("/")
            new_watch_db[new_source] = value
        # save the watch database
        with open(watch_db_path, 'w') as f:
            json.dump(new_watch_db, f, indent=4)
    # save the watch database
    if args.add or args.remove or args.update:
        with open(watch_db_path, 'w') as f:
            json.dump(watch_db, f, indent=4)


if __name__ == '__main__':
    # Configure logging with RotatingFileHandler

    # Create a RotatingFileHandler
    handler = RotatingFileHandler('watch.log', maxBytes=10 * 1024 * 1024, backupCount=2)
    handler.setLevel(logging.INFO)

    # Optionally set a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # logger = logging.getLogger('watch_logger')
    # logger.setLevel(logging.INFO)
    # handler = RotatingFileHandler('watch.log', maxBytes=10 * 1024 * 1024, backupCount=2)  # 5 MB file size
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    main()
