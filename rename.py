import argparse
import os
import re
import shutil


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
                regex = r"\[(\d+)\]"
                episode_number = re.search(regex, file)
                if episode_number:
                    episode_number = episode_number.group(1)
                    # add leading 0 if episode number is less than 10
                    if int(episode_number) < 10:
                        episode_number = f"0{int(episode_number)}"
                else:
                    print(f"Could not find episode number for {file}")
                    print(f"Please enter the episode number for {file}")
                    episode_number = input()
                file_ext = file.split(".")[-1]
                if file_ext == "ass":
                    ass_lang = file.split(".")[-2]
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{ass_lang}.{file_ext}"
                else:
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"

            elif "special" in season_name.lower() or "extra" in season_name.lower():
                season_number = "00"
                print(f"Please enter the episode number for {file}")
                episode_number = input()
                # make leading 0 if episode number is less than 10
                if int(episode_number) < 10:
                    episode_number = f"0{episode_number}"
                file_ext = file.split(".")[-1]
                if file_ext == "ass":
                    ass_lang = file.split(".")[-2]
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{ass_lang}.{file_ext}"
                else:
                    new_file_name = f"{show_name} S{season_number}E{episode_number}.{file_ext}"
            # else:
            #     print(f"Moving {os.path.join(root, file)} to {os.path.join(working_dir, file)}")
            #     shutil.move(os.path.join(root, file), os.path.join(working_dir, file))
            if not reformat_all:
                print(f"Renaming \n\tOld: {file} \n\tNew: {new_file_name}")
                move = False
                while not move:
                    print(f"Is this correct? [y/n/A(ll)/q(uit)]")
                    response = input()
                    if response.lower() == "y":
                        move = True
                    elif response.lower() == "n":
                        print(f"Please enter the new file name for {file}")
                        new_file_name = input()
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
                shutil.move(os.path.join(root, file), os.path.join(working_dir, new_file_name))


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
    dest_path = args.dest
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
    print(f"Show folder name: {show_folder_name}\n\n\n")
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
        else:
            print(f"Please enter the season name: i.e Season 01, Specials, Extras")
            season_name = input()
            working_dir = os.path.join(dest_path, show_folder_name, season_name)
            print(f"Copied files will be saved in {working_dir}")
            os.makedirs(working_dir, exist_ok=True)
            reformat_files(src_path, working_dir, show_name, season_name)
    print("Cleaning up empty directories")
    for root, dirs, files in os.walk(src_path):
        if not dirs and not files:
            os.rmdir(root)
    print("Done")


if __name__ == '__main__':
    main()
