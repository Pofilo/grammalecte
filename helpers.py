"""
Tools for handling files
"""

import os
import shutil
import errno
import zipfile

from string import Template


def convertDictToString (dDict, nDepth=1, nIndent=2):
    "returns <dDict> as a indented string"
    sResult = "{\n"
    sIndent = " " * nIndent
    for key, val in dDict.items():
        sKey = f"'{key}'"  if type(key) is str  else str(key)
        if nDepth > 0 and type(val) is dict:
            sVal = convertDictToString(val, nDepth-1, nIndent+nIndent)
        else:
            sVal = f"'{val}'"  if type(val) is str  else str(val)
        sResult += f'{sIndent}{sKey}: {sVal},\n'
    sResult = sResult + sIndent[:-2] + "}"
    return sResult


class CD:
    "Context manager for changing the current working directory"
    def __init__ (self, newPath):
        self.newPath = os.path.expanduser(newPath)
        self.savedPath = ""

    def __enter__ (self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__ (self, etype, value, traceback):
        os.chdir(self.savedPath)


def unzip (spfZip, spDest, bCreatePath=False):
    "unzip file <spfZip> at <spfDest>"
    if spDest:
        if bCreatePath and not os.path.exists(spDest):
            os.makedirs(spDest, exist_ok=True)
        print("> unzip in: "+ spDest)
        spInstall = os.path.abspath(spDest)
        if os.path.isdir(spInstall):
            eraseFolderContent(spInstall)
            with zipfile.ZipFile(spfZip) as hZip:
                hZip.extractall(spDest)
        else:
            print("# folder <" + spDest + "> not found")
    else:
        print("path destination is empty")


def eraseFolderContent (sp):
    "erase content of a folder"
    for sf in os.listdir(sp):
        spf = os.path.join(sp, sf)
        try:
            if os.path.isfile(spf):
                os.unlink(spf)
            elif os.path.isdir(spf):
                shutil.rmtree(spf)
        except (OSError, shutil.Error) as e:
            print(e)


def createCleanFolder (sp):
    "make an empty folder or erase its content if not empty"
    if not os.path.exists(sp):
        os.makedirs(sp, exist_ok=True)
    else:
        eraseFolderContent(sp)


def copyFolder (spSrc, spDst):
    "copy folder content from src to dst"
    try:
        shutil.copytree(spSrc, spDst)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(spSrc, spDst)
        else:
            print("Error while copying folder <"+spSrc+"> to <"+spDst+">.")


def moveFolderContent (spSrc, spDst, sPrefix="", bLog=False):
    "move folder content from <spSrc> to <spDst>: if files already exist in <spDst>, they are replaced. (not recursive)"
    try:
        if not os.path.isdir(spSrc):
            print("Folder <"+spSrc+"> not found. Can’t move files.")
            return
        if not os.path.isdir(spDst):
            print("Folder <"+spDst+"> not found. Can’t move files.")
            return
        for sf in os.listdir(spSrc):
            spfSrc = os.path.join(spSrc, sf)
            if os.path.isfile(spfSrc):
                spfDst = os.path.join(spDst, sPrefix + sf)
                shutil.move(spfSrc, spfDst)
                if bLog:
                    print("file <" + spfSrc + "> moved to <"+spfDst+">")
    except Error as e:
        print("Error while moving folder <"+spSrc+"> to <"+spDst+">.")
        print(e)


def fileFile (spf, dVars):
    "return file <spf> as a text filed with variables from <dVars>"
    return Template(open(spf, "r", encoding="utf-8").read()).safe_substitute(dVars)


def copyAndFileTemplate (spfSrc, spfDst, dVars):
    "write file <spfSrc> as <spfDst> with variables filed with <dVars>"
    sText = Template(open(spfSrc, "r", encoding="utf-8").read()).safe_substitute(dVars)
    open(spfDst, "w", encoding="utf-8", newline="\n").write(sText)


def addFileToZipAndFileFile (hZip, spfSrc, spfDst, dVars):
    "add a file to zip archive and file it with <dVars>"
    if spfSrc.endswith((".txt", ".md", ".py", ".js", ".json", ".html", ".htm", ".css", ".xcu", ".xul", ".rdf", ".dtd", ".properties")):
        hZip.writestr(spfDst, fileFile(spfSrc, dVars))
    else:
        hZip.write(spfSrc, spfDst)


def addFolderToZipAndFileFile (hZip, spSrc, spDst, dVars, bRecursive):
    "add folder content to zip archive and file files with <dVars>"
    # recursive function
    spSrc = spSrc.strip("/ ")
    spDst = spDst.strip("/ ")
    for sf in os.listdir(spSrc):
        spfSrc = (spSrc + "/" + sf).strip("/ ")
        spfDst = (spDst + "/" + sf).strip("/ ")
        if os.path.isdir(spfSrc):
            if bRecursive:
                addFolderToZipAndFileFile(hZip, spfSrc, spfDst, dVars, bRecursive)
        else:
            addFileToZipAndFileFile(hZip, spfSrc, spfDst, dVars)
