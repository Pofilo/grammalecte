#!python3

# FRENCH DATA BUILDER
#
# by Olivier R.
# License: MPL 2

import json
import os

import grammalecte.ibdawg as ibdawg
from grammalecte.echo import echo
from grammalecte.str_transform import defineSuffixCode
import grammalecte.fr.conj as conj


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
                if sLine and not sLine.startswith("#"):
                    yield sLine
    else:
        raise OSError("# Error. File not found or not loadable: " + spf)


def makeDictionaries (sp, sVersion):
    with cd(sp+"/dictionnaire"):
        os.system("genfrdic.py -s -gl -v "+sVersion)


def makeConj (sp, bJS=False):
    print("> Conjugaisons ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    dVerb = {}
    lVtyp = []; dVtyp = {}; nVtyp = 0
    lTags = []; dTags = {}; nTags = 0

    dPatternList = { ":PQ": [], ":Ip": [], ":Iq": [], ":Is": [], ":If": [], ":K": [], ":Sp": [], ":Sq": [], ":E": [] }
    dTrad = {   "infi": ":Y", "ppre": ":PQ", "ppas": ":PQ",
                "ipre": ":Ip", "iimp": ":Iq", "ipsi": ":Is", "ifut": ":If",
                "spre": ":Sp", "simp": ":Sq",
                "cond": ":K", "impe": ":E",
                "1sg": ":1s", "2sg": ":2s", "3sg": ":3s", "1pl": ":1p", "2pl": ":2p", "3pl": ":3p", "1isg": ":1ś",
                "mas sg": ":Q1", "mas pl": ":Q2", "mas inv": ":Q1", "fem sg": ":Q3", "fem pl": ":Q4", "epi inv": ":Q1"
            }

    # read lexicon
    nStop = 0
    for n, sLine in enumerate(readFile(sp+"/data/dictConj.txt")):
        nTab = sLine.count("\t")
        if nTab == 1:
            # new entry
            sLemma, sVtyp = sLine.split("\t")
            dConj = {   ":PQ": { ":P": "", ":Q1": "", ":Q2": "", ":Q3": "", ":Q4": ""},
                        ":Ip": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":Iq": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":Is": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":If": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":K": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "" },
                        ":Sp": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":Sq": { ":1s": "", ":2s": "", ":3s": "", ":1p": "", ":2p": "", ":3p": "", ":1ś": "" },
                        ":E": { ":2s": "", ":1p": "", ":2p": "" }
                    }
            if sVtyp not in lVtyp:
                dVtyp[sVtyp] = nVtyp
                lVtyp.append(sVtyp)
                nVtyp += 1
        elif nTab == 2:
            # flexion
            _, sTag, sFlex = sLine.split("\t")
            if sTag.count(" ") == 0:
                if sTag == "ppre":
                    dConj[":PQ"][":P"] = defineSuffixCode(sLemma, sFlex)
            else:
                try:
                    mode, g = sTag.split(maxsplit=1)
                    mode = dTrad[mode]
                    g = dTrad[g]
                    if dConj[mode][g] == "":
                        dConj[mode][g] = defineSuffixCode(sLemma, sFlex)
                    else:
                        # comment gérer les autres graphies ?
                        pass
                except:
                    print(sLemma.encode("utf-8").decode("ascii"), " - ", sTag, " - non géré: ", mode, " / ", g)
        elif sLine == "$":
            # we store the dictionary of rules for this lemma
            if dConj[":Ip"][":1ś"] == "2è":
                dConj[":Ip"][":1ś"] = "2é"
            elif sLemma == "pouvoir":
                dConj[":Ip"][":1ś"] = "6uis"
            lConjTags = []
            for key in [":PQ", ":Ip", ":Iq", ":Is", ":If", ":K", ":Sp", ":Sq", ":E"]:
                bFound = False
                for i, d in enumerate(dPatternList[key]):
                    if dConj[key] == d:
                        bFound = True
                        lConjTags.append(i)
                        break
                if not bFound:
                    lConjTags.append(len(dPatternList[key]))
                    dPatternList[key].append(dConj[key])
            tConjTags = tuple(lConjTags)
            if tConjTags not in lTags:
                dTags[tConjTags] = nTags
                lTags.append(tConjTags)
                nTags += 1
            dVerb[sLemma] = (dVtyp[sVtyp], dTags[tConjTags])
        else:
            print("# Error - unknown line #", n)

    # convert tuples to bytes string
    # si ça merde, toute la partie conversion peut être supprimée
    # lBytesTags = []
    # for t in lTags:
    #     b = b""
    #     for n in t:
    #         if n > 255:
    #             print("Erreur : l'indice ne peut être supérieur à 256 pour utiliser des chaînes d'octets (bytes strings)")
    #             exit()
    #         b += n.to_bytes(1, byteorder="big")
    #     lBytesTags.append(b)
    # lTags = lBytesTags

    # for key in dVerb.keys():
    #     b = b""
    #     for n in dVerb[key]:
    #         if n > 255:
    #             print("Erreur : l'indice ne peut être supérieur à 256 pour utiliser des chaînes d'octets (bytes strings)")
    #             exit()
    #         b += n.to_bytes(1, byteorder="big")
    #     dVerb[key] = b
    # end conversion


    ## write file for Python
    sCode = "## generated data (do not edit)\n\n" + \
            "# Informations about verbs\n" + \
            "lVtyp = " + str(lVtyp) + "\n\n" + \
            "# indexes of tenses in _dPatternConj\n" + \
            "lTags = " + str(lTags) + "\n\n" + \
            "# lists of affix codes to generate inflected forms\n" + \
            "dPatternConj = " + str(dPatternList) + "\n\n" + \
            "# dictionary of verbs : (index of Vtyp, index of Tags)\n" + \
            "dVerb = " + str(dVerb) + "\n"
    open(sp+"/modules/conj_data.py", "w", encoding="utf-8", newline="\n").write(sCode)

    if bJS:
        ## write file for JavaScript
        with open(sp+"/modules-js/conj_data.json", "w", encoding="utf-8", newline="\n") as hDst:
            hDst.write("{\n")
            hDst.write('    "lVtyp": ' + json.dumps(lVtyp, ensure_ascii=False) + ",\n")
            hDst.write('    "lTags": ' + json.dumps(lTags, ensure_ascii=False) + ",\n")
            hDst.write('    "dPatternConj": ' + json.dumps(dPatternList, ensure_ascii=False) + ",\n")
            hDst.write('    "dVerb": ' + json.dumps(dVerb, ensure_ascii=False) + "\n")
            hDst.write("}\n")


def makeMfsp (sp, bJS=False):
    print("> Pluriel/singulier/masculin/féminin ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    aPlurS = set()
    dTag = {}
    lTagMasForm = []
    lTagMiscPlur = []
    dMiscPlur = {}
    dMasForm = {}
    lTag = []
    lTagMasPl = []
    for n, sLine in enumerate(readFile(sp+"/data/dictDecl.txt")):
        sLine = sLine.strip()
        nTab = sLine.count("\t")
        if nTab == 1:
            # new entry
            lTag.clear()
            lTagMasPl.clear()
            sLemma, sFlags = sLine.split("\t")
            if sFlags.startswith("S"):
                cType = "s"
            elif sFlags.startswith("X"):
                cType = "p"
            elif sFlags.startswith("A"):
                cType = "p"
            elif sFlags.startswith("I"):
                cType = "p"
            elif sFlags.startswith("F"):
                cType = "m"
            elif sFlags.startswith("W"):
                cType = "m"
            else:
                cType = "?"
                print(" > inconnu : " + sFlags)
        elif nTab == 2:
            if cType == "s":
                continue
            _, sFlexTags, sFlex = sLine.split("\t")
            if cType == "p":
                if sFlexTags.endswith("pl"):
                    lTag.append(defineSuffixCode(sLemma, sFlex))
            elif cType == "m":
                if sFlexTags.endswith("mas sg") or sFlexTags.endswith("mas inv"):
                    lTag.append(defineSuffixCode(sLemma, sFlex))
                if sFlexTags.endswith("mas pl"):
                    lTagMasPl.append(defineSuffixCode(sLemma, sFlex))
            else:
                print("erreur: " + cType)
        elif sLine == "$":
            if cType == "s":
                aPlurS.add(sLemma)
            elif cType == "p":
                sTag = "|".join(lTag)
                if sTag not in dTag:
                    dTag[sTag] = len(lTagMiscPlur)
                    lTagMiscPlur.append(sTag)
                dMiscPlur[sLemma] = dTag[sTag]
            elif cType == "m":
                sTag = "|".join(lTag)
                if lTagMasPl:
                    sTag += "/" + "|".join(lTagMasPl)
                if sTag not in dTag:
                    dTag[sTag] = len(lTagMasForm)
                    lTagMasForm.append(sTag)
                dMasForm[sLemma] = dTag[sTag]
            else:
                print("unknown tag: " + ctype)
        else:
            print("# Error - unknown line #", n)

    ## write file for Python
    sCode = "# generated data (do not edit)\n\n" + \
            "# list of affix codes\n" + \
            "lTagMiscPlur = " + str(lTagMiscPlur) + "\n" + \
            "lTagMasForm = " + str(lTagMasForm) + "\n\n" + \
            "# dictionary of words with uncommon plurals (-x, -ux, english, latin and italian plurals) and tags to generate them\n" + \
            "dMiscPlur = " + str(dMiscPlur) + "\n\n" + \
            "# dictionary of feminine forms and tags to generate masculine forms (singular and plural)\n" + \
            "dMasForm = " + str(dMasForm) + "\n"
    open(sp+"/modules/mfsp_data.py", "w", encoding="utf-8", newline="\n").write(sCode)

    if bJS:
        ## write file for JavaScript
        sCode = '{\n' + \
                '    "lTagMiscPlur": ' +  json.dumps(lTagMiscPlur, ensure_ascii=False) + ",\n" + \
                '    "lTagMasForm": ' +  json.dumps(lTagMasForm, ensure_ascii=False) + ",\n" + \
                '    "dMiscPlur": ' +  json.dumps(dMiscPlur, ensure_ascii=False) + ",\n" + \
                '    "dMasForm": ' +  json.dumps(dMasForm, ensure_ascii=False) + "\n}"
        open(sp+"/modules-js/mfsp_data.json", "w", encoding="utf-8", newline="\n").write(sCode)


def makePhonetTable (sp, bJS=False):
    print("> Correspondances phonétiques ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    
    try:
        oDict = ibdawg.IBDAWG("French.bdic")
    except:
        traceback.print_exc()
        return

    # set of homophonic words
    lSet = []
    for sLine in readFile(sp+"/data/phonet_simil.txt"):
        lWord = sLine.split()
        aMore = set()
        for sWord in lWord:
            if sWord.endswith("er") and conj.isVerb(sWord):
                aMore = aMore.union(conj.getConjSimilInfiV1(sWord))
        lWord.extend(list(aMore))
        lSet.append(sorted(set(lWord)))

    # dictionary of words
    dWord = {}
    for i, aSet in enumerate(lSet):
        for sWord in aSet:
            if oDict.lookup(sWord):
                dWord[sWord] = i  # warning, what if word in several sets?
            else:
                echo("Mot inconnu : " + sWord)
    # dictionary of morphologies
    dMorph = {}
    for sWord in dWord:
        dMorph[sWord] = oDict.getMorph(sWord)

    # write file for Python
    sCode = "# generated data (do not edit)\n\n" + \
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


def makeLocutions (sp, bJS=False):
    "compile list of locutions in JSON"
    print("> Locutions ", end="")
    print("(Python et JavaScript)"  if bJS  else "(Python seulement)")
    dLocutions = {}
    sVal = ":H"
    for sLine in readFile(sp+"/data/locutions.txt"):
        if sLine.startswith("[") and sLine.endswith("]"):
            sLabel, sVal = sLine[1:-1].split("|", 1)
            continue
        lElem = sLine.split()
        dCur = dLocutions
        for sWord in lElem:
            if sWord not in dCur:
                dCur[sWord] = {}
            dCur = dCur[sWord]
        dCur[":"] = sVal

    sCode = "# generated data (do not edit)\n\n" + \
            "dLocutions = " + str(dLocutions) + "\n"
    open(sp+"/modules/locutions_data.py", "w", encoding="utf-8", newline="\n").write(sCode)
    if bJS:
        open(sp+"/modules-js/locutions_data.json", "w", encoding="utf-8", newline="\n").write(json.dumps(dLocutions, ensure_ascii=False))


def before (spLaunch, dVars, bJS=False):
    print("========== Build Hunspell dictionaries ==========")
    makeDictionaries(spLaunch, dVars['oxt_version'])


def after (spLaunch, dVars, bJS=False):
    print("========== Build French data ==========")
    makeMfsp(spLaunch, bJS)
    makeConj(spLaunch, bJS)
    makePhonetTable(spLaunch, bJS)
    makeLocutions(spLaunch, bJS)
