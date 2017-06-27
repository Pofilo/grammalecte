#### GRAMMAR CHECKING ENGINE PLUGIN: Suggestion mechanisms

from . import conj
from . import mfsp
from . import phonet


## Verbs

def suggVerb (sFlex, sWho, funcSugg2=None):
    aSugg = set()
    for sStem in stem(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            # we get the tense
            aTense = set()
            for sMorph in _dAnalyses.get(sFlex, []): # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
                for m in re.finditer(sStem+" .*?(:(?:Y|I[pqsf]|S[pq]|K|P))", sMorph):
                    # stem must be used in regex to prevent confusion between different verbs (e.g. sauras has 2 stems: savoir and saurer)
                    if m:
                        if m.group(1) == ":Y":
                            aTense.add(":Ip")
                            aTense.add(":Iq")
                            aTense.add(":Is")
                        elif m.group(1) == ":P":
                            aTense.add(":Ip")
                        else:
                            aTense.add(m.group(1))
            for sTense in aTense:
                if sWho == ":1ś" and not conj._hasConjWithTags(tTags, sTense, ":1ś"):
                    sWho = ":1s"
                if conj._hasConjWithTags(tTags, sTense, sWho):
                    aSugg.add(conj._getConjWithTags(sStem, tTags, sTense, sWho))
    if funcSugg2:
        aSugg2 = funcSugg2(sFlex)
        if aSugg2:
            aSugg.add(aSugg2)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggVerbPpas (sFlex, sWhat=None):
    aSugg = set()
    for sStem in stem(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            if not sWhat:
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"))
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"))
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"))
                aSugg.discard("")
            elif sWhat == ":m:s":
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
            elif sWhat == ":m:p":
                if conj._hasConjWithTags(tTags, ":PQ", ":Q2"):
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"))
                else:
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
            elif sWhat == ":f:s":
                if conj._hasConjWithTags(tTags, ":PQ", ":Q3"):
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"))
                else:
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
            elif sWhat == ":f:p":
                if conj._hasConjWithTags(tTags, ":PQ", ":Q4"):
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"))
                else:
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
            elif sWhat == ":s":
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"))
                aSugg.discard("")
            elif sWhat == ":p":
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"))
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"))
                aSugg.discard("")
            else:
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"))
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggVerbTense (sFlex, sTense, sWho):
    aSugg = set()
    for sStem in stem(sFlex):
        if conj.hasConj(sStem, sTense, sWho):
            aSugg.add(conj.getConj(sStem, sTense, sWho))
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggVerbImpe (sFlex):
    aSugg = set()
    for sStem in stem(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            if conj._hasConjWithTags(tTags, ":E", ":2s"):
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":2s"))
            if conj._hasConjWithTags(tTags, ":E", ":1p"):
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":1p"))
            if conj._hasConjWithTags(tTags, ":E", ":2p"):
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":2p"))
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggVerbInfi (sFlex):
    return "|".join([ sStem  for sStem in stem(sFlex)  if conj.isVerb(sStem) ])


_dQuiEst = { "je": ":1s", "j’": ":1s", "j’en": ":1s", "j’y": ":1s", \
             "tu": ":2s", "il": ":3s", "on": ":3s", "elle": ":3s", "nous": ":1p", "vous": ":2p", "ils": ":3p", "elles": ":3p" }
_lIndicatif = [":Ip", ":Iq", ":Is", ":If"]
_lSubjonctif = [":Sp", ":Sq"]

def suggVerbMode (sFlex, cMode, sSuj):
    if cMode == ":I":
        lMode = _lIndicatif
    elif cMode == ":S":
        lMode = _lSubjonctif
    elif cMode.startswith((":I", ":S")):
        lMode = [cMode]
    else:
        return ""
    sWho = _dQuiEst.get(sSuj.lower(), None)
    if not sWho:
        if sSuj[0:1].islower(): # pas un pronom, ni un nom propre
            return ""
        sWho = ":3s"
    aSugg = set()
    for sStem in stem(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            for sTense in lMode:
                if conj._hasConjWithTags(tTags, sTense, sWho):
                    aSugg.add(conj._getConjWithTags(sStem, tTags, sTense, sWho))
    if aSugg:
        return "|".join(aSugg)
    return ""


## Nouns and adjectives

def suggPlur (sFlex, sWordToAgree=None):
    "returns plural forms assuming sFlex is singular"
    if sWordToAgree:
        if sWordToAgree not in _dAnalyses and not _storeMorphFromFSA(sWordToAgree):
            return ""
        sGender = cr.getGender(_dAnalyses.get(sWordToAgree, []))
        if sGender == ":m":
            return suggMasPlur(sFlex)
        elif sGender == ":f":
            return suggFemPlur(sFlex)
    aSugg = set()
    if "-" not in sFlex:
        if sFlex.endswith("l"):
            if sFlex.endswith("al") and len(sFlex) > 2 and _oDict.isValid(sFlex[:-1]+"ux"):
                aSugg.add(sFlex[:-1]+"ux")
            if sFlex.endswith("ail") and len(sFlex) > 3 and _oDict.isValid(sFlex[:-2]+"ux"):
                aSugg.add(sFlex[:-2]+"ux")
        if _oDict.isValid(sFlex+"s"):
            aSugg.add(sFlex+"s")
        if _oDict.isValid(sFlex+"x"):
            aSugg.add(sFlex+"x")
    if mfsp.hasMiscPlural(sFlex):
        aSugg.update(mfsp.getMiscPlural(sFlex))
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggSing (sFlex):
    "returns singular forms assuming sFlex is plural"
    if "-" in sFlex:
        return ""
    aSugg = set()
    if sFlex.endswith("ux"):
        if _oDict.isValid(sFlex[:-2]+"l"):
            aSugg.add(sFlex[:-2]+"l")
        if _oDict.isValid(sFlex[:-2]+"il"):
            aSugg.add(sFlex[:-2]+"il")
    if _oDict.isValid(sFlex[:-1]):
        aSugg.add(sFlex[:-1])
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggMasSing (sFlex, bSuggSimil=False):
    "returns masculine singular forms"
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    for sMorph in _dAnalyses.get(sFlex, []):
        if not ":V" in sMorph:
            # not a verb
            if ":m" in sMorph or ":e" in sMorph:
                aSugg.add(suggSing(sFlex))
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isFemForm(sStem):
                    aSugg.update(mfsp.getMasForm(sStem, False))
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":PQ", ":Q1") and conj.hasConj(sVerb, ":PQ", ":Q3"):
                # We also check if the verb has a feminine form.
                # If not, we consider it’s better to not suggest the masculine one, as it can be considered invariable.
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q1"))
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":m:[si]"):
            aSugg.add(e)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggMasPlur (sFlex, bSuggSimil=False):
    "returns masculine plural forms"
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    for sMorph in _dAnalyses.get(sFlex, []):
        if not ":V" in sMorph:
            # not a verb
            if ":m" in sMorph or ":e" in sMorph:
                aSugg.add(suggPlur(sFlex))
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isFemForm(sStem):
                    aSugg.update(mfsp.getMasForm(sStem, True))
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":PQ", ":Q2"):
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q2"))
            elif conj.hasConj(sVerb, ":PQ", ":Q1"):
                sSugg = conj.getConj(sVerb, ":PQ", ":Q1")
                # it is necessary to filter these flexions, like “succédé” or “agi” that are not masculine plural.
                if sSugg.endswith("s"):
                    aSugg.add(sSugg)
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":m:[pi]"):
            aSugg.add(e)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggFemSing (sFlex, bSuggSimil=False):
    "returns feminine singular forms"
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    for sMorph in _dAnalyses.get(sFlex, []):
        if not ":V" in sMorph:
            # not a verb
            if ":f" in sMorph or ":e" in sMorph:
                aSugg.add(suggSing(sFlex))
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isFemForm(sStem):
                    aSugg.add(sStem)
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":PQ", ":Q3"):
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q3"))
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":f:[si]"):
            aSugg.add(e)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggFemPlur (sFlex, bSuggSimil=False):
    "returns feminine plural forms"
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    for sMorph in _dAnalyses.get(sFlex, []):
        if not ":V" in sMorph:
            # not a verb
            if ":f" in sMorph or ":e" in sMorph:
                aSugg.add(suggPlur(sFlex))
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isFemForm(sStem):
                    aSugg.add(sStem+"s")
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":PQ", ":Q4"):
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q4"))
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":f:[pi]"):
            aSugg.add(e)
    if aSugg:
        return "|".join(aSugg)
    return ""


def hasFemForm (sFlex):
    for sStem in stem(sFlex):
        if mfsp.isFemForm(sStem) or conj.hasConj(sStem, ":PQ", ":Q3"):
            return True
    if phonet.hasSimil(sFlex, ":f"):
        return True
    return False


def hasMasForm (sFlex):
    for sStem in stem(sFlex):
        if mfsp.isFemForm(sStem) or conj.hasConj(sStem, ":PQ", ":Q1"):
            # what has a feminine form also has a masculine form
            return True
    if phonet.hasSimil(sFlex, ":m"):
        return True
    return False


def switchGender (sFlex, bPlur=None):
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    if bPlur == None:
        for sMorph in _dAnalyses.get(sFlex, []):
            if ":f" in sMorph:
                if ":s" in sMorph:
                    aSugg.add(suggMasSing(sFlex))
                elif ":p" in sMorph:
                    aSugg.add(suggMasPlur(sFlex))
            elif ":m" in sMorph:
                if ":s" in sMorph:
                    aSugg.add(suggFemSing(sFlex))
                elif ":p" in sMorph:
                    aSugg.add(suggFemPlur(sFlex))
                else:
                    aSugg.add(suggFemSing(sFlex))
                    aSugg.add(suggFemPlur(sFlex))
    elif bPlur:
        for sMorph in _dAnalyses.get(sFlex, []):
            if ":f" in sMorph:
                aSugg.add(suggMasPlur(sFlex))
            elif ":m" in sMorph:
                aSugg.add(suggFemPlur(sFlex))
    else:
        for sMorph in _dAnalyses.get(sFlex, []):
            if ":f" in sMorph:
                aSugg.add(suggMasSing(sFlex))
            elif ":m" in sMorph:
                aSugg.add(suggFemSing(sFlex))
    if aSugg:
        return "|".join(aSugg)
    return ""


def switchPlural (sFlex):
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = set()
    for sMorph in _dAnalyses.get(sFlex, []):
        if ":s" in sMorph:
            aSugg.add(suggPlur(sFlex))
        elif ":p" in sMorph:
            aSugg.add(suggSing(sFlex))
    if aSugg:
        return "|".join(aSugg)
    return ""


def hasSimil (sWord, sPattern=None):
    return phonet.hasSimil(sWord, sPattern)


def suggSimil (sWord, sPattern=None):
    "return list of words phonetically similar to sWord and whom POS is matching sPattern"
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    aSugg = phonet.selectSimil(sWord, sPattern)
    for sMorph in _dAnalyses.get(sWord, []):
        for e in conj.getSimil(sWord, sMorph, sPattern):
            aSugg.add(e)
        #aSugg = aSugg.union(conj.getSimil(sWord, sMorph))
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggCeOrCet (sWord):
    if re.match("(?i)[aeéèêiouyâîï]", sWord):
        return "cet"
    if sWord[0:1] == "h" or sWord[0:1] == "H":
        return "ce|cet"
    return "ce"


def suggLesLa (sWord):
    # we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    if any( ":p" in sMorph  for sMorph in _dAnalyses.get(sWord, []) ):
        return "les|la"
    return "la"


_zBinary = re.compile("^[01]+$")

def formatNumber (s):
    nLen = len(s)
    if nLen < 4:
        return s
    sRes = ""
    # nombre ordinaire
    nEnd = nLen
    while nEnd > 0:
        nStart = max(nEnd-3, 0)
        sRes = s[nStart:nEnd] + " " + sRes  if sRes  else s[nStart:nEnd]
        nEnd = nEnd - 3
    # binaire
    if _zBinary.search(s):
        nEnd = nLen
        sBin = ""
        while nEnd > 0:
            nStart = max(nEnd-4, 0)
            sBin = s[nStart:nEnd] + " " + sBin  if sBin  else s[nStart:nEnd]
            nEnd = nEnd - 4
        sRes += "|" + sBin
    # numéros de téléphone
    if nLen == 10:
        if s.startswith("0"):
            sRes += "|" + s[0:2] + " " + s[2:4] + " " + s[4:6] + " " + s[6:8] + " " + s[8:] # téléphone français
            if s[1] == "4" and (s[2]=="7" or s[2]=="8" or s[2]=="9"):
                sRes += "|" + s[0:4] + " " + s[4:6] + " " + s[6:8] + " " + s[8:]            # mobile belge
            sRes += "|" + s[0:3] + " " + s[3:6] + " " + s[6:8] + " " + s[8:]                # téléphone suisse
        sRes += "|" + s[0:4] + " " + s[4:7] + "-" + s[7:]                                   # téléphone canadien ou américain
    elif nLen == 9 and s.startswith("0"):
        sRes += "|" + s[0:3] + " " + s[3:5] + " " + s[5:7] + " " + s[7:9]                   # fixe belge 1
        sRes += "|" + s[0:2] + " " + s[2:5] + " " + s[5:7] + " " + s[7:9]                   # fixe belge 2
    return sRes


def formatNF (s):
    try:
        m = re.match("NF[  -]?(C|E|P|Q|S|X|Z|EN(?:[  -]ISO|))[  -]?([0-9]+(?:[/‑-][0-9]+|))", s)
        if not m:
            return ""
        return "NF " + m.group(1).upper().replace(" ", " ").replace("-", " ") + " " + m.group(2).replace("/", "‑").replace("-", "‑")
    except:
        traceback.print_exc()
        return "# erreur #"


def undoLigature (c):
    if c == "ﬁ":
        return "fi"
    elif c == "ﬂ":
        return "fl"
    elif c == "ﬀ":
        return "ff"
    elif c == "ﬃ":
        return "ffi"
    elif c == "ﬄ":
        return "ffl"
    elif c == "ﬅ":
        return "ft"
    elif c == "ﬆ":
        return "st"
    return "_"
