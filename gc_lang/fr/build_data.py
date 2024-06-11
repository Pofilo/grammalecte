#!python3

# FRENCH DATA BUILDER
#
# by Olivier R.
# License: MPL 2

import json
import os
import itertools
import traceback
import platform
import importlib

import graphspell.ibdawg as ibdawg
from graphspell.echo import echo
from graphspell.str_transform import defineSuffixCode
import graphspell.tokenizer as tkz


oDict = None


class cd:
    """Context manager for changing the current working directory"""
    def __init__ (self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__ (self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__ (self, etype, value, traceback):
        os.chdir(self.savedPath)


def readFile (spf):
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                sLine = sLine.strip()
                if sLine == "__END__":
                    break
                if sLine and not sLine.startswith("#"):
                    yield sLine
    else:
        raise OSError("# Error. File not found or not loadable: " + spf)


def loadDictionary ():
    global oDict
    if not oDict:
        try:
            oDict = ibdawg.IBDAWG("fr-allvars.json")
        except:
            traceback.print_exc()


def makeDictionaries (sp, sVersion):
    with cd(sp+"/dictionnaire"):
        if platform.system() == "Windows":
            os.system("python genfrdic.py -s -gl -v "+sVersion)
        else:
            os.system("python3 ./genfrdic.py -s -gl -v "+sVersion)


def makeConj (sp, bJS=False):
    print("> Conjugaisons ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    dVerb = {}
    lVinfo = []; dVinfo = {}; nVinfo = 0
    lTags = []; dTags = {}; nTags = 0
    dVerbNames = {}

    dPatternList = {
        ":P": [], ":Q": [], ":Ip": [], ":Iq": [], ":Is": [], ":If": [], ":K": [], ":Sp": [], ":Sq": [], ":E": []
    }
    dTrad = {
        "infi": ":Y", "ppre": ":P", "ppas": ":Q",
        "ipre": ":Ip", "iimp": ":Iq", "ipsi": ":Is", "ifut": ":If",
        "spre": ":Sp", "simp": ":Sq",
        "cond": ":K", "impe": ":E",
        "1sg": ":1s", "2sg": ":2s", "3sg": ":3s", "1pl": ":1p", "2pl": ":2p", "3pl": ":3p", "1isg": ":1ś",
        "mas sg": ":m:s", "mas pl": ":m:p", "mas inv": ":m:s", "fem sg": ":f:s", "fem pl": ":f:p", "epi inv": ":m:s"
    }

    loadDictionary()

    # read lexicon
    nStop = 0
    for n, sLine in enumerate(readFile(sp+"/data/dictConj.txt")):
        nTab = sLine.count("\t")
        if nTab == 1:
            # new entry
            sInfi, sVinfo = sLine.split("\t")
            dConj = {   ":P": { ":P": "" },
                        ":Q": { ":m:s": "", ":f:s": "", ":m:p": "", ":f:p": "" },
                        ":Ip": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":Iq": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":Is": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":If": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":K":  { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":Sp": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":Sq": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":E":  { ":2s": "", ":1p": "", ":2p": "" }
                    }
            if sVinfo not in lVinfo:
                dVinfo[sVinfo] = nVinfo
                lVinfo.append(sVinfo)
                nVinfo += 1
            # looking for names derivating from verb
            for sMorph in oDict.getMorph(sInfi):
                if ":N" in sMorph:
                    dVerbNames[sInfi] = { sInfi }
                    break
        elif nTab == 2:
            # flexion
            _, sTag, sFlex = sLine.split("\t")
            if sTag.count(" ") == 0:
                if sTag == "ppre":
                    dConj[":P"][":P"] = defineSuffixCode(sInfi, sFlex)
            else:
                try:
                    mode, g = sTag.split(maxsplit=1)
                    mode = dTrad[mode]
                    g = dTrad[g]
                    if dConj[mode][g] == "":
                        dConj[mode][g] = defineSuffixCode(sInfi, sFlex)
                    else:
                        # comment gérer les autres graphies ?
                        pass
                except:
                    echo(f"{sInfi} - {sTag} - non géré: {mode} /  {g}")
            # looking for names derivating from verb
            for sMorph in oDict.getMorph(sFlex):
                if ":N" in sMorph:
                    if sInfi not in dVerbNames:
                        dVerbNames[sInfi] = set()
                    dVerbNames[sInfi].add(sFlex)
                    sLemma = sMorph[1:sMorph.find("/")]
                    if sFlex != sLemma:
                        dVerbNames[sInfi].add(sLemma)
        elif sLine == "$":
            # we store the dictionary of rules for this lemma
            if dConj[":Ip"][":1ś"] == "2è":
                dConj[":Ip"][":1ś"] = "2é"
            elif sInfi == "pouvoir":
                dConj[":Ip"][":1ś"] = "6uis"
            lConjTags = []
            for sTense in [":P", ":Q", ":Ip", ":Iq", ":Is", ":If", ":K", ":Sp", ":Sq", ":E"]:
                bFound = False
                for i, d in enumerate(dPatternList[sTense]):
                    if dConj[sTense] == d:
                        bFound = True
                        lConjTags.append(i)
                        break
                if not bFound:
                    lConjTags.append(len(dPatternList[sTense]))
                    dPatternList[sTense].append(dConj[sTense])
            tConjTags = tuple(lConjTags)
            if tConjTags not in lTags:
                dTags[tConjTags] = nTags
                lTags.append(tConjTags)
                nTags += 1
            dVerb[sInfi] = (dVinfo[sVinfo], dTags[tConjTags])
        else:
            print("# Error - unknown line", n)

    for sInfi, aNames in dVerbNames.items():
        dVerbNames[sInfi] = tuple(aNames)  # convert set to tuple

    ## write file for Python
    sCode = "## generated data (do not edit)\n\n" + \
            "# Informations about verbs\n" + \
            "lVtyp = " + str(lVinfo) + "\n\n" + \
            "# indexes of tenses in _dPatternConj\n" + \
            "lTags = " + str(lTags) + "\n\n" + \
            "# lists of affix codes to generate inflected forms\n" + \
            "dPatternConj = " + str(dPatternList) + "\n\n" + \
            "# dictionary of verbs : (index of Vtyp, index of Tags)\n" + \
            "dVerb = " + str(dVerb) + "\n\n" + \
            "# names as derivatives from verbs\n" + \
            "dVerbNames = " + str(dVerbNames) + "\n"
    open(sp+"/modules/conj_data.py", "w", encoding="utf-8", newline="\n").write(sCode)

    if bJS:
        ## write file for JavaScript
        with open(sp+"/modules-js/conj_data.json", "w", encoding="utf-8", newline="\n") as hDst:
            hDst.write("{\n")
            hDst.write('    "lVtyp": ' + json.dumps(lVinfo, ensure_ascii=False) + ",\n")
            hDst.write('    "lTags": ' + json.dumps(lTags, ensure_ascii=False) + ",\n")
            hDst.write('    "dPatternConj": ' + json.dumps(dPatternList, ensure_ascii=False) + ",\n")
            hDst.write('    "dVerb": ' + json.dumps(dVerb, ensure_ascii=False) + ",\n")
            hDst.write('    "dVerbNames": ' + json.dumps(dVerbNames, ensure_ascii=False) + "\n")
            hDst.write("}\n")


def makeMfsp (sp, bJS=False):
    print("> Pluriel/singulier/masculin/féminin ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    aPlurS = set()      # pluriels en -s
    dTag = {}
    lTagFemForm = []
    lTagMiscPlur = []   # pluriels spéciaux
    dMiscPlur = {}
    dMasForm = {}
    lTag = []
    lTagFemPl = []
    for n, sLine in enumerate(readFile(sp+"/data/dictDecl.txt")):
        nTab = sLine.count("\t")
        if nTab == 1:
            # new entry
            lTag.clear()
            lTagFemPl.clear()
            sLemma, sFlags = sLine.split("\t")
            if sFlags.startswith("S"):
                cType = "sg"
            elif sFlags.startswith("X"):
                cType = "pl"
            elif sFlags.startswith("A"):
                cType = "pl"
            elif sFlags.startswith("I"):
                cType = "pl"
            elif sFlags.startswith("F"):
                cType = "mf"
            elif sFlags.startswith("W"):
                cType = "mf"
            else:
                cType = "?"
                print(" > inconnu : " + sFlags)
        elif nTab == 2:
            if cType == "sg":
                # nothing to do
                continue
            _, sFlexTags, sFlex = sLine.split("\t")
            if cType == "pl":
                if sFlexTags.endswith("pl"):
                    lTag.append(defineSuffixCode(sLemma, sFlex))
            elif cType == "mf":
                if sFlexTags.endswith("fem sg"):
                    lTag.append(defineSuffixCode(sLemma, sFlex))
                if sFlexTags.endswith("fem pl"):
                    lTagFemPl.append(defineSuffixCode(sLemma, sFlex))
            else:
                print("erreur: " + cType)
        elif sLine == "$":
            if cType == "sg":
                aPlurS.add(sLemma)
            elif cType == "pl":
                sTag = "|".join(lTag)
                if sTag not in dTag:
                    dTag[sTag] = len(lTagMiscPlur)
                    lTagMiscPlur.append(sTag)
                dMiscPlur[sLemma] = dTag[sTag]
            elif cType == "mf":
                sTag = "|".join(lTag) + "/" + "|".join(lTagFemPl)
                if sTag not in dTag:
                    dTag[sTag] = len(lTagFemForm)
                    lTagFemForm.append(sTag)
                dMasForm[sLemma] = dTag[sTag]
            else:
                print("unknown tag: " + ctype)
        else:
            print("# Error - unknown line #", n)

    ## write file for Python
    sCode = "# generated data (do not edit)\n\n" + \
            "# list of affix codes\n" + \
            "lTagMiscPlur = " + str(lTagMiscPlur) + "\n" + \
            "lTagFemForm = " + str(lTagFemForm) + "\n\n" + \
            "# dictionary of words with uncommon plurals (-x, -ux, english, latin and italian plurals) and tags to generate them\n" + \
            "dMiscPlur = " + str(dMiscPlur) + "\n\n" + \
            "# dictionary of feminine forms and tags to generate masculine forms (singular and plural)\n" + \
            "dMasForm = " + str(dMasForm) + "\n"
    open(sp+"/modules/mfsp_data.py", "w", encoding="utf-8", newline="\n").write(sCode)

    if bJS:
        ## write file for JavaScript
        sCode = '{\n' + \
                '    "lTagMiscPlur": ' +  json.dumps(lTagMiscPlur, ensure_ascii=False) + ",\n" + \
                '    "lTagFemForm": ' +  json.dumps(lTagFemForm, ensure_ascii=False) + ",\n" + \
                '    "dMiscPlur": ' +  json.dumps(dMiscPlur, ensure_ascii=False) + ",\n" + \
                '    "dMasForm": ' +  json.dumps(dMasForm, ensure_ascii=False) + "\n}"
        open(sp+"/modules-js/mfsp_data.json", "w", encoding="utf-8", newline="\n").write(sCode)


def makePhonetTable (sp, bJS=False):
    print("> Correspondances phonétiques ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")

    loadDictionary()

    conj = importlib.import_module("gc_lang.fr.modules.conj")

    # set of homophonic words
    lSet = []
    for sLine in readFile(sp+"/data/phonet_simil.txt"):
        lWord = sLine.split()
        for sWord in lWord:
            if sWord.endswith("er") and conj.isVerb(sWord):
                lWord.extend(conj.getConjSimilInfiV1(sWord))
        lSet.append(set(lWord))

    # dictionary of words
    dWord = {}
    aMultiSetWord = set()
    lNewSet = []
    nAppend = 0
    for i, aSet in enumerate(lSet):
        for sWord in aSet:
            if oDict.lookup(sWord):
                if sWord not in dWord:
                    dWord[sWord] = i
                else:
                    # word in several set
                    aMultiSetWord.add(sWord)
                    iSet = dWord[sWord]
                    lNewSet.append(lSet[iSet].union(aSet))
                    dWord[sWord] = len(lSet) + nAppend
                    nAppend += 1
            else:
                echo(f"  Mot inconnu : <{sWord}>")
    lSet.extend(lNewSet)
    lSet = [ sorted(aSet) for aSet in lSet ]
    print("  Mots appartenant à plusieurs ensembles: ", ", ".join(aMultiSetWord))

    # dictionary of morphologies
    dMorph = {}
    for sWord in dWord:
        dMorph[sWord] = oDict.getMorph(sWord)

    # write file for Python
    sCode = "# generated data built in build_data.py (do not edit)\n\n" + \
            "dWord = " + str(dWord) + "\n\n" + \
            "lSet = " + str(lSet) + "\n\n" + \
            "dMorph = " + str(dMorph) + "\n"
    open(sp+"/modules/phonet_data.py", "w", encoding="utf-8", newline="\n").write(sCode)

    if bJS:
        ## write file for JavaScript
        sCode = "{\n" + \
                '    "dWord": ' + json.dumps(dWord, ensure_ascii=False) + ",\n" + \
                '    "lSet": ' + json.dumps(lSet, ensure_ascii=False) + ",\n" + \
                '    "dMorph": ' + json.dumps(dMorph, ensure_ascii=False) + "\n}"
        open(sp+"/modules-js/phonet_data.json", "w", encoding="utf-8", newline="\n").write(sCode)


def before (spLaunch, dVars, bJS=False):
    print("========== Build Hunspell dictionaries ==========")
    makeDictionaries(spLaunch, dVars['oxt_version'])


def after (spLaunch, dVars, bJS=False):
    print("========== Build French data ==========")
    makeMfsp(spLaunch, bJS)
    makeConj(spLaunch, bJS)
    makePhonetTable(spLaunch, bJS)
