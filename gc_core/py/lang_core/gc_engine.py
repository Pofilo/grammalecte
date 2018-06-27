"""
Grammalecte
Grammar checker engine
"""

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



#### Initialization

def load (sContext="Python"):
    "initialization of the grammar checker"
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

_zEndOfSentence = re.compile(r'([.?!:;…][ .?!… »”")]*|.$)')
_zBeginOfParagraph = re.compile(r"^\W*")
_zEndOfParagraph = re.compile(r"\W*$")

def _getSentenceBoundaries (sText):
    iStart = _zBeginOfParagraph.match(sText).end()
    for m in _zEndOfSentence.finditer(sText):
        yield (iStart, m.end())
        iStart = m.end()


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
                bParagraphChange, s = oSentence.parse(dAllGraph[sGraphName], dPriority, sCountry, dOptions, bShowRuleId, bDebug, bContext)
                dErrs.update(oSentence.dError)
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
                                        if nErrorStart not in dErrs or nPriority > dPriority.get(nErrorStart, -1):
                                            dErrs[nErrorStart] = _createError(s, sx, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bShowRuleId, sOption, bContext)
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


def _createError (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
    nStart = nOffset + m.start(iGroup)
    nEnd = nOffset + m.end(iGroup)
    # suggestions
    if sRepl[0:1] == "=":
        sSugg = globals()[sRepl[1:]](s, m)
        lSugg = sSugg.split("|")  if sSugg  else []
    elif sRepl == "_":
        lSugg = []
    else:
        lSugg = m.expand(sRepl).split("|")
    if bUppercase and lSugg and m.group(iGroup)[0:1].isupper():
        lSugg = list(map(str.capitalize, lSugg))
    # Message
    sMessage = globals()[sMsg[1:]](s, m)  if sMsg[0:1] == "="  else  m.expand(sMsg)
    if bShowRuleId:
        sMessage += "  # " + sLineId + " # " + sRuleId
    #
    if _bWriterError:
        xErr = SingleProofreadingError()    # uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
        xErr.nErrorStart = nStart
        xErr.nErrorLength = nEnd - nStart
        xErr.nErrorType = PROOFREADING
        xErr.aRuleIdentifier = sRuleId
        xErr.aShortComment = sMessage   # sMessage.split("|")[0]     # in context menu
        xErr.aFullComment = sMessage   # sMessage.split("|")[-1]    # in dialog
        if bShowRuleId:
            xErr.aShortComment += "  " + sLineId + " # " + sRuleId
        xErr.aSuggestions = tuple(lSugg)
        if sURL:
            xProperty = PropertyValue()
            xProperty.Name = "FullCommentURL"
            xProperty.Value = sURL
            xErr.aProperties = (xProperty,)
        else:
            xErr.aProperties = ()
        return xErr
    else:
        dErr = {}
        dErr["nStart"] = nStart
        dErr["nEnd"] = nEnd
        dErr["sLineId"] = sLineId
        dErr["sRuleId"] = sRuleId
        dErr["sType"] = sOption  if sOption  else "notype"
        dErr["sMessage"] = sMessage
        dErr["aSuggestions"] = lSugg
        dErr["URL"] = sURL  if sURL  else ""
        if bContext:
            dErr['sUnderlined'] = self.sSentence0[nStart:nEnd]
            dErr['sBefore'] = self.sSentence0[max(0,nStart-80):nStart]
            dErr['sAfter'] = self.sSentence0[nEnd:nEnd+80]
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
    "disable rule <sRuleId>"
    _aIgnoredRules.add(sRuleId)


def resetIgnoreRules ():
    "clear all ignored rules"
    _aIgnoredRules.clear()


def reactivateRule (sRuleId):
    "(re)activate rule <sRuleId>"
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
    "display the name of rules, with the filter <sFilter>"
    echo("List of rules. Filter: << " + str(sFilter) + " >>")
    for sOption, sLineId, sRuleId in listRules(sFilter):
        echo("{:<10} {:<10} {}".format(sOption, sLineId, sRuleId))


def setOption (sOpt, bVal):
    "set option <sOpt> with <bVal> if it exists"
    if sOpt in _dOptions:
        _dOptions[sOpt] = bVal


def setOptions (dOpt):
    "update the dictionary of options with <dOpt>"
    for sKey, bVal in dOpt.items():
        if sKey in _dOptions:
            _dOptions[sKey] = bVal


def getOptions ():
    "return the dictionary of current options"
    return _dOptions


def getDefaultOptions ():
    "return the dictionary of default options"
    return dict(gc_options.getOptions(_sAppContext))


def getOptionsLabels (sLang):
    "return options labels"
    return gc_options.getUI(sLang)


def displayOptions (sLang):
    "display the list of grammar checking options"
    echo("List of options")
    echo("\n".join( [ k+":\t"+str(v)+"\t"+gc_options.getUI(sLang).get(k, ("?", ""))[0]  for k, v  in sorted(_dOptions.items()) ] ))
    echo("")


def resetOptions ():
    "set options to default values"
    global _dOptions
    _dOptions = dict(gc_options.getOptions(_sAppContext))


def getSpellChecker ():
    "return the spellchecker object"
    return _oSpellChecker


def _getPath ():
    return os.path.join(os.path.dirname(sys.modules[__name__].__file__), __name__ + ".py")



#### common functions

def option (sOpt):
    "return True if option <sOpt> is active"
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
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(s)  for s in lMorph)
    return any(zPattern.search(s)  for s in lMorph)


def morphex (dTokenPos, tWord, sPattern, sNegPattern, bNoWord=False):
    "analyse a tuple (position, word), returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)"
    if not tWord:
        return bNoWord
    lMorph = dTokenPos[tWord[0]]["lMorph"]  if tWord[0] in dTokenPos and "lMorph" in dTokenPos[tWord[0]]  else _oSpellChecker.getMorph(tWord[1])
    if not lMorph:
        return False
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(s)  for s in lMorph):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(s)  for s in lMorph)


def analyse (sWord, sPattern, bStrict=True):
    "analyse a word, return True if sPattern in morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph:
        return False
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(s)  for s in lMorph)
    return any(zPattern.search(s)  for s in lMorph)


def analysex (sWord, sPattern, sNegPattern):
    "analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)"
    lMorph = _oSpellChecker.getMorph(sWord)
    if not lMorph:
        return False
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(s)  for s in lMorph):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(s)  for s in lMorph)



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
    "Disambiguation: select morphologies of <sWord> matching <sPattern>"
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
    "Disambiguation: exclude morphologies of <sWord> matching <sPattern>"
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
    "Disambiguation: set morphologies of token at <nPos> with <lMorph>"
    if nPos not in dTokenPos:
        print("Error. There should be a token at this position: ", nPos)
        return True
    dTokenPos[nPos]["lMorph"] = lMorph
    return True




#### TOKEN SENTENCE CHECKER

class TokenSentence:
    "Text parser"

    def __init__ (self, sSentence, sSentence0, nOffset):
        self.sSentence = sSentence
        self.sSentence0 = sSentence0
        self.nOffsetWithinParagraph = nOffset
        self.lToken = list(_oTokenizer.genTokens(sSentence, True))
        self.dTokenPos = { dToken["nStart"]: dToken  for dToken in self.lToken }
        self.dTags = {}
        self.dError = {}

    def update (self, sSentence):
        "update <sSentence> and retokenize"
        self.sSentence = sSentence
        self.lToken = list(_oTokenizer.genTokens(sSentence, True))

    def _getNextMatchingNodes (self, dToken, dGraph, dNode, bDebug=False):
        "generator: return nodes where <dToken> “values” match <dNode> arcs"
        # token value
        if dToken["sValue"] in dNode:
            if bDebug:
                print("  MATCH:", dToken["sValue"])
            yield dGraph[dNode[dToken["sValue"]]]
        if dToken["sValue"][0:2].istitle(): # we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
            sValue = dToken["sValue"].lower()
            if sValue in dNode:
                if bDebug:
                    print("  MATCH:", sValue)
                yield dGraph[dNode[sValue]]
        elif dToken["sValue"].isupper():
            sValue = dToken["sValue"].lower()
            if sValue in dNode:
                if bDebug:
                    print("  MATCH:", sValue)
                yield dGraph[dNode[sValue]]
            sValue = dToken["sValue"].capitalize()
            if sValue in dNode:
                if bDebug:
                    print("  MATCH:", sValue)
                yield dGraph[dNode[sValue]]
        # token lemmas
        if "<lemmas>" in dNode:
            for sLemma in _oSpellChecker.getLemma(dToken["sValue"]):
                if sLemma in dNode["<lemmas>"]:
                    if bDebug:
                        print("  MATCH: >" + sLemma)
                    yield dGraph[dNode["<lemmas>"][sLemma]]
        # regex value arcs
        if "<re_value>" in dNode:
            for sRegex in dNode["<re_value>"]:
                if "¬" not in sRegex:
                    # no anti-pattern
                    if re.search(sRegex, dToken["sValue"]):
                        if bDebug:
                            print("  MATCH: ~" + sRegex)
                        yield dGraph[dNode["<re_value>"][sRegex]]
                else:
                    # there is an anti-pattern
                    sPattern, sNegPattern = sRegex.split("¬", 1)
                    if sNegPattern and re.search(sNegPattern, dToken["sValue"]):
                        continue
                    if not sPattern or re.search(sPattern, dToken["sValue"]):
                        if bDebug:
                            print("  MATCH: ~" + sRegex)
                        yield dGraph[dNode["<re_value>"][sRegex]]
        # regex morph arcs
        if "<re_morph>" in dNode:
            for sRegex in dNode["<re_morph>"]:
                if "¬" not in sRegex:
                    # no anti-pattern
                    if any(re.search(sRegex, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                        if bDebug:
                            print("  MATCH: @" + sRegex)
                        yield dGraph[dNode["<re_morph>"][sRegex]]
                else:
                    # there is an anti-pattern
                    sPattern, sNegPattern = sRegex.split("¬", 1)
                    if sNegPattern == "*":
                        # all morphologies must match with <sPattern>
                        if sPattern and all(re.search(sPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            if bDebug:
                                print("  MATCH: @" + sRegex)
                            yield dGraph[dNode["<re_morph>"][sRegex]]
                    else:
                        if sNegPattern and any(re.search(sNegPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            continue
                        if not sPattern or any(re.search(sPattern, sMorph)  for sMorph in _oSpellChecker.getMorph(dToken["sValue"])):
                            if bDebug:
                                print("  MATCH: @" + sRegex)
                            yield dGraph[dNode["<re_morph>"][sRegex]]
        # meta arc (for token type)
        if "<meta>" in dNode:
            for sMeta in dNode["<meta>"]:
                # not regex here, we just search if <dNode["sType"]> exists within <sMeta>
                if sMeta == "*":
                    if bDebug:
                        print("  MATCH: *" + sMeta)
                    yield dGraph[dNode["<meta>"]["*"]]
                elif "¬" in sMeta:
                    if dToken["sType"] not in sMeta:
                        if bDebug:
                            print("  MATCH: *" + sMeta)
                        yield dGraph[dNode["<meta>"][sMeta]]
                elif dToken["sType"] in sMeta:
                    if bDebug:
                        print("  MATCH: *" + sMeta)
                    yield dGraph[dNode["<meta>"][sMeta]]

    def parse (self, dGraph, dPriority, sCountry="${country_default}", dOptions=None, bShowRuleId=False, bDebug=False, bContext=False):
        "parse tokens from the text and execute actions encountered"
        self.dError = {}
        dPriority = {}  # Key = position; value = priority
        dOpt = _dOptions  if not dOptions  else dOptions
        lPointer = []
        bTagAndRewrite = False
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
                    bChange, dErr = self._executeActions(dGraph, dPointer["dNode"]["<rules>"], dPointer["iToken"]-1, dToken["i"], dPriority, dOpt, sCountry, bShowRuleId, bDebug, bContext)
                    self.dError.update(dErr)
                    if bChange:
                        bTagAndRewrite = True
        if bTagAndRewrite:
            self.rewrite(bDebug)
        return (bTagAndRewrite, self.sSentence)

    def _executeActions (self, dGraph, dNode, nTokenOffset, nLastToken, dPriority, dOptions, sCountry, bShowRuleId, bDebug, bContext):
        "execute actions found in the DARG"
        dError = {}
        bChange = False
        for sLineId, nextNodeKey in dNode.items():
            bCondMemo = None
            for sRuleId in dGraph[nextNodeKey]:
                try:
                    if bDebug:
                        print("  TRY:", sRuleId)
                    sOption, sFuncCond, cActionType, sWhat, *eAct = dRule[sRuleId]
                    # Suggestion    [ option, condition, "-", replacement/suggestion/action, iTokenStart, iTokenEnd, nPriority, message, URL ]
                    # TextProcessor [ option, condition, "~", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    # Disambiguator [ option, condition, "=", replacement/suggestion/action ]
                    # Sentence Tag  [ option, condition, "/", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    # Test          [ option, condition, ">", "" ]
                    if not sOption or dOptions.get(sOption, False):
                        bCondMemo = not sFuncCond or globals()[sFuncCond](self.lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, self.dTags, self.sSentence, self.sSentence0)
                        if bCondMemo:
                            if cActionType == "-":
                                # grammar error
                                nTokenErrorStart = nTokenOffset + eAct[0]
                                if "bImmune" not in self.lToken[nTokenErrorStart]:
                                    nTokenErrorEnd = (nTokenOffset + eAct[1])  if eAct[1]  else nLastToken
                                    nErrorStart = self.nOffsetWithinParagraph + self.lToken[nTokenErrorStart]["nStart"]
                                    nErrorEnd = self.nOffsetWithinParagraph + self.lToken[nTokenErrorEnd]["nEnd"]
                                    if nErrorStart not in dError or eAct[2] > dPriority.get(nErrorStart, -1):
                                        dError[nErrorStart] = self._createError(sWhat, nTokenOffset, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, True, eAct[3], eAct[4], bShowRuleId, "notype", bContext)
                                        dPriority[nErrorStart] = eAct[2]
                                        if bDebug:
                                            print("  NEW_ERROR:", dError[nErrorStart], "\n  ", dRule[sRuleId])
                            elif cActionType == "~":
                                # text processor
                                if bDebug:
                                    print("  TAG_PREPARE:\n  ", dRule[sRuleId])
                                nEndToken = (nTokenOffset + eAct[1])  if eAct[1]  else nLastToken
                                self._tagAndPrepareTokenForRewriting(sWhat, nTokenOffset + eAct[0], nEndToken, nTokenOffset, True, bDebug)
                                bChange = True
                            elif cActionType == "=":
                                # disambiguation
                                if bDebug:
                                    print("  DISAMBIGUATOR:\n  ", dRule[sRuleId])
                                globals()[sWhat](self.lToken, nTokenOffset)
                            elif cActionType == ">":
                                # we do nothing, this test is just a condition to apply all following actions
                                if bDebug:
                                    print("  COND_OK")
                                pass
                            elif cActionType == "/":
                                # sentence tags
                                if bDebug:
                                    print("  SENTENCE_TAG:\n  ", dRule[sRuleId])
                                nTokenTag = nTokenOffset + eAct[0]
                                if sWhat not in self.dTags:
                                    self.dTags[sWhat] = (nTokenTag, nTokenTag)
                                elif nTokenTag > self.dTags[sWhat][1]:
                                    self.dTags[sWhat] = (self.dTags[sWhat][0], nTokenTag)
                            else:
                                print("# error: unknown action at " + sLineId)
                        elif cActionType == ">":
                            if bDebug:
                                print("  COND_BREAK")
                            break
                except Exception as e:
                    raise Exception(str(e), sLineId, sRuleId, self.sSentence)
        return bChange, dError

    def _createError (self, sSugg, nTokenOffset, iFirstToken, nStart, nEnd, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext):
        # suggestions
        if sSugg[0:1] == "=":
            sSugg = globals()[sSugg[1:]](self.lToken, nTokenOffset)
            lSugg = sSugg.split("|")  if sSugg  else []
        elif sSugg == "_":
            lSugg = []
        else:
            lSugg = self._expand(sSugg, nTokenOffset).split("|")
        if bUppercase and lSugg and self.lToken[iFirstToken]["sValue"][0:1].isupper():
            lSugg = list(map(str.capitalize, lSugg))
        # Message
        sMessage = globals()[sMsg[1:]](self.lToken, nTokenOffset)  if sMsg[0:1] == "="  else self._expand(sMsg, nTokenOffset)
        if bShowRuleId:
            sMessage += "  " + sLineId + " # " + sRuleId
        #
        if _bWriterError:
            xErr = SingleProofreadingError()    # uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
            xErr.nErrorStart = nStart
            xErr.nErrorLength = nEnd - nStart
            xErr.nErrorType = PROOFREADING
            xErr.aRuleIdentifier = sRuleId
            xErr.aShortComment = sMessage   # sMessage.split("|")[0]     # in context menu
            xErr.aFullComment = sMessage   # sMessage.split("|")[-1]    # in dialog
            if bShowRuleId:
                xErr.aShortComment += "  " + sLineId + " # " + sRuleId
            xErr.aSuggestions = tuple(lSugg)
            if sURL:
                xProperty = PropertyValue()
                xProperty.Name = "FullCommentURL"
                xProperty.Value = sURL
                xErr.aProperties = (xProperty,)
            else:
                xErr.aProperties = ()
            return xErr
        else:
            dErr = {}
            dErr["nStart"] = nStart
            dErr["nEnd"] = nEnd
            dErr["sLineId"] = sLineId
            dErr["sRuleId"] = sRuleId
            dErr["sType"] = sOption  if sOption  else "notype"
            dErr["sMessage"] = sMessage
            dErr["aSuggestions"] = lSugg
            dErr["URL"] = sURL  if sURL  else ""
            if bContext:
                dErr['sUnderlined'] = self.sSentence0[nStart:nEnd]
                dErr['sBefore'] = self.sSentence0[max(0,nStart-80):nStart]
                dErr['sAfter'] = self.sSentence0[nEnd:nEnd+80]
            return dErr

    def _expand (self, sText, nTokenOffset):
        #print("*", sText)
        for m in re.finditer(r"\\([0-9]+)", sText):
            sText = sText.replace(m.group(0), self.lToken[int(m.group(1))+nTokenOffset]["sValue"])
        #print(">", sText)
        return sText

    def _tagAndPrepareTokenForRewriting (self, sWhat, nTokenRewriteStart, nTokenRewriteEnd, nTokenOffset, bUppercase=True, bDebug=False):
        "text processor: rewrite tokens between <nTokenRewriteStart> and <nTokenRewriteEnd> position"
        if bDebug:
            print("  REWRITING:", nTokenRewriteStart, nTokenRewriteEnd)
        if sWhat == "*":
            # purge text
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                self.lToken[nTokenRewriteStart]["bToRemove"] = True
            else:
                for i in range(nTokenRewriteStart, nTokenRewriteEnd+1):
                    self.lToken[i]["bToRemove"] = True
        elif sWhat == "␣":
            # merge tokens
            self.lToken[nTokenRewriteStart]["nMergeUntil"] = nTokenRewriteEnd
        elif sWhat == "!":
            # immunity
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                self.lToken[nTokenRewriteStart]["bImmune"] = True
            else:
                for i in range(nTokenRewriteStart, nTokenRewriteEnd+1):
                    self.lToken[i]["bImmune"] = True
        elif sWhat == "_":
            # neutralized token
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                self.lToken[nTokenRewriteStart]["sNewValue"] = "_"
            else:
                for i in range(nTokenRewriteStart, nTokenRewriteEnd+1):
                    self.lToken[i]["sNewValue"] = "_"
        else:
            if sWhat.startswith("="):
                sWhat = globals()[sWhat[1:]](self.lToken, nTokenOffset)
            else:
                sWhat = self._expand(sWhat, nTokenOffset)
            bUppercase = bUppercase and self.lToken[nTokenRewriteStart]["sValue"][0:1].isupper()
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                # one token
                sWhat = sWhat + " " * (len(self.lToken[nTokenRewriteStart]["sValue"])-len(sWhat))
                if bUppercase:
                    sWhat = sWhat[0:1].upper() + sWhat[1:]
                self.lToken[nTokenRewriteStart]["sNewValue"] = sWhat
            else:
                # several tokens
                lTokenValue = sWhat.split("|")
                if len(lTokenValue) != (nTokenRewriteEnd - nTokenRewriteStart + 1):
                    print("Error. Text processor: number of replacements != number of tokens.")
                    return
                for i, sValue in zip(range(nTokenRewriteStart, nTokenRewriteEnd+1), lTokenValue):
                    if not sValue or sValue == "*":
                        self.lToken[i]["bToRemove"] = True
                    else:
                        if bUppercase:
                            sValue = sValue[0:1].upper() + sValue[1:]
                        self.lToken[i]["sNewValue"] = sValue

    def rewrite (self, bDebug=False):
        "rewrite the sentence, modify tokens, purge the token list"
        if bDebug:
            print("REWRITE")
        lNewToken = []
        nMergeUntil = 0
        dTokenMerger = None
        for dToken in self.lToken:
            bKeepToken = True
            if "bImmune" in dToken:
                nErrorStart = self.nOffsetWithinParagraph + dToken["nStart"]
                if nErrorStart in self.dError:
                    if bDebug:
                        print("immunity -> error removed:", self.dError[nErrorStart])
                    del self.dError[nErrorStart]
            if nMergeUntil and dToken["i"] <= nMergeUntil:
                dTokenMerger["sValue"] += " " * (dToken["nStart"] - dTokenMerger["nEnd"]) + dToken["sValue"]
                dTokenMerger["nEnd"] = dToken["nEnd"]
                if bDebug:
                    print("  MERGED TOKEN:", dTokenMerger["sValue"])
                bKeepToken = False
            if "nMergeUntil" in dToken:
                if dToken["i"] > nMergeUntil: # this token is not already merged with a previous token
                    dTokenMerger = dToken
                if dToken["nMergeUntil"] > nMergeUntil:
                    nMergeUntil = dToken["nMergeUntil"]
                del dToken["nMergeUntil"]
            elif "bToRemove" in dToken:
                if bDebug:
                    print("  REMOVED:", dToken["sValue"])
                self.sSentence = self.sSentence[:dToken["nStart"]] + " " * (dToken["nEnd"] - dToken["nStart"]) + self.sSentence[dToken["nEnd"]:]
                bKeepToken = False
            #
            if bKeepToken:
                lNewToken.append(dToken)
                if "sNewValue" in dToken:
                    # rewrite token and sentence
                    if bDebug:
                        print(dToken["sValue"], "->", dToken["sNewValue"])
                    dToken["sRealValue"] = dToken["sValue"]
                    dToken["sValue"] = dToken["sNewValue"]
                    nDiffLen = len(dToken["sRealValue"]) - len(dToken["sNewValue"])
                    sNewRepl = (dToken["sNewValue"] + " " * nDiffLen)  if nDiffLen >= 0  else dToken["sNewValue"][:len(dToken["sRealValue"])]
                    self.sSentence = self.sSentence[:dToken["nStart"]] + sNewRepl + self.sSentence[dToken["nEnd"]:]
                    del dToken["sNewValue"]
        if bDebug:
            print("  REWRITED:", self.sSentence)
        self.lToken.clear()
        self.lToken = lNewToken



#### Analyse tokens

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
        else:
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
            zPattern = re.compile(sPattern)
            return all(zPattern.search(sMorph)  for sMorph in lMorph)
        else:
            zNegPattern = re.compile(sNegPattern)
            if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
                return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)


def g_tag_before (dToken, dTags, sTag):
    if sTag not in dTags:
        return False
    if dToken["i"] > dTags[sTag][0]:
        return True
    return False


def g_tag_after (dToken, dTags, sTag):
    if sTag not in dTags:
        return False
    if dToken["i"] < dTags[sTag][1]:
        return True
    return False


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



#### GRAMMAR CHECKER PLUGINS

${plugins}


#### CALLABLES FOR REGEX RULES (generated code)

${callables}


#### CALLABLES FOR GRAPH RULES (generated code)

${graph_callables}
