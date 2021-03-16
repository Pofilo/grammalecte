#### GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

from . import cregex as cr


def g_morphVC (dToken, sPattern, sNegPattern=""):
    "lance la fonction g_morph() sur la première partie d’un verbe composé (ex: vient-il)"
    nEnd = dToken["sValue"].rfind("-")
    if dToken["sValue"].count("-") > 1:
        if "-t-" in dToken["sValue"]:
            nEnd = nEnd - 2
        elif re.search("-l(?:es?|a)-(?:[mt]oi|nous|leur)$|(?:[nv]ous|lui|leur)-en$", dToken["sValue"]):
            nEnd = dToken["sValue"][0:nEnd].rfind("-")
    return g_morph(dToken, sPattern, sNegPattern, 0, nEnd)


def apposition (sWord1, sWord2):
    "returns True if nom + nom (no agreement required)"
    return len(sWord2) < 2 or (cr.mbNomNotAdj(_oSpellChecker.getMorph(sWord2)) and cr.mbPpasNomNotAdj(_oSpellChecker.getMorph(sWord1)))


def g_agreement (dToken1, dToken2, bNotOnlyNames=True):
    "check agreement between <dToken1> and <dToken2>"
    lMorph1 = dToken1["lMorph"]  if "lMorph" in dToken1  else  _oSpellChecker.getMorph(dToken1["sValue"])
    if not lMorph1:
        return True
    lMorph2 = dToken2["lMorph"]  if "lMorph" in dToken2  else  _oSpellChecker.getMorph(dToken2["sValue"])
    if not lMorph2:
        return True
    if bNotOnlyNames and not (cr.mbAdj(lMorph2) or cr.mbAdjNb(lMorph1)):
        return False
    return cr.agreement(lMorph1, lMorph2)


_zUnitSpecial = re.compile("[µ/⁰¹²³⁴⁵⁶⁷⁸⁹Ωℓ·]")
_zUnitNumbers = re.compile("[0-9]")

def mbUnit (s):
    "returns True it can be a measurement unit"
    if _zUnitSpecial.search(s):
        return True
    if 1 < len(s) < 16 and s[0:1].islower() and (not s[1:].islower() or _zUnitNumbers.search(s)):
        return True
    return False

def queryNamesPOS (sWord1, sWord2):
    "returns POS tag for <sWord1> and <sWord2> as a whole"
    lMorph1 = _oSpellChecker.getMorph(sWord1)
    lMorph2 = _oSpellChecker.getMorph(sWord2)
    if not lMorph1 or not lMorph2:
        return ":N:e:p"
    sGender1, _ = cr.getGenderNumber(lMorph1)
    sGender2, _ = cr.getGenderNumber(lMorph2)
    if sGender1 == ":m" or sGender2 == ":m":
        return ":N:m:p"
    if sGender1 == ":f" or sGender2 == ":f":
        return ":N:f:p"
    return ":N:e:p"
