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


CHARMAP = str.maketrans({ '(': ' ',  ')': ' ',  '[': ' ',  ']': ' ',  '{': ' ',  '}': ' ',  '+': ' ',
                          '/': ' ',  '<': ' ',  '>': ' ',  '*': ' ',  '@': ' ',  '?': ' ',  '?': ' ',
                          '«': ' ',  '»': ' ',  '"': ' ',  '“': ' ',  '”': ' ',  ':': ' ',  ',': ' ',
                          ';': ' ',  '?': ' ',  '!': ' ',  '&': ' ',  '=': ' ',  '%': ' ',  '#': ' ',
                          '$': ' ',  '~': ' ',  '…': ' ',  '`': ' ',  '|': ' ',  '—': ' ',  '–': ' ',
                          "’": "'",  '\\': ' ' })


def cleanLine (sLine):
    sLine = sLine.replace("&lt;", "<").replace("&gt;", ">")
    sLine = re.sub("<sha1>[a-z0-9]+</sha1>", " ", sLine)
    sLine = re.sub("<timestamp>[0-9:TZ -]+</timestamp>", " ", sLine)
    sLine = re.sub("</?[a-z]+>", " ", sLine)
    sLine = re.sub("&[a-z]+;", " ", sLine)
    sLine = sLine.replace("-t-", " ")
    sLine = re.sub("-(je|tu|ils?|elles?|nous|vous|on|l[àae]s?)\\b", " \\1", sLine)
    sLine = sLine.translate(CHARMAP)
    sLine = re.sub(" ([nldmtsjcçNLDMTSJCÇ])'", " \\1e ", sLine)
    sLine = re.sub("^([nldmtsjcçNLDMTSJCÇ])'", " \\1e ", sLine)
    sLine = re.sub(" ([çÇ])'", " \\1a ", sLine)
    sLine = re.sub("^([çÇ])'", " \\1a ", sLine)
    sLine = re.sub("(?i)puisqu'", "puisque ", sLine)
    sLine = re.sub("(?i)lorsqu'", "lorsque ", sLine)
    sLine = re.sub("(?i)quoiqu'", "quoique ", sLine)
    sLine = re.sub("(?i)jusqu'", "jusque ", sLine)
    sLine = re.sub("(?i)\\bqu'", "que ", sLine)
    sLine = re.sub("''+", " ", sLine)
    sLine = re.sub("--+", " ", sLine)
    sLine = re.sub("[.]+", " ", sLine)
    return sLine


def isWordAcceptable (sWord, n=7):
    return len(sWord) < 41 and not sWord.startswith(("-", "_", "–", "—", "'", "’")) \
            and not ("-" in sWord and sWord.count("-") > 4) \
            and not ("_" in sWord and sWord.count("_") > 4) \
            and not re.match("[0-9].+[_-]", sWord) \
            and not re.search("[0-9]{4,}", sWord) \
            and not (len(sWord) > 6 and re.search("[a-zA-Z]\\d[a-zA-Z]|\\d[a-zA-Z]\\d", sWord)) \
            and not re.match("[0-9_-]+$", sWord) \
            and not re.search("[\u0400-\u07BF]", sWord) \
            and not (n <= 3 and not re.match("[a-zA-Zà-öÀ-Ö_-]+$", sWord))


def cleanText (spf):
    with open(spf+".purged.txt", "w", encoding="utf-8", newline="\n") as hDst:
        for i, sLine in enumerate(readFile(spf)):
            hDst.write(cleanLine(sLine))
            if not (i % 1000):
                print(i, end="\r")


def countWord (spf):
    d = {}
    for i, sLine in enumerate(readFile(spf)):
        for sWord in cleanLine(sLine).split():
            if isWordAcceptable(sWord):
                d[sWord] = d.get(sWord, 0) + 1
        if not (i % 1000):
            print(i, end="\r")
    with open("stats_"+spf+".txt", "w", encoding="utf-8", newline="\n") as hDst:
        for sWord, nVal in sorted(d.items(), key=lambda x: (x[1], x[0]), reverse=True):
            hDst.write(sWord + " " + str(nVal) + "\n")


def purgeWords (spf):
    lTuple = []
    for i, sLine in enumerate(readFile(spf)):
        sWord, sCount = sLine.split()
        if isWordAcceptable(sWord, int(sCount)):
            lTuple.append((sWord, int(sCount)))
        if not (i % 1000):
            print(i, end="\r")

    lTuple.sort(key=lambda x: (x[1], x[0]), reverse=True)
    with open(spf+".purgedlist.txt", "w", encoding="utf-8", newline="\n") as hDst:
        for sWord, nVal in lTuple:
            hDst.write(sWord + "\t" + str(nVal) + "\n")


def main ():
    #cleanText(sys.argv[1])
    #countWord(sys.argv[1])
    purgeWords(sys.argv[1])


if __name__ == '__main__' :
    main()
