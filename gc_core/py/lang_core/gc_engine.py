"""
Grammalecte
Grammar checker engine
"""

import re
import traceback
#import unicodedata
from itertools import chain

from ..graphspell.spellchecker import SpellChecker
from ..graphspell.echo import echo

from .. import text

from . import gc_options

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
            "ignoreRule", "resetIgnoreRules", "reactivateRule", "listRules", "displayRules", "setWriterUnderliningStyle" ]

__version__ = "${version}"


lang = "${lang}"
locales = ${loc}
pkg = "${implname}"
name = "${name}"
version = "${version}"
author = "${author}"

# Modules
_rules = None                               # module gc_rules
_rules_graph = None                         # module gc_rules_graph

# Tools
_oSpellChecker = None
_oTokenizer = None

# Data
_sAppContext = ""                           # what software is running
_aIgnoredRules = set()

# Writer underlining style
_dOptionsColors = None
_bMulticolor = True
_nUnderliningStyle = 0


#### Initialization

def load (sContext="Python", sColorType="aRGB"):
    "initialization of the grammar checker"
    global _oSpellChecker
    global _sAppContext
    global _dOptionsColors
    global _oTokenizer
    try:
        _sAppContext = sContext
        _oSpellChecker = SpellChecker("${lang}", "${dic_main_filename_py}", "${dic_community_filename_py}", "${dic_personal_filename_py}")
        _oSpellChecker.activateStorage()
        _oTokenizer = _oSpellChecker.getTokenizer()
        gc_options.load(sContext)
        _dOptionsColors = gc_options.getOptionsColors(sContext, sColorType)
    except:
        traceback.print_exc()


def getSpellChecker ():
    "return the spellchecker object"
    return _oSpellChecker


#### Rules

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
    from . import gc_rules_graph
    global _rules
    global _rules_graph
    _rules = gc_rules
    _rules_graph = gc_rules_graph
    # compile rules regex
    for sOption, lRuleGroup in chain(_rules.lParagraphRules, _rules.lSentenceRules):
        if sOption != "@@@@":
            for aRule in lRuleGroup:
                try:
                    aRule[0] = re.compile(aRule[0])
                except (IndexError, re.error):
                    echo("Bad regular expression in # " + str(aRule[2]))
                    aRule[0] = "(?i)<Grammalecte>"


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
        except re.error:
            echo("# Error. List rules: wrong regex.")
            sFilter = None
    # regex rules
    for sOption, lRuleGroup in chain(_getRules(True), _getRules(False)):
        if sOption != "@@@@":
            for _, _, sLineId, sRuleId, _, _ in lRuleGroup:
                if not sFilter or zFilter.search(sRuleId):
                    yield ("RegEx", sOption, sLineId, sRuleId)
    # tokens rules
    for sRuleName, lActions in _rules_graph.dRule.items():
        sLineId, sOption, _, cActionType, *_ = lActions
        if cActionType == "-":
            yield("Tokens", sOption, sLineId, sRuleName)


def displayRules (sFilter=None):
    "display the name of rules, with the filter <sFilter>"
    echo("List of rules. Filter: << " + str(sFilter) + " >>")
    for sOption, sLineId, sRuleId, sType in listRules(sFilter):
        echo("{:<8} {:<10} {:<10} {}".format(sOption, sLineId, sRuleId, sType))


#### Options (just calls to gc_options, to keep for compatibility)

def setOption (sOpt, bVal):
    "set option <sOpt> with <bVal> if it exists"
    gc_options.setOption(sOpt, bVal)


def setOptions (dOpt):
    "update the dictionary of options with <dOpt>"
    gc_options.setOptions(dOpt)


def getOptions ():
    "return the dictionary of current options"
    return gc_options.getOptions()


def getDefaultOptions ():
    "return the dictionary of default options"
    return gc_options.getDefaultOptions()


def getOptionsLabels (sLang="${lang}"):
    "return options labels"
    return gc_options.getOptionLabels(sLang)


def displayOptions (sLang="${lang}"):
    "print options"
    gc_options.displayOptions(sLang)


def resetOptions ():
    "set options to default values"
    gc_options.resetOptions()


def setWriterUnderliningStyle (sStyle="BOLDWAVE", bMulticolor=True):
    "set underlining style for Writer (WAVE, BOLDWAVE, BOLD)"
    global _nUnderliningStyle
    global _bMulticolor
    # https://api.libreoffice.org/docs/idl/ref/FontUnderline_8idl.html
    # WAVE: 10, BOLD: 12, BOLDWAVE: 18 DASH: 5
    if sStyle == "WAVE":
        _nUnderliningStyle = 0  # 0 for default Writer setting
    elif sStyle == "BOLDWAVE":
        _nUnderliningStyle = 18
    elif sStyle == "BOLD":
        _nUnderliningStyle = 12
    elif sStyle == "DASH":
        _nUnderliningStyle = 5
    else:
        _nUnderliningStyle = 0
    _bMulticolor = bMulticolor


#### Parsing

def parse (sText, sCountry="${country_default}", bDebug=False, dOptions=None, bContext=False, bFullInfo=False):
    "init point to analyse <sText> and returns an iterable of errors or (with option <bFullInfo>) paragraphs errors and sentences with tokens and errors"
    oText = TextParser(sText)
    return oText.parse(sCountry, bDebug, dOptions, bContext, bFullInfo)


#### TEXT PARSER

class TextParser:
    "Text parser"

    def __init__ (self, sText):
        self.sText = sText
        self.sText0 = sText
        self.sSentence = ""
        self.sSentence0 = ""
        self.nOffsetWithinParagraph = 0
        self.lToken = []
        self.dTokenPos = {}         # {position: token}
        self.dTags = {}             # {position: tags}
        self.dError = {}            # {position: error}
        self.dSentenceError = {}    # {position: error} (for the current sentence only)
        self.dErrorPriority = {}    # {position: priority of the current error}

    def __str__ (self):
        s = "===== TEXT =====\n"
        s += "sentence: " + self.sSentence0 + "\n"
        s += "now:      " + self.sSentence  + "\n"
        for dToken in self.lToken:
            s += '#{i}\t{nStart}:{nEnd}\t{sValue}\t{sType}'.format(**dToken)
            if "lMorph" in dToken:
                s += "\t" + str(dToken["lMorph"])
            if "aTags" in dToken:
                s += "\t" + str(dToken["aTags"])
            s += "\n"
        #for nPos, dToken in self.dTokenPos.items():
        #    s += "{}\t{}\n".format(nPos, dToken)
        return s

    def parse (self, sCountry="${country_default}", bDebug=False, dOptions=None, bContext=False, bFullInfo=False):
        "analyses <sText> and returns an iterable of errors or (with option <bFullInfo>) paragraphs errors and sentences with tokens and errors"
        #sText = unicodedata.normalize("NFC", sText)
        dOpt = dOptions or gc_options.dOptions
        bShowRuleId = option('idrule')
        # parse paragraph
        try:
            self.parseText(self.sText, self.sText0, True, 0, sCountry, dOpt, bShowRuleId, bDebug, bContext)
        except:
            raise
        if bFullInfo:
            lParagraphErrors = list(self.dError.values())
            lSentences = []
            self.dSentenceError.clear()
        # parse sentences
        sText = self._getCleanText()
        for iStart, iEnd in text.getSentenceBoundaries(sText):
            if 4 < (iEnd - iStart) < 2000:
                try:
                    self.sSentence = sText[iStart:iEnd]
                    self.sSentence0 = self.sText0[iStart:iEnd]
                    self.nOffsetWithinParagraph = iStart
                    self.lToken = list(_oTokenizer.genTokens(self.sSentence, True))
                    self.dTokenPos = { dToken["nStart"]: dToken  for dToken in self.lToken  if dToken["sType"] != "INFO" }
                    if bFullInfo:
                        dSentence = { "nStart": iStart, "nEnd": iEnd, "sSentence": self.sSentence, "lToken": list(self.lToken) }
                        for dToken in dSentence["lToken"]:
                            if dToken["sType"] == "WORD":
                                dToken["bValidToken"] = _oSpellChecker.isValidToken(dToken["sValue"])
                        # the list of tokens is duplicated, to keep all tokens from being deleted when analysis
                    self.parseText(self.sSentence, self.sSentence0, False, iStart, sCountry, dOpt, bShowRuleId, bDebug, bContext)
                    if bFullInfo:
                        dSentence["lGrammarErrors"] = list(self.dSentenceError.values())
                        lSentences.append(dSentence)
                        self.dSentenceError.clear()
                except:
                    raise
        if bFullInfo:
            # Grammar checking and sentence analysis
            return lParagraphErrors, lSentences
        else:
            # Grammar checking only
            return self.dError.values() # this is a view (iterable)

    def _getCleanText (self):
        sText = self.sText
        if " " in sText:
            sText = sText.replace(" ", ' ') # nbsp
        if " " in sText:
            sText = sText.replace(" ", ' ') # nnbsp
        if "'" in sText:
            sText = sText.replace("'", "’")
        if "‐" in sText:
            sText = sText.replace("‐", "-") # Hyphen (U+2010)
        if "‑" in sText:
            sText = sText.replace("‑", "-") # Non-Breaking Hyphen (U+2011)
        if "@@" in sText:
            sText = re.sub("@@+", "", sText)
        return sText

    def parseText (self, sText, sText0, bParagraph, nOffset, sCountry, dOptions, bShowRuleId, bDebug, bContext):
        "parse the text with rules"
        bChange = False
        for sOption, lRuleGroup in _getRules(bParagraph):
            if sOption == "@@@@":
                # graph rules
                if not bParagraph and bChange:
                    self.update(sText, bDebug)
                    bChange = False
                for sGraphName, sLineId in lRuleGroup:
                    if sGraphName not in dOptions or dOptions[sGraphName]:
                        if bDebug:
                            echo("\n>>>> GRAPH: " + sGraphName + " " + sLineId)
                        sText = self.parseGraph(_rules_graph.dAllGraph[sGraphName], sCountry, dOptions, bShowRuleId, bDebug, bContext)
            elif not sOption or dOptions.get(sOption, False):
                # regex rules
                for zRegex, bUppercase, sLineId, sRuleId, nPriority, lActions in lRuleGroup:
                    if sRuleId not in _aIgnoredRules:
                        for m in zRegex.finditer(sText):
                            bCondMemo = None
                            for sFuncCond, cActionType, sWhat, *eAct in lActions:
                                # action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                                try:
                                    bCondMemo = not sFuncCond or globals()[sFuncCond](sText, sText0, m, self.dTokenPos, sCountry, bCondMemo)
                                    if bCondMemo:
                                        if bDebug:
                                            echo("RULE: " + sLineId)
                                        if cActionType == "-":
                                            # grammar error
                                            nErrorStart = nOffset + m.start(eAct[0])
                                            if nErrorStart not in self.dError or nPriority > self.dErrorPriority.get(nErrorStart, -1):
                                                self.dError[nErrorStart] = self._createErrorFromRegex(sText, sText0, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bShowRuleId, sOption, bContext)
                                                self.dErrorPriority[nErrorStart] = nPriority
                                                self.dSentenceError[nErrorStart] = self.dError[nErrorStart]
                                        elif cActionType == "~":
                                            # text processor
                                            sText = self.rewriteText(sText, sWhat, eAct[0], m, bUppercase)
                                            bChange = True
                                            if bDebug:
                                                echo("~ " + sText + "  -- " + m.group(eAct[0]) + "  # " + sLineId)
                                        elif cActionType == "=":
                                            # disambiguation
                                            if not bParagraph:
                                                globals()[sWhat](sText, m, self.dTokenPos)
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
        if bChange:
            if bParagraph:
                self.sText = sText
            else:
                self.sSentence = sText

    def update (self, sSentence, bDebug=False):
        "update <sSentence> and retokenize"
        self.sSentence = sSentence
        lNewToken = list(_oTokenizer.genTokens(sSentence, True))
        for dToken in lNewToken:
            if "lMorph" in self.dTokenPos.get(dToken["nStart"], {}):
                dToken["lMorph"] = self.dTokenPos[dToken["nStart"]]["lMorph"]
            if "aTags" in self.dTokenPos.get(dToken["nStart"], {}):
                dToken["aTags"] = self.dTokenPos[dToken["nStart"]]["aTags"]
        self.lToken = lNewToken
        self.dTokenPos = { dToken["nStart"]: dToken  for dToken in self.lToken  if dToken["sType"] != "INFO" }
        if bDebug:
            echo("UPDATE:")
            echo(self)

    def _getNextPointers (self, dToken, dGraph, dPointer, bDebug=False):
        "generator: return nodes where <dToken> “values” match <dNode> arcs"
        dNode = dGraph[dPointer["iNode"]]
        iToken1 = dPointer["iToken1"]
        bTokenFound = False
        # token value
        if dToken["sValue"] in dNode:
            if bDebug:
                echo("  MATCH: " + dToken["sValue"])
            yield { "iToken1": iToken1, "iNode": dNode[dToken["sValue"]] }
            bTokenFound = True
        if dToken["sValue"][0:2].istitle(): # we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
            sValue = dToken["sValue"].lower()
            if sValue in dNode:
                if bDebug:
                    echo("  MATCH: " + sValue)
                yield { "iToken1": iToken1, "iNode": dNode[sValue] }
                bTokenFound = True
        elif dToken["sValue"].isupper():
            sValue = dToken["sValue"].lower()
            if sValue in dNode:
                if bDebug:
                    echo("  MATCH: " + sValue)
                yield { "iToken1": iToken1, "iNode": dNode[sValue] }
                bTokenFound = True
            sValue = dToken["sValue"].capitalize()
            if sValue in dNode:
                if bDebug:
                    echo("  MATCH: " + sValue)
                yield { "iToken1": iToken1, "iNode": dNode[sValue] }
                bTokenFound = True
        # regex value arcs
        if dToken["sType"] not in frozenset(["INFO", "PUNC", "SIGN"]):
            if "<re_value>" in dNode:
                for sRegex in dNode["<re_value>"]:
                    if "¬" not in sRegex:
                        # no anti-pattern
                        if re.search(sRegex, dToken["sValue"]):
                            if bDebug:
                                echo("  MATCH: ~" + sRegex)
                            yield { "iToken1": iToken1, "iNode": dNode["<re_value>"][sRegex] }
                            bTokenFound = True
                    else:
                        # there is an anti-pattern
                        sPattern, sNegPattern = sRegex.split("¬", 1)
                        if sNegPattern and re.search(sNegPattern, dToken["sValue"]):
                            continue
                        if not sPattern or re.search(sPattern, dToken["sValue"]):
                            if bDebug:
                                echo("  MATCH: ~" + sRegex)
                            yield { "iToken1": iToken1, "iNode": dNode["<re_value>"][sRegex] }
                            bTokenFound = True
        # analysable tokens
        if dToken["sType"][0:4] == "WORD":
            # token lemmas
            if "<lemmas>" in dNode:
                for sLemma in _oSpellChecker.getLemma(dToken["sValue"]):
                    if sLemma in dNode["<lemmas>"]:
                        if bDebug:
                            echo("  MATCH: >" + sLemma)
                        yield { "iToken1": iToken1, "iNode": dNode["<lemmas>"][sLemma] }
                        bTokenFound = True
            # morph arcs
            if "<morph>" in dNode:
                lMorph = dToken.get("lMorph", _oSpellChecker.getMorph(dToken["sValue"]))
                if lMorph:
                    for sSearch in dNode["<morph>"]:
                        if "¬" not in sSearch:
                            # no anti-pattern
                            if any(sSearch in sMorph  for sMorph in lMorph):
                                if bDebug:
                                    echo("  MATCH: $" + sSearch)
                                yield { "iToken1": iToken1, "iNode": dNode["<morph>"][sSearch] }
                                bTokenFound = True
                        else:
                            # there is an anti-pattern
                            sPattern, sNegPattern = sSearch.split("¬", 1)
                            if sNegPattern == "*":
                                # all morphologies must match with <sPattern>
                                if sPattern:
                                    if all(sPattern in sMorph  for sMorph in lMorph):
                                        if bDebug:
                                            echo("  MATCH: $" + sSearch)
                                        yield { "iToken1": iToken1, "iNode": dNode["<morph>"][sSearch] }
                                        bTokenFound = True
                            else:
                                if sNegPattern and any(sNegPattern in sMorph  for sMorph in lMorph):
                                    continue
                                if not sPattern or any(sPattern in sMorph  for sMorph in lMorph):
                                    if bDebug:
                                        echo("  MATCH: $" + sSearch)
                                    yield { "iToken1": iToken1, "iNode": dNode["<morph>"][sSearch] }
                                    bTokenFound = True
            # regex morph arcs
            if "<re_morph>" in dNode:
                lMorph = dToken.get("lMorph", _oSpellChecker.getMorph(dToken["sValue"]))
                if lMorph:
                    for sRegex in dNode["<re_morph>"]:
                        if "¬" not in sRegex:
                            # no anti-pattern
                            if any(re.search(sRegex, sMorph)  for sMorph in lMorph):
                                if bDebug:
                                    echo("  MATCH: @" + sRegex)
                                yield { "iToken1": iToken1, "iNode": dNode["<re_morph>"][sRegex] }
                                bTokenFound = True
                        else:
                            # there is an anti-pattern
                            sPattern, sNegPattern = sRegex.split("¬", 1)
                            if sNegPattern == "*":
                                # all morphologies must match with <sPattern>
                                if sPattern:
                                    if all(re.search(sPattern, sMorph)  for sMorph in lMorph):
                                        if bDebug:
                                            echo("  MATCH: @" + sRegex)
                                        yield { "iToken1": iToken1, "iNode": dNode["<re_morph>"][sRegex] }
                                        bTokenFound = True
                            else:
                                if sNegPattern and any(re.search(sNegPattern, sMorph)  for sMorph in lMorph):
                                    continue
                                if not sPattern or any(re.search(sPattern, sMorph)  for sMorph in lMorph):
                                    if bDebug:
                                        echo("  MATCH: @" + sRegex)
                                    yield { "iToken1": iToken1, "iNode": dNode["<re_morph>"][sRegex] }
                                    bTokenFound = True
        # token tags
        if "aTags" in dToken and "<tags>" in dNode:
            for sTag in dToken["aTags"]:
                if sTag in dNode["<tags>"]:
                    if bDebug:
                        echo("  MATCH: /" + sTag)
                    yield { "iToken1": iToken1, "iNode": dNode["<tags>"][sTag] }
                    bTokenFound = True
        # meta arc (for token type)
        if "<meta>" in dNode:
            for sMeta in dNode["<meta>"]:
                # no regex here, we just search if <dNode["sType"]> exists within <sMeta>
                if sMeta == "*" or dToken["sType"] == sMeta:
                    if bDebug:
                        echo("  MATCH: *" + sMeta)
                    yield { "iToken1": iToken1, "iNode": dNode["<meta>"][sMeta] }
                    bTokenFound = True
                elif "¬" in sMeta:
                    if dToken["sType"] not in sMeta:
                        if bDebug:
                            echo("  MATCH: *" + sMeta)
                        yield { "iToken1": iToken1, "iNode": dNode["<meta>"][sMeta] }
                        bTokenFound = True
        if not bTokenFound and "bKeep" in dPointer:
            yield dPointer
        # JUMP
        # Warning! Recurssion!
        if "<>" in dNode:
            dPointer2 = { "iToken1": iToken1, "iNode": dNode["<>"], "bKeep": True }
            yield from self._getNextPointers(dToken, dGraph, dPointer2, bDebug)

    def parseGraph (self, dGraph, sCountry="${country_default}", dOptions=None, bShowRuleId=False, bDebug=False, bContext=False):
        "parse graph with tokens from the text and execute actions encountered"
        lPointer = []
        bTagAndRewrite = False
        for iToken, dToken in enumerate(self.lToken):
            if bDebug:
                echo("TOKEN: " + dToken["sValue"])
            # check arcs for each existing pointer
            lNextPointer = []
            for dPointer in lPointer:
                lNextPointer.extend(self._getNextPointers(dToken, dGraph, dPointer, bDebug))
            lPointer = lNextPointer
            # check arcs of first nodes
            lPointer.extend(self._getNextPointers(dToken, dGraph, { "iToken1": iToken, "iNode": 0 }, bDebug))
            # check if there is rules to check for each pointer
            for dPointer in lPointer:
                #if bDebug:
                #    echo("+", dPointer)
                if "<rules>" in dGraph[dPointer["iNode"]]:
                    bChange = self._executeActions(dGraph, dGraph[dPointer["iNode"]]["<rules>"], dPointer["iToken1"]-1, iToken, dOptions, sCountry, bShowRuleId, bDebug, bContext)
                    if bChange:
                        bTagAndRewrite = True
        if bTagAndRewrite:
            self.rewriteFromTags(bDebug)
        if bDebug:
            echo(self)
        return self.sSentence

    def _executeActions (self, dGraph, dNode, nTokenOffset, nLastToken, dOptions, sCountry, bShowRuleId, bDebug, bContext):
        "execute actions found in the DARG"
        bChange = False
        for sLineId, nextNodeKey in dNode.items():
            bCondMemo = None
            for sRuleId in dGraph[nextNodeKey]:
                try:
                    if bDebug:
                        echo("   >TRY: " + sRuleId + " " + sLineId)
                    _, sOption, sFuncCond, cActionType, sWhat, *eAct = _rules_graph.dRule[sRuleId]
                    # Suggestion    [ option, condition, "-", replacement/suggestion/action, iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, iURL ]
                    # TextProcessor [ option, condition, "~", replacement/suggestion/action, iTokenStart, iTokenEnd, bCaseSvty ]
                    # Disambiguator [ option, condition, "=", replacement/suggestion/action ]
                    # Tag           [ option, condition, "/", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    # Immunity      [ option, condition, "!", "",                            iTokenStart, iTokenEnd ]
                    # Test          [ option, condition, ">", "" ]
                    if not sOption or dOptions.get(sOption, False):
                        bCondMemo = not sFuncCond or globals()[sFuncCond](self.lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, self.dTags, self.sSentence, self.sSentence0)
                        if bCondMemo:
                            if cActionType == "-":
                                # grammar error
                                iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, iURL = eAct
                                nTokenErrorStart = nTokenOffset + iTokenStart  if iTokenStart > 0  else nLastToken + iTokenStart
                                if "bImmune" not in self.lToken[nTokenErrorStart]:
                                    nTokenErrorEnd = nTokenOffset + iTokenEnd  if iTokenEnd > 0  else nLastToken + iTokenEnd
                                    nErrorStart = self.nOffsetWithinParagraph + (self.lToken[nTokenErrorStart]["nStart"] if cStartLimit == "<"  else self.lToken[nTokenErrorStart]["nEnd"])
                                    nErrorEnd = self.nOffsetWithinParagraph + (self.lToken[nTokenErrorEnd]["nEnd"] if cEndLimit == ">"  else self.lToken[nTokenErrorEnd]["nStart"])
                                    if nErrorStart not in self.dError or nPriority > self.dErrorPriority.get(nErrorStart, -1):
                                        self.dError[nErrorStart] = self._createErrorFromTokens(sWhat, nTokenOffset, nLastToken, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, bCaseSvty, \
                                                                                               sMessage, _rules_graph.dURL.get(iURL, ""), bShowRuleId, sOption, bContext)
                                        self.dErrorPriority[nErrorStart] = nPriority
                                        self.dSentenceError[nErrorStart] = self.dError[nErrorStart]
                                        if bDebug:
                                            echo("    NEW_ERROR: {}".format(self.dError[nErrorStart]))
                            elif cActionType == "~":
                                # text processor
                                nTokenStart = nTokenOffset + eAct[0]  if eAct[0] > 0  else nLastToken + eAct[0]
                                nTokenEnd = nTokenOffset + eAct[1]  if eAct[1] > 0  else nLastToken + eAct[1]
                                self._tagAndPrepareTokenForRewriting(sWhat, nTokenStart, nTokenEnd, nTokenOffset, nLastToken, eAct[2], bDebug)
                                bChange = True
                                if bDebug:
                                    echo("    TEXT_PROCESSOR: [{}:{}]  > {}".format(self.lToken[nTokenStart]["sValue"], self.lToken[nTokenEnd]["sValue"], sWhat))
                            elif cActionType == "=":
                                # disambiguation
                                globals()[sWhat](self.lToken, nTokenOffset, nLastToken)
                                if bDebug:
                                    echo("    DISAMBIGUATOR: ({})  [{}:{}]".format(sWhat, self.lToken[nTokenOffset+1]["sValue"], self.lToken[nLastToken]["sValue"]))
                            elif cActionType == ">":
                                # we do nothing, this test is just a condition to apply all following actions
                                if bDebug:
                                    echo("    COND_OK")
                            elif cActionType == "/":
                                # Tag
                                nTokenStart = nTokenOffset + eAct[0]  if eAct[0] > 0  else nLastToken + eAct[0]
                                nTokenEnd = nTokenOffset + eAct[1]  if eAct[1] > 0  else nLastToken + eAct[1]
                                for i in range(nTokenStart, nTokenEnd+1):
                                    if "aTags" in self.lToken[i]:
                                        self.lToken[i]["aTags"].update(sWhat.split("|"))
                                    else:
                                        self.lToken[i]["aTags"] = set(sWhat.split("|"))
                                if bDebug:
                                    echo("    TAG: {} >  [{}:{}]".format(sWhat, self.lToken[nTokenStart]["sValue"], self.lToken[nTokenEnd]["sValue"]))
                                for sTag in sWhat.split("|"):
                                    if sTag not in self.dTags:
                                        self.dTags[sTag] = [nTokenStart, nTokenEnd]
                                    else:
                                        self.dTags[sTag][0] = min(nTokenStart, self.dTags[sTag][0])
                                        self.dTags[sTag][1] = max(nTokenEnd, self.dTags[sTag][1])
                            elif cActionType == "!":
                                # immunity
                                if bDebug:
                                    echo("    IMMUNITY: " + sLineId + " / " + sRuleId)
                                nTokenStart = nTokenOffset + eAct[0]  if eAct[0] > 0  else nLastToken + eAct[0]
                                nTokenEnd = nTokenOffset + eAct[1]  if eAct[1] > 0  else nLastToken + eAct[1]
                                if nTokenEnd - nTokenStart == 0:
                                    self.lToken[nTokenStart]["bImmune"] = True
                                    nErrorStart = self.nOffsetWithinParagraph + self.lToken[nTokenStart]["nStart"]
                                    if nErrorStart in self.dError:
                                        del self.dError[nErrorStart]
                                else:
                                    for i in range(nTokenStart, nTokenEnd+1):
                                        self.lToken[i]["bImmune"] = True
                                        nErrorStart = self.nOffsetWithinParagraph + self.lToken[i]["nStart"]
                                        if nErrorStart in self.dError:
                                            del self.dError[nErrorStart]
                            else:
                                echo("# error: unknown action at " + sLineId)
                        elif cActionType == ">":
                            if bDebug:
                                echo("    COND_BREAK")
                            break
                except Exception as e:
                    raise Exception(str(e), sLineId, sRuleId, self.sSentence)
        return bChange

    def _createErrorFromRegex (self, sText, sText0, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bCaseSvty, sMsg, sURL, bShowRuleId, sOption, bContext):
        nStart = nOffset + m.start(iGroup)
        nEnd = nOffset + m.end(iGroup)
        # suggestions
        if sRepl[0:1] == "=":
            sSugg = globals()[sRepl[1:]](sText, m)
            lSugg = sSugg.split("|")  if sSugg  else []
        elif sRepl == "_":
            lSugg = []
        else:
            lSugg = m.expand(sRepl).split("|")
        if bCaseSvty and lSugg and m.group(iGroup)[0:1].isupper():
            lSugg = list(map(lambda s: s.upper(), lSugg))  if m.group(iGroup).isupper()  else list(map(lambda s: s[0:1].upper()+s[1:], lSugg))
        # Message
        sMessage = globals()[sMsg[1:]](sText, m)  if sMsg[0:1] == "="  else  m.expand(sMsg)
        if bShowRuleId:
            sMessage += "  #" + sLineId + " / " + sRuleId
        #
        if _bWriterError:
            return self._createErrorForWriter(nStart, nEnd - nStart, sRuleId, sOption, sMessage, lSugg, sURL)
        return self._createErrorAsDict(nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext)

    def _createErrorFromTokens (self, sSugg, nTokenOffset, nLastToken, iFirstToken, nStart, nEnd, sLineId, sRuleId, bCaseSvty, sMsg, sURL, bShowRuleId, sOption, bContext):
        # suggestions
        if sSugg[0:1] == "=":
            sSugg = globals()[sSugg[1:]](self.lToken, nTokenOffset, nLastToken)
            lSugg = sSugg.split("|")  if sSugg  else []
        elif sSugg == "_":
            lSugg = []
        else:
            lSugg = self._expand(sSugg, nTokenOffset, nLastToken).split("|")
        if bCaseSvty and lSugg and self.lToken[iFirstToken]["sValue"][0:1].isupper():
            lSugg = list(map(lambda s: s.upper(), lSugg))  if self.sSentence[nStart:nEnd].isupper()  else list(map(lambda s: s[0:1].upper()+s[1:], lSugg))
        # Message
        sMessage = globals()[sMsg[1:]](self.lToken, nTokenOffset, nLastToken)  if sMsg[0:1] == "="  else self._expand(sMsg, nTokenOffset, nLastToken)
        if bShowRuleId:
            sMessage += "  #" + sLineId + " / " + sRuleId
        #
        if _bWriterError:
            return self._createErrorForWriter(nStart, nEnd - nStart, sRuleId, sOption, sMessage, lSugg, sURL)
        return self._createErrorAsDict(nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext)

    def _createErrorForWriter (self, nStart, nLen, sRuleId, sOption, sMessage, lSugg, sURL):
        xErr = SingleProofreadingError()    # uno.createUnoStruct( "com.sun.star.linguistic2.SingleProofreadingError" )
        xErr.nErrorStart = nStart
        xErr.nErrorLength = nLen
        xErr.nErrorType = PROOFREADING
        xErr.aRuleIdentifier = sRuleId
        xErr.aShortComment = sMessage   # sMessage.split("|")[0]     # in context menu
        xErr.aFullComment = sMessage    # sMessage.split("|")[-1]    # in dialog
        xErr.aSuggestions = tuple(lSugg)
        # Properties
        lProperties = []
        if _nUnderliningStyle:
            lProperties.append(PropertyValue(Name="LineType", Value=_nUnderliningStyle))
        if _bMulticolor:
            lProperties.append(PropertyValue(Name="LineColor", Value=_dOptionsColors.get(sOption, 33023)))
        if sURL:
            lProperties.append(PropertyValue(Name="FullCommentURL", Value=sURL))
        xErr.aProperties = lProperties
        return xErr

    def _createErrorAsDict (self, nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext):
        dErr = {
            "nStart": nStart,
            "nEnd": nEnd,
            "sLineId": sLineId,
            "sRuleId": sRuleId,
            "sType": sOption  if sOption  else "notype",
            "aColor": _dOptionsColors.get(sOption, None),
            "sMessage": sMessage,
            "aSuggestions": lSugg,
            "URL": sURL
        }
        if bContext:
            dErr['sUnderlined'] = self.sText0[nStart:nEnd]
            dErr['sBefore'] = self.sText0[max(0,nStart-80):nStart]
            dErr['sAfter'] = self.sText0[nEnd:nEnd+80]
        return dErr

    def _expand (self, sText, nTokenOffset, nLastToken):
        for m in re.finditer(r"\\(-?[0-9]+)", sText):
            if m.group(1)[0:1] == "-":
                sText = sText.replace(m.group(0), self.lToken[nLastToken+int(m.group(1))+1]["sValue"])
            else:
                sText = sText.replace(m.group(0), self.lToken[nTokenOffset+int(m.group(1))]["sValue"])
        return sText

    def rewriteText (self, sText, sRepl, iGroup, m, bUppercase):
        "text processor: write <sRepl> in <sText> at <iGroup> position"
        nLen = m.end(iGroup) - m.start(iGroup)
        if sRepl == "*":
            sNew = " " * nLen
        elif sRepl == "_":
            sNew = "_" * nLen
        elif sRepl == "@":
            sNew = "@" * nLen
        elif sRepl[0:1] == "=":
            sNew = globals()[sRepl[1:]](sText, m)
            sNew = sNew + " " * (nLen-len(sNew))
            if bUppercase and m.group(iGroup)[0:1].isupper():
                sNew = sNew.capitalize()
        else:
            sNew = m.expand(sRepl)
            sNew = sNew + " " * (nLen-len(sNew))
        return sText[0:m.start(iGroup)] + sNew + sText[m.end(iGroup):]

    def _tagAndPrepareTokenForRewriting (self, sWhat, nTokenRewriteStart, nTokenRewriteEnd, nTokenOffset, nLastToken, bCaseSvty, bDebug):
        "text processor: rewrite tokens between <nTokenRewriteStart> and <nTokenRewriteEnd> position"
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
        elif sWhat == "_":
            # neutralized token
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                self.lToken[nTokenRewriteStart]["sNewValue"] = "_"
            else:
                for i in range(nTokenRewriteStart, nTokenRewriteEnd+1):
                    self.lToken[i]["sNewValue"] = "_"
        else:
            if sWhat.startswith("="):
                sWhat = globals()[sWhat[1:]](self.lToken, nTokenOffset, nLastToken)
            else:
                sWhat = self._expand(sWhat, nTokenOffset, nLastToken)
            bUppercase = bCaseSvty and self.lToken[nTokenRewriteStart]["sValue"][0:1].isupper()
            if nTokenRewriteEnd - nTokenRewriteStart == 0:
                # one token
                if bUppercase:
                    sWhat = sWhat[0:1].upper() + sWhat[1:]
                self.lToken[nTokenRewriteStart]["sNewValue"] = sWhat
            else:
                # several tokens
                lTokenValue = sWhat.split("|")
                if len(lTokenValue) != (nTokenRewriteEnd - nTokenRewriteStart + 1):
                    if (bDebug):
                        echo("Error. Text processor: number of replacements != number of tokens.")
                    return
                for i, sValue in zip(range(nTokenRewriteStart, nTokenRewriteEnd+1), lTokenValue):
                    if not sValue or sValue == "*":
                        self.lToken[i]["bToRemove"] = True
                    else:
                        if bUppercase:
                            sValue = sValue[0:1].upper() + sValue[1:]
                        self.lToken[i]["sNewValue"] = sValue

    def rewriteFromTags (self, bDebug=False):
        "rewrite the sentence, modify tokens, purge the token list"
        if bDebug:
            echo("REWRITE")
        lNewToken = []
        nMergeUntil = 0
        dTokenMerger = {}
        for iToken, dToken in enumerate(self.lToken):
            bKeepToken = True
            if dToken["sType"] != "INFO":
                if nMergeUntil and iToken <= nMergeUntil:
                    dTokenMerger["sValue"] += " " * (dToken["nStart"] - dTokenMerger["nEnd"]) + dToken["sValue"]
                    dTokenMerger["nEnd"] = dToken["nEnd"]
                    if bDebug:
                        echo("  MERGED TOKEN: " + dTokenMerger["sValue"])
                    bKeepToken = False
                if "nMergeUntil" in dToken:
                    if iToken > nMergeUntil: # this token is not already merged with a previous token
                        dTokenMerger = dToken
                    if dToken["nMergeUntil"] > nMergeUntil:
                        nMergeUntil = dToken["nMergeUntil"]
                    del dToken["nMergeUntil"]
                elif "bToRemove" in dToken:
                    if bDebug:
                        echo("  REMOVED: " + dToken["sValue"])
                    self.sSentence = self.sSentence[:dToken["nStart"]] + " " * (dToken["nEnd"] - dToken["nStart"]) + self.sSentence[dToken["nEnd"]:]
                    bKeepToken = False
            #
            if bKeepToken:
                lNewToken.append(dToken)
                if "sNewValue" in dToken:
                    # rewrite token and sentence
                    if bDebug:
                        echo(dToken["sValue"] + " -> " + dToken["sNewValue"])
                    dToken["sRealValue"] = dToken["sValue"]
                    dToken["sValue"] = dToken["sNewValue"]
                    nDiffLen = len(dToken["sRealValue"]) - len(dToken["sNewValue"])
                    sNewRepl = (dToken["sNewValue"] + " " * nDiffLen)  if nDiffLen >= 0  else dToken["sNewValue"][:len(dToken["sRealValue"])]
                    self.sSentence = self.sSentence[:dToken["nStart"]] + sNewRepl + self.sSentence[dToken["nEnd"]:]
                    del dToken["sNewValue"]
            else:
                try:
                    del self.dTokenPos[dToken["nStart"]]
                except KeyError:
                    echo(self)
                    echo(dToken)
        if bDebug:
            echo("  TEXT REWRITED: " + self.sSentence)
        self.lToken.clear()
        self.lToken = lNewToken


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

def displayInfo (dTokenPos, tWord):
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


def g_tag_before (dToken, dTags, sTag):
    "returns True if <sTag> is present on tokens before <dToken>"
    if sTag not in dTags:
        return False
    if dToken["i"] > dTags[sTag][0]:
        return True
    return False


def g_tag_after (dToken, dTags, sTag):
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

def select (dTokenPos, nPos, sWord, sPattern, lDefault=None):
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
        echo("Error. There should be a token at this position: ", nPos)
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


def define (dTokenPos, nPos, sMorphs):
    "Disambiguation: set morphologies of token at <nPos> with <sMorphs>"
    if nPos not in dTokenPos:
        echo("Error. There should be a token at this position: ", nPos)
        return True
    dTokenPos[nPos]["lMorph"] = sMorphs.split("|")
    return True


#### Disambiguation for graph rules

def g_select (dToken, sPattern, lDefault=None):
    "Disambiguation: select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        if lDefault:
            dToken["lMorph"] = lDefault
            #echo("DA:", dToken["sValue"], dToken["lMorph"])
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    #echo("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_exclude (dToken, sPattern, lDefault=None):
    "Disambiguation: select morphologies for <dToken> according to <sPattern>, always return True"
    lMorph = dToken["lMorph"]  if "lMorph" in dToken  else _oSpellChecker.getMorph(dToken["sValue"])
    if not lMorph or len(lMorph) == 1:
        if lDefault:
            dToken["lMorph"] = lDefault
            #echo("DA:", dToken["sValue"], dToken["lMorph"])
        return True
    lSelect = [ sMorph  for sMorph in lMorph  if not re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    #echo("DA:", dToken["sValue"], dToken["lMorph"])
    return True


def g_add_morph (dToken, sNewMorph):
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


def g_define_from (dToken, nLeft=None, nRight=None):
    "Disambiguation: set morphologies of <dToken> with slicing its value with <nLeft> and <nRight>"
    if nLeft is not None:
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"][slice(nLeft, nRight)])
    else:
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"])
    return True


def g_change_meta (dToken, sType):
    "Disambiguation: change type of token"
    dToken["sType"] = sType
    return True



#### GRAMMAR CHECKER PLUGINS

${plugins}


#### CALLABLES FOR REGEX RULES (generated code)

${callables}


#### CALLABLES FOR GRAPH RULES (generated code)

${graph_callables}
