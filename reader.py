#!python3
# Just a file for one-shot scripts

import os
import sys
import re

import grammalecte.ibdawg as ibdawg

oDict = ibdawg.IBDAWG("French.bdic")


def readFile (spf):
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                yield sLine
    else:
        print("# Error: file not found.")

# --------------------------------------------------------------------------------------------------

def listUnknownWords (spf):
    with open(spf+".res.txt", "w", encoding="utf-8") as hDst:
        for sLine in readFile(spfSrc):
            sLine = sLine.strip()
            if sLine:
                for sWord in sLine.split():
                    if not oDict.isValid(sWord): 
                        hDst.write(sWord+"\n")

# --------------------------------------------------------------------------------------------------

def createLexStatFile (spf, dStat):
    dWord = {}
    for i, sLine in enumerate(readFile(spf)):
        if not sLine.startswith("#"):
            sWord = sLine.strip()
            if sWord not in dWord:
                dWord[sWord] = dStat.get(sWord, 0)
        print(i, end="\r")

    with open(spf+".res.txt", "w", encoding="utf-8") as hDst:
        for sWord, nVal in sorted(dWord.items(), key=lambda x: (x[1], x[0]), reverse=True):
            if not oDict.isValid(sWord):
                hDst.write(sWord + " " + str(nVal) + "\n")


def readStatFile (spf, dStat):
    print("read stats: " + spf)
    for sLine in readFile(spf):
        if not sLine.startswith("#"):
            sWord, sCount = sLine.split()
            dStat[sWord] = dStat.get(sWord, 0) + int(sCount)
    return dStat


def readStatFilesAndCreateLexicon ():
    dStat = {}
    readStatFile("stats1.txt", dStat)
    readStatFile("stats2.txt", dStat)
    readStatFile("stats3.txt", dStat)
    createLexStatFile("propositions.txt", dStat)

# --------------------------------------------------------------------------------------------------

def isMoreThanOneSetInList (lSet):
    aFirst = lSet.pop(0)
    for aSet in lSet:
        if aSet != aFirst:
            return True
    return False

def filterLinesWithWordsWithDifferentStems (spf):
    with open(spf+".res.txt", "w", encoding="utf-8") as hDst:
        for sLine in readFile(spf):
            lStemSet = [ set(oDict.stem(sWord))  for sWord in sLine.strip().split()]
            if isMoreThanOneSetInList(lStemSet):
                hDst.write(sLine)

def filterHomophonicWords ():
    filterLinesWithWordsWithDifferentStems("homophones.txt")

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__' :
    filterHomophonicWords()