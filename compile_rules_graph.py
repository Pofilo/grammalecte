"""
Grammalecte: compile rules
Create a Direct Acyclic Rule Graphs (DARGs)
"""

import re
import os
import time
import concurrent.futures

import darg
import compile_rules_js_convert as jsconv
import helpers


#### PROCESS POOL EXECUTOR ####
xProcessPoolExecutor = None

def initProcessPoolExecutor (nMultiCPU=None):
    "process pool executor initialisation"
    global xProcessPoolExecutor
    if xProcessPoolExecutor:
        # we shutdown the ProcessPoolExecutor which may have been launched previously
        print("  ProcessPoolExecutor shutdown.")
        xProcessPoolExecutor.shutdown(wait=False)
    nMaxCPU = max(os.cpu_count()-1, 1)
    if nMultiCPU is None or not (1 <= nMultiCPU <= nMaxCPU):
        nMultiCPU = nMaxCPU
    print("  CPU processes used for workers: ", nMultiCPU)
    xProcessPoolExecutor = concurrent.futures.ProcessPoolExecutor(max_workers=nMultiCPU)


def rewriteCode (sCode):
    "convert simple code syntax to a string of Python code"
    if sCode[0:1] == "=":
        sCode = sCode[1:]
    sCode = sCode.replace("__also__", "bCondMemo")
    sCode = sCode.replace("__else__", "not bCondMemo")
    sCode = sCode.replace("sContext", "_sAppContext")
    sCode = re.sub(r"\b(morph|morphVC|analyse|value|tag|displayInfo)[(]\\(\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', sCode)
    sCode = re.sub(r"\b(morph|morphVC|analyse|value|tag|displayInfo)[(]\\-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', sCode)
    sCode = re.sub(r"\b(select|exclude|define|define_from|rewrite|add_morph|change_meta)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', sCode)
    sCode = re.sub(r"\b(select|exclude|define|define_from|rewrite|add_morph|change_meta)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', sCode)
    sCode = re.sub(r"\b(tag_before|tag_after)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2], dTags', sCode)
    sCode = re.sub(r"\b(tag_before|tag_after)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1], dTags', sCode)
    sCode = re.sub(r"\bspace_after[(][\\](\d+)", 'g_space_between_tokens(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', sCode)
    sCode = re.sub(r"\bspace_after[(][\\]-(\d+)", 'g_space_between_tokens(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', sCode)
    sCode = re.sub(r"\banalyse_with_next[(][\\](\d+)", 'g_merged_analyse(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', sCode)
    sCode = re.sub(r"\banalyse_with_next[(][\\]-(\d+)", 'g_merged_analyse(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', sCode)
    sCode = re.sub(r"\b(morph|analyse|tag|value)\(>1", 'g_\\1(lToken[nLastToken+1]', sCode)                       # next token
    sCode = re.sub(r"\b(morph|analyse|tag|value)\(<1", 'g_\\1(lToken[nTokenOffset]', sCode)                       # previous token
    sCode = re.sub(r"\b(morph|analyse|tag|value)\(>(\d+)", 'g_\\1(g_token(lToken, nLastToken+\\2)', sCode)        # next token
    sCode = re.sub(r"\b(morph|analyse|tag|value)\(<(\d+)", 'g_\\1(g_token(lToken, nTokenOffset+1-\\2)', sCode)    # previous token
    sCode = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', sCode)
    sCode = re.sub(r"\bbefore\(\s*", 'look(sSentence[:lToken[1+nTokenOffset]["nStart"]], ', sCode)          # before(sCode)
    sCode = re.sub(r"\bafter\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', sCode)                 # after(sCode)
    sCode = re.sub(r"\bbefore0\(\s*", 'look(sSentence0[:lToken[1+nTokenOffset]["nStart"]], ', sCode)        # before0(sCode)
    sCode = re.sub(r"\bafter0\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', sCode)                # after0(sCode)
    sCode = re.sub(r"\banalyseWord[(]", 'analyse(', sCode)
    sCode = re.sub(r"\bcheckAgreement[(]\\(\d+), *\\(\d+)", 'g_checkAgreement(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\2]', sCode)
    sCode = re.sub(r"[\\](\d+)", 'lToken[nTokenOffset+\\1]["sValue"]', sCode)
    sCode = re.sub(r"[\\]-(\d+)", 'lToken[nLastToken-\\1+1]["sValue"]', sCode)
    sCode = re.sub(r">1", 'lToken[nLastToken+1]["sValue"]', sCode)
    sCode = re.sub(r"<1", 'lToken[nTokenOffset]["sValue"]', sCode)
    return sCode


def changeReferenceToken (sText, dPos):
    "change group reference in <sText> with values in <dPos>"
    if "\\" not in sText:
        return sText
    for i in range(len(dPos), 0, -1):
        sText = re.sub("\\\\"+str(i)+"(?![0-9])", "\\\\"+str(dPos[i]), sText)
    return sText


def checkTokenNumbers (sText, sActionId, nToken):
    "check if token references in <sText> greater than <nToken> (debugging)"
    for x in re.finditer(r"\\(\d+)", sText):
        if int(x.group(1)) > nToken:
            print("# Error in token index at line " + sActionId + " ("+str(nToken)+" tokens only)")
            print(sText)


def checkIfThereIsCode (sText, sActionId):
    "check if there is code in <sText> (debugging)"
    if re.search(r"[.]\w+[(]|sugg\w+[(]|\(\\[0-9]|\[(?:[0-9]:|:)", sText):
        print("# Warning at line " + sActionId + ":  This message looks like code. Line should probably begin with =")
        print(sText)



class GraphBuilder:

    def __init__ (self, sGraphName, sGraphCode, sLang, dDef, dDecl, dOptPriority):
        self.sGraphName = sGraphName
        self.sGraphCode = sGraphCode
        self.sLang = sLang
        self.dDef = dDef
        self.dDecl = dDecl
        self.dOptPriority = dOptPriority
        self.dAntiPatterns = {}
        self.dActions = {}
        self.dFuncName = {}
        self.dFunctions = {}

    def _genTokenLines (self, sTokenLine):
        "tokenize a string and return a list of lines of tokens"
        lTokenLines = []
        for sTokBlock in sTokenLine.split():
            # replace merger characters by spaces
            if "␣" in sTokBlock:
                sTokBlock = sTokBlock.replace("␣", " ")
            # optional token?
            bNullPossible = sTokBlock.startswith("?") and sTokBlock.endswith("¿")
            if bNullPossible:
                sTokBlock = sTokBlock[1:-1]
            # token with definition?
            if sTokBlock.startswith("({") and sTokBlock.endswith("})") and sTokBlock[1:-1] in self.dDef:
                sTokBlock = "(" + self.dDef[sTokBlock[1:-1]] + ")"
            elif sTokBlock.startswith("{") and sTokBlock.endswith("}") and sTokBlock in self.dDef:
                sTokBlock = self.dDef[sTokBlock]
            if ( (sTokBlock.startswith("[") and sTokBlock.endswith("]")) or (sTokBlock.startswith("([") and sTokBlock.endswith("])")) ):
                # multiple token
                bSelectedGroup = sTokBlock.startswith("(") and sTokBlock.endswith(")")
                if bSelectedGroup:
                    sTokBlock = sTokBlock[1:-1]
                lToken = self._createTokenList(sTokBlock)
                if not lTokenLines:
                    lTokenLines = [ ["("+s+")"]  for s  in lToken ]  if bSelectedGroup  else [ [s]  for s  in lToken ]
                    if bNullPossible:
                        lTokenLines.extend([ []  for i  in range(len(lToken)+1) ])
                else:
                    lNewTemp = []
                    if bNullPossible:
                        for aRule in lTokenLines:
                            for sElem in lToken:
                                aNewRule = list(aRule)
                                aNewRule.append(sElem)
                                lNewTemp.append(aNewRule)
                    else:
                        sElem1 = lToken.pop(0)
                        for aRule in lTokenLines:
                            for sElem in lToken:
                                aNewRule = list(aRule)
                                aNewRule.append("(" + sElem + ")"  if bSelectedGroup  else sElem)
                                lNewTemp.append(aNewRule)
                            aRule.append("(" + sElem1 + ")"  if bSelectedGroup  else sElem1)
                    lTokenLines.extend(lNewTemp)
            else:
                # simple token
                if not lTokenLines:
                    lTokenLines = [[sTokBlock], []]  if bNullPossible  else [[sTokBlock]]
                else:
                    if bNullPossible:
                        lNewTemp = []
                        for aRule in lTokenLines:
                            lNew = list(aRule)
                            lNew.append(sTokBlock)
                            lNewTemp.append(lNew)
                        lTokenLines.extend(lNewTemp)
                    else:
                        for aRule in lTokenLines:
                            aRule.append(sTokBlock)
        for aRule in lTokenLines:
            yield aRule

    def _createTokenList (self, sTokBlock):
        "return a list of tokens from a block of tokens"
        lToken = []
        for sToken in sTokBlock[1:-1].split("|"):
            if "+" in sToken and not sToken.startswith("+"):
                for sCode in self.dDecl:
                    if sToken.endswith(sCode):
                        sToken = sToken[:-len(sCode)]
                        lToken.append(sToken)
                        for sSuffix in self.dDecl[sCode]:
                            lToken.append(sToken+sSuffix)
                        break
            else:
                lToken.append(sToken)
        return lToken

    def createGraphAndActions (self, lRuleLine):
        "create a graph as a dictionary with <lRuleLine>"
        fStartTimer = time.time()
        print("{:>8,} rules in {:<30} ".format(len(lRuleLine), f"<{self.sGraphName}|{self.sGraphCode}>"), end="")
        lPreparedRule = []
        for i, sRuleName, sTokenLine, iActionBlock, lActions, nPriority in lRuleLine:
            for aRule in self.createRule(i, sRuleName, sTokenLine, iActionBlock, lActions, nPriority):
                lPreparedRule.append(aRule)
        # Debugging
        if False:
            print("\nRULES:")
            for e in lPreparedRule:
                if e[-2] == "##2211":
                    print(e)
        # Graph creation
        oDARG = darg.DARG(lPreparedRule, self.sLang)
        dGraph = oDARG.createGraph()
        print(oDARG, end="")
        # debugging
        if False:
            print("\nGRAPH:", self.sGraphName)
            for k, v in dGraph.items():
                print(k, "\t", v)
        print("\tin {:>8.2f} s".format(time.time()-fStartTimer))
        sPyCallables, sJSCallables = self.createCallables()
        return dGraph, self.dActions, sPyCallables, sJSCallables

    def createRule (self, iLine, sRuleName, sTokenLine, iActionBlock, lActions, nPriority):
        "generator: create rule as list"
        # print(iLine, "//", sRuleName, "//", sTokenLine, "//", lActions, "//", nPriority)
        if sTokenLine.startswith("!!") and sTokenLine.endswith("¡¡"):
            # antipattern
            sTokenLine = sTokenLine[2:-2].strip()
            if sRuleName not in self.dAntiPatterns:
                self.dAntiPatterns[sRuleName]= []
            for lToken in self._genTokenLines(sTokenLine):
                self.dAntiPatterns[sRuleName].append(lToken)
        else:
            # pattern
            for lToken in self._genTokenLines(sTokenLine):
                if sRuleName in self.dAntiPatterns and lToken in self.dAntiPatterns[sRuleName]:
                    # <lToken> matches an antipattern -> discard
                    continue
                # Calculate positions
                dPos = {}   # key: iGroup, value: iToken
                iGroup = 0
                #if iLine == 15818: # debug
                #    print(" ".join(lToken))
                for i, sToken in enumerate(lToken):
                    if sToken.startswith("(") and sToken.endswith(")"):
                        lToken[i] = sToken[1:-1]
                        iGroup += 1
                        dPos[iGroup] = i + 1    # we add 1, for we count tokens from 1 to n (not from 0)

                # Parse actions
                for iAction, (iActionLine, sAction) in enumerate(lActions, 1):
                    sAction = sAction.strip()
                    if sAction:
                        sActionId = f"{self.sGraphCode}__{sRuleName}__b{iActionBlock}_a{iAction}"
                        aAction = self.createAction(sActionId, sAction, nPriority, len(lToken), dPos, iActionLine)
                        if aAction:
                            sActionName = self.storeAction(sActionId, aAction)
                            lResult = list(lToken)
                            lResult.extend(["##"+str(iLine), sActionName])
                            #if iLine == 13341:
                            #    print("  ".join(lToken))
                            #    print(sActionId, aAction)
                            yield lResult
                        else:
                            print("# Error on action at line:", iLine)
                            print(sTokenLine, "\n", lActions)
                            exit()
                    else:
                        print("No action found for ", iActionLine)
                        exit()

    def createAction (self, sActionId, sAction, nPriority, nToken, dPos, iActionLine):
        "create action rule as a list"
        sLineId = "#" + str(iActionLine)

        # Option
        sOption = False
        m = re.match("/(\\w+)/", sAction)
        if m:
            sOption = m.group(1)
            sAction = sAction[m.end():].strip()
        if nPriority == -1:
            nPriority = self.dOptPriority.get(sOption, 4)

        # valid action?
        m = re.search(r"(?P<action>[-=~/!>])(?P<start>-?\d+\.?|)(?P<end>:\.?-?\d+|)(?P<casing>:|)>>", sAction)
        if not m:
            print("\n# Error. No action found at: ", sLineId, sActionId)
            exit()

        # Condition
        sCondition = sAction[:m.start()].strip()
        if sCondition:
            sCondition = changeReferenceToken(sCondition, dPos)
            sCondition = self.createFunction("cond", sCondition)
        else:
            sCondition = ""

        # Case sensitivity
        bCaseSensitivity = not bool(m.group("casing"))

        # Action
        cAction = m.group("action")
        sAction = sAction[m.end():].strip()
        sAction = changeReferenceToken(sAction, dPos)
        # target
        cStartLimit = "<"
        cEndLimit = ">"
        if not m.group("start"):
            iStartAction = 1
            iEndAction = 0
        else:
            if cAction != "-" and (m.group("start").endswith(".") or m.group("end").startswith(":.")):
                print("\n# Error. Wrong selection on tokens at: ", sLineId ,sActionId)
                return None
            if m.group("start").endswith("."):
                cStartLimit = ">"
            iStartAction = int(m.group("start").rstrip("."))
            if not m.group("end"):
                iEndAction = iStartAction
            else:
                if m.group("end").startswith(":."):
                    cEndLimit = "<"
                iEndAction = int(m.group("end").lstrip(":."))
        if dPos and m.group("start"):
            iStartAction = dPos.get(iStartAction, iStartAction)
            if iEndAction:
                iEndAction = dPos.get(iEndAction, iEndAction)
        if iStartAction < 0:
            iStartAction += 1
        if iEndAction < 0:
            iEndAction += 1

        if cAction == "-":
            ## error
            iMsg = sAction.find(" && ")
            if iMsg == -1:
                sMsg = "# Error. Error message not found."
                sURL = ""
                print("\n# Error. No message at: ", sLineId, sActionId)
                exit()
            else:
                sMsg = sAction[iMsg+4:].strip()
                sAction = sAction[:iMsg].strip()
                sURL = ""
                mURL = re.search("[|] *(https?://.*)", sMsg)
                if mURL:
                    sURL = mURL.group(1).strip()
                    sMsg = sMsg[:mURL.start(0)].strip()
                checkTokenNumbers(sMsg, sActionId, nToken)
                if sMsg[0:1] == "=":
                    sMsg = self.createFunction("msg", sMsg, True)
                else:
                    checkIfThereIsCode(sMsg, sActionId)

        # checking consistancy
        checkTokenNumbers(sAction, sActionId, nToken)

        if cAction == ">":
            ## no action, break loop if condition is False
            return [sLineId, sOption, sCondition, cAction, ""]

        if not sAction and cAction != "!":
            print(f"\n# Error in action at line <{sLineId}/{sActionId}>:  This action is empty.")
            exit()

        if sAction[0:1] != "=" and cAction != "=":
            checkIfThereIsCode(sAction, sActionId)

        if cAction == "-":
            ## error detected --> suggestion
            if sAction[0:1] == "=":
                sAction = self.createFunction("sugg", sAction, True)
            elif sAction.startswith('"') and sAction.endswith('"'):
                sAction = sAction[1:-1]
            if not sMsg:
                print(f"\n# Error in action at line <{sLineId}/{sActionId}>:  The message is empty.")
                exit()
            return [sLineId, sOption, sCondition, cAction, sAction, iStartAction, iEndAction, cStartLimit, cEndLimit, bCaseSensitivity, nPriority, sMsg, sURL]
        if cAction == "~":
            ## text processor
            if sAction[0:1] == "=":
                sAction = self.createFunction("tp", sAction, True)
            elif sAction.startswith('"') and sAction.endswith('"'):
                sAction = sAction[1:-1]
            elif sAction not in "␣*_":
                nToken = sAction.count("|") + 1
                if iStartAction > 0 and iEndAction > 0:
                    if (iEndAction - iStartAction + 1) != nToken:
                        print(f"\n# Error in action at line <{sLineId}/{sActionId}>: numbers of modified tokens modified.")
                elif iStartAction < 0 or iEndAction < 0 and iStartAction != iEndAction:
                    print(f"\n# Warning in action at line <{sLineId}/{sActionId}>: rewriting with possible token position modified.")
            return [sLineId, sOption, sCondition, cAction, sAction, iStartAction, iEndAction, bCaseSensitivity]
        if cAction in "!/":
            ## tags
            return [sLineId, sOption, sCondition, cAction, sAction, iStartAction, iEndAction]
        if cAction == "=":
            ## disambiguator
            sAction = self.createFunction("da", sAction)
            return [sLineId, sOption, sCondition, cAction, sAction]
        print("\n# Unknown action at ", sLineId, sActionId)
        return None

    def storeAction (self, sActionId, aAction):
        "store <aAction> in <self.dActions> avoiding duplicates and return action name"
        nVar = 1
        while True:
            sActionName = sActionId + "_" + str(nVar)
            if sActionName not in self.dActions:
                self.dActions[sActionName] = aAction
                return sActionName
            if aAction == self.dActions[sActionName]:
                return sActionName
            nVar += 1

    def showActions (self):
        "debugging function"
        print("\nActions:")
        for sActionName, aAction in oFunctionManager.dActions.items():
            print(sActionName, aAction)

    def createFunction (self, sType, sCode, bStartWithEqual=False):
        "create a function (stored in <self.dFunctions>) and return function name"
        sCode = rewriteCode(sCode)
        sFuncName = self._getNameForCode(sType, sCode)
        self.dFunctions[sFuncName] = sCode
        return sFuncName  if not bStartWithEqual  else "="+sFuncName

    def _getNameForCode (self, sType, sCode):
        "create and get a name for a code"
        if sType not in self.dFuncName:
            self.dFuncName[sType] = {}
        if sCode not in self.dFuncName[sType]:
            self.dFuncName[sType][sCode] = len(self.dFuncName[sType])+1
        return "_g_" + sType + "_" + self.sGraphCode + "_" + str(self.dFuncName[sType][sCode])

    def createCallables (self):
        "return callables for Python and JavaScript"
        sPyCallables = ""
        sJSCallables = ""
        for sFuncName, sReturn in self.dFunctions.items():
            if sFuncName.startswith("_g_cond_"): # condition
                sParams = "lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, dTags, sSentence, sSentence0"
            elif sFuncName.startswith("_g_msg_"): # message
                sParams = "lToken, nTokenOffset, nLastToken"
            elif sFuncName.startswith("_g_sugg_"): # suggestion
                sParams = "lToken, nTokenOffset, nLastToken"
            elif sFuncName.startswith("_g_tp_"): # text preprocessor
                sParams = "lToken, nTokenOffset, nLastToken"
            elif sFuncName.startswith("_g_da_"): # disambiguator
                sParams = "lToken, nTokenOffset, nLastToken"
            else:
                print("# Unknown function type in [" + sFuncName + "]")
                continue
            # Python
            sPyCallables += f"def {sFuncName} ({sParams}):\n"
            sPyCallables += f"    return {sReturn}\n"
            # JavaScript
            sJSCallables += f"    {sFuncName}: function ({sParams}) {{\n"
            sJSCallables += "        return " + jsconv.py2js(sReturn) + ";\n"
            sJSCallables += "    },\n"
        return sPyCallables, sJSCallables


def processing (sGraphName, sGraphCode, sLang, lRuleLine, dDef, dDecl, dOptPriority):
    "to be run in a separate process"
    oGraphBuilder = GraphBuilder(sGraphName, sGraphCode, sLang, dDef, dDecl, dOptPriority)
    dGraph, dActions, sPy, sJS = oGraphBuilder.createGraphAndActions(lRuleLine)
    return (sGraphName, dGraph, dActions, sPy, sJS)


def make (lRule, sLang, dDef, dDecl, dOptPriority):
    "compile rules, returns a dictionary of values"
    # for clarity purpose, don’t create any file here

    # removing comments, zeroing empty lines, creating definitions, storing tests, merging rule lines
    print("  parsing graph rules...")
    lTokenLine = []
    lActions = []
    bActionBlock = False
    nPriority = -1
    dAllGraph = {}
    dGraphCode = {}
    sGraphName = ""
    iActionBlock = 0
    aRuleName = set()

    for iLine, sLine in lRule:
        sLine = sLine.rstrip()
        if "\t" in sLine:
            # tabulation not allowed
            print("# Error. Tabulation at line: ", iLine)
            exit()
        elif sLine.startswith("@@@@GRAPH: "):
            # rules graph call
            m = re.match(r"@@@@GRAPH: *(\w+) *[|] *(\w+)", sLine.strip())
            if m:
                sGraphName = m.group(1)
                sGraphCode = m.group(2)
                if sGraphName in dAllGraph or sGraphCode in dGraphCode:
                    print(f"# Error at line {iLine}. Graph name <{sGraphName}> or graph code <{sGraphCode}> already exists.")
                    exit()
                dAllGraph[sGraphName] = []
                dGraphCode[sGraphName] = sGraphCode
            else:
                print("# Error. Graph name not found at line", iLine)
                exit()
        elif sLine.startswith("__") and sLine.endswith("__"):
            # new rule group
            m = re.match("__(\\w+)(!\\d|)__", sLine)
            if m:
                sRuleName = m.group(1)
                if sRuleName in aRuleName:
                    print(f"# Error at line {iLine}. Rule name <{sRuleName}> already exists.")
                    exit()
                aRuleName.add(sRuleName)
                iActionBlock = 1
                nPriority = int(m.group(2)[1:]) if m.group(2)  else -1
            else:
                print("# Syntax error in rule group: ", sLine, " -- line:", iLine)
                exit()
        elif re.match("    \\S", sLine):
            # tokens line
            lTokenLine.append([iLine, sLine.strip()])
        elif sLine.startswith("        ||"):
            # tokens line continuation
            iPrevLine, sPrevLine = lTokenLine[-1]
            lTokenLine[-1] = [iPrevLine, sPrevLine + " " + sLine.strip()[2:]]
        elif sLine.startswith("        <<- "):
            # actions
            lActions.append([iLine, sLine[12:].strip()])
            if not re.search(r"[-=~/!>](?:-?\d\.?(?::\.?-?\d+|)|):?>>", sLine):
                bActionBlock = True
        elif sLine.startswith("        && "):
            # action message
            iPrevLine, sPrevLine = lActions[-1]
            lActions[-1] = [iPrevLine, sPrevLine + sLine]
        elif sLine.startswith("        ") and bActionBlock:
            # action line continuation
            iPrevLine, sPrevLine = lActions[-1]
            lActions[-1] = [iPrevLine, sPrevLine + " " + sLine.strip()]
            if re.search(r"[-=~/!>](?:-?\d\.?(?::\.?-?\d+|)|):?>>", sLine):
                bActionBlock = False
        elif re.match("[  ]*$", sLine):
            # empty line to end merging
            if not lTokenLine:
                continue
            if bActionBlock or not lActions:
                print("# Error. No action found at line:", iLine)
                print(bActionBlock, lActions)
                exit()
            if not sGraphName:
                print("# Error. All rules must belong to a named graph. Line: ", iLine)
                exit()
            for j, sTokenLine in lTokenLine:
                dAllGraph[sGraphName].append((j, sRuleName, sTokenLine, iActionBlock, list(lActions), nPriority))
            lTokenLine.clear()
            lActions.clear()
            iActionBlock += 1
        else:
            print("# Unknown line at:", iLine)
            print(sLine)
            exit()

    # processing rules
    print("  processing graph rules...")
    initProcessPoolExecutor(len(dAllGraph))
    fStartTimer = time.time()
    # build graph
    lResult = []
    nRule = 0
    for sGraphName, lRuleLine in dAllGraph.items():
        nRule += len(lRuleLine)
        try:
            xFuture = xProcessPoolExecutor.submit(processing, sGraphName, dGraphCode[sGraphName], sLang, lRuleLine, dDef, dDecl, dOptPriority)
            lResult.append(xFuture)
        except (concurrent.futures.TimeoutError, concurrent.futures.CancelledError):
            return "Analysis aborted (time out or cancelled)"
        except concurrent.futures.BrokenExecutor:
            return "Executor broken. The server failed."
    # merging results
    xProcessPoolExecutor.shutdown(wait=True) # waiting that everything is finished
    dAllActions = {}
    sPyCallables = ""
    sJSCallables = ""
    for xFuture in lResult:
        sGraphName, dGraph, dActions, sPy, sJS = xFuture.result()
        dAllGraph[sGraphName] = dGraph
        dAllActions.update(dActions)
        sPyCallables += sPy
        sJSCallables += sJS
    # create a dictionary of URL
    dTempURL = { "": 0 }
    i = 1
    for sKey, lValue in dAllActions.items():
        if lValue[3] == "-":
            if lValue[-1]:
                if lValue[-1] not in dTempURL:
                    dTempURL[lValue[-1]] = i
                    i += 1
                lValue[-1] = dTempURL[lValue[-1]]
            else:
                lValue[-1] = 0
    dURL = { v: k  for k, v in dTempURL.items() } # reversing key and values
    # end
    print("  Total: ", nRule, "rules, ", len(dAllActions), "actions")
    print("  Build time: {:.2f} s".format(time.time() - fStartTimer))

    return {
        # the graphs describe paths of tokens to actions which eventually execute callables
        "rules_graphs": str(dAllGraph), # helpers.convertDictToString(dAllGraph)
        "rules_actions": helpers.convertDictToString(dAllActions), # str(dAllActions)
        "rules_graph_URL": helpers.convertDictToString(dURL), # str(dURL)
        "rules_graphsJS": str(dAllGraph),
        "rules_actionsJS": jsconv.pyActionsToString(dAllActions),
        "rules_graph_URLJS": str(dURL),
        "graph_callables": sPyCallables,
        "graph_callablesJS": sJSCallables
    }
