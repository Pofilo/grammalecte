# Thesaurus builder

import os
import re


def readFile (spf):
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                yield sLine.strip()
    else:
        print("# Error. File not found or not loadable: " + spf)



class ThesaurusBuilder ():

    def __init__ (self):
        # synsets
        self.dSynEntry = {}     # {sWord: iSynset}
        self.dSynset = {}       # {iSynset: lSynset}
        # thesaurus
        self.dThesEntry = {}    # {sWord: lWord}

    def readSynsets (self, spf):
        if not spf:
            return
        for i, sLine in enumerate(readFile(spf), 1):
            sPOS, *lSynset = sLine.split("|")
            lSynset = self._removeDuplicatesFrom(lSynset)
            self.dSynset[i] = lSynset
            for sWord in lSynset:
                if not sWord.endswith("*"):
                    if "(" in sWord:
                        sWord = re.sub("\\(.*\\)", "", sWord).strip()
                    if sWord not in self.dSynEntry:
                        self.dSynEntry[sWord] = [ (sPOS, i) ]
                    else:
                        self.dSynEntry[sWord].append( (sPOS, i) )

    def showSynsetEntries (self):
        for sWord, lSynset in self.dSynEntry.items():
            for sPOS, iSynset in lSynset:
                print(sWord, sPOS, "|".join(self.dSynset[iSynset]))

    def readThesaurus (self, spf):
        if not spf:
            return
        genRead = readFile(spf)
        sLine1 = next(genRead)
        sEntry = ""
        iEntryLine = 0
        nClass = 0
        nClassFound = 0
        for i, sLine in enumerate(genRead, 2):
            sLine = sLine.strip()
            if re.search(r"^[^|]+\|[1-9][0-9]*$", sLine):
                # new entry
                if nClass != nClassFound:
                    print("Ligne:", iEntryLine, ", nombre de liste incorrect")
                iEntryLine = i
                sEntry, sNum = sLine.split("|")
                self.dThesEntry[sEntry] = []
                nClass = int(sNum)
                nClassFound = 0
            else:
                # new list of synonyms
                nClassFound += 1
                sPOS, *lClass = sLine.split("|")
                lClass = self._removeDuplicatesFrom(lClass)
                self.dThesEntry[sEntry].append( (sPOS, lClass) )

    def showThesaurusEntries (self):
        for sWord, lClass in self.dThesEntry.items():
            for sPOS, lWord in lClass:
                print(sWord, sPOS, "|".join(lWord))

    def _removeDuplicatesFrom (self, lWord):
        return [ sWord.strip()  for sWord  in dict.fromkeys(lWord) ]  # remove duplicates: use <dict.fromkeys()> instead of <set()> to keep order

    def merge (self):
        for sWord, lSynset in self.dSynEntry.items():
            for sPOS, iSynset in lSynset:
                if sWord in self.dThesEntry:
                    self.dThesEntry[sWord].append( (sPOS, self.dSynset[iSynset]) )
                else:
                    self.dThesEntry[sWord] = [ (sPOS, self.dSynset[iSynset]) ]

    def write (self, spDest):
        nOffset = 0     # the offset for finding data is the number of bytes (-> encoding("utf-8"))
        dOffset = {}
        with open(spDest + "/thes_fr.dat", "w", encoding="utf-8", newline="\n") as hThes:
            sHeader = "UTF-8\n"
            hThes.write(sHeader)
            nOffset = len(sHeader.encode("utf-8"))
            for sWord, lClass in self.dThesEntry.items():
                dOffset[sWord] = nOffset
                sWordLine = sWord+"|"+str(len(lClass))+"\n"
                hThes.write(sWordLine)
                nOffset += len(sWordLine.encode("utf-8"))
                for sPOS, lWord in lClass:
                    sClassLine = sPOS+"|"+"|".join(lWord)+"\n"
                    hThes.write(sClassLine)
                    nOffset += len(sClassLine.encode("utf-8"))
        with open(spDest + "/thes_fr.idx", "w", encoding="utf-8", newline="\n") as hIndex:
            hIndex.write("UTF-8\n")
            hIndex.write(str(len(self.dThesEntry))+"\n")
            for sWord, nOffset in sorted(dOffset.items()):
                hIndex.write(sWord+"|"+str(nOffset)+"\n")


def build (spfThesaurus="", spfSynsets="", spDest="_build"):
    oThes = ThesaurusBuilder()
    oThes.readSynsets(spfSynsets)
    #oThes.showSynsetEntries()
    oThes.readThesaurus(spfThesaurus)
    #oThes.showThesaurusEntries()
    oThes.merge()
    oThes.write(spDest)


if __name__ == '__main__':
    build("thesaurus/thes_fr.dat", "thesaurus/synsets_fr.dat")
