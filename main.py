import argparse
import filecmp
import os
import shutil
from pathlib import Path
import datetime
from tqdm import tqdm
from time import sleep


class ReplicaMaker:
    default_time = 180
    format = "[%Y-%m-%d %H:%M:%S]"

    def __init__(self):
        self.src_path = None
        self.dst_path = None
        self.log_path = None
        self.time = None
        self.descriptor = None

    def get_args(self):
        parser = argparse.ArgumentParser(description="This program periodically makes a replica of a given folder.")
        parser.add_argument("src", help="You need to set up a source directory")
        parser.add_argument("dst", help="You need to set up a replica's directory")
        parser.add_argument("log", help="You need to set up a log directory")
        parser.add_argument("-t", "--time", default=self.default_time,
                            help="You can set up an interval between making a copy, the default value is 3 minutes")
        args = parser.parse_args()

        self.src_path = args.src
        self.dst_path = args.dst
        self.log_path = args.log
        self.time = int(args.time)

    def make_replica(self):
        if not Path(self.src_path).exists():
            print("Source directory doesn't exist! Please, specify another directory.")
            exit()
        if Path(self.dst_path).exists() and not os.path.isdir(self.dst_path):
            print("Wrong replica's directory. Please, specify another directory.")
            exit()

        while True:
            self.descriptor = open(self.log_path, 'a')
            now = datetime.datetime.now()
            self.descriptor.write(f"{now.strftime(self.format)} [STARTED SYNCHRONIZATION]\n")
            print(f"{now.strftime(self.format)} [STARTED SYNCHRONIZATION]")
            if not Path(self.dst_path).exists():
                os.mkdir(self.dst_path)
                self.descriptor.write(f"{now.strftime(self.format)} [+] Added replica's directory")
                print(f"{now.strftime(self.format)} [+] Added replica's directory")
            self._compare_directories(self.src_path, self.dst_path)
            now = datetime.datetime.now()
            self.descriptor.write(f"{now.strftime(self.format)} [FINISHED SYNCHRONIZATION]\n")
            print(f"{now.strftime(self.format)} [FINISHED SYNCHRONIZATION]")
            self.descriptor.close()

            with tqdm(total=self.time) as pbar:
                for i in range(self.time):
                    sleep(1)
                    pbar.update(1)

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
                now = datetime.datetime.now()
                self.descriptor.write(f"{now.strftime(self.format)} [->] Copied {path}\n")
                print(f"{now.strftime(self.format)} [->] Copied {path}")

    def _remove(self, path, *items, overwrite=False):
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.unlink(item_path)
            now = datetime.datetime.now()
            if not overwrite:
                self.descriptor.write(f"{now.strftime(self.format)} [-] Removed {item_path}\n")
                print(f"{now.strftime(self.format)} [-] Removed {item_path}")
            else:
                self.descriptor.write(f"{now.strftime(self.format)} [=>] Overwritten {item_path}\n")
                print(f"{now.strftime(self.format)} [=>] Overwritten {item_path}")

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
