import os
import shutil
import subprocess
from pyfzf.pyfzf import FzfPrompt
from urllib.parse import unquote

"""
this file is a version of fzf using the pyfzf library which was the original
code for main.py (trasher) but i opted for using the subprocess library instead 
since pyfzf is a wrapped library and would only run in a venv

all this is really is my code which is imported from main.py in order to conviniently run
this file

credit to nk412 on github
here's the link to the repo: https://github.com/nk412/pyfzf
 - be sure to give him a star
"""

fzf = FzfPrompt()
tr_path = os.path.join(os.environ["HOME"], ".local/share/Trash")
tr_files = os.path.join(tr_path, "files")
tr_info = os.path.join(tr_path, "info")


def decog_path(info_file):
    if not os.path.exists(info_file):
        return None
    with open(info_file) as f:
        for line in f:
            if line.startswith("Path="):
                return unquote(line.strip().split("=", 1)[1])
    return None


def restore_file(filename):
    trash_file = os.path.join(tr_files, filename)
    info_file = os.path.join(tr_info, filename + ".trashinfo")
    og_path = decog_path(info_file)

    if not og_path:
        print(f"Cannot restore {filename}: missing path or possibly missing .trashinfo")
        return

    os.makedirs(os.path.dirname(og_path), exist_ok=True)
    os.rename(trash_file, og_path)
    os.remove(info_file)

    print(f" Restored {filename} to {og_path}")


def get_choice(prompt, valid_options):
    while True:
        choice = input(prompt).lower()
        if choice in valid_options:
            return choice
        print("Invalid Input")


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


def fzf_path():
    mapping = {}

    for filename in os.listdir(tr_files):
        info_file = os.path.join(tr_info, filename + ".trashinfo")
        og_path = decog_path(info_file)
        if og_path:
            mapping[og_path] = filename
    return mapping


def fzf_choice(rawdata):
    data = fzf.prompt(rawdata, fzf_options="--reverse --multi")
    return data


if __name__ == "__main__":
    try:
        mapping = fzf_path()
        choices = fzf_choice(list(mapping.keys()))
        if not choices or choices == [""]:
            print("\nNothing selected")

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

    except KeyboardInterrupt:
        print("\n\n... Quitting trasher")
        exit(0)

"""
remember this code can only be used with a venv in python,
it is of course possible to use the subprocess library to call fzf
within this file as well but it took too long to write this and figure it out 
to just delete it, so its here for you to do what you want.
"""
