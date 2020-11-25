"""
Grammar checking functions
"""

# generated code, do not edit
# template: <gc_core/py/lang_core/gc_functions.py>
# variables generated in <compile_rules.py>


import re

from . import gc_options
from ..graphspell.echo import echo


_sAppContext = "Python"         # what software is running
_oSpellChecker = None


def load (sContext, oSpellChecker):
    global _sAppContext
    global _oSpellChecker
    _sAppContext = sContext
    _oSpellChecker = oSpellChecker


#### common functions

def option (sOpt):
    "return True if option <sOpt> is active"
    return gc_options.dOptions.get(sOpt, False)


#### Functions to get text outside pattern scope

# warning: check compile_rules.py to understand how it works

_zNextWord = re.compile(r" +(\w[\w-]*)")
_zPrevWord = re.compile(r"(\w[\w-]*) +$")

def nextword (s, iStart, n):
    "get the nth word of the input string or empty string"
    m = re.match("(?: +[\\w%-]+){" + str(n-1) + "} +([\\w%-]+)", s[iStart:])
    if not m:
        return None
    return (iStart+m.start(1), m.group(1))


def prevword (s, iEnd, n):
    "get the (-)nth word of the input string or empty string"
    m = re.search("([\\w%-]+) +(?:[\\w%-]+ +){" + str(n-1) + "}$", s[:iEnd])
    if not m:
        return None
    return (m.start(1), m.group(1))


def nextword1 (s, iStart):
    "get next word (optimization)"
    m = _zNextWord.match(s[iStart:])
    if not m:
        return None
    return (iStart+m.start(1), m.group(1))


def prevword1 (s, iEnd):
    "get previous word (optimization)"
    m = _zPrevWord.search(s[:iEnd])
    if not m:
        return None
    return (m.start(1), m.group(1))


def look (s, sPattern, sNegPattern=None):
    "seek sPattern in s (before/after/fulltext), if sNegPattern not in s"
    if sNegPattern and re.search(sNegPattern, s):
        return False
    if re.search(sPattern, s):
        return True
    return False


def look_chk1 (dTokenPos, s, nOffset, sPattern, sPatternGroup1, sNegPatternGroup1=""):
    "returns True if s has pattern sPattern and m.group(1) has pattern sPatternGroup1"
    m = re.search(sPattern, s)
    if not m:
        return False
    try:
        sWord = m.group(1)
        nPos = m.start(1) + nOffset
    except IndexError:
        return False
    return morph(dTokenPos, (nPos, sWord), sPatternGroup1, sNegPatternGroup1)



#### Analyse groups for regex rules

def info (dTokenPos, tWord):
    "for debugging: retrieve info of word"
    if not tWord:
        echo("> nothing to find")
        return True
    lMorph = _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        echo("> not in dictionary")
        return True
    echo("TOKENS:", dTokenPos)
    if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]:
        echo("DA: " + str(dTokenPos[tWord[0]]["lMorph"]))
    echo("FSA: " + str(lMorph))
    return True


def morph (dTokenPos, tWord, sPattern, sNegPattern="", bNoWord=False):
    "analyse a tuple (position, word), returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    lMorph = dTokenPos[tWord[0]]["lMorph"]  if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]  else _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            # all morph must match sPattern
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        zNegPattern = re.compile(sNegPattern)
        if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
            return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def analyse (sWord, sPattern, sNegPattern=""):
    "analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        zNegPattern = re.compile(sNegPattern)
        if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
            return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


#### Analyse tokens for graph rules

def g_value (dToken, sValues, nLeft=None, nRight=None):
    "test if <dToken['sValue']> is in sValues (each value should be separated with |)"
    sValue = "|"+dToken["sValue"]+"|"  if nLeft is None  else "|"+dToken["sValue"][slice(nLeft, nRight)]+"|"
    if sValue in sValues:
        return True
    if dToken["sValue"][0:2].istitle(): # we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
        if sValue.lower() in sValues:
            return True
    elif dToken["sValue"].isupper():
        #if sValue.lower() in sValues:
        #    return True
        sValue = "|"+sValue[1:].capitalize()
        if sValue in sValues:
            return True
        sValue = sValue.lower()
        if sValue in sValues:
            return True
    return False


def g_morph (dToken, sPattern, sNegPattern="", nLeft=None, nRight=None, bMemorizeMorph=True):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies"
    if "lMorph" in dToken:
        lMorph = dToken["lMorph"]
    else:
        if nLeft is not None:
            lMorph = _oSpellChecker.getMorph(dToken["sValue"][slice(nLeft, nRight)])
            if bMemorizeMorph:
                dToken["lMorph"] = lMorph
        else:
            lMorph = _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            # all morph must match sPattern
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        zNegPattern = re.compile(sNegPattern)
        if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
            return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def g_analyse (dToken, sPattern, sNegPattern="", nLeft=None, nRight=None, bMemorizeMorph=True):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)"
    if nLeft is not None:
        lMorph = _oSpellChecker.getMorph(dToken["sValue"][slice(nLeft, nRight)])
        if bMemorizeMorph:
            dToken["lMorph"] = lMorph
    else:
        lMorph = _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            # all morph must match sPattern
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        zNegPattern = re.compile(sNegPattern)
        if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
            return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def g_merged_analyse (dToken1, dToken2, cMerger, sPattern, sNegPattern="", bSetMorph=True):
    "merge two token values, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(dToken1["sValue"] + cMerger + dToken2["sValue"])
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            # all morph must match sPattern
            zPattern = re.compile(sPattern)
            bResult = all(zPattern.search(sMorph)  for sMorph in lMorph)
            if bResult and bSetMorph:
                dToken1["lMorph"] = lMorph
            return bResult
        zNegPattern = re.compile(sNegPattern)
        if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
            return False
    # search sPattern
    zPattern = re.compile(sPattern)
    bResult = any(zPattern.search(sMorph)  for sMorph in lMorph)
    if bResult and bSetMorph:
        dToken1["lMorph"] = lMorph
    return bResult


def g_tagbefore (dToken, dTags, sTag):
    "returns True if <sTag> is present on tokens before <dToken>"
    if sTag not in dTags:
        return False
    if dToken["i"] > dTags[sTag][0]:
        return True
    return False


def g_tagafter (dToken, dTags, sTag):
    "returns True if <sTag> is present on tokens after <dToken>"
    if sTag not in dTags:
        return False
    if dToken["i"] < dTags[sTag][1]:
        return True
    return False


def g_tag (dToken, sTag):
    "returns True if <sTag> is present on token <dToken>"
    return "aTags" in dToken and sTag in dToken["aTags"]


def g_meta (dToken, sType):
    "returns True if <sType> is equal to the token type"
    return dToken["sType"] == sType


def g_space_between_tokens (dToken1, dToken2, nMin, nMax=None):
    "checks if spaces between tokens is >= <nMin> and <= <nMax>"
    nSpace = dToken2["nStart"] - dToken1["nEnd"]
    if nSpace < nMin:
        return False
    if nMax is not None and nSpace > nMax:
        return False
    return True


def g_token (lToken, i):
    "return token at index <i> in lToken (or the closest one)"
    if i < 0:
        return lToken[0]
    if i >= len(lToken):
        return lToken[-1]
    return lToken[i]



#### Disambiguator for regex rules

def select (dTokenPos, nPos, sWord, sPattern):
    "Disambiguation: select morphologies of <sWord> matching <sPattern>"
    if not sWord:
        return True
    if nPos not in dTokenPos:
        echo("Error. There should be a token at this position: ", nPos)
        return True
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect and len(lSelect) != len(lMorph):
        dTokenPos[nPos]["lMorph"] = lSelect
    return True


def exclude (dTokenPos, nPos, sWord, sPattern):
    "Disambiguation: exclude morphologies of <sWord> matching <sPattern>"
    if not sWord:
        return True
    if nPos not in dTokenPos:
        echo("Error. There should be a token at this position: ", nPos)
        return True
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect and len(lSelect) != len(lMorph):
        dTokenPos[nPos]["lMorph"] = lSelect
    return True


def define (dTokenPos, nPos, sMorphs):
    "Disambiguation: set morphologies of token at <nPos> with <sMorphs>"
    if nPos not in dTokenPos:
        echo("Error. There should be a token at this position: ", nPos)
        return True
    dTokenPos[nPos]["lMorph"] = sMorphs.split("|")
    return True


#### Disambiguation for graph rules

def g_select (dToken, sPattern):
    "Disambiguation: select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect and len(lSelect) != len(lMorph):
        dToken["lMorph"] = lSelect
    #echo("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_exclude (dToken, sPattern):
    "Disambiguation: select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect and len(lSelect) != len(lMorph):
        dToken["lMorph"] = lSelect
    #echo("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_addmorph (dToken, sNewMorph):
    "Disambiguation: add a morphology to a token"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    lMorph.extend(sNewMorph.split("|"))
    dToken["lMorph"] = lMorph
    return True


def g_rewrite (dToken, sToReplace, sReplace):
    "Disambiguation: rewrite morphologies"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    dToken["lMorph"] = [ sMorph.replace(sToReplace, sReplace)  for sMorph in lMorph ]
    return True


def g_define (dToken, sMorphs):
    "Disambiguation: set morphologies of <dToken>, always return True"
    dToken["lMorph"] = sMorphs.split("|")
    #echo("DA:", dToken["sValue"], lMorph)
    return True


def g_definefrom (dToken, nLeft=None, nRight=None):
    "Disambiguation: set morphologies of <dToken> with slicing its value with <nLeft> and <nRight>"
    if nLeft is not None:
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"][slice(nLeft, nRight)])
    else:
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"])
    return True


def g_setmeta (dToken, sType):
    "Disambiguation: change type of token"
    dToken["sType"] = sType
    return True



#### GRAMMAR CHECKER PLUGINS

${plugins}


#### CALLABLES FOR REGEX RULES (generated code)

${callables}


#### CALLABLES FOR GRAPH RULES (generated code)

${graph_callables}
