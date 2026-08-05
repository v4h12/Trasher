#!/usr/bin/env python3
import argparse, os, sys
from . import __version__
from .core import trash_file, delete_file, list_dir, restore_file, tr_files, tr_info
from .fzf import fzf_opt
from .utils import get_choice, get_file_num
try:
    import argcomplete
except ImportError as e:
    print(f"Argcomplete not found {e}")


def interactive_mode():

    try:
        # this is used to call the list_dir function (originally not a function)
        files = list_dir()

        # user input
        what = get_choice("\nRestore or Delete files? (r/d): ", ["r", "d"])

        # if you chose 'r' to restore files
        if what == "r":
            resaf = get_choice("\nRestore all files? (y/n): ", ["y", "n"])
            if resaf == "y":
                # print("\n" + "┌" + "─" * 55 + "┐")
                for filename in os.listdir(tr_files):
                    restore_file(filename)
                # print("└" + "─" * 55 + "┘")

            elif resaf == "n":
                indices = get_file_num("\nSelect number/s to restore: ", len(files))
                # print("\n" + "┌" + "─" * 55 + "┐")
                for index in indices:
                    restore_file(files[index])
                # print("└" + "─" * 55 + "┘")

        # if you choose 'd' to delete files
        elif what == "d":
            delaf = get_choice("\nDelete all files? (y/n): ", ["y", "n"])
            if delaf == "y":
                # print("\n" + "┌" + "─" * 55 + "┐")
                for filename in os.listdir(tr_files):
                    delete_file(filename)
                # print("└" + "─" * 55 + "┘")

            elif delaf == "n":
                indices = get_file_num("\nSelect number/s to delete: ", len(files))
                # print("\n" + "┌" + "─" * 55 + "┐")
                for index in indices:
                    delete_file(files[index])
                # print("└" + "─" * 55 + "┘")

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher\n")
        sys.exit(0)

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


def main():
    parser = argparse.ArgumentParser(
        prog="trasher",
        usage="trasher [OPTION]... [FILE]...",
        description="Your CLI trash manager, Trasher",
    )

    parser.add_argument("files", metavar="Files", nargs="*", help=" ")

    parser.add_argument(
        "-n",
        "--numbered",
        action="store_true",
        help="list all files and restore/delete from numbered list",
    )

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

    # parser.add_argument(
    #     "-t",
    #     "--trash",
    #     metavar="[FILE]",
    #     nargs="+",
    #     help="trash a file or directory",
    # )

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

    # trasher -n or --numbered
    if args.numbered:
        interactive_mode()
        return

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
                return

        except KeyboardInterrupt:
            print("\n\n... Quitting trasher")

        return

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
                return

        except KeyboardInterrupt:
            print("\n\n... Quitting trasher")

        return

    if args.restore:
        print("\n┌" + "─" * 55 + "┐")
        for filename in args.restore:
            match = find_trash(filename)
            if match:
                restore_file(match)  # check
            else:
                print(f" '{filename}' not found in trash.")
        print("└" + "─" * 55 + "┘")
        return

    if args.delete:
        print("\n┌" + "─" * 55 + "┐")
        for filename in args.delete:
            match = find_trash(filename)
            if match:
                delete_file(match)  # check
            else:
                print(f" '{filename}' not found in trash.")
        print("└" + "─" * 55 + "┘")
        return

    # if args.trash:
        # print("\n┌" + "─" * 55 + "┐")
        # print("Trashed:")
        # for filepath in args.trash:
            # decimate_file(filepath)
        # print("└" + "─" * 55 + "┘")
        # return

    # trasher --version
    if args.version:
        print(f"""Trasher {__version__} - (Pre-Release)
    Github repo: https://github.com/v4h12/trasher\n
    Copyright (C) 2026 Free Software Foundation, Inc. <https://fsf.org/>
    License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law
    """)
        return

    # TODO:
    # for files in root, "sudo trasher -v" is needed else theres is errno 2 for it cannot read it
    # this makes me believe 'trasher -t' is not explicit enough due to not trashing items in the correct place
    if args.verbose:
        for filename in args.verbose:
            match = find_trash(filename)
            if match:
                info_file = os.path.join(tr_info, match + ".trashinfo")
                with open(info_file) as file:
                    print(file.read())

                # print(open(info_file).read())

            else:
                print(f" '{filename}' not found in trash.")
        return

    if args.verbose_all:
        for filename in os.listdir(tr_info):
            info_file = os.path.join(tr_info, filename)
            with open(info_file) as file:
                print(file.read())

            # print(open(info_file).read())

        return

    # trasher -l or --list | (TODO) add date and time (wip)
    if args.list:
        list_dir()
        return

    if args.fzf:
        if not os.listdir(tr_files):
            print("\ntrash is empty, nothing to trash :( \n")
        else:
            fzf_opt()
        return

    if args.files:
        print("Trashed:")
        for filepath in args.files:
            trash_file(filepath) #print help
        return
