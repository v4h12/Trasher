#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse
import argcomplete
from urllib.parse import unquote, quote
from datetime import datetime


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

# check if trash dir exists, if not then make it (shouldve been here from the start)
trash_dir = os.path.expanduser("~/.local/share/Trash")
if not os.path.isdir(trash_dir):
    for subdir in ("info", "files", "expunged"):
        os.makedirs(os.path.join(trash_dir, subdir), exist_ok=True)


# grab directory to create variables of the output (files, info, expunged)
tr_path = os.path.join(os.environ["HOME"], ".local/share/Trash")
tr_files = os.path.join(tr_path, "files")
tr_info = os.path.join(tr_path, "info")


# this is to get the original path and decode it for the restore_file function
# unquote is used here for percent encoded sequences from the .trashinfo files
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
        print(
            f"Cannot restore {filename}: missing path or possibly missing .trashinfo \n - Check .local/share/Trash/info for {filename}.trashinfo"
        )
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
def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


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


#######################################################################################
#
# implementation of trashing files
# this follows freedesktop.org trash spec:
#
# the point is to move the file to .local/share/Trash/ where there
# are 2 directories they go inside ~ 'files' and 'info'
# Files:
#   - this is where the original file/dir will be placed, with their
#   original path only, nothing else changed (keep in mind for dupes)
# Info:
#   - this is the trickier part, paths need to be percent encoded
#     (this has already been dealt with by decog_path which does the opposite)
#   - time and date is required as 'DeletionDate', use datetime library and
#     this deals with FILES ONLY not directories.
#
# PREVIEW of what .trashinfo file should look like:
# [Trash Info]
# Path=/home/v4h/Documents/learning/server%2B/1.11%20-%20server%20components.pdf
# DeletionDate=2026-03-05T11:10:52
#
######################################################################################


# abspath is used when user types path to be deleted
def decimate_file(filepath):
    fpath = os.path.abspath(filepath)
    if not os.path.exists(fpath):
        print(f"Cannot trash {filepath}: file or directory doesn't exist")
        return

    # create variables for paths including the file destination (coord)
    filename = os.path.basename(fpath)
    coord = os.path.join(tr_files, filename)
    info_file = os.path.join(tr_info, filename + ".trashinfo")

    # added a counter for dupes, whether it'll work im not sure due to
    # the restore function, splitext splits the name from the extention (ext)
    # e.g. text(1).txt text(2).txt *ONLY* when names are the same, thats why 'or' is used
    counter = 1
    while os.path.exists(coord) or os.path.exists(info_file):
        name, ext = os.path.splitext(filename)
        dname = f"{name}({counter}){ext}"
        coord = os.path.join(tr_files, dname)
        info_file = os.path.join(tr_info, dname + ".trashinfo")
        counter += 1

    # this is ti write to the .trashinfo file - changes time to a string
    # info_file is important here as it is used for making the .trashinfo file
    # use quote to percent encode the sequence (opposite to decog_path)
    deletion_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(info_file, "w") as f:
        f.write("[Trash Info]\n")
        f.write(f"Path={quote(fpath, safe='/')}\n")
        f.write(f"DeletionDate={deletion_date}\n")

    # shutil to easily move file to destination (trash) and exception clause for safety
    try:
        shutil.move(fpath, coord)
        print(f" {fpath}")
    except Exception as e:
        os.remove(info_file)
        print(f"Failed to trash {fpath}: {e}")


#####################################################################################
# fzf implementation option for ease of use of speed
# changed mapping to trash path instead of og path for ease of fzf preview
def fzf_path():
    mapping = {}
    for filename in os.listdir(tr_files):
        info_file = os.path.join(tr_info, filename + ".trashinfo")
        og_path = decog_path(info_file)
        if og_path:
            trash_path = os.path.join(tr_files, filename)
            mapping[og_path] = trash_path
    return mapping


# use fzf file preview (--preview=cat {}) - this is done, includinfg pdftotext,
# i already regret thinking about this but image preview as well
# TODO:
# - change fzf path to og_path (currently showing trash path (.local/share/Trash/files))
#   something to do with --with-nth and --delimiter
# - add image preview to the retardedly bitchass long '--preview' line - gotta be a better way to do this
def fzf_choice(mapping):
    lines = [f"{og}\t{trash}" for og, trash in mapping.items()]
    try:
        result = subprocess.run(
            [
                "fzf",
                "--reverse",
                "--multi",
                "--with-nth=1",
                "--delimiter=\t",
                '--preview=f={2}; ext="${f##*.}"; if [ -d "$f" ]; then ls -lah "$f"; elif [ "$ext" = "pdf" ]; then pdftotext "$f" -; else cat "$f"; fi',
            ],
            input="\n".join(lines),
            text=True,
            capture_output=True,
        )

        # reference for different terminals with bash: (https://kszenes.github.io/blog/2024/ImgCat/)
        #   - another option is chafa which seems to work well over imgcat which is mainly for iTerm2
        # if [ "$LC_TERMINAL" = "iTerm2" ]; then
        #   alias icat="imgcat -H 33%"
        # else
        #   alias icat="kitten icat"
        # fi

        selected = []
        for line in result.stdout.strip().split("\n"):
            if line:
                og, trash = line.split("\t")
                selected.append((og, trash))
        return selected
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        print("fzf not found in system")
        exit(1)


# convert the dict into a list for fzf and
# use the values from the tuple to show user trashed files
def fzf_opt():
    try:
        mapping = fzf_path()
        # choices = fzf_choice(list(mapping.values()))
        choices = fzf_choice(mapping)
        # reverse = {v: k for k, v in mapping.items()}
        if not choices or choices == [""]:
            print("\nNothing selected")
            return

        print("┌" + "─" * 55 + "┐")
        print(" Selected: ")
        # for path in choices:
        for og, trash in choices:
            print(f" - {og}")
        print("└" + "─" * 55 + "┘")

        what = get_choice("\nRestore or Delete? (r/d): ", ["r", "d"])

        print("\n┌" + "─" * 55 + "┐")
        if what == "r":
            # for path in choices:
            for og, trash in choices:
                tr_filename = os.path.basename(trash)
                restore_file(tr_filename)
        elif what == "d":
            # for path in choices:
            for og, trash in choices:
                tr_filename = os.path.basename(trash)
                delete_file(tr_filename)
        print("└" + "─" * 55 + "┘")
        return choices

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher")


#################################################################################
#                                                                               #
#       This is section is for any flags (ArgumentParser, Argcomplete)          #
#                                                                               #
#################################################################################

# should be noted that it works with multiple arguments, but pipx needs to be installed
# so that argcomplete can be installed - in bash it needs to be evaluated, in zsh and fish... not sure.

# basic af honestly, still annoying (https://pypi.org/project/argcomplete/)
# still dunno what **kwargs is though, copy and paste
def trash_completer(**kwargs):
    return os.listdir(tr_files)


# trying to implement a case insensitive autocomplete but idk
def find_trash(filename):
    for f in os.listdir(tr_files):
        if f.lower() == filename.lower():
            return f
    return None


parser = argparse.ArgumentParser(
    prog="trasher",
    usage="trasher [OPTION]... [FILE]...",
    description="Your CLI trash manager, Trasher",
)

parser.add_argument("files", metavar="Files", nargs="*", help=" ")

parser.add_argument(
    "-l", "--list", action="store_true", help="list files or directories in the trash"
)

parser.add_argument(
    "-V",
    "--verbose-all",
    action="store_true",
    help="Give verbose information (.trashinfo) about all files",
)

parser.add_argument(
    "-v",
    "--verbose",
    metavar="[FILE]",
    nargs="+",
    help="Give verbose information (.trashinfo) about a specific file",
).completer = trash_completer  # ignore these errors

parser.add_argument(
    "-t",
    "--trash",
    metavar="[FILE]",
    nargs="+",
    help="trash a file or directory",
)

parser.add_argument(
    "-R",
    "--restore-all",
    action="store_true",
    help="restore all files or directories in the trash",
)

parser.add_argument(
    "-r",
    "--restore",
    metavar="[file]",
    nargs="+",
    help="restore all files or directories in the trash",
).completer = trash_completer  # ignore these errors

parser.add_argument(
    "-D",
    "--delete-all",
    action="store_true",
    help="permanently delete all files or directories in the trash",
)

parser.add_argument(
    "-d",
    "--delete",
    metavar="[file]",
    nargs="+",
    help="permanently delete all files or directories in the trash",
).completer = trash_completer  # ignore these errors

parser.add_argument(
    "-f",
    "--fzf",
    action="store_true",
    help="use fzf (fuzzyfinder) to restore or delete files",
)

parser.add_argument(
    "--version", action="store_true", help="shows softwares version number"
)

# this reads what the users input is for the argparse function and the argcomplete
argcomplete.autocomplete(parser)
args = parser.parse_args()

# trasher -R or --restore
if args.restore_all:
    try:
        what = get_choice("\nRestore all files in the trash? (y/n): ", ["y", "n"])

        if what == "y":
            print("\n┌" + "─" * 55 + "┐")
            for filename in os.listdir(tr_files):
                restore_file(filename)
            print("└" + "─" * 55 + "┘")

        elif what == "n":
            print("\n\n... Quitting trasher\n")
            exit()

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher")

    exit()

# trasher -D or --delete
if args.delete_all:
    try:
        what = get_choice("\nDelete all files in the trash? (y/n): ", ["y", "n"])

        if what == "y":
            print("\n┌" + "─" * 55 + "┐")
            for filename in os.listdir(tr_files):
                delete_file(filename)
            print("└" + "─" * 55 + "┘")

        elif what == "n":
            print("\n\n... Quitting trasher\n")
            exit()

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher")

    exit()

if args.restore:
    print("\n┌" + "─" * 55 + "┐")
    for filename in args.restore:
        match = find_trash(filename)
        if match:
            restore_file(filename)
        else:
            print(f" '{filename}' not found in trash.")
    print("└" + "─" * 55 + "┘")
    exit()

if args.delete:
    print("\n┌" + "─" * 55 + "┐")
    for filename in args.delete:
        match = find_trash(filename)
        if match:
            delete_file(filename)
        else:
            print(f" '{filename}' not found in trash.")
    print("└" + "─" * 55 + "┘")
    exit()

if args.trash:
    print("\n┌" + "─" * 55 + "┐")
    print(" Trashed:")
    for filepath in args.trash:
        decimate_file(filepath)
    print("└" + "─" * 55 + "┘")
    exit()

# trasher --version
if args.version:
    print("\n0.2.1 - (Pre-Release)")
    exit()

if args.verbose:
    for filename in args.verbose:
        match = find_trash(filename)
        if match:
            info_file = os.path.join(tr_info, match + ".trashinfo")
            print(open(info_file).read())
        else:
            print(f" '{filename}' not found in trash.")
    exit()

if args.verbose_all:
    for filename in os.listdir(tr_info):
        info_file = os.path.join(tr_info, filename)
        print(open(info_file).read())
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


# TODO:
# implement error code for if trash dir is not yet created / create trash dir on install within install script
# create delete function for multiple files - then implement fzf
# - this also follows the freedesktop.org trash spec: (https://specifications.freedesktop.org/trash/1.0/)
# there is no autocomplete (tab) for when using arguments -r and -d
# argcomplete on PyPI seems to have the solution

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
#
# ┌ ┐ ┘ └ ─
# -------------------------------------------------#

# FIX:
# Traceback (most recent call last):
#   File "/usr/local/bin/trasher", line 476, in <module>
#     files = list_dir()
#   File "/usr/local/bin/trasher", line 210, in list_dir
#     size_bytes = os.stat(os.path.join(tr_files, filename)).st_size
#                  ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# FileNotFoundError: [Errno 2] No such file or directory: '/home/v4h/.local/share/Trash/files/config.jsonc'

# TODO:
# this is due to config.jsonc being an empty symlink - removing the symlink from .local/share/Trash gets rid of the issue but doesnt fix it:
# is os library there is a section about symlinks, anyway - the .trashinfo still stayed behind, cant remember if it was just
# because i deleted the file in .local/share/Trash/files but whatever
# os.stat() is following the symlinka nd failing - os.lstat() in list_dir() is better - could wrap in a try/except also

# -r and -d uses find_trash(filename) for case insensitivity, but should pass the original filename to restore_file instead of match, like:
# if match:
#     restore_file(match)

# argparse should be inside main incase anything gets imported.

# ROOT
# a big issue is not being able tp trash items in the root directory - this is because the trash spec has different places for trash there,
# check trash spec for location, use something like os.stat().st_dev for device id of the files against the ones in the home dir, check for if trash is there
# and account for it. files owned by root will use something similar to delete_file() function. MOUNT-POINT DETETCION.

# DONE:
# changed format_size param to 'size' from 'bytes'
