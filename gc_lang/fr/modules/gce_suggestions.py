#### GRAMMAR CHECKING ENGINE PLUGIN: Suggestion mechanisms

from . import conj
from . import mfsp
from . import phonet


## Verbs

def splitVerb (sVerb):
    "renvoie le verbe et les pronoms séparément"
    iRight = sVerb.rfind("-")
    sSuffix = sVerb[iRight:]
    sVerb = sVerb[:iRight]
    if sVerb.endswith(("-t", "-le", "-la", "-les", "-nous", "-vous", "-leur", "-lui")):
        iRight = sVerb.rfind("-")
        sSuffix = sVerb[iRight:] + sSuffix
        sVerb = sVerb[:iRight]
    return sVerb, sSuffix


def suggVerb (sFlex, sWho, bVC=False, funcSugg2=None, *args):
    "change <sFlex> conjugation according to <sWho>"
    if bVC:
        sFlex, sSfx = splitVerb(sFlex)
    dSugg = {}
    for sStem in _oSpellChecker.getLemma(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            # we get the tense
            aTense = {} # we use dict as ordered set
            for sMorph in _oSpellChecker.getMorph(sFlex):
                for m in re.finditer(">"+sStem+"/.*?(:(?:Y|I[pqsf]|S[pq]|K|P|Q))", sMorph):
                    # stem must be used in regex to prevent confusion between different verbs (e.g. sauras has 2 stems: savoir and saurer)
                    if m:
                        if m.group(1) == ":Y" or m.group(1) == ":Q":
                            aTense[":Ip"] = ""
                            aTense[":Iq"] = ""
                            aTense[":Is"] = ""
                        elif m.group(1) == ":P":
                            aTense[":Ip"] = ""
                        else:
                            aTense[m.group(1)] = ""
            for sTense in aTense:
                if sWho == ":1ś" and not conj._hasConjWithTags(tTags, sTense, ":1ś"):
                    sWho = ":1s"
                if conj._hasConjWithTags(tTags, sTense, sWho):
                    dSugg[conj._getConjWithTags(sStem, tTags, sTense, sWho)] = ""
    if funcSugg2:
        sSugg2 = funcSugg2(*args)  if args  else funcSugg2(sFlex)
        if sSugg2:
            dSugg[sSugg2] = ""
    if dSugg:
        if bVC:
            return "|".join([ joinVerbAndSuffix(sSugg, sSfx)  for sSugg in dSugg ])
        return "|".join(dSugg)
    return ""


def joinVerbAndSuffix (sFlex, sSfx):
    "join <sFlex> verb with <sSfx> suffix, modifying <sFlex> to prevent irregular forms"
    if sSfx.startswith(("-t-", "-T-")) and sFlex.endswith(("t", "d", "T", "D")):
        return sFlex + sSfx[2:]
    if sFlex.endswith(("e", "a", "c", "E", "A", "C")):
        if re.match("(?i)-(?:en|y)$", sSfx):
            return sFlex + "s" + sSfx
        if re.match("(?i)-(?:ie?l|elle|on)$", sSfx):
            return sFlex + "-t" + sSfx
    return sFlex + sSfx


def suggVerbPpas (sFlex, sPattern=None):
    "suggest past participles for <sFlex>"
    dSugg = {}
    for sStem in _oSpellChecker.getLemma(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            if not sPattern:
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:p")] = ""
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:s")] = ""
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:p")] = ""
            elif sPattern == ":m:s":
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
            elif sPattern == ":m:p":
                if conj._hasConjWithTags(tTags, ":Q", ":m:p"):
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:p")] = ""
                else:
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
            elif sPattern == ":f:s":
                if conj._hasConjWithTags(tTags, ":Q", ":f:s"):
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:s")] = ""
                else:
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
            elif sPattern == ":f:p":
                if conj._hasConjWithTags(tTags, ":Q", ":f:p"):
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:p")] = ""
                else:
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
            elif sPattern == ":s":
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:s")] = ""
            elif sPattern == ":p":
                if conj._hasConjWithTags(tTags, ":Q", ":m:p"):
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:p")] = ""
                else:
                    dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":f:p")] = ""
            else:
                dSugg[conj._getConjWithTags(sStem, tTags, ":Q", ":m:s")] = ""
    if "" in dSugg:
        del dSugg[""]
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggVerbTense (sFlex, sTense, sWho):
    "change <sFlex> to a verb according to <sTense> and <sWho>"
    dSugg = {}
    for sStem in _oSpellChecker.getLemma(sFlex):
        if conj.hasConj(sStem, sTense, sWho):
            dSugg[conj.getConj(sStem, sTense, sWho)] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggVerbFrom (sStem, sFlex, sWho=""):
    "conjugate <sStem> according to <sFlex> (and eventually <sWho>)"
    dSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        lTenses = [ m.group(0)  for m in re.finditer(":(?:Y|I[pqsf]|S[pq]|K|P)", sMorph) ]
        if sWho:
            for sTense in lTenses:
                if conj.hasConj(sStem, sTense, sWho):
                    dSugg[conj.getConj(sStem, sTense, sWho)] = ""
        else:
            for sTense in lTenses:
                for sWho2 in [ m.group(0)  for m in re.finditer(":(?:[123][sp]|P|Y)", sMorph) ]:
                    if conj.hasConj(sStem, sTense, sWho2):
                        dSugg[conj.getConj(sStem, sTense, sWho2)] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggVerbImpe (sFlex, bVC=False):
    "change <sFlex> to a verb at imperative form"
    if bVC:
        sFlex, sSfx = splitVerb(sFlex)
    aSugg = []
    for sStem in _oSpellChecker.getLemma(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            if conj._hasConjWithTags(tTags, ":E", ":2s"):
                aSugg.append(conj._getConjWithTags(sStem, tTags, ":E", ":2s"))
            if conj._hasConjWithTags(tTags, ":E", ":1p"):
                aSugg.append(conj._getConjWithTags(sStem, tTags, ":E", ":1p"))
            if conj._hasConjWithTags(tTags, ":E", ":2p"):
                aSugg.append(conj._getConjWithTags(sStem, tTags, ":E", ":2p"))
    if aSugg:
        if bVC:
            aSugg = [ joinVerbAndSuffix(sSugg, sSfx)  for sSugg in aSugg ]
        return "|".join(aSugg)
    return ""


def suggVerbInfi (sFlex):
    "returns infinitive forms of <sFlex>"
    return "|".join([ sStem  for sStem in _oSpellChecker.getLemma(sFlex)  if conj.isVerb(sStem) ])


_dQuiEst = { "je": ":1s", "j’": ":1s", "tu": ":2s", "il": ":3s", "on": ":3s", "elle": ":3s", "iel": ":3s", \
             "nous": ":1p", "vous": ":2p", "ils": ":3p", "elles": ":3p", "iels": ":3p" }

_dModeSugg = { "es": "aies", "aies": "es", "est": "ait", "ait": "est" }

def suggVerbMode (sFlex, cMode, sSuj):
    "returns other conjugations of <sFlex> acconding to <cMode> and <sSuj>"
    if cMode == ":I":
        lMode = [":Ip", ":Iq", ":Is", ":If"]
    elif cMode == ":S":
        lMode = [":Sp", ":Sq"]
    elif cMode.startswith((":I", ":S")):
        lMode = [cMode]
    else:
        return ""
    sWho = _dQuiEst.get(sSuj.lower(), sSuj)
    dSugg = {}
    for sStem in _oSpellChecker.getLemma(sFlex):
        tTags = conj._getTags(sStem)
        if tTags:
            for sTense in lMode:
                if conj._hasConjWithTags(tTags, sTense, sWho):
                    dSugg[conj._getConjWithTags(sStem, tTags, sTense, sWho)] = ""
    if sFlex in _dModeSugg:
        dSugg[_dModeSugg[sFlex]] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


## Nouns and adjectives

def suggPlur (sFlex, bSelfSugg=False):
    "returns plural forms assuming sFlex is singular"
    aSugg = []
    if sFlex.endswith("l"):
        if sFlex.endswith("al") and len(sFlex) > 2 and _oSpellChecker.isValid(sFlex[:-1]+"ux"):
            aSugg.append(sFlex[:-1]+"ux")
        if sFlex.endswith("ail") and len(sFlex) > 3 and _oSpellChecker.isValid(sFlex[:-2]+"ux"):
            aSugg.append(sFlex[:-2]+"ux")
    if sFlex.endswith("L"):
        if sFlex.endswith("AL") and len(sFlex) > 2 and _oSpellChecker.isValid(sFlex[:-1]+"UX"):
            aSugg.append(sFlex[:-1]+"UX")
        if sFlex.endswith("AIL") and len(sFlex) > 3 and _oSpellChecker.isValid(sFlex[:-2]+"UX"):
            aSugg.append(sFlex[:-2]+"UX")
    if sFlex[-1:].islower():
        if _oSpellChecker.isValid(sFlex+"s"):
            aSugg.append(sFlex+"s")
        if _oSpellChecker.isValid(sFlex+"x"):
            aSugg.append(sFlex+"x")
    else:
        if _oSpellChecker.isValid(sFlex+"S"):
            aSugg.append(sFlex+"S")
        if _oSpellChecker.isValid(sFlex+"X"):
            aSugg.append(sFlex+"X")
    if mfsp.hasMiscPlural(sFlex):
        aSugg.extend(mfsp.getMiscPlural(sFlex))
    if not aSugg and bSelfSugg and sFlex.endswith(("s", "x", "S", "X")):
        aSugg.append(sFlex)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggSing (sFlex, bSelfSugg=True):
    "returns singular forms assuming sFlex is plural"
    aSugg = []
    if sFlex.endswith("ux"):
        if _oSpellChecker.isValid(sFlex[:-2]+"l"):
            aSugg.append(sFlex[:-2]+"l")
        if _oSpellChecker.isValid(sFlex[:-2]+"il"):
            aSugg.append(sFlex[:-2]+"il")
    if sFlex.endswith("UX"):
        if _oSpellChecker.isValid(sFlex[:-2]+"L"):
            aSugg.append(sFlex[:-2]+"L")
        if _oSpellChecker.isValid(sFlex[:-2]+"IL"):
            aSugg.append(sFlex[:-2]+"IL")
    if sFlex.endswith(("s", "x", "S", "X")) and _oSpellChecker.isValid(sFlex[:-1]):
        aSugg.append(sFlex[:-1])
    if bSelfSugg and not aSugg:
        aSugg.append(sFlex)
    if aSugg:
        return "|".join(aSugg)
    return ""


def suggMasSing (sFlex, bSuggSimil=False):
    "returns masculine singular forms"
    dSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        if not ":V" in sMorph:
            # not a verb
            if ":m" in sMorph or ":e" in sMorph:
                dSugg[suggSing(sFlex)] = ""
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isMasForm(sStem):
                    dSugg[sStem] = ""
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":Q", ":m:s") and conj.hasConj(sVerb, ":Q", ":f:s"):
                # We also check if the verb has a feminine form.
                # If not, we consider it’s better to not suggest the masculine one, as it can be considered invariable.
                dSugg[conj.getConj(sVerb, ":Q", ":m:s")] = ""
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":m:[si]"):
            dSugg[e] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggMasPlur (sFlex, bSuggSimil=False):
    "returns masculine plural forms"
    dSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        if not ":V" in sMorph:
            # not a verb
            if ":m" in sMorph or ":e" in sMorph:
                dSugg[suggPlur(sFlex)] = ""
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isMasForm(sStem):
                    dSugg[suggPlur(sStem, True)] = ""
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":Q", ":m:p"):
                dSugg[conj.getConj(sVerb, ":Q", ":m:p")] = ""
            elif conj.hasConj(sVerb, ":Q", ":m:s"):
                sSugg = conj.getConj(sVerb, ":Q", ":m:s")
                # it is necessary to filter these flexions, like “succédé” or “agi” that are not masculine plural.
                if sSugg.endswith("s"):
                    dSugg[sSugg] = ""
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":m:[pi]"):
            dSugg[e] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggFemSing (sFlex, bSuggSimil=False):
    "returns feminine singular forms"
    dSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        if not ":V" in sMorph:
            # not a verb
            if ":f" in sMorph or ":e" in sMorph:
                dSugg[suggSing(sFlex)] = ""
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isMasForm(sStem):
                    dSugg.update(dict.fromkeys(mfsp.getFemForm(sStem, False), ""))
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":Q", ":f:s"):
                dSugg[conj.getConj(sVerb, ":Q", ":f:s")] = ""
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":f:[si]"):
            dSugg[e] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggFemPlur (sFlex, bSuggSimil=False):
    "returns feminine plural forms"
    dSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        if not ":V" in sMorph:
            # not a verb
            if ":f" in sMorph or ":e" in sMorph:
                dSugg[suggPlur(sFlex)] = ""
            else:
                sStem = cr.getLemmaOfMorph(sMorph)
                if mfsp.isMasForm(sStem):
                    dSugg.update(dict.fromkeys(mfsp.getFemForm(sStem, True)))
        else:
            # a verb
            sVerb = cr.getLemmaOfMorph(sMorph)
            if conj.hasConj(sVerb, ":Q", ":f:p"):
                dSugg[conj.getConj(sVerb, ":Q", ":f:p")] = ""
    if bSuggSimil:
        for e in phonet.selectSimil(sFlex, ":f:[pi]"):
            dSugg[e] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def suggAgree (sFlexDest, sFlexSrc):
    "returns suggestions for <sFlexDest> that matches agreement with <sFlexSrc>"
    lMorphSrc = _oSpellChecker.getMorph(sFlexSrc)
    if not lMorphSrc:
        return ""
    sGender, sNumber = cr.getGenderNumber(lMorphSrc)
    if sGender == ":m":
        if sNumber == ":s":
            return suggMasSing(sFlexDest)
        if sNumber == ":p":
            return suggMasPlur(sFlexDest)
        return suggMasSing(sFlexDest)
    if sGender == ":f":
        if sNumber == ":s":
            return suggFemSing(sFlexDest)
        if sNumber == ":p":
            return suggFemPlur(sFlexDest)
        return suggFemSing(sFlexDest)
    if sGender == ":e":
        if sNumber == ":s":
            return suggSing(sFlexDest)
        if sNumber == ":p":
            return suggPlur(sFlexDest)
        return sFlexDest
    return ""


def g_suggAgree (dTokenDst, dTokenSrc):
    "returns suggestions for <dTokenDst> that matches agreement with <dTokenSrc>"
    lMorphSrc = dTokenSrc["lMorph"]  if "lMorph" in dTokenSrc  else  _oSpellChecker.getMorph(dTokenSrc["sValue"])
    if not lMorphSrc:
        return ""
    sGender, sNumber = cr.getGenderNumber(lMorphSrc)
    if sGender == ":m":
        if sNumber == ":s":
            return suggMasSing(dTokenDst["sValue"])
        if sNumber == ":p":
            return suggMasPlur(dTokenDst["sValue"])
        return suggMasSing(dTokenDst["sValue"])
    if sGender == ":f":
        if sNumber == ":s":
            return suggFemSing(dTokenDst["sValue"])
        if sNumber == ":p":
            return suggFemPlur(dTokenDst["sValue"])
        return suggFemSing(dTokenDst["sValue"])
    if sGender == ":e":
        if sNumber == ":s":
            return suggSing(dTokenDst["sValue"])
        if sNumber == ":p":
            return suggPlur(dTokenDst["sValue"])
        return dTokenDst["sValue"]
    return ""


def hasFemForm (sFlex):
    "return True if there is a feminine form of <sFlex>"
    for sStem in _oSpellChecker.getLemma(sFlex):
        if mfsp.isMasForm(sStem) or conj.hasConj(sStem, ":Q", ":f:s"):
            return True
    if phonet.hasSimil(sFlex, ":f"):
        return True
    return False


def hasMasForm (sFlex):
    "return True if there is a masculine form of <sFlex>"
    for sStem in _oSpellChecker.getLemma(sFlex):
        if mfsp.isMasForm(sStem) or conj.hasConj(sStem, ":Q", ":m:s"):
            # what has a feminine form also has a masculine form
            return True
    if phonet.hasSimil(sFlex, ":m"):
        return True
    return False


def switchGender (sFlex, bPlur=None):
    "return feminine or masculine form(s) of <sFlex>"
    dSugg = {}
    if bPlur is None:
        for sMorph in _oSpellChecker.getMorph(sFlex):
            if ":f" in sMorph:
                if ":s" in sMorph:
                    dSugg[suggMasSing(sFlex)] = ""
                elif ":p" in sMorph:
                    dSugg[suggMasPlur(sFlex)] = ""
                else:
                    dSugg[suggMasSing(sFlex)] = ""
                    dSugg[suggMasPlur(sFlex)] = ""
            elif ":m" in sMorph:
                if ":s" in sMorph:
                    dSugg[suggFemSing(sFlex)] = ""
                elif ":p" in sMorph:
                    dSugg[suggFemPlur(sFlex)] = ""
                else:
                    dSugg[suggFemSing(sFlex)] = ""
                    dSugg[suggFemPlur(sFlex)] = ""
    elif bPlur:
        for sMorph in _oSpellChecker.getMorph(sFlex):
            if ":f" in sMorph:
                dSugg[suggMasPlur(sFlex)] = ""
            elif ":m" in sMorph:
                dSugg[suggFemPlur(sFlex)] = ""
    else:
        for sMorph in _oSpellChecker.getMorph(sFlex):
            if ":f" in sMorph:
                dSugg[suggMasSing(sFlex)] = ""
            elif ":m" in sMorph:
                dSugg[suggFemSing(sFlex)] = ""
    if dSugg:
        return "|".join(dSugg)
    return ""


def switchPlural (sFlex):
    "return plural or singular form(s) of <sFlex>"
    aSugg = {}
    for sMorph in _oSpellChecker.getMorph(sFlex):
        if ":s" in sMorph:
            aSugg[suggPlur(sFlex)] = ""
        elif ":p" in sMorph:
            aSugg[suggSing(sFlex)] = ""
    if aSugg:
        return "|".join(aSugg)
    return ""


def hasSimil (sWord, sPattern=None):
    "return True if there is words phonetically similar to <sWord> (according to <sPattern> if required)"
    return phonet.hasSimil(sWord, sPattern)


def suggSimil (sWord, sPattern=None, bSubst=False, bVC=False):
    "return list of words phonetically similar to <sWord> and whom POS is matching <sPattern>"
    if bVC:
        sWord, sSfx = splitVerb(sWord)
    dSugg = dict.fromkeys(phonet.selectSimil(sWord, sPattern), "")
    if not dSugg and bSubst:
        for sMorph in _oSpellChecker.getMorph(sWord):
            if ":V" in sMorph:
                sInfi = sMorph[1:sMorph.find("/")]
                if sPattern:
                    for sName in conj.getNamesFrom(sInfi):
                        if any(re.search(sPattern, sMorph2)  for sMorph2 in _oSpellChecker.getMorph(sName)):
                            dSugg[sName] = ""
                else:
                    dSugg.update(dict.fromkeys(conj.getNamesFrom(sInfi), ""))
                break
    if dSugg:
        if bVC:
            return "|".join([ joinVerbAndSuffix(sSugg, sSfx)  for sSugg in dSugg ])
        return "|".join(dSugg)
    return ""


def suggCeOrCet (sWord):
    "suggest “ce” or “cet” or both according to the first letter of <sWord>"
    if re.match("(?i)[aeéèêiouyâîï]", sWord):
        return "cet"
    if sWord[0:1] in "hH":
        return "ce|cet"
    return "ce"


def suggLesLa (sWord):
    "suggest “les” or “la” according to <sWord>"
    if any( ":p" in sMorph  for sMorph in _oSpellChecker.getMorph(sWord) ):
        return "les|la"
    return "la"


_zBinary = re.compile("^[01]+$")

def formatNumber (sNumber, bOnlySimpleFormat=False):
    "add spaces or hyphens to big numbers"
    nLen = len(sNumber)
    if nLen < 4:
        return sNumber
    sRes = ""
    if "," not in sNumber:
        # nombre entier
        sRes = _formatNumber(sNumber, 3)
        if not bOnlySimpleFormat:
            # binaire
            if _zBinary.search(sNumber):
                sRes += "|" + _formatNumber(sNumber, 4)
            # numéros de téléphone
            if nLen == 10:
                if sNumber.startswith("0"):
                    sRes += "|" + _formatNumber(sNumber, 2)                                                                 # téléphone français
                    if sNumber[1] == "4" and (sNumber[2]=="7" or sNumber[2]=="8" or sNumber[2]=="9"):
                        sRes += "|" + sNumber[0:4] + " " + sNumber[4:6] + " " + sNumber[6:8] + " " + sNumber[8:]            # mobile belge
                    sRes += "|" + sNumber[0:3] + " " + sNumber[3:6] + " " + sNumber[6:8] + " " + sNumber[8:]                # téléphone suisse
                sRes += "|" + sNumber[0:4] + " " + sNumber[4:7] + "-" + sNumber[7:]                                         # téléphone canadien ou américain
            elif nLen == 9 and sNumber.startswith("0"):
                sRes += "|" + sNumber[0:3] + " " + sNumber[3:5] + " " + sNumber[5:7] + " " + sNumber[7:9]                   # fixe belge 1
                sRes += "|" + sNumber[0:2] + " " + sNumber[2:5] + " " + sNumber[5:7] + " " + sNumber[7:9]                   # fixe belge 2
    else:
        # Nombre réel
        sInt, sFloat = sNumber.split(",", 1)
        sRes = _formatNumber(sInt, 3) + "," + sFloat
    return sRes

def _formatNumber (sNumber, nGroup=3):
    sRes = ""
    nEnd = len(sNumber)
    while nEnd > 0:
        nStart = max(nEnd-nGroup, 0)
        sRes = sNumber[nStart:nEnd] + " " + sRes  if sRes  else sNumber[nStart:nEnd]
        nEnd = nEnd - nGroup
    return sRes


def formatNF (s):
    "typography: format NF reference (norme française)"
    try:
        m = re.match("NF[  -]?(C|E|P|Q|S|X|Z|EN(?:[  -]ISO|))[  -]?([0-9]+(?:[/‑-][0-9]+|))", s)
        if not m:
            return ""
        return "NF " + m.group(1).upper().replace(" ", " ").replace("-", " ") + " " + m.group(2).replace("/", "‑").replace("-", "‑")
    except (re.error, IndexError):
        traceback.print_exc()
        return "# erreur #"


def undoLigature (c):
    "typography: split ligature character <c> in several chars"
    if c == "ﬁ":
        return "fi"
    if c == "ﬂ":
        return "fl"
    if c == "ﬀ":
        return "ff"
    if c == "ﬃ":
        return "ffi"
    if c == "ﬄ":
        return "ffl"
    if c == "ﬅ":
        return "ft"
    if c == "ﬆ":
        return "st"
    return "_"




_xNormalizedCharsForInclusiveWriting = str.maketrans({
    '(': '·',  ')': '·',
    '.': '·',  '·': '·',  '•': '·',
    '–': '·',  '—': '·',
    '/': '·'
})


def normalizeInclusiveWriting (sToken):
    "typography: replace word separators used in inclusive writing by underscore (_)"
    return sToken.translate(_xNormalizedCharsForInclusiveWriting).replace("èr·", "er·").replace("ÈR·", "ER·")
