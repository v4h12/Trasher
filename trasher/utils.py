#!/usr/bin/env python3

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


# helper function for boxes
def print_box(lines):
    if not lines:
        return
    max_len = max(len(line) for line in lines)
    width = max_len + 1
    print("┌" + "─" * width + "┐")
    for line in lines:
        print(f"{line}{' ' * (max_len - len(line))}")
    print("└" + "─" * width + "┘")

