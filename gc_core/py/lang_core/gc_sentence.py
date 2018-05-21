# Sentence checker

from ..graphspell.tokenizer import Tokenizer
from .gc_graph import dGraph


oTokenizer = Tokenizer("${lang}")


class Sentence:

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
                        dErr = self._executeActions(dNode)
        return dErr

    def _getNextMatchingNodes (self, dToken, dNode):
        if dToken["sValue"] in dNode:
            yield dGraph[dNode[dToken["sValue"]]]
        for sLemma in dToken["sLemma"]:
            if sLemma in dNode:
                yield dGraph[dNode[dToken["sValue"]]]
        if "~" in dNode:
            for sRegex in dNode["~"]:
                for sMorph in dToken["lMorph"]:
                    if re.search(sRegex, sMorph):
                        yield dGraph[dNode["~"][sRegex]]

    def _executeActions (self, dNode):
        for sLineId, nextNodeKey in dNode.items():
            for sArc in dGraph[nextNodeKey]:
                bCondMemo = None
                sFuncCond, cActionType, sWhat, *eAct = dRule[sArc]
                # action in lActions: [ condition, action type, replacement/suggestion/action[, iGroupStart, iGroupEnd[, message, URL]] ]
                try:
                    bCondMemo = not sFuncCond or globals()[sFuncCond](self, dDA, sCountry, bCondMemo)
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
                            self.lToken = _rewrite(self, sWhat, nErrorStart, nErrorEnd, bUppercase)
                            bChange = True
                        elif cActionType == "@":
                            # text processor
                            self.lToken = _rewrite(self, sWhat, nErrorStart, nErrorEnd, bUppercase)
                            bChange = True
                        elif cActionType == "=":
                            # disambiguation
                            globals()[sWhat](self, dDA)
                        elif cActionType == ">":
                            # we do nothing, this test is just a condition to apply all following actions
                            pass
                        else:
                            echo("# error: unknown action at " + sLineId)
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


#### Common functions

def option ():
    pass


#### Analyse tokens

def morph ():
    pass

def morphex ():
    pass

def analyse ():
    pass

def analysex ():
    pass


#### Go outside scope

def nextToken ():
    pass

def prevToken ():
    pass

def look ():
    pass

def lookAndCheck ():
    pass


#### Disambiguator

def select ():
    pass

def exclude ():
    pass

def define ():
    pass
