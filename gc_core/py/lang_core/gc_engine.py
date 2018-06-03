# Grammalecte
# Grammar checker engine

import re
import sys
import os
import traceback
#import unicodedata
from itertools import chain

from ..graphspell.spellchecker import SpellChecker
from ..graphspell.echo import echo
from . import gc_options

from ..graphspell.tokenizer import Tokenizer
from .gc_rules_graph import dGraph, dRule


__all__ = [ "lang", "locales", "pkg", "name", "version", "author", \
            "load", "parse", "getSpellChecker", \
            "setOption", "setOptions", "getOptions", "getDefaultOptions", "getOptionsLabels", "resetOptions", "displayOptions", \
            "ignoreRule", "resetIgnoreRules", "reactivateRule", "listRules", "displayRules" ]

__version__ = "${version}"


lang = "${lang}"
locales = ${loc}
pkg = "${implname}"
name = "${name}"
version = "${version}"
author = "${author}"

_rules = None                               # module gc_rules

# data
_sAppContext = ""                           # what software is running
_dOptions = None
_aIgnoredRules = set()
_oSpellChecker = None
_oTokenizer = None


#### Parsing

def parse (sText, sCountry="${country_default}", bDebug=False, dOptions=None, bContext=False):
    "analyses the paragraph sText and returns list of errors"
    #sText = unicodedata.normalize("NFC", sText)
    aErrors = None
    sRealText = sText
    dDA = {}        # Disambiguisator. Key = position; value = list of morphologies
    dPriority = {}  # Key = position; value = priority
    dOpt = _dOptions  if not dOptions  else dOptions
    bShowRuleId = option('idrule')

    # parse paragraph
    try:
        sNew, aErrors = _proofread(sText, sRealText, 0, True, dDA, dPriority, sCountry, dOpt, bShowRuleId, bDebug, bContext)
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
                # regex parser
                _, errs = _proofread(sText[iStart:iEnd], sRealText[iStart:iEnd], iStart, False, dDA, dPriority, sCountry, dOpt, bShowRuleId, bDebug, bContext)
                aErrors.update(errs)
                # token parser
                oSentence = TokenSentence(sText[iStart:iEnd], sRealText[iStart:iEnd], iStart)
                _, errs = oSentence.parse(dPriority, sCountry, dOpt, bShowRuleId, bDebug, bContext)
                aErrors.update(errs)
            except:
                raise
    return aErrors.values() # this is a view (iterable)


def _getSentenceBoundaries (sText):
    iStart = _zBeginOfParagraph.match(sText).end()
    for m in _zEndOfSentence.finditer(sText):
        yield (iStart, m.end())
        iStart = m.end()


def _proofread (s, sx, nOffset, bParagraph, dDA, dPriority, sCountry, dOptions, bShowRuleId, bDebug, bContext):
    dErrs = {}
    bChange = False
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
                                            dErrs[nErrorStart] = _createRegexError(s, sx, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bShowRuleId, sOption, bContext)
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


def _createRegexWriterError (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
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
    if bShowRuleId:
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


def _createRegexDictError (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
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
            dErr["aSuggestions"] = []
    elif sRepl == "_":
        dErr["aSuggestions"] = []
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
    if bShowRuleId:
        dErr["sMessage"] += "  # " + sLineId + " # " + sRuleId
    # URL
    dErr["URL"] = sURL  if sURL  else ""
    # Context
    if bContext:
        dErr['sUnderlined'] = sx[m.start(iGroup):m.end(iGroup)]
        dErr['sBefore'] = sx[max(0,m.start(iGroup)-80):m.start(iGroup)]
        dErr['sAfter'] = sx[m.end(iGroup):m.end(iGroup)+80]
    return dErr


def _createTokenWriterError (lToken, sSentence, sSentence0, sRepl, iFirstToken, nStart, nEnd, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
    "error for Writer (LO/OO)"
    xErr = SingleProofreadingError()
    #xErr = uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
    xErr.nErrorStart = nStart
    xErr.nErrorLength = nEnd - nStart
    xErr.nErrorType = PROOFREADING
    xErr.aRuleIdentifier = sRuleId
    # suggestions
    if sRepl[0:1] == "=":
        sSugg = globals()[sRepl[1:]](lToken)
        if sSugg:
            if bUppercase and lToken[iFirstToken]["sValue"][0:1].isupper():
                xErr.aSuggestions = tuple(map(str.capitalize, sSugg.split("|")))
            else:
                xErr.aSuggestions = tuple(sSugg.split("|"))
        else:
            xErr.aSuggestions = ()
    elif sRepl == "_":
        xErr.aSuggestions = ()
    else:
        if bUppercase and lToken[iFirstToken]["sValue"][0:1].isupper():
            xErr.aSuggestions = tuple(map(str.capitalize, sRepl.split("|")))
        else:
            xErr.aSuggestions = tuple(sRepl.split("|"))
    # Message
    if sMsg[0:1] == "=":
        sMessage = globals()[sMsg[1:]](lToken)
    else:
        sMessage = sMsg
    xErr.aShortComment = sMessage   # sMessage.split("|")[0]     # in context menu
    xErr.aFullComment = sMessage   # sMessage.split("|")[-1]    # in dialog
    if bShowRuleId:
        xErr.aShortComment += "  " + sLineId + " # " + sRuleId
    # URL
    if sURL:
        p = PropertyValue()
        p.Name = "FullCommentURL"
        p.Value = sURL
        xErr.aProperties = (p,)
    else:
        xErr.aProperties = ()
    return xErr

                                                         
def _createTokenDictError (lToken, sSentence, sSentence0, sRepl, iFirstToken, nStart, nEnd, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
    "error as a dictionary"
    dErr = {}
    dErr["nStart"] = nStart
    dErr["nEnd"] = nEnd
    dErr["sLineId"] = sLineId
    dErr["sRuleId"] = sRuleId
    dErr["sType"] = sOption  if sOption  else "notype"
    # suggestions
    if sRepl[0:1] == "=":
        sugg = globals()[sRepl[1:]](lToken)
        if sugg:
            if bUppercase and lToken[iFirstToken]["sValue"][0:1].isupper():
                dErr["aSuggestions"] = list(map(str.capitalize, sugg.split("|")))
            else:
                dErr["aSuggestions"] = sugg.split("|")
        else:
            dErr["aSuggestions"] = []
    elif sRepl == "_":
        dErr["aSuggestions"] = []
    else:
        if bUppercase and lToken[iFirstToken]["sValue"][0:1].isupper():
            dErr["aSuggestions"] = list(map(str.capitalize, sRepl.split("|")))
        else:
            dErr["aSuggestions"] = sRepl.split("|")
    # Message
    if sMsg[0:1] == "=":
        sMessage = globals()[sMsg[1:]](lToken)
    else:
        sMessage = sMsg
    dErr["sMessage"] = sMessage
    if bShowRuleId:
        dErr["sMessage"] += "  " + sLineId + " # " + sRuleId
    # URL
    dErr["URL"] = sURL  if sURL  else ""
    # Context
    if bContext:
        dErr['sUnderlined'] = sSentence0[dErr["nStart"]:dErr["nEnd"]]
        dErr['sBefore'] = sSentence0[max(0,dErr["nStart"]-80):dErr["nStart"]]
        dErr['sAfter'] = sSentence0[dErr["nEnd"]:dErr["nEnd"]+80]
    return dErr


def _rewrite (sSentence, sRepl, iGroup, m, bUppercase):
    "text processor: write <sRepl> in <sSentence> at <iGroup> position"
    nLen = m.end(iGroup) - m.start(iGroup)
    if sRepl == "*":
        sNew = " " * nLen
    elif sRepl == "_":
        sNew = sRepl + " " * (nLen-1)
    elif sRepl[0:1] == "=":
        sNew = globals()[sRepl[1:]](sSentence, m)
        sNew = sNew + " " * (nLen-len(sNew))
        if bUppercase and m.group(iGroup)[0:1].isupper():
            sNew = sNew.capitalize()
    else:
        sNew = m.expand(sRepl)
        sNew = sNew + " " * (nLen-len(sNew))
    return sSentence[0:m.start(iGroup)] + sNew + sSentence[m.end(iGroup):]


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
    _createRegexError = _createRegexWriterError
    _createTokenError = _createTokenWriterError
except ImportError:
    _createRegexError = _createRegexDictError
    _createTokenError = _createTokenDictError


def load (sContext="Python"):
    global _oSpellChecker
    global _sAppContext
    global _dOptions
    global _oTokenizer
    try:
        _oSpellChecker = SpellChecker("${lang}", "${dic_main_filename_py}", "${dic_extended_filename_py}", "${dic_community_filename_py}", "${dic_personal_filename_py}")
        _sAppContext = sContext
        _dOptions = dict(gc_options.getOptions(sContext))   # duplication necessary, to be able to reset to default
        _oTokenizer = _oSpellChecker.getTokenizer()
        _oSpellChecker.activateStorage()
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
    return dict(gc_options.getOptions(_sAppContext))


def getOptionsLabels (sLang):
    return gc_options.getUI(sLang)


def displayOptions (sLang):
    echo("List of options")
    echo("\n".join( [ k+":\t"+str(v)+"\t"+gc_options.getUI(sLang).get(k, ("?", ""))[0]  for k, v  in sorted(_dOptions.items()) ] ))
    echo("")


def resetOptions ():
    global _dOptions
    _dOptions = dict(gc_options.getOptions(_sAppContext))


def getSpellChecker ():
    return _oSpellChecker


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
_zEndOfSentence = re.compile(r'([.?!:;…][ .?!… »”")]*|.$)')
_zBeginOfParagraph = re.compile(r"^\W*")
_zEndOfParagraph = re.compile(r"\W*$")
_zNextWord = re.compile(r" +(\w[\w-]*)")
_zPrevWord = re.compile(r"(\w[\w-]*) +$")


def option (sOpt):
    "return True if option sOpt is active"
    return _dOptions.get(sOpt, False)


def displayInfo (dDA, tWord):
    "for debugging: retrieve info of word"
    if not tWord:
        echo("> nothing to find")
        return True
    lMorph = _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        echo("> not in dictionary")
        return True
    if tWord[0] in dDA:
        echo("DA: " + str(dDA[tWord[0]]))
    echo("FSA: " + str(lMorph))
    return True


def morph (dDA, tWord, sPattern, bStrict=True, bNoWord=False):
    "analyse a tuple (position, word), return True if sPattern in morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    lMorph = dDA[tWord[0]]  if tWord[0] in dDA  else _oSpellChecker.getMorph(tWord[1])
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
    lMorph = dDA[tWord[0]]  if tWord[0] in dDA  else _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        return False
    # check negative condition
    np = re.compile(sNegPattern)
    if any(np.search(s)  for s in lMorph):
        return False
    # search sPattern
    p = re.compile(sPattern)
    return any(p.search(s)  for s in lMorph)


def analyse (sWord, sPattern, bStrict=True):
    "analyse a word, return True if sPattern in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph:
        return False
    p = re.compile(sPattern)
    if bStrict:
        return all(p.search(s)  for s in lMorph)
    return any(p.search(s)  for s in lMorph)


def analysex (sWord, sPattern, sNegPattern):
    "analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph:
        return False
    # check negative condition
    np = re.compile(sNegPattern)
    if any(np.search(s)  for s in lMorph):
        return False
    # search sPattern
    p = re.compile(sPattern)
    return any(p.search(s)  for s in lMorph)



## functions to get text outside pattern scope

# warning: check compile_rules.py to understand how it works

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
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dDA[nPos] = lSelect
    elif lDefault:
        dDA[nPos] = lDefault
    return True


def exclude (dDA, nPos, sWord, sPattern, lDefault=None):
    if not sWord:
        return True
    if nPos in dDA:
        return True
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dDA[nPos] = lSelect
    elif lDefault:
        dDA[nPos] = lDefault
    return True


def define (dDA, nPos, lMorph):
    dDA[nPos] = lMorph
    return True


#### GRAMMAR CHECKER PLUGINS

${plugins}


#### CALLABLES (generated code)

${callables}



#### TOKEN SENTENCE CHECKER

class TokenSentence:

    def __init__ (self, sSentence, sSentence0, iStart):
        self.sSentence = sSentence
        self.sSentence0 = sSentence0
        self.iStart = iStart
        self.lToken = list(_oTokenizer.genTokens(sSentence, True))

    def _getNextMatchingNodes (self, dToken, dNode):
        "generator: return nodes where <dToken> “values” match <dNode> arcs"
        # token value
        if dToken["sValue"] in dNode:
            #print("value found: ", dToken["sValue"])
            yield dGraph[dNode[dToken["sValue"]]]
        # token lemmas
        if "<lemmas>" in dNode:
            for sLemma in _oSpellChecker.getLemma(dToken["sValue"]):
                if sLemma in dNode["<lemmas>"]:
                    #print("lemma found: ", sLemma)
                    yield dGraph[dNode["<lemmas>"][sLemma]]
        # universal arc
        if "*" in dNode:
            #print("generic arc")
            yield dGraph[dNode["*"]]
        # regex value arcs
        if "<re_value>" in dNode:
            for sRegex in dNode["<re_value>"]:
                if re.search(sRegex, dToken["sValue"]):
                    #print("value regex matching: ", sRegex)
                    yield dGraph[dNode["<re_value>"][sRegex]]
        # regex morph arcs
        if "<re_morph>" in dNode:
            for sRegex in dNode["<re_morph>"]:
                for sMorph in _oSpellChecker.getMorph(dToken["sValue"]):
                    if re.search(sRegex, sMorph):
                        #print("morph regex matching: ", sRegex)
                        yield dGraph[dNode["<re_morph>"][sRegex]]

    def parse (self, dPriority, sCountry="${country_default}", dOptions=None, bShowRuleId=False, bDebug=False, bContext=False):
        dErr = {}
        dPriority = {}  # Key = position; value = priority
        dOpt = _dOptions  if not dOptions  else dOptions
        lPointer = []
        bChange = False
        for dToken in self.lToken:
            # check arcs for each existing pointer
            lNewPointer = []
            for i, dPointer in enumerate(lPointer):
                bValid = False
                bFirst = True
                for dNode in self._getNextMatchingNodes(dToken, dPointer["dNode"]):
                    if bFirst:
                        dPointer["dNode"] = dNode
                    else:
                        lNewPointer.append({"nOffset": dPointer["nOffset"], "dNode": dNode})
                    bFirst = False
                    bValid = True
                if not bValid:
                    del lPointer[i]
            lPointer.extend(lNewPointer)
            # check arcs of first nodes
            for dNode in self._getNextMatchingNodes(dToken, dGraph[0]):
                lPointer.append({"nOffset": dToken["i"], "dNode": dNode})
            # check if there is rules to check for each pointer
            for dPointer in lPointer:
                if "<rules>" in dPointer["dNode"]:
                    bHasChanged, errs = self._executeActions(dPointer["dNode"]["<rules>"], dPointer["nOffset"]-1, dPriority, dOpt, bShowRuleId, bContext)
                    dErr.update(errs)
                    if bHasChanged:
                        bChange = True
        if dErr:
            print(dErr)
        return (bChange, dErr)

    def _executeActions (self, dNode, nTokenOffset, dPriority, dOpt, bShowRuleId, bContext):
        #print(locals())
        dErrs = {}
        bChange = False
        for sLineId, nextNodeKey in dNode.items():
            for sRuleId in dGraph[nextNodeKey]:
                print(sRuleId)
                bCondMemo = None
                sFuncCond, cActionType, sWhat, *eAct = dRule[sRuleId]
                # action in lActions: [ condition, action type, replacement/suggestion/action[, iTokenStart, iTokenEnd[, nPriority, message, URL]] ]
                try:
                    bCondMemo = not sFuncCond or globals()[sFuncCond](self, sCountry, bCondMemo)
                    if bCondMemo:
                        if cActionType == "-":
                            # grammar error
                            print("-")
                            nTokenErrorStart = nTokenOffset + eAct[0]
                            nTokenErrorEnd = nTokenOffset + eAct[1]
                            nErrorStart = self.iStart + self.lToken[nTokenErrorStart]["nStart"]
                            nErrorEnd = self.iStart + self.lToken[nTokenErrorEnd]["nEnd"]
                            if nErrorStart not in dErrs or eAct[2] > dPriority[nErrorStart]:
                                dErrs[nErrorStart] = _createTokenError(self.lToken, self.sSentence, self.sSentence0, sWhat, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, True, eAct[3], eAct[4], bShowRuleId, "notype", bContext)
                                dPriority[nErrorStart] = eAct[2]
                        elif cActionType == "~":
                            # text processor
                            print("~")
                            self._rewrite(sWhat, nErrorStart, nErrorEnd)
                        elif cActionType == "@":
                            # jump
                            print("@")
                            self._jump(sWhat)
                        elif cActionType == "=":
                            # disambiguation
                            print("=")
                            globals()[sWhat](self.lToken)
                        elif cActionType == ">":
                            # we do nothing, this test is just a condition to apply all following actions
                            print(">")
                            pass
                        else:
                            print("# error: unknown action at " + sLineId)
                    elif cActionType == ">":
                        break
                except Exception as e:
                    raise Exception(str(e), sLineId)
        return bChange, dErrs

    def _rewrite (self, sWhat, nErrorStart, nErrorEnd):
        "text processor: rewrite tokens between <nErrorStart> and <nErrorEnd> position"
        lTokenValue = sWhat.split("|")
        if len(lTokenValue) != (nErrorEnd - nErrorStart + 1):
            print("Error. Text processor: number of replacements != number of tokens.")
            return
        for i, sValue in zip(range(nErrorStart, nErrorEnd+1), lTokenValue):
            self.lToken[i]["sValue"] = sValue

    def _jump (self, sWhat):
        try:
            nFrom, nTo = sWhat.split(">")
            self.lToken[int(nFrom)]["iJump"] = int(nTo)
        except:
            print("# Error. Jump failed: ", sWhat)
            traceback.print_exc()
            return


#### Analyse tokens

def g_morph (dToken, sPattern, bStrict=True):
    "analyse a token, return True if <sPattern> in morphologies"
    if "lMorph" in dToken:
        lMorph = dToken["lMorph"]
    else:
        lMorph = _oSpellChecker.getMorph(dToken["sValue"])
        if not lMorph:
            return False
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(sMorph)  for sMorph in lMorph)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)

def g_morphex (dToken, sPattern, sNegPattern):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies"
    if "lMorph" in dToken:
        lMorph = dToken["lMorph"]
    else:
        lMorph = _oSpellChecker.getMorph(dToken["sValue"])
        if not lMorph:
            return False
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)

def g_analyse (dToken, sPattern, bStrict=True):
    "analyse a token, return True if <sPattern> in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph:
        return False
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(sMorph)  for sMorph in lMorph)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def g_analysex (dToken, sPattern, sNegPattern):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph:
        return False
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


#### Go outside the rule scope

def g_nextToken (i):
    pass

def g_prevToken (i):
    pass

def g_look ():
    pass

def g_lookAndCheck ():
    pass


#### Disambiguator

def g_select (dToken, sPattern, lDefault=None):
    "select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    return True


def g_exclude (dToken, sPattern, lDefault=None):
    "select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    return True


def g_define (dToken, lMorph):
    "set morphologies of <dToken>, always return True"
    dToken["lMorph"] = lMorph
    return True


#### CALLABLES (generated code)

${graph_callables}
