# Replica-Maker

A program that synchronizes two folders: source and replica.
The program maintain a full, identical copy of destination folder at replica folder.

    1. Synchronization works in one-way.    
    2. Synchronization performes periodically.
    3. File creation/copying/removal operations are logging to a file and to the console output.
    4. Folder paths, synchronization interval and log file path provide by the command line arguments.

## Requirements
colorama

## Usage:
main.py [-h] [-t TIME] src dst log

    Press CTRL+C to interrupt an execution

Positional arguments:
* ```src``` - You need to set up a source directory
* ```dst``` - You need to set up a replica's directory
* ```log``` - You need to set up a log directory

Options:
* ```-h, --help``` - show this help message and exit
* ```-t TIME, --time TIME``` - You can set up an interval between making a copy in format H:M:S, the default value is 30 seconds
