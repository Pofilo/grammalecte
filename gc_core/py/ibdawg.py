#!python3

import os
import traceback
import pkgutil
import re
from itertools import chain

from . import str_transform as st
from . import char_player as cp
from .echo import echo


def show (nDeep, sText):
    print(nDeep * "  " + sText)


class IBDAWG:
    """INDEXABLE BINARY DIRECT ACYCLIC WORD GRAPH"""

    def __init__ (self, sDicName):
        self.by = pkgutil.get_data(__package__, "_dictionaries/" + sDicName)
        if not self.by:
            raise OSError("# Error. File not found or not loadable: "+sDicName)

        if self.by[0:7] != b"/pyfsa/":
            raise TypeError("# Error. Not a pyfsa binary dictionary. Header: {}".format(self.by[0:9]))
        if not(self.by[7:8] == b"1" or self.by[7:8] == b"2" or self.by[7:8] == b"3"):
            raise ValueError("# Error. Unknown dictionary version: {}".format(self.by[7:8]))
        try:
            header, info, values, bdic = self.by.split(b"\0\0\0\0", 3)
        except Exception:
            raise Exception

        self.sName = sDicName
        self.nVersion = int(self.by[7:8].decode("utf-8"))
        self.sHeader = header.decode("utf-8")
        self.lArcVal = values.decode("utf-8").split("\t")
        self.nArcVal = len(self.lArcVal)
        self.byDic = bdic

        l = info.decode("utf-8").split("/")
        self.sLang = l[0]
        self.nChar = int(l[1])
        self.nBytesArc = int(l[2])
        self.nBytesNodeAddress = int(l[3])
        self.nEntries = int(l[4])
        self.nNode = int(l[5])
        self.nArc = int(l[6])
        self.nAff = int(l[7])
        self.cStemming = l[8]
        if self.cStemming == "S":
            self.funcStemming = st.changeWordWithSuffixCode
        elif self.cStemming == "A":
            self.funcStemming = st.changeWordWithAffixCode
        else:
            self.funcStemming = st.noStemming
        self.nTag = self.nArcVal - self.nChar - self.nAff
        # <dChar> to get the value of an arc, <dCharVal> to get the char of an arc with its value
        self.dChar = {}
        for i in range(1, self.nChar):
            self.dChar[self.lArcVal[i]] = i
        self.dCharVal = { v: k  for k, v in self.dChar.items() }
            
        self._arcMask = (2 ** ((self.nBytesArc * 8) - 3)) - 1
        self._finalNodeMask = 1 << ((self.nBytesArc * 8) - 1)
        self._lastArcMask = 1 << ((self.nBytesArc * 8) - 2)
        self._addrBitMask = 1 << ((self.nBytesArc * 8) - 3)  # version 2

        self.nBytesOffset = 1 # version 3

        # Configuring DAWG functions according to nVersion
        if self.nVersion == 1:
            self.morph = self._morph1
            self.stem = self._stem1
            self._lookupArcNode = self._lookupArcNode1
            self._getArcs = self._getArcs1
            self._writeNodes = self._writeNodes1
        elif self.nVersion == 2:
            self.morph = self._morph2
            self.stem = self._stem2
            self._lookupArcNode = self._lookupArcNode2
            self._getArcs = self._getArcs2
            self._writeNodes = self._writeNodes2
        elif self.nVersion == 3:
            self.morph = self._morph3
            self.stem = self._stem3
            self._lookupArcNode = self._lookupArcNode3
            self._getArcs = self._getArcs3
            self._writeNodes = self._writeNodes3
        else:
            raise ValueError("  # Error: unknown code: {}".format(self.nVersion))

        self.bOptNumSigle = False
        self.bOptNumAtLast = False

    def getInfo (self):
        return  "  Language: {0.sLang:>10}      Version: {0.nVersion:>2}      Stemming: {0.cStemming}FX\n" \
                "  Arcs values:  {0.nArcVal:>10,} = {0.nChar:>5,} characters,  {0.nAff:>6,} affixes,  {0.nTag:>6,} tags\n" \
                "  Dictionary: {0.nEntries:>12,} entries,    {0.nNode:>11,} nodes,   {0.nArc:>11,} arcs\n" \
                "  Address size: {0.nBytesNodeAddress:>1} bytes,  Arc size: {0.nBytesArc:>1} bytes\n".format(self)

    def writeAsJSObject (self, spfDest, bInJSModule=False, bBinaryDictAsHexString=False):
        "write IBDAWG as a JavaScript object in a JavaScript module"
        import json
        with open(spfDest, "w", encoding="utf-8", newline="\n") as hDst:
            if bInJSModule:
                hDst.write('// JavaScript\n// Generated data (do not edit)\n\n"use strict";\n\nconst dictionary = ')
            hDst.write(json.dumps({
                            "sName": self.sName,
                            "nVersion": self.nVersion,
                            "sHeader": self.sHeader,
                            "lArcVal": self.lArcVal,
                            "nArcVal": self.nArcVal,
                            # JavaScript is a pile of shit, so Mozilla’s JS parser don’t like file bigger than 4 Mb!
                            # So, if necessary, we use an hexadecimal string, that we will convert later in Firefox’s extension.
                            # https://github.com/mozilla/addons-linter/issues/1361
                            "byDic": self.byDic.hex()  if bBinaryDictAsHexString  else [ e  for e in self.byDic ],
                            "sLang": self.sLang,
                            "nChar": self.nChar,
                            "nBytesArc": self.nBytesArc,
                            "nBytesNodeAddress": self.nBytesNodeAddress,
                            "nEntries": self.nEntries,
                            "nNode": self.nNode,
                            "nArc": self.nArc,
                            "nAff": self.nAff,
                            "cStemming": self.cStemming,
                            "nTag": self.nTag,
                            "dChar": self.dChar,
                            "_arcMask": self._arcMask,
                            "_finalNodeMask": self._finalNodeMask,
                            "_lastArcMask": self._lastArcMask,
                            "_addrBitMask": self._addrBitMask,
                            "nBytesOffset": self.nBytesOffset
                        }, ensure_ascii=False))
            if bInJSModule:
                hDst.write(";\n\nexports.dictionary = dictionary;\n")

    def isValidToken (self, sToken):
        "checks if <sToken> is valid (if there is hyphens in <sToken>, <sToken> is split, each part is checked)"
        if self.isValid(sToken):
            return True
        if "-" in sToken:
            if sToken.count("-") > 4:
                return True
            return all(self.isValid(sWord)  for sWord in sToken.split("-"))
        return False

    def isValid (self, sWord):
        "checks if <sWord> is valid (different casing tested if the first letter is a capital)"
        if not sWord:
            return None
        if "’" in sWord: # ugly hack
            sWord = sWord.replace("’", "'")
        if self.lookup(sWord):
            return True
        if sWord[0:1].isupper():
            if len(sWord) > 1:
                if sWord.istitle():
                    return self.lookup(sWord.lower())
                if sWord.isupper():
                    if self.bOptNumSigle:
                        return True
                    return self.lookup(sWord.lower()) or self.lookup(sWord.capitalize())
                return self.lookup(sWord[:1].lower() + sWord[1:])
            else:
                return self.lookup(sWord.lower())
        return False

    def lookup (self, sWord):
        "returns True if <sWord> in dictionary (strict verification)"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return False
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return False
        return bool(int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask)

    def getMorph (self, sWord):
        "retrieves morphologies list, different casing allowed"
        l = self.morph(sWord)
        if sWord[0:1].isupper():
            l.extend(self.morph(sWord.lower()))
            if sWord.isupper() and len(sWord) > 1:
                l.extend(self.morph(sWord.capitalize()))
        return l

    def suggest (self, sWord, nMaxSugg=10):
        "returns a set of suggestions for <sWord>"
        sAdd = ""
        if "-" in sWord:
            nLastHyphenPos = sWord.rfind("-")
            if sWord[nLastHyphenPos+1:] in cp.aExcludedSfx:
                sAdd = sWord[nLastHyphenPos:]
                sWord = sWord[:nLastHyphenPos]
        nMaxDel = len(sWord) // 5
        nMaxHardRepl = max((len(sWord) - 5) // 4, 1)
        aSugg = self._suggest(sWord, nMaxDel=nMaxDel, nMaxHardRepl=nMaxHardRepl)
        if sWord.istitle():
            aSugg.update(self._suggest(sWord.lower(), nMaxDel=nMaxDel, nMaxHardRepl=nMaxHardRepl))
            aSugg = set(map(lambda sSugg: sSugg.title(), aSugg))
        elif sWord.islower():
            aSugg.update(self._suggest(sWord.title(), nMaxDel=nMaxDel, nMaxHardRepl=nMaxHardRepl))
        if not aSugg:
            #print("crush useless chars")
            aSugg.update(self._suggestWithCrushedUselessChars(cp.clearWord(sWord)))
        aSugg = filter(lambda sSugg: not sSugg.endswith(("è", "È")), aSugg) # fr language 
        aSugg = sorted(aSugg, key=lambda sSugg: cp.distanceDamerauLevenshtein(sWord, sSugg))[:nMaxSugg]
        if sAdd:
            # we add what we removed
            return list(map(lambda sSug: sSug+sAdd, aSugg))
        return aSugg

    def _suggest (self, sRemain, nMaxDel=0, nMaxHardRepl=0, nDeep=0, iAddr=0, sNewWord="", bAvoidLoop=False):
        "returns a set of suggestions"
        # recursive function
        #show(nDeep, sNewWord + ":" + sRemain)
        aSugg = set()
        if not sRemain:
            if int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask:
                #show(nDeep, "___" + sNewWord + "___")
                aSugg.add(sNewWord)
            for sTail in self._getTails(iAddr):
                aSugg.add(sNewWord+sTail)
            return aSugg
        cCurrent = sRemain[0:1]
        for cChar, jAddr in self._getSimilarArcs(cCurrent, iAddr):
            aSugg.update(self._suggest(sRemain[1:], nMaxDel, nMaxHardRepl, nDeep+1, jAddr, sNewWord+cChar))
        if not bAvoidLoop: # avoid infinite loop
            if cCurrent == sRemain[1:2]:
                # same char, we remove 1 char without adding 1 to <sNewWord>
                aSugg.update(self._suggest(sRemain[1:], nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord))
            else:
                # switching chars
                aSugg.update(self._suggest(sRemain[1:2]+sRemain[0:1]+sRemain[2:], nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
                # delete char
                if nMaxDel > 0:
                    aSugg.update(self._suggest(sRemain[1:], nMaxDel-1, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
            # Phonetic replacements
            for sRepl in cp.d1toX.get(cCurrent, ()):
                aSugg.update(self._suggest(sRepl + sRemain[1:], nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
            for sRepl in cp.d2toX.get(sRemain[0:2], ()):
                aSugg.update(self._suggest(sRepl + sRemain[2:], nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
            # Hard replacements
            if nDeep > 3 and nMaxHardRepl and len(sRemain) >= 2:
                for nVal, kAddr in self._getArcs1(iAddr):
                    if nVal in self.dCharVal:
                        cChar = self.dCharVal[nVal]
                        if cChar not in cp.d1to1.get(cCurrent, ""):
                            aSugg.update(self._suggest(sRemain[1:], nMaxDel, nMaxHardRepl-1, nDeep+1, kAddr, sNewWord+cChar, True))
            # end of word
            if len(sRemain) == 2:
                for sRepl in cp.dFinal2.get(sRemain, ()):
                    aSugg.update(self._suggest(sRepl, nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
            elif len(sRemain) == 1:
                aSugg.update(self._suggest("", nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True)) # remove last char and go on
                for sRepl in cp.dFinal1.get(sRemain, ()):
                    aSugg.update(self._suggest(sRepl, nMaxDel, nMaxHardRepl, nDeep+1, iAddr, sNewWord, True))
        return aSugg

    def _getSimilarArcs (self, cChar, iAddr):
        "generator: yield similar char of <cChar> and address of the following node"
        for c in cp.d1to1.get(cChar, [cChar]):
            if c in self.dChar:
                jAddr = self._lookupArcNode(self.dChar[c], iAddr)
                if jAddr:
                    yield (c, jAddr)

    def _getTails (self, iAddr, sTail="", n=2):
        "return a list of suffixes ending at a distance of <n> from <iAddr>"
        aTails = set()
        for nVal, jAddr in self._getArcs(iAddr):
            if nVal < self.nChar:
                if int.from_bytes(self.byDic[jAddr:jAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask:
                    aTails.add(sTail + self.dCharVal[nVal])
                if n and not aTails:
                    aTails.update(self._getTails(jAddr, sTail+self.dCharVal[nVal], n-1))
        return aTails

    def _suggestWithCrushedUselessChars (self, sWord, nDeep=0, iAddr=0, sNewWord="", bAvoidLoop=False):
        aSugg = set()
        if not sWord:
            if int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask:
                #show(nDeep, "!!! " + sNewWord + " !!!")
                aSugg.add(sNewWord)
            return aSugg
        cCurrent = sWord[0:1]
        for cChar, jAddr in self._getSimilarArcsAndCrushedChars(cCurrent, iAddr):
            #show(nDeep, cChar)
            aSugg.update(self._suggestWithCrushedUselessChars(sWord[1:], nDeep+1, jAddr, sNewWord+cChar))
        return aSugg

    def _getSimilarArcsAndCrushedChars (self, cChar, iAddr):
        "generator: yield similar char of <cChar> and address of the following node"
        for nVal, jAddr in self._getArcs(iAddr):
            if self.dCharVal.get(nVal, None) in cp.aVovels:
                yield (self.dCharVal[nVal], jAddr)
        yield from self._getSimilarArcs(cChar, iAddr)

    def drawPath (self, sWord, iAddr=0):
        "show the path taken by <sWord> in the graph"
        cChar = sWord[0:1]  if sWord  else " "
        iPos = -1
        n = 0
        print(cChar + ": ", end="")
        for nVal, jAddr in self._getArcs(iAddr):
            if nVal in self.dCharVal:
                print(self.dCharVal[nVal], end="")
                if self.dCharVal[nVal] == sWord[0:1]:
                    iNextNodeAddr = jAddr
                    iPos = n
                n += 1
        if not sWord:
            return
        if iPos >= 0:
            print("\n   "+ " " * iPos + "|")
            self.drawPath(sWord[1:], iNextNodeAddr)

    def select (self, sPattern=""):
        "generator: returns all entries which morphology fits <sPattern>"
        zPattern = None
        try:
            zPattern = re.compile(sPattern)
        except:
            print("# Error in regex pattern")
            traceback.print_exc()
        yield from self._select1(zPattern, 0, "")

    # def morph (self, sWord):
    #     is defined in __init__

    # VERSION 1
    def _select1 (self, zPattern, iAddr, sWord):
        # recursive generator
        for nVal, jAddr in self._getArcs1(iAddr):
            if nVal < self.nChar:
                # simple character
                yield from self._select1(zPattern, jAddr, sWord + self.lArcVal[nVal])
            else:
                sEntry = sWord + "\t" + self.funcStemming(sWord, self.lArcVal[nVal])
                for nMorphVal, _ in self._getArcs1(jAddr):
                    if not zPattern or zPattern.search(self.lArcVal[nMorphVal]):
                        yield sEntry + "\t" + self.lArcVal[nMorphVal]

    def _morph1 (self, sWord):
        "returns morphologies of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    sStem = ">" + self.funcStemming(sWord, self.lArcVal[nArc])
                    # Now , we go to the next node and retrieve all following arcs values, all of them are tags
                    iAddr2 = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    nRawArc2 = 0
                    while not (nRawArc2 & self._lastArcMask):
                        iEndArcAddr2 = iAddr2 + self.nBytesArc
                        nRawArc2 = int.from_bytes(self.byDic[iAddr2:iEndArcAddr2], byteorder='big')
                        l.append(sStem + " " + self.lArcVal[nRawArc2 & self._arcMask])
                        iAddr2 = iEndArcAddr2+self.nBytesNodeAddress
                iAddr = iEndArcAddr+self.nBytesNodeAddress
            return l
        return []

    def _stem1 (self, sWord):
        "returns stems list of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    l.append(self.funcStemming(sWord, self.lArcVal[nArc]))
                iAddr = iEndArcAddr+self.nBytesNodeAddress
            return l
        return []

    def _lookupArcNode1 (self, nVal, iAddr):
        "looks if <nVal> is an arc at the node at <iAddr>, if yes, returns address of next node else None"
        while True:
            iEndArcAddr = iAddr+self.nBytesArc
            nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
            if nVal == (nRawArc & self._arcMask):
                # the value we are looking for 
                # we return the address of the next node
                return int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
            else:
                # value not found
                if (nRawArc & self._lastArcMask):
                    return None
                iAddr = iEndArcAddr+self.nBytesNodeAddress

    def _getArcs1 (self, iAddr):
        "generator: return all arcs at <iAddr> as tuples of (nVal, iAddr)"
        while True:
            iEndArcAddr = iAddr+self.nBytesArc
            nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
            yield (nRawArc & self._arcMask, int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big'))
            if (nRawArc & self._lastArcMask):
                break
            iAddr = iEndArcAddr+self.nBytesNodeAddress

    def _writeNodes1 (self, spfDest):
        "for debugging only"
        print(" > Write binary nodes")
        with codecs.open(spfDest, 'w', 'utf-8', newline="\n") as hDst:
            iAddr = 0
            hDst.write("i{:_>10} -- #{:_>10}\n".format("0", iAddr))
            while iAddr < len(self.byDic):
                iEndArcAddr = iAddr+self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                hDst.write("  {:<20}  {:0>16}  i{:>10}   #{:_>10}\n".format(self.lArcVal[nArc], bin(nRawArc)[2:], "?", \
                                                                            int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], \
                                                                                           byteorder='big')))
                iAddr = iEndArcAddr+self.nBytesNodeAddress
                if (nRawArc & self._lastArcMask) and iAddr < len(self.byDic):
                    hDst.write("\ni{:_>10} -- #{:_>10}\n".format("?", iAddr))
            hDst.close()

    # VERSION 2
    def _morph2 (self, sWord):
        "returns morphologies of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    sStem = ">" + self.funcStemming(sWord, self.lArcVal[nArc])
                    # Now , we go to the next node and retrieve all following arcs values, all of them are tags
                    if not (nRawArc & self._addrBitMask):
                        iAddr2 = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    else:
                        # we go to the end of the node
                        iAddr2 = iEndArcAddr
                        while not (nRawArc & self._lastArcMask):
                            nRawArc = int.from_bytes(self.byDic[iAddr2:iAddr2+self.nBytesArc], byteorder='big')
                            iAddr2 += self.nBytesArc + self.nBytesNodeAddress
                    nRawArc2 = 0
                    while not (nRawArc2 & self._lastArcMask):
                        iEndArcAddr2 = iAddr2 + self.nBytesArc
                        nRawArc2 = int.from_bytes(self.byDic[iAddr2:iEndArcAddr2], byteorder='big')
                        l.append(sStem + " " + self.lArcVal[nRawArc2 & self._arcMask])
                        iAddr2 = iEndArcAddr2+self.nBytesNodeAddress  if not (nRawArc2 & self._addrBitMask) else iEndArcAddr2
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr
            return l
        return []

    def _stem2 (self, sWord):
        "returns stems list of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    l.append(self.funcStemming(sWord, self.lArcVal[nArc]))
                    # Now , we go to the next node
                    if not (nRawArc & self._addrBitMask):
                        iAddr2 = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    else:
                        # we go to the end of the node
                        iAddr2 = iEndArcAddr
                        while not (nRawArc & self._lastArcMask):
                            nRawArc = int.from_bytes(self.byDic[iAddr2:iAddr2+self.nBytesArc], byteorder='big')
                            iAddr2 += self.nBytesArc + self.nBytesNodeAddress
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr
            return l
        return []

    def _lookupArcNode2 (self, nVal, iAddr):
        "looks if <nVal> is an arc at the node at <iAddr>, if yes, returns address of next node else None"
        while True:
            iEndArcAddr = iAddr+self.nBytesArc
            nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
            if nVal == (nRawArc & self._arcMask):
                # the value we are looking for 
                if not (nRawArc & self._addrBitMask):
                    # we return the address of the next node
                    return int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                else:
                    # we go to the end of the node
                    iAddr = iEndArcAddr
                    while not (nRawArc & self._lastArcMask):
                        nRawArc = int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big')
                        iAddr += self.nBytesArc + self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else self.nBytesArc
                    return iAddr
            else:
                # value not found
                if (nRawArc & self._lastArcMask):
                    return None
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr

    def _writeNodes2 (self, spfDest):
        "for debugging only"
        print(" > Write binary nodes")
        with codecs.open(spfDest, 'w', 'utf-8', newline="\n") as hDst:
            iAddr = 0
            hDst.write("i{:_>10} -- #{:_>10}\n".format("0", iAddr))
            while iAddr < len(self.byDic):
                iEndArcAddr = iAddr+self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if not (nRawArc & self._addrBitMask):
                    iNextNodeAddr = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    hDst.write("  {:<20}  {:0>16}  i{:>10}   #{:_>10}\n".format(self.lArcVal[nArc], bin(nRawArc)[2:], "?", iNextNodeAddr))
                    iAddr = iEndArcAddr+self.nBytesNodeAddress
                else:
                    hDst.write("  {:<20}  {:0>16}\n".format(self.lArcVal[nArc], bin(nRawArc)[2:]))
                    iAddr = iEndArcAddr
                if (nRawArc & self._lastArcMask):
                    hDst.write("\ni{:_>10} -- #{:_>10}\n".format("?", iAddr))
            hDst.close()

    # VERSION 3
    def _morph3 (self, sWord):
        "returns morphologies of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            iAddrNode = iAddr
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    sStem = ">" + self.funcStemming(sWord, self.lArcVal[nArc])
                    # Now , we go to the next node and retrieve all following arcs values, all of them are tags
                    if not (nRawArc & self._addrBitMask):
                        iAddr2 = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    else:
                        iAddr2 = iAddrNode + int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesOffset], byteorder='big')
                    nRawArc2 = 0
                    while not (nRawArc2 & self._lastArcMask):
                        iEndArcAddr2 = iAddr2 + self.nBytesArc
                        nRawArc2 = int.from_bytes(self.byDic[iAddr2:iEndArcAddr2], byteorder='big')
                        l.append(sStem + " " + self.lArcVal[nRawArc2 & self._arcMask])
                        iAddr2 = iEndArcAddr2+self.nBytesNodeAddress  if not (nRawArc2 & self._addrBitMask) else iEndArcAddr2+self.nBytesOffset
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr+self.nBytesOffset
            return l
        return []

    def _stem3 (self, sWord):
        "returns stems list of <sWord>"
        iAddr = 0
        for c in sWord:
            if c not in self.dChar:
                return []
            iAddr = self._lookupArcNode(self.dChar[c], iAddr)
            if iAddr == None:
                return []
        if (int.from_bytes(self.byDic[iAddr:iAddr+self.nBytesArc], byteorder='big') & self._finalNodeMask):
            l = []
            nRawArc = 0
            iAddrNode = iAddr
            while not (nRawArc & self._lastArcMask):
                iEndArcAddr = iAddr + self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if nArc >= self.nChar:
                    # This value is not a char, this is a stemming code 
                    l.append(self.funcStemming(sWord, self.lArcVal[nArc]))
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr+self.nBytesOffset
            return l
        return []

    def _lookupArcNode3 (self, nVal, iAddr):
        "looks if <nVal> is an arc at the node at <iAddr>, if yes, returns address of next node else None"
        iAddrNode = iAddr
        while True:
            iEndArcAddr = iAddr+self.nBytesArc
            nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
            if nVal == (nRawArc & self._arcMask):
                # the value we are looking for 
                if not (nRawArc & self._addrBitMask):
                    return int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                else:
                    return iAddrNode + int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesOffset], byteorder='big')
            else:
                # value not found
                if (nRawArc & self._lastArcMask):
                    return None
                iAddr = iEndArcAddr+self.nBytesNodeAddress  if not (nRawArc & self._addrBitMask)  else iEndArcAddr+self.nBytesOffset

    def _writeNodes3 (self, spfDest):
        "for debugging only"
        print(" > Write binary nodes")
        with codecs.open(spfDest, 'w', 'utf-8', newline="\n") as hDst:
            iAddr = 0
            hDst.write("i{:_>10} -- #{:_>10}\n".format("0", iAddr))
            while iAddr < len(self.byDic):
                iEndArcAddr = iAddr+self.nBytesArc
                nRawArc = int.from_bytes(self.byDic[iAddr:iEndArcAddr], byteorder='big')
                nArc = nRawArc & self._arcMask
                if not (nRawArc & self._addrBitMask):
                    iNextNodeAddr = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesNodeAddress], byteorder='big')
                    hDst.write("  {:<20}  {:0>16}  i{:>10}   #{:_>10}\n".format(self.lArcVal[nArc], bin(nRawArc)[2:], "?", iNextNodeAddr))
                    iAddr = iEndArcAddr+self.nBytesNodeAddress
                else:
                    iNextNodeAddr = int.from_bytes(self.byDic[iEndArcAddr:iEndArcAddr+self.nBytesOffset], byteorder='big')
                    hDst.write("  {:<20}  {:0>16}  i{:>10}   +{:_>10}\n".format(self.lArcVal[nArc], bin(nRawArc)[2:], "?", iNextNodeAddr))
                    iAddr = iEndArcAddr+self.nBytesOffset
                if (nRawArc & self._lastArcMask):
                    hDst.write("\ni{:_>10} -- #{:_>10}\n".format("?", iAddr))
            hDst.close()
