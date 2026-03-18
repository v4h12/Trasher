from datetime import datetime
from urllib.parse import quote


def trash_file(filepath):
    src = os.path.abspath(filepath)
    if not os.path.exists(src):
        print(f"Cannot trash {filepath}: file or directory not found")
        return

    filename = os.path.basename(src)
    dest = os.path.join(tr_files, filename)
    info_file = os.path.join(tr_info, filename + ".trashinfo")

    # handle name collisions
    counter = 1
    while os.path.exists(dest) or os.path.exists(info_file):
        name, ext = os.path.splitext(filename)
        new_name = f"{name}_{counter}{ext}"
        dest = os.path.join(tr_files, new_name)
        info_file = os.path.join(tr_info, new_name + ".trashinfo")
        counter += 1

    # write .trashinfo before moving
    deletion_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(info_file, "w") as f:
        f.write("[Trash Info]\n")
        f.write(f"Path={quote(src, safe='/')}\n")
        f.write(f"DeletionDate={deletion_date}\n")

    try:
        shutil.move(src, dest)
        print(f" Trashed {filename}")
    except Exception as e:
        os.remove(info_file)
        print(f"Failed to trash {filename}: {e}")
