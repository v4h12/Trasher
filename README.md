# Trasher

## Meet Trasher

Trasher is a basic CLI program made with python that manages your trash and makes it simple.

## How to Install

- git clone <https://github.com/v4h12/Trasher>
- cd trasher
- chmod +x install.sh
- ./install.sh
- Then Bob's your uncle, you're ready to go!

## How it looks

~ trasher
Files in Trash:

1. Test-file.txt - 0.1B
2. Test-dir(/) - 2.3MB
3. Test-Movie.mp4 - 1.9GB
Restore or Delete files? (r/d): 'r'
Restore all files? (y/n): 'n'
Select number/s to restore: '1 2'
Restored Test-Movie.mpd4 to /home/user/Downloads/Movies
Restored Test-dir to /home/user/test/Test-dir

## The way it works

- Type 'trasher' into your terminal, the program will start and immediately list any files or directories in your trash.
- You can decide whether you want to restore or delete anything with 'r/d'.
- Either select all or individual files which are numbered within the list.
- Type in which number you'd like to restore or delete and hit enter to let Trasher do its thing!

**Note**
~ any files that are protected through root privileges or permissions can still be deleted and you will be prompted with your password when you are at that point.
Be careful doing this, any important files that you delete are at your own discretion.

**To Add:**

- I plan on adding a TUI version with the curses library... More to come.
- There is also a plan on adding in flags for more specific usage of Trasher
- Desktop use (ascii art)

**Inspiration**
This is my very first actual project that I have created from scratch, I have spent the past year learning python - having no previous coding experience. It has been quite the journey so far and quite the steep learning process - such as learning libraries I have never used and reading through docs, going through stackoverflow for the most basic issues and also just keeping up and remembering which part of your code does what. These projects are what I enjoy making - something useful, simple and fun!
In lieu of the many free resources I myself have used, i thought it would only be fitting to give something in return, regardless of how small it may be.

Please feel free to make any suggestions, pull requests or anything - it will all be appreciated.

**Additional Notes:**

- Created and Tested on Python 3.13.7
- Made using Arch Linux and designed for linux specific use
