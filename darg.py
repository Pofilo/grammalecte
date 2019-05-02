#!python3

"""
RULE GRAPH BUILDER
"""

# by Olivier R.
# License: MPL 2

import re
import traceback



class DARG:
    """DIRECT ACYCLIC RULE GRAPH"""
    # This code is inspired from Steve Hanov’s DAWG, 2011. (http://stevehanov.ca/blog/index.php?id=115)

    def __init__ (self, lRule, sLangCode):
        print(" > DARG", end="")

        # Preparing DARG
        self.sLangCode = sLangCode
        self.nRule = len(lRule)
        self.aPreviousRule = []
        Node.resetNextId()
        self.oRoot = Node()
        self.lUncheckedNodes = []  # list of nodes that have not been checked for duplication.
        self.lMinimizedNodes = {}  # list of unique nodes that have been checked for duplication.
        self.nNode = 0
        self.nArc = 0

        # build
        lRule.sort()
        for aRule in lRule:
            self.insert(aRule)
        self.finish()
        self.countNodes()
        self.countArcs()
        self.displayInfo()

    # BUILD DARG
    def insert (self, aRule):
        "insert a new rule (tokens must be inserted in order)"
        if aRule < self.aPreviousRule:
            exit("# Error: tokens must be inserted in order.")

        # find common prefix between word and previous word
        nCommonPrefix = 0
        for i in range(min(len(aRule), len(self.aPreviousRule))):
            if aRule[i] != self.aPreviousRule[i]:
                break
            nCommonPrefix += 1

        # Check the lUncheckedNodes for redundant nodes, proceeding from last
        # one down to the common prefix size. Then truncate the list at that point.
        self._minimize(nCommonPrefix)

        # add the suffix, starting from the correct node mid-way through the graph
        if len(self.lUncheckedNodes) == 0:
            oNode = self.oRoot
        else:
            oNode = self.lUncheckedNodes[-1][2]

        iToken = nCommonPrefix
        for sToken in aRule[nCommonPrefix:]:
            oNextNode = Node()
            oNode.dArcs[sToken] = oNextNode
            self.lUncheckedNodes.append((oNode, sToken, oNextNode))
            if iToken == (len(aRule) - 2):
                oNode.bFinal = True
            iToken += 1
            oNode = oNextNode
        oNode.bFinal = True
        self.aPreviousRule = aRule

    def finish (self):
        "minimize unchecked nodes"
        self._minimize(0)

    def _minimize (self, downTo):
        # proceed from the leaf up to a certain point
        for i in range( len(self.lUncheckedNodes)-1, downTo-1, -1 ):
            oNode, sToken, oChildNode = self.lUncheckedNodes[i]
            if oChildNode in self.lMinimizedNodes:
                # replace the child with the previously encountered one
                oNode.dArcs[sToken] = self.lMinimizedNodes[oChildNode]
            else:
                # add the state to the minimized nodes.
                self.lMinimizedNodes[oChildNode] = oChildNode
            self.lUncheckedNodes.pop()

    def countNodes (self):
        "count nodes within the whole graph"
        self.nNode = len(self.lMinimizedNodes)

    def countArcs (self):
        "count arcs within the whole graph"
        self.nArc = len(self.oRoot.dArcs)
        for oNode in self.lMinimizedNodes:
            self.nArc += len(oNode.dArcs)

    def displayInfo (self):
        "display informations about the rule graph"
        print(": {:>10,} rules,  {:>10,} nodes,  {:>10,} arcs".format(self.nRule, self.nNode, self.nArc))

    def createGraph (self):
        "create the graph as a dictionary"
        dGraph = { 0: self.oRoot.getNodeAsDict() }
        for oNode in self.lMinimizedNodes:
            sHashId = oNode.__hash__()
            if sHashId not in dGraph:
                dGraph[sHashId] = oNode.getNodeAsDict()
            else:
                print("Error. Double node… same id: ", sHashId)
                print(str(oNode.getNodeAsDict()))
        dGraph = self._rewriteKeysOfDARG(dGraph)
        self._sortActions(dGraph)
        self._checkRegexes(dGraph)
        return dGraph

    def _rewriteKeysOfDARG (self, dGraph):
        "keys of DARG are long numbers (hashes): this function replace these hashes with smaller numbers (to reduce storing size)"
        # create translation dictionary
        dKeyTrans = {}
        for i, nKey in enumerate(dGraph):
            dKeyTrans[nKey] = i
        # replace keys
        dNewGraph = {}
        for nKey, dVal in dGraph.items():
            dNewGraph[dKeyTrans[nKey]] = dVal
        for nKey, dVal in dGraph.items():
            for sArc, val in dVal.items():
                if type(val) is int:
                    dVal[sArc] = dKeyTrans[val]
                else:
                    for sArc, nKey in val.items():
                        val[sArc] = dKeyTrans[nKey]
        return dNewGraph

    def _sortActions (self, dGraph):
        "when a pattern is found, several actions may be launched, and it must be performed in a certain order"
        for nKey, dVal in dGraph.items():
            if "<rules>" in dVal:
                for sLineId, nKey in dVal["<rules>"].items():
                    # we change the dictionary of actions in a list of actions (values of dictionary all points to the final node)
                    if isinstance(dGraph[nKey], dict):
                        dGraph[nKey] = sorted(dGraph[nKey].keys())

    def _checkRegexes (self, dGraph):
        "check validity of regexes"
        aRegex = set()
        for nKey, dVal in dGraph.items():
            if "<re_value>" in dVal:
                for sRegex in dVal["<re_value>"]:
                    if sRegex not in aRegex:
                        self._checkRegex(sRegex)
                        aRegex.add(sRegex)
            if "<re_morph>" in dVal:
                for sRegex in dVal["<re_morph>"]:
                    if sRegex not in aRegex:
                        self._checkRegex(sRegex)
                        aRegex.add(sRegex)
        aRegex.clear()

    def _checkRegex (self, sRegex):
        #print(sRegex)
        if "¬" in sRegex:
            sPattern, sNegPattern = sRegex.split("¬")
            try:
                if not sNegPattern:
                    print("# Warning! Empty negpattern:", sRegex)
                re.compile(sPattern)
                if sNegPattern != "*":
                    re.compile(sNegPattern)
            except:
                print("# Error. Wrong regex:", sRegex)
                exit()
        else:
            try:
                if not sRegex:
                    print("# Warning! Empty pattern:", sRegex)
                re.compile(sRegex)
            except:
                print("# Error. Wrong regex:", sRegex)
                exit()


class Node:
    """Node of the rule graph"""

    NextId = 0

    def __init__ (self):
        self.i = Node.NextId
        Node.NextId += 1
        self.bFinal = False
        self.dArcs = {}          # key: arc value; value: a node

    @classmethod
    def resetNextId (cls):
        "reset to 0 the node counter"
        cls.NextId = 0

    def __str__ (self):
        # Caution! this function is used for hashing and comparison!
        cFinal = "1"  if self.bFinal  else "0"
        l = [cFinal]
        for (key, oNode) in self.dArcs.items():
            l.append(str(key))
            l.append(str(oNode.i))
        return "_".join(l)

    def __hash__ (self):
        # Used as a key in a python dictionary.
        return self.__str__().__hash__()

    def __eq__ (self, other):
        # Used as a key in a python dictionary.
        # Nodes are equivalent if they have identical arcs, and each identical arc leads to identical states.
        return self.__str__() == other.__str__()

    def getNodeAsDict (self):
        "returns the node as a dictionary structure"
        dNode = {}
        dReValue = {}
        dReMorph = {}
        dRule = {}
        dLemma = {}
        dMeta = {}
        dTag = {}
        for sArc, oNode in self.dArcs.items():
            if sArc.startswith("@") and len(sArc) > 1:
                dReMorph[sArc[1:]] = oNode.__hash__()
            elif sArc.startswith("~") and len(sArc) > 1:
                dReValue[sArc[1:]] = oNode.__hash__()
            elif sArc.startswith(">") and len(sArc) > 1:
                dLemma[sArc[1:]] = oNode.__hash__()
            elif sArc.startswith("*") and len(sArc) > 1:
                dMeta[sArc[1:]] = oNode.__hash__()
            elif sArc.startswith("/") and len(sArc) > 1:
                dTag[sArc[1:]] = oNode.__hash__()
            elif sArc.startswith("##"):
                dRule[sArc[1:]] = oNode.__hash__()
            else:
                dNode[sArc] = oNode.__hash__()
        if dReValue:
            dNode["<re_value>"] = dReValue
        if dReMorph:
            dNode["<re_morph>"] = dReMorph
        if dLemma:
            dNode["<lemmas>"] = dLemma
        if dTag:
            dNode["<tags>"] = dTag
        if dMeta:
            dNode["<meta>"] = dMeta
        if dRule:
            dNode["<rules>"] = dRule
        #if self.bFinal:
        #    dNode["<final>"] = 1
        return dNode
