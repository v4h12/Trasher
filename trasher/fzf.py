#!/usr/bin/env python3
import os, subprocess, sys
from .core import decog_path, delete_file, restore_file, tr_files, tr_info
from .utils import get_choice

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
            check=False,
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
        sys.exit(1)


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
