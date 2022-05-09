# Replica-Maker

A program that synchronizes two folders: source and replica.
The program maintain a full, identical copy of destination folder at replica folder.
    • Synchronization works in one-way;
    • Synchronization performes periodically;
    • File creation/copying/removal operations are logging to a file and to the console output;
    • Folder paths, synchronization interval and log file path provide by the command line arguments.

## Usage:
usage: main.py [-h] [-t TIME] src dst log

positional arguments:
  src                   You need to set up a source directory
  dst                   You need to set up a replica's directory
  log                   You need to set up a log directory

options:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  You can set up an interval between making a copy, the default value is 3 minutes
