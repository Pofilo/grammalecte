# Python

import os
import argparse
import sys
import shutil

import helpers


def getFolders (sp):
    for sf in os.listdir(sp):
        if os.path.isdir(sp+"/"+sf):
            yield from getFolders(sp+"/"+sf)
            yield (sf, sp+"/"+sf)


def purge (sFolderName, bDeleteContentOnly):
    for sf, sp in getFolders("."):
        if sf == sFolderName:
            if bDeleteContentOnly:
                helpers.eraseFolderContent(sp)
                print(sp, "[content deleted]")
            else:
                shutil.rmtree(sp)
                print(sp, "[erased]")


def main ():
    "purge cruft and other files"
    print("Python: " + sys.version)
    if sys.version < "3.7":
        print("Python 3.7+ required")
        return

    xParser = argparse.ArgumentParser()
    xParser.add_argument("-b", "--build", help="purge _build", action="store_true")
    xArgs = xParser.parse_args()

    purge("__pycache__", False)
    if xArgs.build:
        purge("_build", True)


if __name__ == '__main__':
    main()
