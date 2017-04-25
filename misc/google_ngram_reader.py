#!python3

import os
import sys
import re


def readFile (spf):
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                yield sLine
    else:
        print("# Error: file not found.")


def countAndWriteFile (spf):
    print(spf)
    print("> counting...")
    d = {}
    i = 0
    for sLine in readFile(spf):
        sToken, sYear, sOccur, sBook = sLine.strip().split("\t")
        if sToken in d:
            d[sToken] = (d[sToken][0]+int(sOccur), d[sToken][1]+int(sBook))
        else:
            d[sToken] = (int(sOccur), int(sBook))
            i += 1
            print("> %d\r" % i, end="")
    
    with open(spf+".sum.txt", "w", encoding="utf-8", newline="\n") as hDst:
        print("> writing...")
        hDst.write("#Token\tsOccur\tnBook\n")
        for sToken, tVal in d.items():
            hDst.write(sToken + "\t" + str(tVal[0]) + "\t" + str(tVal[1]) + "\n")


def mergeFile (spf, hDst):
    print("merge: " + spf)
    d = {}
    for sLine in readFile(spf):
        if sLine.startswith("#"):
            continue
        sToken, sOccur, sBook = sLine.strip().split()
        if "_" in sToken:
            sToken = sToken[:sToken.find("_")]
        sToken = sToken.rstrip(".")
        if sToken.startswith(("l'", "d'", "s'", "m'", "t'", "n'", "j'", "c'", "ç'")):
            sToken = sToken[2:]
        elif sToken.startswith("qu'"):
            sToken = sToken[3:]
        if not sToken:
            continue
        if sToken not in d:
            d[sToken] = int(sOccur)
        else:
            d[sToken] = d[sToken] + int(sOccur)
    
    for k, v in d.items():
        hDst.write(k + " " + str(v) + "\n")


def main ():
    for sf in os.listdir("."):
        if not sf.endswith((".txt", ".", ".py")):
            countAndWriteFile(sf)
    
    with open("stats_google_ngram_5_2012.txt", "w", encoding="utf-8", newline="\n") as hDst:
        for sf in os.listdir("."):
            if sf.endswith(".sum.txt"):
                mergeFile(sf, hDst)
    
if __name__ == '__main__' :
    main()
