```
   ████████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗ 
   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
      ██║   ██████╔╝███████║███████╗███████║█████╗  ██████╔╝
      ██║   ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██╔══██╗
      ██║   ██║  ██║██║  ██║███████║██║  ██║███████╗██║  ██║
      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

## Meet Trasher

Trasher is a basic CLI program made with python that manages your trash and makes it simple.

## How to Install

```bash
- git clone <https://github.com/v4h12/Trasher>
- cd trasher
- chmod +x install.sh
- ./install.sh
```

Then Bob's your uncle, you're ready to go!

## How it looks

```bash
$ trasher
Files in Trash:
┌───────────────────────────────────────────────────────┐
 1.) test1 - 0.0B
 2.) test2 - 0.0B
 3.) anothertest - 0.0B
 4.) test3 - 0.0B
 5.) testa - 0.0B
└───────────────────────────────────────────────────────┘

Restore or Delete files? (r/d): r

Restore all files? (y/n): n

Select number/s to restore: 1 2 4

┌───────────────────────────────────────────────────────┐
 Restored test1 to /home/v4h/test-dir/test
 Restored test2 to /home/v4h/test-dir/test2
 Restored test3 to /home/v4h/test-dir/test3
└───────────────────────────────────────────────────────┘
```

## The way it works

- Type 'trasher' into your terminal, the program will start and immediately list any files or directories in your trash.
- You can decide whether you want to restore or delete anything with 'r/d'.
- Either select all or individual files which are numbered within the list.
- Type in which number you'd like to restore or delete and hit enter to let Trasher do its thing!

**Note**
~ any files that are protected through root privileges or permissions can still be deleted and you will be prompted with your password when you are at that point.
Be careful doing this, any important files that you delete are at your own discretion.

## Inspiration

This is my very first project that I have created from scratch, I have spent the past year learning python - having no previous coding experience. It has been quite the journey so far and quite the steep learning process - such as learning libraries I have never used and reading through docs, going through StackOverFlow for the most basic issues and also just keeping up and remembering which part of your code does what. These projects are what I enjoy making - something useful, simple and fun!
In lieu of the many free resources I myself have used, i thought it would only be fitting to give something in return, regardless of how small it may be.

Please feel free to make any suggestions, pull requests or anything - it will all be appreciated.

##

**To Add:**

- Desktop use (ascii art)
- Restore and delete files using fzf + multi-select (includes trashing files from anywhere)
- I plan on adding a TUI version with the curses library... More to come.

**Additional Notes:**

- Created and Tested on Python 3.13.7
- Made using Arch Linux and designed for Linux specific use
