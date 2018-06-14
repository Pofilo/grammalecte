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
from .gc_rules_graph import dAllGraph, dRule

try:
    # LibreOffice / OpenOffice
    from com.sun.star.linguistic2 import SingleProofreadingError
    from com.sun.star.text.TextMarkupType import PROOFREADING
    from com.sun.star.beans import PropertyValue
    #import lightproof_handler_${implname} as opt
    _bWriterError = True
except ImportError:
    _bWriterError = False


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
_oSpellChecker = None
_oTokenizer = None
_aIgnoredRules = set()

# functions
_createRegexError = None


#### Initialization

def load (sContext="Python"):
    global _oSpellChecker
    global _sAppContext
    global _dOptions
    global _oTokenizer
    global _createRegexError
    global _createTokenError
    try:
        _oSpellChecker = SpellChecker("${lang}", "${dic_main_filename_py}", "${dic_extended_filename_py}", "${dic_community_filename_py}", "${dic_personal_filename_py}")
        _sAppContext = sContext
        _dOptions = dict(gc_options.getOptions(sContext))   # duplication necessary, to be able to reset to default
        _oTokenizer = _oSpellChecker.getTokenizer()
        _oSpellChecker.activateStorage()
        _createRegexError = _createRegexWriterError  if _bWriterError  else _createRegexDictError
    except:
        traceback.print_exc()


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
    for sOption, lRuleGroup in chain(_rules.lParagraphRules, _rules.lSentenceRules):
        if sOption != "@@@@":
            for aRule in lRuleGroup:
                try:
                    aRule[0] = re.compile(aRule[0])
                except:
                    echo("Bad regular expression in # " + str(aRule[2]))
                    aRule[0] = "(?i)<Grammalecte>"


#### Parsing

def parse (sText, sCountry="${country_default}", bDebug=False, dOptions=None, bContext=False):
    "analyses the paragraph sText and returns list of errors"
    #sText = unicodedata.normalize("NFC", sText)
    aErrors = None
    sRealText = sText
    dPriority = {}  # Key = position; value = priority
    dOpt = _dOptions  if not dOptions  else dOptions
    bShowRuleId = option('idrule')

    # parse paragraph
    try:
        sNew, aErrors = _proofread(None, sText, sRealText, 0, True, dPriority, sCountry, dOpt, bShowRuleId, bDebug, bContext)
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
            try:
                oSentence = TokenSentence(sText[iStart:iEnd], sRealText[iStart:iEnd], iStart)
                _, errs = _proofread(oSentence, sText[iStart:iEnd], sRealText[iStart:iEnd], iStart, False, dPriority, sCountry, dOpt, bShowRuleId, bDebug, bContext)
                aErrors.update(errs)
            except:
                raise
    return aErrors.values() # this is a view (iterable)


_zEndOfSentence = re.compile(r'([.?!:;…][ .?!… »”")]*|.$)')
_zBeginOfParagraph = re.compile(r"^\W*")
_zEndOfParagraph = re.compile(r"\W*$")

def _getSentenceBoundaries (sText):
    iStart = _zBeginOfParagraph.match(sText).end()
    for m in _zEndOfSentence.finditer(sText):
        yield (iStart, m.end())
        iStart = m.end()


def _proofread (oSentence, s, sx, nOffset, bParagraph, dPriority, sCountry, dOptions, bShowRuleId, bDebug, bContext):
    dErrs = {}
    bParagraphChange = False
    bSentenceChange = False
    dTokenPos = oSentence.dTokenPos if oSentence else {}
    for sOption, lRuleGroup in _getRules(bParagraph):
        if sOption == "@@@@":
            # graph rules
            if not bParagraph and bSentenceChange:
                oSentence.update(s)
                bSentenceChange = False
            for sGraphName, sLineId in lRuleGroup:
                if bDebug:
                    print("\n>>>> GRAPH:", sGraphName, sLineId)
                bParagraphChange, errs = oSentence.parse(dAllGraph[sGraphName], dPriority, sCountry, dOptions, bShowRuleId, bDebug, bContext)
                dErrs.update(errs)
                if bParagraphChange:
                    s = oSentence.rewrite()
                    if bDebug:
                        print("~", oSentence.sSentence)
        elif not sOption or dOptions.get(sOption, False):
            # regex rules
            for zRegex, bUppercase, sLineId, sRuleId, nPriority, lActions in lRuleGroup:
                if sRuleId not in _aIgnoredRules:
                    for m in zRegex.finditer(s):
                        bCondMemo = None
                        for sFuncCond, cActionType, sWhat, *eAct in lActions:
                            # action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                            try:
                                bCondMemo = not sFuncCond or globals()[sFuncCond](s, sx, m, dTokenPos, sCountry, bCondMemo)
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
                                        bParagraphChange = True
                                        bSentenceChange = True
                                        if bDebug:
                                            echo("~ " + s + "  -- " + m.group(eAct[0]) + "  # " + sLineId)
                                    elif cActionType == "=":
                                        # disambiguation
                                        if not bParagraph:
                                            globals()[sWhat](s, m, dTokenPos)
                                            if bDebug:
                                                echo("= " + m.group(0) + "  # " + sLineId)
                                    elif cActionType == ">":
                                        # we do nothing, this test is just a condition to apply all following actions
                                        pass
                                    else:
                                        echo("# error: unknown action at " + sLineId)
                                elif cActionType == ">":
                                    break
                            except Exception as e:
                                raise Exception(str(e), "# " + sLineId + " # " + sRuleId)
    if bParagraphChange:
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
    sMessage = globals()[sMsg[1:]](s, m)  if sMsg[0:1] == "="  else  m.expand(sMsg)
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
    dErr["sMessage"] = globals()[sMsg[1:]](s, m)  if sMsg[0:1] == "="  else  m.expand(sMsg)
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
        if sOption != "@@@@":
            for _, _, sLineId, sRuleId, _, _ in lRuleGroup:
                if not sFilter or zFilter.search(sRuleId):
                    yield (sOption, sLineId, sRuleId)


def displayRules (sFilter=None):
    echo("List of rules. Filter: << " + str(sFilter) + " >>")
    for sOption, sLineId, sRuleId in listRules(sFilter):
        echo("{:<10} {:<10} {}".format(sOption, sLineId, sRuleId))


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


def _getPath ():
    return os.path.join(os.path.dirname(sys.modules[__name__].__file__), __name__ + ".py")



#### common functions

def option (sOpt):
    "return True if option sOpt is active"
    return _dOptions.get(sOpt, False)


def displayInfo (dTokenPos, tWord):
    "for debugging: retrieve info of word"
    if not tWord:
        echo("> nothing to find")
        return True
    lMorph = _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        echo("> not in dictionary")
        return True
    if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]:
        echo("DA: " + str(dTokenPos[tWord[0]]["lMorph"]))
    echo("FSA: " + str(lMorph))
    return True


def morph (dTokenPos, tWord, sPattern, bStrict=True, bNoWord=False):
    "analyse a tuple (position, word), return True if sPattern in morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    lMorph = dTokenPos[tWord[0]]["lMorph"]  if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]  else _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        return False
    p = re.compile(sPattern)
    if bStrict:
        return all(p.search(s)  for s in lMorph)
    return any(p.search(s)  for s in lMorph)


def morphex (dTokenPos, tWord, sPattern, sNegPattern, bNoWord=False):
    "analyse a tuple (position, word), returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    lMorph = dTokenPos[tWord[0]]["lMorph"]  if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]  else _oSpellChecker.getMorph(tWord[1])
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


def look_chk1 (dTokenPos, s, nOffset, sPattern, sPatternGroup1, sNegPatternGroup1=None):
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
        return morphex(dTokenPos, (nPos, sWord), sPatternGroup1, sNegPatternGroup1)
    return morph(dTokenPos, (nPos, sWord), sPatternGroup1, False)


#### Disambiguator

def select (dTokenPos, nPos, sWord, sPattern, lDefault=None):
    if not sWord:
        return True
    if nPos not in dTokenPos:
        print("Error. There should be a token at this position: ", nPos)
        return True
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dTokenPos[nPos]["lMorph"] = lSelect
    elif lDefault:
        dTokenPos[nPos]["lMorph"] = lDefault
    return True


def exclude (dTokenPos, nPos, sWord, sPattern, lDefault=None):
    if not sWord:
        return True
    if nPos not in dTokenPos:
        print("Error. There should be a token at this position: ", nPos)
        return True
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph or len(lMorph) == 1:
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dTokenPos[nPos]["lMorph"] = lSelect
    elif lDefault:
        dTokenPos[nPos]["lMorph"] = lDefault
    return True


def define (dTokenPos, nPos, lMorph):
    if nPos not in dTokenPos:
        print("Error. There should be a token at this position: ", nPos)
        return True
    dTokenPos[nPos]["lMorph"] = lMorph
    return True


#### GRAMMAR CHECKER PLUGINS

${plugins}



#### TOKEN SENTENCE CHECKER

class TokenSentence:

    def __init__ (self, sSentence, sSentence0, nOffset):
        self.sSentence = sSentence
        self.sSentence0 = sSentence0
        self.nOffset = nOffset
        self.lToken = list(_oTokenizer.genTokens(sSentence, True))
        self.dTokenPos = { dToken["nStart"]: dToken  for dToken in self.lToken }
        self.createError = self._createWriterError  if _bWriterError  else self._createDictError

    def update (self, sSentence):
        self.sSentence = sSentence
        self.lToken = list(_oTokenizer.genTokens(sSentence, True))

    def _getNextMatchingNodes (self, dToken, dGraph, dNode, bDebug=False):
        "generator: return nodes where <dToken> “values” match <dNode> arcs"
        # token value
        if dToken["sValue"] in dNode:
            if bDebug:
                print("MATCH:", dToken["sValue"])
            yield dGraph[dNode[dToken["sValue"]]]
        # token lemmas
        if "<lemmas>" in dNode:
            for sLemma in _oSpellChecker.getLemma(dToken["sValue"]):
                if sLemma in dNode["<lemmas>"]:
                    if bDebug:
                        print("MATCH: >" + sLemma)
                    yield dGraph[dNode["<lemmas>"][sLemma]]
        # universal arc
        if "*" in dNode:
            if bDebug:
                print("MATCH: *")
            yield dGraph[dNode["*"]]
        # regex value arcs
        if "<re_value>" in dNode:
            for sRegex in dNode["<re_value>"]:
                if re.search(sRegex, dToken["sValue"]):
                    if bDebug:
                        print("MATCH: ~" + sRegex)
                    yield dGraph[dNode["<re_value>"][sRegex]]
        # regex morph arcs
        if "<re_morph>" in dNode:
            for sRegex in dNode["<re_morph>"]:
                if "¬" not in sRegex:
                    # no anti-pattern
                    if any(re.search(sRegex, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                        if bDebug:
                            print("MATCH: @" + sRegex)
                        yield dGraph[dNode["<re_morph>"][sRegex]]
                else:
                    # there is an anti-pattern
                    sPattern, sNegPattern = sRegex.split("¬", 1)
                    if sNegPattern == "*":
                        # all morphologies must match with <sPattern>
                        if all(re.search(sPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            if bDebug:
                                print("MATCH: @" + sRegex)
                            yield dGraph[dNode["<re_morph>"][sRegex]]
                    else:
                        if sNegPattern and any(re.search(sNegPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            continue
                        if any(re.search(sPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            if bDebug:
                                print("MATCH: @" + sRegex)
                            yield dGraph[dNode["<re_morph>"][sRegex]]

    def parse (self, dGraph, dPriority, sCountry="${country_default}", dOptions=None, bShowRuleId=False, bDebug=False, bContext=False):
        dErr = {}
        dPriority = {}  # Key = position; value = priority
        dOpt = _dOptions  if not dOptions  else dOptions
        lPointer = []
        bChange = False
        for dToken in self.lToken:
            if bDebug:
                print("TOKEN:", dToken["sValue"])
            # check arcs for each existing pointer
            lNextPointer = []
            for dPointer in lPointer:
                for dNode in self._getNextMatchingNodes(dToken, dGraph, dPointer["dNode"], bDebug):
                    lNextPointer.append({"iToken": dPointer["iToken"], "dNode": dNode})
            lPointer = lNextPointer
            # check arcs of first nodes
            for dNode in self._getNextMatchingNodes(dToken, dGraph, dGraph[0], bDebug):
                lPointer.append({"iToken": dToken["i"], "dNode": dNode})
            # check if there is rules to check for each pointer
            for dPointer in lPointer:
                #if bDebug:
                #    print("+", dPointer)
                if "<rules>" in dPointer["dNode"]:
                    bHasChanged, errs = self._executeActions(dGraph, dPointer["dNode"]["<rules>"], dPointer["iToken"]-1, dPriority, dOpt, sCountry, bShowRuleId, bDebug, bContext)
                    dErr.update(errs)
                    if bHasChanged:
                        bChange = True
        return (bChange, dErr)

    def _executeActions (self, dGraph, dNode, nTokenOffset, dPriority, dOptions, sCountry, bShowRuleId, bDebug, bContext):
        "execute actions found in the DARG"
        dErrs = {}
        bChange = False
        for sLineId, nextNodeKey in dNode.items():
            bCondMemo = None
            for sRuleId in dGraph[nextNodeKey]:
                try:
                    if bDebug:
                        print("ACTION:", sRuleId)
                        print(dRule[sRuleId])
                    sOption, sFuncCond, cActionType, sWhat, *eAct = dRule[sRuleId]
                    # action in lActions: [ condition, action type, replacement/suggestion/action[, iTokenStart, iTokenEnd[, nPriority, message, URL]] ]
                    if not sOption or dOptions.get(sOption, False):
                        bCondMemo = not sFuncCond or globals()[sFuncCond](self.lToken, nTokenOffset, sCountry, bCondMemo)
                        if bCondMemo:
                            if cActionType == "-":
                                # grammar error
                                nTokenErrorStart = nTokenOffset + eAct[0]
                                nTokenErrorEnd = nTokenOffset + eAct[1]
                                nErrorStart = self.nOffset + self.lToken[nTokenErrorStart]["nStart"]
                                nErrorEnd = self.nOffset + self.lToken[nTokenErrorEnd]["nEnd"]
                                if nErrorStart not in dErrs or eAct[2] > dPriority[nErrorStart]:
                                    dErrs[nErrorStart] = self.createError(sWhat, nTokenOffset, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, True, eAct[3], eAct[4], bShowRuleId, "notype", bContext)
                                    dPriority[nErrorStart] = eAct[2]
                                    if bDebug:
                                        print("-", sRuleId, dErrs[nErrorStart])
                            elif cActionType == "~":
                                # text processor
                                self._tagAndPrepareTokenForRewriting(sWhat, nTokenOffset + eAct[0], nTokenOffset + eAct[1])
                                if bDebug:
                                    print("~", sRuleId)
                                bChange = True
                            elif cActionType == "=":
                                # disambiguation
                                globals()[sWhat](self.lToken, nTokenOffset)
                                if bDebug:
                                    print("=", sRuleId)
                            elif cActionType == ">":
                                # we do nothing, this test is just a condition to apply all following actions
                                if bDebug:
                                    print(">", sRuleId)
                                pass
                            else:
                                print("# error: unknown action at " + sLineId)
                        elif cActionType == ">":
                            if bDebug:
                                print(">!", sRuleId)
                            break
                except Exception as e:
                    raise Exception(str(e), sLineId)
        return bChange, dErrs

    def _createWriterError (self, sSugg, nTokenOffset, iFirstToken, nStart, nEnd, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
        "error for Writer (LO/OO)"
        xErr = SingleProofreadingError()
        #xErr = uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
        xErr.nErrorStart = nStart
        xErr.nErrorLength = nEnd - nStart
        xErr.nErrorType = PROOFREADING
        xErr.aRuleIdentifier = sRuleId
        # suggestions
        if sSugg[0:1] == "=":
            sSugg = globals()[sSugg[1:]](self.lToken, nTokenOffset)
            if sSugg:
                if bUppercase and self.lToken[iFirstToken]["sValue"][0:1].isupper():
                    xErr.aSuggestions = tuple(map(str.capitalize, sSugg.split("|")))
                else:
                    xErr.aSuggestions = tuple(sSugg.split("|"))
            else:
                xErr.aSuggestions = ()
        elif sSugg == "_":
            xErr.aSuggestions = ()
        else:
            if bUppercase and self.lToken[iFirstToken]["sValue"][0:1].isupper():
                xErr.aSuggestions = tuple(map(str.capitalize, self._expand(sSugg, nTokenOffset).split("|")))
            else:
                xErr.aSuggestions = tuple(self._expand(sSugg, nTokenOffset).split("|"))
        # Message
        sMessage = globals()[sMsg[1:]](self.lToken)  if sMsg[0:1] == "="  else self._expand(sMsg, nTokenOffset)
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

    def _createDictError (self, sSugg, nTokenOffset, iFirstToken, nStart, nEnd, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
        "error as a dictionary"
        dErr = {}
        dErr["nStart"] = nStart
        dErr["nEnd"] = nEnd
        dErr["sLineId"] = sLineId
        dErr["sRuleId"] = sRuleId
        dErr["sType"] = sOption  if sOption  else "notype"
        # suggestions
        if sSugg[0:1] == "=":
            sSugg = globals()[sSugg[1:]](self.lToken, nTokenOffset)
            if sSugg:
                if bUppercase and self.lToken[iFirstToken]["sValue"][0:1].isupper():
                    dErr["aSuggestions"] = list(map(str.capitalize, sSugg.split("|")))
                else:
                    dErr["aSuggestions"] = sSugg.split("|")
            else:
                dErr["aSuggestions"] = []
        elif sSugg == "_":
            dErr["aSuggestions"] = []
        else:
            if bUppercase and self.lToken[iFirstToken]["sValue"][0:1].isupper():
                dErr["aSuggestions"] = list(map(str.capitalize, self._expand(sSugg, nTokenOffset).split("|")))
            else:
                dErr["aSuggestions"] = self._expand(sSugg, nTokenOffset).split("|")
        # Message
        dErr["sMessage"] = globals()[sMsg[1:]](self.lToken)  if sMsg[0:1] == "="  else self._expand(sMsg, nTokenOffset)
        if bShowRuleId:
            dErr["sMessage"] += "  " + sLineId + " # " + sRuleId
        # URL
        dErr["URL"] = sURL  if sURL  else ""
        # Context
        if bContext:
            dErr['sUnderlined'] = self.sSentence0[dErr["nStart"]:dErr["nEnd"]]
            dErr['sBefore'] = self.sSentence0[max(0,dErr["nStart"]-80):dErr["nStart"]]
            dErr['sAfter'] = self.sSentence0[dErr["nEnd"]:dErr["nEnd"]+80]
        return dErr

    def _expand (self, sMsg, nTokenOffset):
        #print("*", sMsg)
        for m in re.finditer(r"\\([0-9]+)", sMsg):
            sMsg = sMsg.replace(m.group(0), self.lToken[int(m.group(1))+nTokenOffset]["sValue"])
        #print(">", sMsg)
        return sMsg

    def _tagAndPrepareTokenForRewriting (self, sWhat, nTokenRewriteStart, nTokenRewriteEnd, bUppercase=True):
        "text processor: rewrite tokens between <nTokenRewriteStart> and <nTokenRewriteEnd> position"
        if sWhat == "*":
            # purge text
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                self.lToken[nTokenRewriteStart]["bToRemove"] = True
            else:
                for i in range(nTokenRewriteStart, nTokenRewriteEnd+1):
                    self.lToken[i]["bToRemove"] = True
        else:
            if sWhat.startswith("="):
                sWhat = globals()[sWhat[1:]](self.lToken)
            bUppercase = bUppercase and self.lToken[nTokenRewriteStart]["sValue"][0:1].isupper()
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                sWhat = sWhat + " " * (len(self.lToken[nTokenRewriteStart]["sValue"])-len(sWhat))
                if bUppercase:
                    sWhat = sWhat[0:1].upper() + sWhat[1:]
                self.lToken[nTokenRewriteStart]["sNewValue"] = sWhat
            else:
                lTokenValue = sWhat.split("|")
                if len(lTokenValue) != (nTokenRewriteEnd - nTokenRewriteStart + 1):
                    print("Error. Text processor: number of replacements != number of tokens.")
                    return
                for i, sValue in zip(range(nTokenRewriteStart, nTokenRewriteEnd+1), lTokenValue):
                    if bUppercase:
                        sValue = sValue[0:1].upper() + sValue[1:]
                    self.lToken[i]["sNewValue"] = sValue

    def rewrite (self):
        "rewrite the sentence, modify tokens, purge the token list"
        lNewToken = []
        for i, dToken in enumerate(self.lToken):
            if "bToRemove" in dToken:
                # remove useless token
                self.sSentence = self.sSentence[:self.nOffset+dToken["nStart"]] + " " * (dToken["nEnd"] - dToken["nStart"]) + self.sSentence[self.nOffset+dToken["nEnd"]:]
                #print("removed:", dToken["sValue"])
            else:
                lNewToken.append(dToken)
                if "sNewValue" in dToken:
                    # rewrite token and sentence
                    #print(dToken["sValue"], "->", dToken["sNewValue"])
                    dToken["sRealValue"] = dToken["sValue"]
                    dToken["sValue"] = dToken["sNewValue"]
                    nDiffLen = len(dToken["sRealValue"]) - len(dToken["sNewValue"])
                    sNewRepl = (dToken["sNewValue"] + " " * nDiffLen)  if nDiffLen >= 0  else dToken["sNewValue"][:len(dToken["sRealValue"])]
                    self.sSentence = self.sSentence[:self.nOffset+dToken["nStart"]] + sNewRepl + self.sSentence[self.nOffset+dToken["nEnd"]:]
                    del dToken["sNewValue"]
        self.lToken.clear()
        self.lToken = lNewToken
        return self.sSentence



#### Analyse tokens

def g_morph (dToken, sPattern, sNegPattern=""):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies"
    if "lMorph" in dToken:
        lMorph = dToken["lMorph"]
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
        else:
            zNegPattern = re.compile(sNegPattern)
            if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
                return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def g_analyse (dToken, sPattern, sNegPattern=""):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph:
        return False
    # check negative condition
    if sNegPattern:
        if sNegPattern == "*":
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        else:
            zNegPattern = re.compile(sNegPattern)
            if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
                return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)



#### Disambiguator

def g_select (dToken, sPattern, lDefault=None):
    "select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        if lDefault:
            dToken["lMorph"] = lDefault
            #print("DA:", dToken["sValue"], dToken["lMorph"])
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    #print("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_exclude (dToken, sPattern, lDefault=None):
    "select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        if lDefault:
            dToken["lMorph"] = lDefault
            #print("DA:", dToken["sValue"], dToken["lMorph"])
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    #print("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_define (dToken, lMorph):
    "set morphologies of <dToken>, always return True"
    dToken["lMorph"] = lMorph
    #print("DA:", dToken["sValue"], lMorph)
    return True


#### CALLABLES FOR REGEX RULES (generated code)

${callables}


#### CALLABLES FOR GRAPH RULES (generated code)

${graph_callables}
