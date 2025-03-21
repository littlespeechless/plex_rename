import argparse
import logging
import os
import re
import shutil


def reformat_files_for_watch(src_path: str, working_dir: str, show_name, season_name):
    """
    Rename all files in a directory to Plex library format for watching dir

    :param src_path: Path to the download media files
    :param working_dir: Path to the destination folder
    :param show_name: Name of the show
    :param season_name: Name of the season
    :return: None
    """
    for root, dirs, files in os.walk(src_path):
        # we ASSUME regex will always find the episode number correctly
        for file in files:
            # we ASSUME season will be in the format Season [d]+
            if "season" in season_name.lower():
                season_number = season_name.split(" ")[1]
                # Koukyuu no Karasu [02][Ma10p_1080p][x265_flac]
                # find the episode number in [] using regex
                regexs = [r"\[(\d+)\]", r"-\s(\d+)\s", r"EP(\d+)", r"S\d+E(\d+)", r"\s(\d+).", r"\s(\d+)\s", ]
                for regex in regexs:
                    episode_number = re.search(regex, file)
                    if episode_number:
                        episode_number = episode_number.group(1)
                        break
                else:
                    print(f"Could not find episode number for {file}")
                    print(f"Please enter the episode number for {file}")
                    logging.error(f"Could not find episode number for {file}, "
                                  f"{src_path}, {show_name}, {season_name}")
                    # exit directly since we are running in watch mode
                    exit(-1)
                # add leading 0 if episode number is less than 10
                if int(episode_number) < 10:
                    episode_number = f"0{int(episode_number)}"
                file_ext = file.split(".")[-1]
                if file_ext == "ass":
                    ass_lang = file.split(".")[-2]
                    if len(ass_lang) >= 3:
                        # case of no ass lang
                        new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"
                    else:
                        new_file_name = f"{show_name} S{season_number}E{episode_number}.{ass_lang}.{file_ext}"
                else:
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"
                file_path = os.path.join(root, file)
                moving_path = os.path.join(working_dir, new_file_name)
                print(f"Moving {file_path} to "
                      f"{moving_path}")
                logging.info(f"Moving {file_path} to "
                             f"{moving_path}")
                # final check
                if not os.path.exists(os.path.dirname(moving_path)):
                    print(f"Failed moving, {moving_path} parent dir not exist")
                    logging.error(f"Failed moving, {moving_path} parent dir "
                                  f"{os.path.exists(os.path.dirname(moving_path))}not exist")
                    exit(-1)
                shutil.move(os.path.join(root, file), os.path.join(working_dir, new_file_name))
            else:
                logging.error(f"Invalid Season name {season_name}")


def reformat_files(src_path: str, working_dir: str, show_name, season_name):
    """
    Rename all files in a directory to Plex library format

    :param src_path: Path to the download media files
    :param working_dir: Path to the destination folder
    :param show_name: Name of the show
    :param season_name: Name of the season
    :return: None
    """
    for root, dirs, files in os.walk(src_path):
        reformat_all = False
        for file in files:
            # check if season is a special or extras
            if "season" in season_name.lower():
                season_number = season_name.split(" ")[1]
                # Koukyuu no Karasu [02][Ma10p_1080p][x265_flac]
                # find the episode number in [] using regex
                regexs = [r"\[(\d+)\]", r"-\s(\d+)\s", r"EP(\d+)", r"S\d+E(\d+)", r"\s(\d+).", r"\s(\d+)\s", ]
                for regex in regexs:
                    episode_number = re.search(regex, file)
                    if episode_number:
                        episode_number = episode_number.group(1)
                        break
                else:
                    print(f"Could not find episode number for {file}")
                    print(f"Please enter the episode number for {file}")
                    episode_number = input()

            elif "special" in season_name.lower() or "extra" in season_name.lower():
                season_number = "00"
                print(f"Please enter the episode number for {file}")
                episode_number = input()
            else:
                print(f"Invalid Folder Structure, folder must be Season #, Specials or Extras")
                exit(-1)
            # add leading 0 if episode number is less than 10
            if int(episode_number) < 10:
                episode_number = f"0{int(episode_number)}"
            file_ext = file.split(".")[-1]
            if file_ext == "ass":
                ass_lang = file.split(".")[-2]
                if len(ass_lang) > 3:
                    # case of no ass lang
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"
                else:
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{ass_lang}.{file_ext}"
            else:
                new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"

            if not reformat_all:
                print(f"Renaming \n\tOld: {file} \n\tNew: {new_file_name}")
                move = False
                while not move:
                    print(f"Is this correct? [y/n/A(ll)/q(uit)]")
                    response = input()
                    if response.lower() == "y":
                        move = True
                    elif response.lower() == "n":
                        print(f"Please enter the show epsoide name for {file}")
                        episode_number = input()
                        if int(episode_number) < 10:
                            episode_number = f"0{int(episode_number)}"
                        new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"
                        # check if is ass
                        if file_ext == "ass" and len(ass_lang) <= 3:
                            new_file_name = f"{show_name} S{season_number}E{episode_number}.{ass_lang}.{file_ext}"
                        move = True
                    elif response.lower() == "a":
                        reformat_all = True
                        move = True
                    elif response.lower() == "q":
                        print("Quitting")
                        exit(0)
            if reformat_all or move:
                print(f"Moving {os.path.join(root, file)} to "
                      f"{os.path.join(working_dir, new_file_name)}")
                # check file path exist or not
                if not os.path.exists(working_dir):
                    print(f"Workingdir {working_dir} not exists")
                    exit(-1)
                shutil.move(os.path.join(root, file), os.path.join(working_dir, new_file_name))


def start_renaming(src_path, dest_path, show_name, show_folder_name):
    print(f"Show folder name: {show_folder_name}\n\n\n")
    working_dir = None
    for root, dirs, files in os.walk(src_path):
        if root == src_path and len(dirs) > 0:
            print("Multiple seasons found now processing each directory")
            for folder in dirs:
                folder: str
                print(f"Processing {folder}, please enter the season name: i.e Season 01, Specials, Extras")
                season_name = input()
                working_dir = os.path.join(dest_path, show_folder_name, season_name)
                print(f"Copied files will be saved in {working_dir}")
                os.makedirs(working_dir, exist_ok=True)
                reformat_files(os.path.join(src_path, folder), working_dir, show_name, season_name)
            break
        else:
            print(f"Please enter the season name: i.e Season 01, Specials, Extras")
            season_name = input()
            working_dir = os.path.join(dest_path, show_folder_name, season_name)
            print(f"Copied files will be saved in {working_dir}")
            os.makedirs(working_dir, exist_ok=True)
            reformat_files(src_path, working_dir, show_name, season_name)

    return working_dir if working_dir else None


def get_show_info(show_name=None):
    """
    Get show info from user via input
    return: show_name, show_folder_name
    """
    if not show_name:
        print(f"Please enter the show name: ")
        show_name = input()
    print(f"Please enter the show year: ")
    show_year = input()
    # validate show year
    if not show_year.isdigit():
        print("Show year must be a number")
        exit(1)
    show_folder_name = f"{show_name} ({show_year})"
    # show_name = f"{show_name} ({show_year})"
    print("Force db id? [y/n]")
    force_db_id = input()
    if force_db_id.lower() == "y":
        print(f"Please enter db show id: i.e tvdb-123456, anidb-12345, tmdb-xxxx")
        db_id = input()
        show_folder_name = "{} [{}]".format(show_folder_name, db_id)
    elif force_db_id.lower() == "n":
        pass
    return show_name, show_folder_name


def main():
    """
    rename downloaded media to plex library format

    """
    # add argparse
    parser = argparse.ArgumentParser(description='rename downloaded media to plex library format')
    # add arguments
    parser.add_argument('--src', type=str, required=True, help='Path to the download media files')
    parser.add_argument('--dest', type=str, required=True, help='Path to the destination folder')
    # parse arguments
    args = parser.parse_args()
    # print arguments
    src_path = args.src
    if src_path[0] == "~":
        src_path = os.path.expanduser(src_path)
    dest_path = args.dest
    if dest_path[0] == "~":
        dest_path = os.path.expanduser(dest_path)

    # print(f"Please enter the show name: ")
    # show_name = input()
    # print(f"Please enter the show year: ")
    # show_year = input()
    # # validate show year
    # if not show_year.isdigit():
    #     print("Show year must be a number")
    #     exit(1)
    # show_folder_name = f"{show_name} ({show_year})"
    # # show_name = f"{show_name} ({show_year})"
    # print("Force db id? [y/n]")
    # force_db_id = input()
    # if force_db_id.lower() == "y":
    #     print(f"Please enter db show id: i.e tvdb-123456, anidb-12345, tmdb-xxxx")
    #     db_id = input()
    #     show_folder_name = "{} [{}]".format(show_folder_name, db_id)
    # elif force_db_id.lower() == "n":
    #     pass

    show_name, show_folder_name = get_show_info()

    working_dir = start_renaming(src_path, dest_path, show_name, show_folder_name)

    print("Is continue? [y/n]")
    c = input()
    if c.lower() == "y":
        pass
    elif c == "n":
        print("Cleaning up empty directories")
        for root, dirs, files in os.walk(src_path):
            if not dirs and not files:
                os.rmdir(root)
        print("Done")


if __name__ == '__main__':
    main()
