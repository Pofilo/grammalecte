# Useful tools

import os
import shutil
import zipfile

from string import Template


class cd:
    "Context manager for changing the current working directory"
    def __init__ (self, newPath):
        self.newPath = os.path.expanduser(newPath)

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
            eraseFolder(spInstall)
            with zipfile.ZipFile(spfZip) as hZip:
                hZip.extractall(spDest)
        else:
            print("# folder not found")
    else:
        print("path destination is empty")


def eraseFolder (sp):
    "erase content of a folder"
    for sf in os.listdir(sp):
        spf = os.path.join(sp, sf)
        try:
            if os.path.isfile(spf):
                os.unlink(spf)
            elif os.path.isdir(spf):
                shutil.rmtree(spf)
        except Exception as e:
            print(e)


def createCleanFolder (sp):
    "make an empty folder or erase its content if not empty"
    if not os.path.exists(sp):
        os.makedirs(sp, exist_ok=True)
    else:
        eraseFolder(sp)


def fileFile (spf, dVars):
    "return file <spf> as a text filed with variables from <dVars>"
    return Template(open(spf, "r", encoding="utf-8").read()).safe_substitute(dVars)


def copyAndFileTemplate (spfSrc, spfDst, dVars):
    "write file <spfSrc> as <spfDst> with variables filed with <dVars>"
    s = Template(open(spfSrc, "r", encoding="utf-8").read()).safe_substitute(dVars)
    open(spfDst, "w", encoding="utf-8", newline="\n").write(s)


def addFolderToZipAndFileFile (hZip, spSrc, spDst, dVars, bRecursive):
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
            if spfSrc.endswith((".css", ".js", ".xcu", ".xul", ".rdf", ".dtd", ".properties")):
                #print(spfSrc + " > " + spfDst)
                hZip.writestr(spfDst, fileFile(spfSrc, dVars))
            else:
                #print(spfSrc + " > " + spfDst)
                hZip.write(spfSrc, spfDst)
