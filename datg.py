#!python3

# RULE GRAPH BUILDER
#
# by Olivier R.
# License: MPL 2


import json
import time
import traceback

from graphspell.progressbar import ProgressBar



class DATG:
    """DIRECT ACYCLIC TOKEN GRAPH"""
    # This code is inspired from Steve Hanov’s DAWG, 2011. (http://stevehanov.ca/blog/index.php?id=115)

    def __init__ (self, lRule, sLangCode):
        print("===== Direct Acyclic Token Graph - Minimal Acyclic Finite State Automaton =====")

        # Preparing DATG
        print(" > Preparing list of tokens")
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
        oProgBar = ProgressBar(0, len(lRule))
        for aRule in lRule:
            self.insert(aRule)
            oProgBar.increment(1)
        oProgBar.done()
        self.finish()
        self.countNodes()
        self.countArcs()
        self.displayInfo()

    # BUILD DATG
    def insert (self, aRule):
        if aRule < self.aPreviousRule:
            sys.exit("# Error: tokens must be inserted in order.")
    
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
        for token in aRule[nCommonPrefix:]:
            oNextNode = Node()
            oNode.dArcs[token] = oNextNode
            self.lUncheckedNodes.append((oNode, token, oNextNode))
            if iToken == (len(aRule) - 4): 
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
            oNode, token, oChildNode = self.lUncheckedNodes[i]
            if oChildNode in self.lMinimizedNodes:
                # replace the child with the previously encountered one
                oNode.dArcs[token] = self.lMinimizedNodes[oChildNode]
            else:
                # add the state to the minimized nodes.
                self.lMinimizedNodes[oChildNode] = oChildNode
            self.lUncheckedNodes.pop()

    def countNodes (self):
        self.nNode = len(self.lMinimizedNodes)

    def countArcs (self):
        self.nArc = 0
        for oNode in self.lMinimizedNodes:
            self.nArc += len(oNode.dArcs)
        
    def lookup (self, sWord):
        oNode = self.oRoot
        for c in sWord:
            if c not in oNode.dArcs:
                return False
            oNode = oNode.dArcs[c]
        return oNode.bFinal

    def displayInfo (self):
        print(" * {:<12} {:>16,}".format("Rules:", self.nRule))
        print(" * {:<12} {:>16,}".format("Nodes:", self.nNode))
        print(" * {:<12} {:>16,}".format("Arcs:", self.nArc))

    def createGraph (self):
        dGraph = { 0: self.oRoot.getNodeAsDict() }
        print(0, "\t", self.oRoot.getNodeAsDict())
        for oNode in self.lMinimizedNodes:
            sHashId = oNode.__hash__() 
            if sHashId not in dGraph:
                dGraph[sHashId] = oNode.getNodeAsDict()
                print(sHashId, "\t", dGraph[sHashId])
            else:
                print("Error. Double node… same id: ", sHashId)
                print(str(oNode.getNodeAsDict()))
        return dGraph



class Node:
    NextId = 0
    
    def __init__ (self):
        self.i = Node.NextId
        Node.NextId += 1
        self.bFinal = False
        self.dArcs = {}          # key: arc value; value: a node

    @classmethod
    def resetNextId (cls):
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
        dRegex = {}
        dRules = {}
        for arc, oNode in self.dArcs.items():
            if type(arc) == str and arc.startswith("~"):
                dRegex[arc[1:]] = oNode.__hash__()
            elif arc.startswith("##"):
                dRules[arc[1:]] = oNode.__hash__()
            else:
                dNode[arc] = oNode.__hash__()
        if dRegex:
            dNode["<regex>"] = dRegex
        if dRules:
            dNode["<rules>"] = dRules
        #if self.bFinal:
        #    dNode["<final>"] = 1
        return dNode
