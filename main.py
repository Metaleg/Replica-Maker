import argparse
import filecmp
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from time import sleep
from signal import signal, SIGINT
from colorama import Fore


class ReplicaMaker:
    default_time = "0:0:30"
    format = "[%Y-%m-%d %H:%M:%S]"
    n = 0  # number of instances of this class
    sign_copy = Fore.GREEN + "[->]" + Fore.RESET
    sign_remove = Fore.RED + "[-]" + Fore.RESET
    sign_overwrite = Fore.BLUE + "[=>]" + Fore.RESET
    sign_add = Fore.YELLOW + "[+]" + Fore.RESET
    start_msg = Fore.MAGENTA + "Started synchronization" + Fore.RESET
    finish_msg = Fore.MAGENTA + "Finished synchronization" + Fore.RESET
    exit_msg = Fore.MAGENTA + "Execution has been interrupted\n" + Fore.RESET + "Have a nice day!"

    def __new__(cls):
        """Used for a singleton"""
        if cls.n == 0:
            cls.n += 1
            return object.__new__(cls)

    def __init__(self):
        self.src_path = None
        self.dst_path = None
        self.log_path = None
        self.time = None
        self.log_descriptor = None

    def sigint_handler(self, sig, frame):
        now = datetime.now()
        print(end='\r')
        if self.log_descriptor.closed:
            self.log_descriptor = open(self.log_path, 'a')

        self.log_descriptor.write(f"{now.strftime(self.format)} Execution has been interrupted\n")
        self.log_descriptor.close()
        print(f"{now.strftime(self.format)}", self.exit_msg, sep=' ')
        exit()

    def get_args(self):
        parser = argparse.ArgumentParser(description="This program periodically makes a replica of a given folder. "
                                                     "Press 'CTRL+C' to finish")
        parser.add_argument("src", help="You need to set up a source directory")
        parser.add_argument("dst", help="You need to set up a replica's directory")
        parser.add_argument("log", help="You need to set up a log directory")
        parser.add_argument("-t", "--time", default=self.default_time,
                            help="You can set up an interval between making a copy in format H:M:S, "
                                 "the default value is 30 seconds")
        args = parser.parse_args()

        self.src_path = args.src
        self.dst_path = args.dst
        self.log_path = args.log
        self.time = args.time

    def get_seconds(self):
        ftr = [3600, 60, 1]
        return sum([a * b for a, b in zip(ftr, map(int, self.time.split(':')))])

    def make_replica(self):
        signal(SIGINT, self.sigint_handler)
        if not Path(self.src_path).exists():
            print("Source directory doesn't exist! Please, specify another directory.")
            exit()
        if Path(self.dst_path).exists() and not os.path.isdir(self.dst_path):
            print("Wrong replica's directory. Please, specify another directory.")
            exit()

        while True:
            self.log_descriptor = open(self.log_path, 'a')
            now = datetime.now()
            self.log_descriptor.write(f"{now.strftime(self.format)} STARTED SYNCHRONIZATION\n")
            print(f"{now.strftime(self.format)}", self.start_msg, sep=' ')
            if not Path(self.dst_path).exists():
                os.mkdir(self.dst_path)
                self.log_descriptor.write(f"{now.strftime(self.format)} [+] Added replica's directory\n")
                print(f"{now.strftime(self.format)}", self.sign_add, "Added replica's directory", sep=' ')
            self._compare_directories(self.src_path, self.dst_path)
            now = datetime.now()
            self.log_descriptor.write(f"{now.strftime(self.format)} FINISHED SYNCHRONIZATION\n")
            print(f"{now.strftime(self.format)}", self.finish_msg, sep=' ')
            self.log_descriptor.close()

            seconds_total = self.get_seconds()
            for i in range(seconds_total):
                print("Next synchronization in:", str(timedelta(seconds=seconds_total - i)), sep=' ', end='\r')
                sleep(1)

    def _compare_directories(self, left, right):
        cmp = filecmp.dircmp(left, right)
        if cmp.common_dirs:
            for d in cmp.common_dirs:
                self._compare_directories(os.path.join(left, d), os.path.join(right, d))
        if cmp.left_only:
            self._copy(left, right, *cmp.left_only)
        if cmp.right_only:
            self._remove(right, *cmp.right_only)
        if cmp.diff_files:
            self._overwrite(left, right, *cmp.diff_files)

    def _copy(self, src, dst, *items, overwrite=False):
        for item in items:
            path = os.path.join(src, item)
            if os.path.isdir(path):
                shutil.copytree(path, os.path.join(dst, item))
            else:
                shutil.copy2(path, dst)
            if not overwrite:
                now = datetime.now()
                self.log_descriptor.write(f"{now.strftime(self.format)} [->] Copied {path}\n")
                print(f"{now.strftime(self.format)}", self.sign_copy, f"Copied {path}", sep=' ')

    def _remove(self, path, *items, overwrite=False):
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.unlink(item_path)
            now = datetime.now()
            if not overwrite:
                self.log_descriptor.write(f"{now.strftime(self.format)} [-] Removed {item_path}\n")
                print(f"{now.strftime(self.format)}", self.sign_remove, f"Removed {item_path}", sep=' ')
            else:
                self.log_descriptor.write(f"{now.strftime(self.format)} [=>] Overwritten {item_path}\n")
                print(f"{now.strftime(self.format)}", self.sign_overwrite, f"Overwritten {item_path}", sep=' ')

    def _overwrite(self, src, dst, *items):
        for item in items:
            self._remove(dst, item, overwrite=True)
            self._copy(src, dst, item, overwrite=True)


def main():
    r = ReplicaMaker()
    r.get_args()
    r.make_replica()


if __name__ == '__main__':
    main()
