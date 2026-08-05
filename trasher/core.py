#!/usr/bin/env python3
import os, shutil, subprocess, sys
from datetime import datetime
from urllib.parse import quote, unquote
from .utils import format_size, get_choice, print_box


tr_path = os.path.join(os.environ["HOME"], ".local/share/Trash")
tr_files = os.path.join(tr_path, "files")
tr_info = os.path.join(tr_path, "info")

# abspath is used when user types path to be deleted
def trash_file(filepath):
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

    try:
        shutil.move(fpath, coord)
        print(f" {fpath}")
    except Exception as e:
        os.remove(info_file)
        print(f"Failed to trash {fpath}: {e}")


def format_entry(i, filename):
    file_path = os.path.join(tr_files, filename)
    suffix = "(/)" if os.path.isdir(file_path) else ""
    size = format_size(os.lstat(file_path).st_size) #change for symlink error
    return f" {i}.) {filename}{suffix} - {size}"


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


# list directories and files in trash - turned into function to become cool
def list_dir():
    files = os.listdir(tr_files)
    if not files:
        print("\nTrash is empty... nothing to trash :(\n")
        sys.exit()

    print("Files in trash: ")
    print_box([format_entry(i, filename) for i, filename in enumerate(files, 1)])
    return files
