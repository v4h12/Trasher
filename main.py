#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse
from urllib.parse import unquote


#################################################################
#                                                               #
#   ████████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗    #
#   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗   #
#      ██║   ██████╔╝███████║███████╗███████║█████╗  ██████╔╝   #
#      ██║   ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██╔══██╗   #
#      ██║   ██║  ██║██║  ██║███████║██║  ██║███████╗██║  ██║   #
#      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   #
#                                                               #
#       This was made by Ethan Scott (v4h12 on github)          #
# ------------------------------------------------------------- #
#            github: https://github.com/v4h12/trasher           #
#            Copyright (c) 2025 Ethan Scott                     #
#            MIT License                                        #
#                                                               #
#################################################################
#                                                               #
#   how the code flows:                                         #
#   - get trash paths > create functions (                      #
#   restore, delete, inbetweens) > main code                    #
#                                                               #
#################################################################
#                                                               #
#   functions in order:                                         #
#                                                               #
#   - decode original path                                      #
#   - restore trashed files/paths to original path              #
#   - delete function which includes:                           #
#       - permission changes (chmod and chown)                  #
#   - choice function where user decides what they want to do   #
#   - numbered list of trashed directories for user input       #
#   - file formatting for file sizes (b, kb, mb, gb)            #
#                                                               #
#################################################################


# grab directory to create variables of the output (files, info, expunged)
tr_path = os.path.join(os.environ["HOME"], ".local/share/Trash")
tr_files = os.path.join(tr_path, "files")
tr_info = os.path.join(tr_path, "info")


# this is to get the original path and decode it for the restore_file function
def decog_path(info_file):
    if not os.path.exists(info_file):
        return None

    with open(info_file) as f:
        for line in f:
            if line.startswith("Path="):
                return unquote(line.strip().split("=", 1)[1])
    return None


# replace variable content with og_path using os.rename
def restore_file(filename):
    trash_file = os.path.join(tr_files, filename)
    info_file = os.path.join(tr_info, filename + ".trashinfo")

    og_path = decog_path(info_file)
    if not og_path:
        print(f"Cannot restore {filename}: missing path or possibly missing .trashinfo")
        return

    # make sure directory exists first with os.makedirs then
    # for os.rename - first is file to be replaced, second is the file used to replace it
    os.makedirs(os.path.dirname(og_path), exist_ok=True)
    os.rename(trash_file, og_path)
    os.remove(info_file)
    print(f" Restored {filename} to {og_path}")


# delete function
def delete_file(filename):
    trash_file = os.path.join(tr_files, filename)
    info_file = os.path.join(tr_info, filename + ".trashinfo")
    og_path = decog_path(info_file)

    try:
        if os.path.isdir(trash_file):
            shutil.rmtree(trash_file)
        else:
            os.remove(trash_file)

        if os.path.exists(info_file):
            os.remove(info_file)
        print(f" Permanently deleted {og_path}")

    # create permission option to change ownership of protected file
    # if user decides no, choices made / the rest get deleted
    except PermissionError:
        print(f"\nPermission denied: {filename} is protected")
        chper = get_choice(
            "Requires root access to delete, Continue? (y/n): ", ["y", "n"]
        )

        if chper == "y":
            try:
                print("requesting sudo access...")

                # change ownership
                subprocess.run(
                    [
                        "sudo",
                        "chown",
                        "-R",
                        f"{os.environ['USER']}:{os.environ['USER']}",
                        trash_file,
                    ],
                    check=True,
                    stderr=subprocess.PIPE,
                )

                # change permissions
                subprocess.run(
                    [
                        "sudo",
                        "chmod",
                        "-R",
                        "u+rw",
                        trash_file,
                    ],
                    check=True,
                )

                print(f"Ownership changed for {filename}. Deleting... ")

                # run files to delete again
                if os.path.isdir(trash_file):
                    shutil.rmtree(trash_file)
                else:
                    os.remove(trash_file)

                if os.path.exists(info_file):
                    os.remove(info_file)
                print(f"Succesfully deleted {filename}")

            except subprocess.CalledProcessError as e:
                print(f"failed to gain root permission {e.stderr.decode().strip()}")
            except Exception as e:
                print(f"Error after permission change {e}")

        elif chper == "n":
            print(f"skipping {filename}...")


# choice function for invalid inputs
def get_choice(prompt, valid_options):
    while True:
        choice = input(prompt).lower()
        if choice in valid_options:
            return choice
        print("Invalid Input")


# function for handling numbered inputs for files
def get_file_num(prompt, max_files):
    while True:
        try:
            choice = input(prompt)
            nums = choice.split()
            indices = []
            for num in nums:
                index = int(num) - 1
                if index < 0 or index >= max_files:
                    print(f"Number {num} is out of range: (1-{max_files})")
                    raise ValueError
                indices.append(index)
            return indices
        except ValueError:
            print("Invalid input")


# list file or directory sizes when files get listed
def format_size(bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"


# list directories and files in trash -- turned into function to become usable
def list_dir():
    if not os.listdir(tr_files):
        print("\nTrash is empty... nothing to trash :(\n")
        exit()
    else:
        print("Files in trash: ")
        print("┌" + "─" * 55 + "┐")
        files = os.listdir(tr_files)
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(tr_files, filename)
            if os.path.isdir(file_path):
                size_bytes = os.stat(os.path.join(tr_files, filename)).st_size
                print(f" {i}.) {filename}(/) - {format_size(size_bytes)}")
            else:
                size_bytes = os.stat(os.path.join(tr_files, filename)).st_size
                print(f" {i}.) {filename} - {format_size(size_bytes)}")
        print("└" + "─" * 55 + "┘")
        return files


# fzf implementation option for ease of use of speed
def fzf_path():
    mapping = {}
    for filename in os.listdir(tr_files):
        info_file = os.path.join(tr_info, filename + ".trashinfo")
        og_path = decog_path(info_file)
        if og_path:
            mapping[og_path] = filename
    return mapping


def fzf_choice(names):
    try:
        result = subprocess.run(
            ["fzf", "--reverse", "--multi"],
            input="\n".join(names),
            text=True,
            capture_output=True,
        )
        return result.stdout.strip().split("\n") if result.stdout else []
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        print("fzf not found in system")
        exit(1)


def fzf_opt():
    """convert the dict into a list for fzf and
    use the keys from the tuple to show user trashed files"""
    try:
        mapping = fzf_path()
        choices = fzf_choice(list(mapping.keys()))
        if not choices or choices == [""]:
            print("\nNothing selected")
            return

        print("┌" + "─" * 55 + "┐")
        print(" Selected: ")
        for path in choices:
            print(f" - {path}")
        print("└" + "─" * 55 + "┘")

        what = get_choice("\nRestore or Delete? r/d): ", ["r", "d"])

        print("\n┌" + "─" * 55 + "┐")
        if what == "r":
            for path in choices:
                tr_filename = mapping[path]
                restore_file(tr_filename)
        elif what == "d":
            for path in choices:
                tr_filename = mapping[path]
                delete_file(tr_filename)
        print("└" + "─" * 55 + "┘")
        return choices

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher")


#################################################################################
#                                                                               #
#           This is section is for any flags (ArgumentParser)                   #
#                                                                               #
#################################################################################

parser = argparse.ArgumentParser()

parser.add_argument(
    "-l", "--list", action="store_true", help="list files or directories in the trash"
)

parser.add_argument(
    "-R",
    "--restore",
    action="store_true",
    help="restore all files or directories in the trash",
)

parser.add_argument(
    "-D",
    "--delete",
    action="store_true",
    help="permanently delete all files or directories in the trash",
)

parser.add_argument(
    "--version", action="store_true", help="shows softwares version number"
)

parser.add_argument(
    "-f",
    "--fzf",
    action="store_true",
    help="use fzf (fuzzyfinder) to restore or delete files",
)

# this reads what the users input is for the argparse function
args = parser.parse_args()

# FIX - after this command is run, main code still runs ~ prints 'trash empty :(" (unnecessary)'
# trasher -R or --restore
if args.restore:
    print("\n┌" + "─" * 55 + "┐")
    for filename in os.listdir(tr_files):
        restore_file(filename)
    print("└" + "─" * 55 + "┘")
    exit()

# trasher -D or --delete
if args.delete:
    print("\n┌" + "─" * 55 + "┐")
    for filename in os.listdir(tr_files):
        delete_file(filename)
    print("└" + "─" * 55 + "┘")
    exit()

# trasher --version
if args.version:
    print("\n0.2.1 - (Pre-Release)")
    exit()

# trasher -l or --list | copy main code to list files and (TODO) add date and time
if args.list:
    list_dir()
    exit()

if args.fzf:
    if not os.listdir(tr_files):
        print("\ntrash is empty, nothing to trash :( \n")
    else:
        fzf_opt()
    exit()

#################################################################################
#                                                                               #
#            MAIN CODE - This is all the user input which uses                  #
#                       the def functions above                                 #
#                                                                               #
#################################################################################


# wrap main code for 'KeyboardInterrupt' prompt
if __name__ == "__main__":
    try:
        # this is used to call the list_dir function (originally not a function)
        files = list_dir()

        # user input
        what = get_choice("\nRestore or Delete files? (r/d): ", ["r", "d"])

        # if you chose 'r' to restore files
        if what == "r":
            resaf = get_choice("\nRestore all files? (y/n): ", ["y", "n"])
            if resaf == "y":
                print("\n" + "┌" + "─" * 55 + "┐")
                for filename in os.listdir(tr_files):
                    restore_file(filename)
                print("└" + "─" * 55 + "┘")

            elif resaf == "n":
                indices = get_file_num("\nSelect number/s to restore: ", len(files))
                print("\n" + "┌" + "─" * 55 + "┐")
                for index in indices:
                    restore_file(files[index])
                print("└" + "─" * 55 + "┘")

        # if you choose 'd' to delete files
        elif what == "d":
            delaf = get_choice("\nDelete all files? (y/n): ", ["y", "n"])
            if delaf == "y":
                print("\n" + "┌" + "─" * 55 + "┐")
                for filename in os.listdir(tr_files):
                    delete_file(filename)
                print("└" + "─" * 55 + "┘")

            elif delaf == "n":
                indices = get_file_num("\nSelect number/s to delete: ", len(files))
                print("\n" + "┌" + "─" * 55 + "┐")
                for index in indices:
                    delete_file(files[index])
                print("└" + "─" * 55 + "┘")

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher\n")
        exit(0)


# -------------------------------------------------#
# **FIXED**
# issue: when deleted files are recovered, they get restored in a directory with the files inside and name instead
# of recovering to original position as the file which was deleted

# issue: .trashinfo out of the for loop

# - packages installed via a package manager will give a permission error:
#   giving trasher root permissons doesnt help since there is a diff trash dir in root
#   possible fixes:
#       - force it to delete
#       - make script to change file permission (with permission from user) to delete
#   (for now give permission error so program doesnt crash)

# -------------------------------------------------#
# box outlines
# ┌ ┐ ┘ └ ─
# -------------------------------------------------#
