#### GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

from . import cregex as cr


def g_morphVC (dToken, sPattern, sNegPattern=""):
    nEnd = dToken["sValue"].rfind("-")
    if "-t-" in dToken["sValue"]:
        nEnd = nEnd - 2
    return g_morph(dToken, sPattern, sNegPattern, 0, nEnd, False)


def rewriteSubject (s1, s2):
    "rewrite complex subject: <s1> a prn/patr/npr (M[12P]) followed by “et” and <s2>"
    if s2 == "lui":
        return "ils"
    if s2 == "moi":
        return "nous"
    if s2 == "toi":
        return "vous"
    if s2 == "nous":
        return "nous"
    if s2 == "vous":
        return "vous"
    if s2 == "eux":
        return "ils"
    if s2 == "elle" or s2 == "elles":
        if cr.mbNprMasNotFem(_oSpellChecker.getMorph(s1)):
            return "ils"
        # si épicène, indéterminable, mais OSEF, le féminin l’emporte
        return "elles"
    return s1 + " et " + s2


def apposition (sWord1, sWord2):
    "returns True if nom + nom (no agreement required)"
    return len(sWord2) < 2 and cr.mbNomNotAdj(_oSpellChecker.getMorph(sWord2)) and cr.mbPpasNomNotAdj(_oSpellChecker.getMorph(sWord1))


def isAmbiguousNAV (sWord):
    "words which are nom|adj and verb are ambiguous (except être and avoir)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not cr.mbNomAdj(lMorph) or sWord == "est":
        return False
    if cr.mbVconj(lMorph) and not cr.mbMG(lMorph):
        return True
    return False


def isAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj):
    "use it if <sWord1> won’t be a verb; <sWord2> is assumed to be True via isAmbiguousNAV"
    a2 = _oSpellChecker.getMorph(sWord2)
    if not a2:
        return False
    if cr.checkConjVerb(a2, sReqMorphConj):
        # verb word2 is ok
        return False
    a1 = _oSpellChecker.getMorph(sWord1)
    if not a1:
        return False
    if cr.checkAgreement(a1, a2) and (cr.mbAdj(a2) or cr.mbAdj(a1)):
        return False
    return True


def isVeryAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj, bLastHopeCond):
    "use it if <sWord1> can be also a verb; <sWord2> is assumed to be True via isAmbiguousNAV"
    a2 = _oSpellChecker.getMorph(sWord2)
    if not a2:
        return False
    if cr.checkConjVerb(a2, sReqMorphConj):
        # verb word2 is ok
        return False
    a1 = _oSpellChecker.getMorph(sWord1)
    if not a1:
        return False
    if cr.checkAgreement(a1, a2) and (cr.mbAdj(a2) or cr.mbAdjNb(a1)):
        return False
    # now, we know there no agreement, and conjugation is also wrong
    if cr.isNomAdj(a1):
        return True
    #if cr.isNomAdjVerb(a1): # considered True
    if bLastHopeCond:
        return True
    return False


def checkAgreement (sWord1, sWord2):
    "check agreement between <sWord1> and <sWord1>"
    a2 = _oSpellChecker.getMorph(sWord2)
    if not a2:
        return True
    a1 = _oSpellChecker.getMorph(sWord1)
    if not a1:
        return True
    return cr.checkAgreement(a1, a2)


_zUnitSpecial = re.compile("[µ/⁰¹²³⁴⁵⁶⁷⁸⁹Ωℓ·]")
_zUnitNumbers = re.compile("[0-9]")

def mbUnit (s):
    "returns True it can be a measurement unit"
    if _zUnitSpecial.search(s):
        return True
    if 1 < len(s) < 16 and s[0:1].islower() and (not s[1:].islower() or _zUnitNumbers.search(s)):
        return True
    return False


#### Syntagmes

_zEndOfNG1 = re.compile(" *$| +(?:, +|)(?:n(?:’|e |o(?:u?s|tre) )|l(?:’|e(?:urs?|s|) |a )|j(?:’|e )|m(?:’|es? |a |on )|t(?:’|es? |a |u )|s(?:’|es? |a )|c(?:’|e(?:t|tte|s|) )|ç(?:a |’)|ils? |vo(?:u?s|tre) )")
_zEndOfNG2 = re.compile(r" +(\w[\w-]+)")
_zEndOfNG3 = re.compile(r" *, +(\w[\w-]+)")

def isEndOfNG (dDA, s, iOffset):
    "returns True if next word doesn’t belong to a noun group"
    if _zEndOfNG1.match(s):
        return True
    m = _zEndOfNG2.match(s)
    if m and morphex(dDA, (iOffset+m.start(1), m.group(1)), ":[VR]", ":[NAQP]"):
        return True
    m = _zEndOfNG3.match(s)
    if m and not morph(dDA, (iOffset+m.start(1), m.group(1)), ":[NA]", False):
        return True
    return False


_zNextIsNotCOD1 = re.compile(" *,")
_zNextIsNotCOD2 = re.compile(" +(?:[mtsnj](e +|’)|[nv]ous |tu |ils? |elles? )")
_zNextIsNotCOD3 = re.compile(r" +([a-zéèî][\w-]+)")

def isNextNotCOD (dDA, s, iOffset):
    "returns True if next word is not a COD"
    if _zNextIsNotCOD1.match(s) or _zNextIsNotCOD2.match(s):
        return True
    m = _zNextIsNotCOD3.match(s)
    if m and morphex(dDA, (iOffset+m.start(1), m.group(1)), ":[123][sp]", ":[DM]"):
        return True
    return False


_zNextIsVerb1 = re.compile(" +[nmts](?:e |’)")
_zNextIsVerb2 = re.compile(r" +(\w[\w-]+)")

def isNextVerb (dDA, s, iOffset):
    "returns True if next word is a verb"
    if _zNextIsVerb1.match(s):
        return True
    m = _zNextIsVerb2.match(s)
    if m and morph(dDA, (iOffset+m.start(1), m.group(1)), ":[123][sp]", False):
        return True
    return False


#### Exceptions

aREGULARPLURAL = frozenset(["abricot", "amarante", "aubergine", "acajou", "anthracite", "brique", "caca", "café", \
                            "carotte", "cerise", "chataigne", "corail", "citron", "crème", "grave", "groseille", \
                            "jonquille", "marron", "olive", "pervenche", "prune", "sable"])
aSHOULDBEVERB = frozenset(["aller", "manger"])
