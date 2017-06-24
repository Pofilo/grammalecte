# Grammalecte
# Grammar checker engine

import re
import sys
import os
import traceback
#import unicodedata
from itertools import chain

from ..ibdawg import IBDAWG
from ..echo import echo
from . import gc_options


__all__ = [ "lang", "locales", "pkg", "name", "version", "author", \
            "load", "parse", "getDictionary", \
            "setOption", "setOptions", "getOptions", "getDefaultOptions", "getOptionsLabels", "resetOptions", "displayOptions", \
            "ignoreRule", "resetIgnoreRules", "reactivateRule", "listRules", "displayRules" ]

__version__ = "${version}"


lang = "${lang}"
locales = ${loc}
pkg = "${implname}"
name = "${name}"
version = "${version}"
author = "${author}"

# grammar rules and dictionary
_sContext = ""                          # what software is running
_rules = None                           # module gc_rules
_dOptions = None
_aIgnoredRules = set()
_oDict = None
_dAnalyses = {}                         # cache for data from dictionary



#### Parsing

def parse (sText, sCountry="${country_default}", bDebug=False, dOptions=None, bContext=False):
    "analyses the paragraph sText and returns list of errors"
    #sText = unicodedata.normalize("NFC", sText)
    aErrors = None
    sAlt = sText
    dDA = {}        # Disambiguisator. Key = position; value = list of morphologies
    dPriority = {}  # Key = position; value = priority
    dOpt = _dOptions  if not dOptions  else dOptions

    # parse paragraph
    try:
        sNew, aErrors = _proofread(sText, sAlt, 0, True, dDA, dPriority, sCountry, dOpt, bDebug, bContext)
        if sNew:
            sText = sNew
    except:
        raise

    # cleanup
    if " " in sText:
        sText = sText.replace(" ", ' ') # nbsp
    if " " in sText:
        sText = sText.replace(" ", ' ') # nnbsp
    if "'" in sText:
        sText = sText.replace("'", "’")
    if "‑" in sText:
        sText = sText.replace("‑", "-") # nobreakdash

    # parse sentences
    for iStart, iEnd in _getSentenceBoundaries(sText):
        if 4 < (iEnd - iStart) < 2000:
            dDA.clear()
            try:
                _, errs = _proofread(sText[iStart:iEnd], sAlt[iStart:iEnd], iStart, False, dDA, dPriority, sCountry, dOpt, bDebug, bContext)
                aErrors.update(errs)
            except:
                raise
    return aErrors.values() # this is a view (iterable)


def _getSentenceBoundaries (sText):
    iStart = _zBeginOfParagraph.match(sText).end()
    for m in _zEndOfSentence.finditer(sText):
        yield (iStart, m.end())
        iStart = m.end()


def _proofread (s, sx, nOffset, bParagraph, dDA, dPriority, sCountry, dOptions, bDebug, bContext):
    dErrs = {}
    bChange = False
    bIdRule = option('idrule')

    for sOption, lRuleGroup in _getRules(bParagraph):
        if not sOption or dOptions.get(sOption, False):
            for zRegex, bUppercase, sLineId, sRuleId, nPriority, lActions in lRuleGroup:
                if sRuleId not in _aIgnoredRules:
                    for m in zRegex.finditer(s):
                        bCondMemo = None
                        for sFuncCond, cActionType, sWhat, *eAct in lActions:
                            # action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                            try:
                                bCondMemo = not sFuncCond or globals()[sFuncCond](s, sx, m, dDA, sCountry, bCondMemo)
                                if bCondMemo:
                                    if cActionType == "-":
                                        # grammar error
                                        nErrorStart = nOffset + m.start(eAct[0])
                                        if nErrorStart not in dErrs or nPriority > dPriority[nErrorStart]:
                                            dErrs[nErrorStart] = _createError(s, sx, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bIdRule, sOption, bContext)
                                            dPriority[nErrorStart] = nPriority
                                    elif cActionType == "~":
                                        # text processor
                                        s = _rewrite(s, sWhat, eAct[0], m, bUppercase)
                                        bChange = True
                                        if bDebug:
                                            echo("~ " + s + "  -- " + m.group(eAct[0]) + "  # " + sLineId)
                                    elif cActionType == "=":
                                        # disambiguation
                                        globals()[sWhat](s, m, dDA)
                                        if bDebug:
                                            echo("= " + m.group(0) + "  # " + sLineId + "\nDA: " + str(dDA))
                                    elif cActionType == ">":
                                        # we do nothing, this test is just a condition to apply all following actions
                                        pass
                                    else:
                                        echo("# error: unknown action at " + sLineId)
                                elif cActionType == ">":
                                    break
                            except Exception as e:
                                raise Exception(str(e), "# " + sLineId + " # " + sRuleId)
    if bChange:
        return (s, dErrs)
    return (False, dErrs)


def _createWriterError (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bIdRule, sOption, bContext):
    "error for Writer (LO/OO)"
    xErr = SingleProofreadingError()
    #xErr = uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
    xErr.nErrorStart = nOffset + m.start(iGroup)
    xErr.nErrorLength = m.end(iGroup) - m.start(iGroup)
    xErr.nErrorType = PROOFREADING
    xErr.aRuleIdentifier = sRuleId
    # suggestions
    if sRepl[0:1] == "=":
        sugg = globals()[sRepl[1:]](s, m)
        if sugg:
            if bUppercase and m.group(iGroup)[0:1].isupper():
                xErr.aSuggestions = tuple(map(str.capitalize, sugg.split("|")))
            else:
                xErr.aSuggestions = tuple(sugg.split("|"))
        else:
            xErr.aSuggestions = ()
    elif sRepl == "_":
        xErr.aSuggestions = ()
    else:
        if bUppercase and m.group(iGroup)[0:1].isupper():
            xErr.aSuggestions = tuple(map(str.capitalize, m.expand(sRepl).split("|")))
        else:
            xErr.aSuggestions = tuple(m.expand(sRepl).split("|"))
    # Message
    if sMsg[0:1] == "=":
        sMessage = globals()[sMsg[1:]](s, m)
    else:
        sMessage = m.expand(sMsg)
    xErr.aShortComment = sMessage   # sMessage.split("|")[0]     # in context menu
    xErr.aFullComment = sMessage   # sMessage.split("|")[-1]    # in dialog
    if bIdRule:
        xErr.aShortComment += "  # " + sLineId + " # " + sRuleId
    # URL
    if sURL:
        p = PropertyValue()
        p.Name = "FullCommentURL"
        p.Value = sURL
        xErr.aProperties = (p,)
    else:
        xErr.aProperties = ()
    return xErr


def _createDictError (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bIdRule, sOption, bContext):
    "error as a dictionary"
    dErr = {}
    dErr["nStart"] = nOffset + m.start(iGroup)
    dErr["nEnd"] = nOffset + m.end(iGroup)
    dErr["sLineId"] = sLineId
    dErr["sRuleId"] = sRuleId
    dErr["sType"] = sOption  if sOption  else "notype"
    # suggestions
    if sRepl[0:1] == "=":
        sugg = globals()[sRepl[1:]](s, m)
        if sugg:
            if bUppercase and m.group(iGroup)[0:1].isupper():
                dErr["aSuggestions"] = list(map(str.capitalize, sugg.split("|")))
            else:
                dErr["aSuggestions"] = sugg.split("|")
        else:
            dErr["aSuggestions"] = ()
    elif sRepl == "_":
        dErr["aSuggestions"] = ()
    else:
        if bUppercase and m.group(iGroup)[0:1].isupper():
            dErr["aSuggestions"] = list(map(str.capitalize, m.expand(sRepl).split("|")))
        else:
            dErr["aSuggestions"] = m.expand(sRepl).split("|")
    # Message
    if sMsg[0:1] == "=":
        sMessage = globals()[sMsg[1:]](s, m)
    else:
        sMessage = m.expand(sMsg)
    dErr["sMessage"] = sMessage
    if bIdRule:
        dErr["sMessage"] += "  # " + sLineId + " # " + sRuleId
    # URL
    dErr["URL"] = sURL  if sURL  else ""
    # Context
    if bContext:
        dErr['sUnderlined'] = sx[m.start(iGroup):m.end(iGroup)]
        dErr['sBefore'] = sx[max(0,m.start(iGroup)-80):m.start(iGroup)]
        dErr['sAfter'] = sx[m.end(iGroup):m.end(iGroup)+80]
    return dErr


def _rewrite (s, sRepl, iGroup, m, bUppercase):
    "text processor: write sRepl in s at iGroup position"
    nLen = m.end(iGroup) - m.start(iGroup)
    if sRepl == "*":
        sNew = " " * nLen
    elif sRepl == ">" or sRepl == "_" or sRepl == "~":
        sNew = sRepl + " " * (nLen-1)
    elif sRepl == "@":
        sNew = "@" * nLen
    elif sRepl[0:1] == "=":
        sNew = globals()[sRepl[1:]](s, m)
        sNew = sNew + " " * (nLen-len(sNew))
        if bUppercase and m.group(iGroup)[0:1].isupper():
            sNew = sNew.capitalize()
    else:
        sNew = m.expand(sRepl)
        sNew = sNew + " " * (nLen-len(sNew))
    return s[0:m.start(iGroup)] + sNew + s[m.end(iGroup):]


def ignoreRule (sRuleId):
    _aIgnoredRules.add(sRuleId)


def resetIgnoreRules ():
    _aIgnoredRules.clear()


def reactivateRule (sRuleId):
    _aIgnoredRules.discard(sRuleId)


def listRules (sFilter=None):
    "generator: returns typle (sOption, sLineId, sRuleId)"
    if sFilter:
        try:
            zFilter = re.compile(sFilter)
        except:
            echo("# Error. List rules: wrong regex.")
            sFilter = None
    for sOption, lRuleGroup in chain(_getRules(True), _getRules(False)):
        for _, _, sLineId, sRuleId, _, _ in lRuleGroup:
            if not sFilter or zFilter.search(sRuleId):
                yield (sOption, sLineId, sRuleId)


def displayRules (sFilter=None):
    echo("List of rules. Filter: << " + str(sFilter) + " >>")
    for sOption, sLineId, sRuleId in listRules(sFilter):
        echo("{:<10} {:<10} {}".format(sOption, sLineId, sRuleId))


#### init

try:
    # LibreOffice / OpenOffice
    from com.sun.star.linguistic2 import SingleProofreadingError
    from com.sun.star.text.TextMarkupType import PROOFREADING
    from com.sun.star.beans import PropertyValue
    #import lightproof_handler_${implname} as opt
    _createError = _createWriterError
except ImportError:
    _createError = _createDictError


def load (sContext="Python"):
    global _oDict
    global _sContext
    global _dOptions
    try:
        _oDict = IBDAWG("${dic_name}.bdic")
        _sContext = sContext
        _dOptions = dict(gc_options.getOptions(sContext))   # duplication necessary, to be able to reset to default
    except:
        traceback.print_exc()


def setOption (sOpt, bVal):
    if sOpt in _dOptions:
        _dOptions[sOpt] = bVal


def setOptions (dOpt):
    for sKey, bVal in dOpt.items():
        if sKey in _dOptions:
            _dOptions[sKey] = bVal


def getOptions ():
    return _dOptions


def getDefaultOptions ():
    return dict(gc_options.getOptions(_sContext))


def getOptionsLabels (sLang):
    return gc_options.getUI(sLang)


def displayOptions (sLang):
    echo("List of options")
    echo("\n".join( [ k+":\t"+str(v)+"\t"+gc_options.getUI(sLang).get(k, ("?", ""))[0]  for k, v  in sorted(_dOptions.items()) ] ))
    echo("")


def resetOptions ():
    global _dOptions
    _dOptions = dict(gc_options.getOptions(_sContext))


def getDictionary ():
    return _oDict


def _getRules (bParagraph):
    try:
        if not bParagraph:
            return _rules.lSentenceRules
        return _rules.lParagraphRules
    except:
        _loadRules()
    if not bParagraph:
        return _rules.lSentenceRules
    return _rules.lParagraphRules


def _loadRules ():
    from . import gc_rules
    global _rules
    _rules = gc_rules
    # compile rules regex
    for lRuleGroup in chain(_rules.lParagraphRules, _rules.lSentenceRules):
        for rule in lRuleGroup[1]:
            try:
                rule[0] = re.compile(rule[0])
            except:
                echo("Bad regular expression in # " + str(rule[2]))
                rule[0] = "(?i)<Grammalecte>"


def _getPath ():
    return os.path.join(os.path.dirname(sys.modules[__name__].__file__), __name__ + ".py")



#### common functions

# common regexes
_zEndOfSentence = re.compile('([.?!:;…][ .?!… »”")]*|.$)')
_zBeginOfParagraph = re.compile("^\W*")
_zEndOfParagraph = re.compile("\W*$")
_zNextWord = re.compile(" +(\w[\w-]*)")
_zPrevWord = re.compile("(\w[\w-]*) +$")


def option (sOpt):
    "return True if option sOpt is active"
    return _dOptions.get(sOpt, False)


def displayInfo (dDA, tWord):
    "for debugging: retrieve info of word"
    if not tWord:
        echo("> nothing to find")
        return True
    if tWord[1] not in _dAnalyses and not _storeMorphFromFSA(tWord[1]):
        echo("> not in FSA")
        return True
    if tWord[0] in dDA:
        echo("DA: " + str(dDA[tWord[0]]))
    echo("FSA: " + str(_dAnalyses[tWord[1]]))
    return True


def _storeMorphFromFSA (sWord):
    "retrieves morphologies list from _oDict -> _dAnalyses"
    global _dAnalyses
    _dAnalyses[sWord] = _oDict.getMorph(sWord)
    return True  if _dAnalyses[sWord]  else False


def morph (dDA, tWord, sPattern, bStrict=True, bNoWord=False):
    "analyse a tuple (position, word), return True if sPattern in morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    if tWord[1] not in _dAnalyses and not _storeMorphFromFSA(tWord[1]):
        return False
    lMorph = dDA[tWord[0]]  if tWord[0] in dDA  else _dAnalyses[tWord[1]]
    if not lMorph:
        return False
    p = re.compile(sPattern)
    if bStrict:
        return all(p.search(s)  for s in lMorph)
    return any(p.search(s)  for s in lMorph)


def morphex (dDA, tWord, sPattern, sNegPattern, bNoWord=False):
    "analyse a tuple (position, word), returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    if tWord[1] not in _dAnalyses and not _storeMorphFromFSA(tWord[1]):
        return False
    lMorph = dDA[tWord[0]]  if tWord[0] in dDA  else _dAnalyses[tWord[1]]
    # check negative condition
    np = re.compile(sNegPattern)
    if any(np.search(s)  for s in lMorph):
        return False
    # search sPattern
    p = re.compile(sPattern)
    return any(p.search(s)  for s in lMorph)


def analyse (sWord, sPattern, bStrict=True):
    "analyse a word, return True if sPattern in morphologies (disambiguation off)"
    if sWord not in _dAnalyses and not _storeMorphFromFSA(sWord):
        return False
    if not _dAnalyses[sWord]:
        return False
    p = re.compile(sPattern)
    if bStrict:
        return all(p.search(s)  for s in _dAnalyses[sWord])
    return any(p.search(s)  for s in _dAnalyses[sWord])


def analysex (sWord, sPattern, sNegPattern):
    "analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)"
    if sWord not in _dAnalyses and not _storeMorphFromFSA(sWord):
        return False
    # check negative condition
    np = re.compile(sNegPattern)
    if any(np.search(s)  for s in _dAnalyses[sWord]):
        return False
    # search sPattern
    p = re.compile(sPattern)
    return any(p.search(s)  for s in _dAnalyses[sWord])


def stem (sWord):
    "returns a list of sWord's stems"
    if not sWord:
        return []
    if sWord not in _dAnalyses and not _storeMorphFromFSA(sWord):
        return []
    return [ s[1:s.find(" ")]  for s in _dAnalyses[sWord] ]


## functions to get text outside pattern scope

# warning: check compile_rules.py to understand how it works

def nextword (s, iStart, n):
    "get the nth word of the input string or empty string"
    m = re.match("( +[\\w%-]+){" + str(n-1) + "} +([\\w%-]+)", s[iStart:])
    if not m:
        return None
    return (iStart+m.start(2), m.group(2))


def prevword (s, iEnd, n):
    "get the (-)nth word of the input string or empty string"
    m = re.search("([\\w%-]+) +([\\w%-]+ +){" + str(n-1) + "}$", s[:iEnd])
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


def look_chk1 (dDA, s, nOffset, sPattern, sPatternGroup1, sNegPatternGroup1=None):
    "returns True if s has pattern sPattern and m.group(1) has pattern sPatternGroup1"
    m = re.search(sPattern, s)
    if not m:
        return False
    try:
        sWord = m.group(1)
        nPos = m.start(1) + nOffset
    except:
        return False
    if sNegPatternGroup1:
        return morphex(dDA, (nPos, sWord), sPatternGroup1, sNegPatternGroup1)
    return morph(dDA, (nPos, sWord), sPatternGroup1, False)


#### Disambiguator

def select (dDA, nPos, sWord, sPattern, lDefault=None):
    if not sWord:
        return True
    if nPos in dDA:
        return True
    if sWord not in _dAnalyses and not _storeMorphFromFSA(sWord):
        return True
    if len(_dAnalyses[sWord]) == 1:
        return True
    lSelect = [ sMorph  for sMorph in _dAnalyses[sWord]  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(_dAnalyses[sWord]):
            dDA[nPos] = lSelect
            #echo("= "+sWord+" "+str(dDA.get(nPos, "null")))
    elif lDefault:
        dDA[nPos] = lDefault
        #echo("= "+sWord+" "+str(dDA.get(nPos, "null")))
    return True


def exclude (dDA, nPos, sWord, sPattern, lDefault=None):
    if not sWord:
        return True
    if nPos in dDA:
        return True
    if sWord not in _dAnalyses and not _storeMorphFromFSA(sWord):
        return True
    if len(_dAnalyses[sWord]) == 1:
        return True
    lSelect = [ sMorph  for sMorph in _dAnalyses[sWord]  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(_dAnalyses[sWord]):
            dDA[nPos] = lSelect
            #echo("= "+sWord+" "+str(dDA.get(nPos, "null")))
    elif lDefault:
        dDA[nPos] = lDefault
        #echo("= "+sWord+" "+str(dDA.get(nPos, "null")))
    return True


def define (dDA, nPos, lMorph):
    dDA[nPos] = lMorph
    #echo("= "+str(nPos)+" "+str(dDA[nPos]))
    return True


#### GRAMMAR CHECKER PLUGINS

${plugins}


${callables}
