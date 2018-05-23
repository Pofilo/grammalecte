# Sentence checker

from ..graphspell.tokenizer import Tokenizer
from .gc_rules_graph import dGraph


oTokenizer = Tokenizer("${lang}")


class TokenSentence:

    def __init__ (self, sSentence, sSentence0, nOffset):
        self.sSentence = sSentence
        self.sSentence0 = sSentence0
        self.nOffset = nOffset
        self.lToken = list(oTokenizer.genTokens())

    def parse (self):
        dErr = {}
        lPointer = []
        for dToken in self.lToken:
            for i, dPointer in enumerate(lPointer):
                bValid = False
                for dNode in self._getNextMatchingNodes(dToken, dPointer["dNode"]):
                    dPointer["nOffset"] = dToken["i"]
                    dPointer["dNode"] = dNode
                    bValid = True
                if not bValid:
                    del lPointer[i]
            for dNode in self._getNextMatchingNodes(dToken, dGraph):
                lPointer.append({"nOffset": 0, "dNode": dNode})
            for dPointer in lPointer:
                if "<rules>" in dPointer["dNode"]:
                    for dNode in dGraph[dPointer["dNode"]["<rules>"]]:
                        dErr = self._executeActions(dNode, nOffset)
        return dErr

    def _getNextMatchingNodes (self, dToken, dNode):
        # token value
        if dToken["sValue"] in dNode:
            yield dGraph[dNode[dToken["sValue"]]]
        # token lemmas
        for sLemma in dToken["lLemma"]:
            if sLemma in dNode:
                yield dGraph[dNode[sLemma]]
        # universal arc
        if "*" in dNode:
            yield dGraph[dNode["*"]]
        # regex arcs
        if "~" in dNode:
            for sRegex in dNode["~"]:
                for sMorph in dToken["lMorph"]:
                    if re.search(sRegex, sMorph):
                        yield dGraph[dNode["~"][sRegex]]

    def _executeActions (self, dNode, nOffset):
        for sLineId, nextNodeKey in dNode.items():
            for sArc in dGraph[nextNodeKey]:
                bCondMemo = None
                sFuncCond, cActionType, sWhat, *eAct = dRule[sArc]
                # action in lActions: [ condition, action type, replacement/suggestion/action[, iGroupStart, iGroupEnd[, message, URL]] ]
                try:
                    bCondMemo = not sFuncCond or globals()[sFuncCond](self, sCountry, bCondMemo)
                    if bCondMemo:
                        if cActionType == "-":
                            # grammar error
                            nErrorStart = nSentenceOffset + m.start(eAct[0])
                            nErrorEnd = nSentenceOffset + m.start(eAct[1])
                            if nErrorStart not in dErrs or nPriority > dPriority[nErrorStart]:
                                dErrs[nErrorStart] = _createError(self, sWhat, nErrorStart, nErrorEnd, sLineId, bUppercase, eAct[2], eAct[3], bIdRule, sOption, bContext)
                                dPriority[nErrorStart] = nPriority
                        elif cActionType == "~":
                            # text processor
                            self._rewrite(sWhat, nErrorStart, nErrorEnd)
                        elif cActionType == "@":
                            # jump
                            self._jump(sWhat)
                        elif cActionType == "=":
                            # disambiguation
                            globals()[sWhat](self.lToken)
                        elif cActionType == ">":
                            # we do nothing, this test is just a condition to apply all following actions
                            pass
                        else:
                            print("# error: unknown action at " + sLineId)
                    elif cActionType == ">":
                        break
                except Exception as e:
                    raise Exception(str(e), "# " + sLineId + " # " + sRuleId)

    def _createWriterError (self):
        d = {}
        return d

    def _createDictError (self):
        d = {}
        return d

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
        if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
            return False
        if not _dAnalyses[dToken["sValue"]]:
            return False
        lMorph = _dAnalyses[dToken["sValue"]]
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(sMorph)  for sMorph in lMorph)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)

def g_morphex (dToken, sPattern, sNegPattern):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies"
    if "lMorph" in dToken:
        lMorph = dToken["lMorph"]
    else:
        if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
            return False
        if not _dAnalyses[dToken["sValue"]]:
            return False
        lMorph = _dAnalyses[dToken["sValue"]]
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(sMorph)  for sMorph in lMorph):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in lMorph)

def g_analyse (dToken, sPattern, bStrict=True):
    "analyse a token, return True if <sPattern> in morphologies (disambiguation off)"
    if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
        return False
    if not _dAnalyses[dToken["sValue"]]:
        return False
    zPattern = re.compile(sPattern)
    if bStrict:
        return all(zPattern.search(sMorph)  for sMorph in _dAnalyses[dToken["sValue"]])
    return any(zPattern.search(sMorph)  for sMorph in _dAnalyses[dToken["sValue"]])


def g_analysex (dToken, sPattern, sNegPattern):
    "analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)"
    if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
        return False
    if not _dAnalyses[dToken["sValue"]]:
        return False
    # check negative condition
    zNegPattern = re.compile(sNegPattern)
    if any(zNegPattern.search(sMorph)  for sMorph in _dAnalyses[dToken["sValue"]]):
        return False
    # search sPattern
    zPattern = re.compile(sPattern)
    return any(zPattern.search(sMorph)  for sMorph in _dAnalyses[dToken["sValue"]])


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
    if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
        return True
    if len(_dAnalyses[dToken["sValue"]]) == 1:
        return True
    lMorph = dToken["lMorph"] or _dAnalyses[dToken["sValue"]]
    lSelect = [ sMorph  for sMorph in lMorph  if re.search(sPattern, sMorph) ]
    if lSelect:
        if len(lSelect) != len(lMorph):
            dToken["lMorph"] = lSelect
    elif lDefault:
        dToken["lMorph"] = lDefault
    return True


def g_exclude (dToken, sPattern, lDefault=None):
    "select morphologies for <dToken> according to <sPattern>, always return True"
    if dToken["sValue"] not in _dAnalyses and not _storeMorphFromFSA(dToken["sValue"]):
        return True
    if len(_dAnalyses[dToken["sValue"]]) == 1:
        return True
    lMorph = dToken["lMorph"] or _dAnalyses[dToken["sValue"]]
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
