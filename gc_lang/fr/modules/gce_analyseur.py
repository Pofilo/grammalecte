#### GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

from . import cregex as cr


def g_morphVC (dToken, sPattern, sNegPattern=""):
    "lance la fonction g_morph() sur la première partie d’un verbe composé (ex: vient-il)"
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
    if s2 in ("elle", "elles"):
        if cr.mbNprMasNotFem(_oSpellChecker.getMorph(s1)):
            return "ils"
        # si épicène, indéterminable, mais OSEF, le féminin l’emporte
        return "elles"
    return s1 + " et " + s2


def apposition (sWord1, sWord2):
    "returns True if nom + nom (no agreement required)"
    return len(sWord2) < 2 or (cr.mbNomNotAdj(_oSpellChecker.getMorph(sWord2)) and cr.mbPpasNomNotAdj(_oSpellChecker.getMorph(sWord1)))


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
    lMorph2 = _oSpellChecker.getMorph(sWord2)
    if not lMorph2:
        return False
    if cr.checkConjVerb(lMorph2, sReqMorphConj):
        # verb word2 is ok
        return False
    lMorph1 = _oSpellChecker.getMorph(sWord1)
    if not lMorph1:
        return False
    if cr.checkAgreement(lMorph1, lMorph2) and (cr.mbAdj(lMorph2) or cr.mbAdj(lMorph1)):
        return False
    return True


def isVeryAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj, bLastHopeCond):
    "use it if <sWord1> can be also a verb; <sWord2> is assumed to be True via isAmbiguousNAV"
    lMorph2 = _oSpellChecker.getMorph(sWord2)
    if not lMorph2:
        return False
    if cr.checkConjVerb(lMorph2, sReqMorphConj):
        # verb word2 is ok
        return False
    lMorph1 = _oSpellChecker.getMorph(sWord1)
    if not lMorph1:
        return False
    if cr.checkAgreement(lMorph1, lMorph2) and (cr.mbAdj(lMorph2) or cr.mbAdjNb(lMorph1)):
        return False
    # now, we know there no agreement, and conjugation is also wrong
    if cr.isNomAdj(lMorph1):
        return True
    #if cr.isNomAdjVerb(lMorph1): # considered True
    if bLastHopeCond:
        return True
    return False


def checkAgreement (sWord1, sWord2):
    "check agreement between <sWord1> and <sWord1>"
    lMorph2 = _oSpellChecker.getMorph(sWord2)
    if not lMorph2:
        return True
    lMorph1 = _oSpellChecker.getMorph(sWord1)
    if not lMorph1:
        return True
    return cr.checkAgreement(lMorph1, lMorph2)


_zUnitSpecial = re.compile("[µ/⁰¹²³⁴⁵⁶⁷⁸⁹Ωℓ·]")
_zUnitNumbers = re.compile("[0-9]")

def mbUnit (s):
    "returns True it can be a measurement unit"
    if _zUnitSpecial.search(s):
        return True
    if 1 < len(s) < 16 and s[0:1].islower() and (not s[1:].islower() or _zUnitNumbers.search(s)):
        return True
    return False


#### Exceptions

aREGULARPLURAL = frozenset(["abricot", "amarante", "aubergine", "acajou", "anthracite", "brique", "caca", "café", \
                            "carotte", "cerise", "chataigne", "corail", "citron", "crème", "grave", "groseille", \
                            "jonquille", "marron", "olive", "pervenche", "prune", "sable"])
aSHOULDBEVERB = frozenset(["aller", "manger"])
