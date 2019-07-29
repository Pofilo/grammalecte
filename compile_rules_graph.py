"""
Grammalecte: compile rules
Create a Direct Acyclic Rule Graphs (DARGs)
"""

import re

import darg
import compile_rules_js_convert as jsconv


dACTIONS = {}
dFUNCTIONS = {}
dFUNCNAME = {}
dDECLENSIONS = {}
dANTIPATTERNS = {}


def createFunction (sType, sCode, bStartWithEqual=False):
    "create a function (stored in <dFUNCTIONS>) and return function name"
    sCode = prepareFunction(sCode)
    if sType not in dFUNCNAME:
        dFUNCNAME[sType] = {}
    if sCode not in dFUNCNAME[sType]:
        dFUNCNAME[sType][sCode] = len(dFUNCNAME[sType])+1
    sFuncName = "_g_" + sType + "_" + str(dFUNCNAME[sType][sCode])
    dFUNCTIONS[sFuncName] = sCode
    return sFuncName  if not bStartWithEqual  else "="+sFuncName


def storeAction (sActionId, aAction):
    "store <aAction> in <dACTIONS> avoiding duplicates"
    nVar = 0
    while True:
        sActionName = sActionId + "_" + str(nVar)
        if sActionName not in dACTIONS:
            dACTIONS[sActionName] = aAction
            return sActionName
        if aAction == dACTIONS[sActionName]:
            return sActionName
        nVar += 1


def prepareFunction (sCode):
    "convert simple rule syntax to a string of Python code"
    if sCode[0:1] == "=":
        sCode = sCode[1:]
    sCode = sCode.replace("__also__", "bCondMemo")
    sCode = sCode.replace("__else__", "not bCondMemo")
    sCode = sCode.replace("sContext", "_sAppContext")
    sCode = re.sub(r"(morph|morphVC|analyse|value|tag|displayInfo)[(]\\(\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', sCode)
    sCode = re.sub(r"(morph|morphVC|analyse|value|tag|displayInfo)[(]\\-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', sCode)
    sCode = re.sub(r"(select|exclude|define|define_from)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', sCode)
    sCode = re.sub(r"(select|exclude|define|define_from)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', sCode)
    sCode = re.sub(r"(tag_before|tag_after)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2], dTags', sCode)
    sCode = re.sub(r"(tag_before|tag_after)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1], dTags', sCode)
    sCode = re.sub(r"space_after[(][\\](\d+)", 'g_space_between_tokens(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', sCode)
    sCode = re.sub(r"space_after[(][\\]-(\d+)", 'g_space_between_tokens(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', sCode)
    sCode = re.sub(r"analyse_with_next[(][\\](\d+)", 'g_merged_analyse(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', sCode)
    sCode = re.sub(r"analyse_with_next[(][\\]-(\d+)", 'g_merged_analyse(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', sCode)
    sCode = re.sub(r"(morph|analyse|tag|value)\(>1", 'g_\\1(lToken[nLastToken+1]', sCode)                       # next token
    sCode = re.sub(r"(morph|analyse|tag|value)\(<1", 'g_\\1(lToken[nTokenOffset]', sCode)                       # previous token
    sCode = re.sub(r"(morph|analyse|tag|value)\(>(\d+)", 'g_\\1(g_token(lToken, nLastToken+\\2)', sCode)        # next token
    sCode = re.sub(r"(morph|analyse|tag|value)\(<(\d+)", 'g_\\1(g_token(lToken, nTokenOffset+1-\\2)', sCode)    # previous token
    sCode = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', sCode)
    sCode = re.sub(r"\bbefore\(\s*", 'look(sSentence[:lToken[1+nTokenOffset]["nStart"]], ', sCode)          # before(sCode)
    sCode = re.sub(r"\bafter\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', sCode)                 # after(sCode)
    sCode = re.sub(r"\bbefore0\(\s*", 'look(sSentence0[:lToken[1+nTokenOffset]["nStart"]], ', sCode)        # before0(sCode)
    sCode = re.sub(r"\bafter0\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', sCode)                # after0(sCode)
    sCode = re.sub(r"analyseWord[(]", 'analyse(', sCode)
    sCode = re.sub(r"[\\](\d+)", 'lToken[nTokenOffset+\\1]["sValue"]', sCode)
    sCode = re.sub(r"[\\]-(\d+)", 'lToken[nLastToken-\\1+1]["sValue"]', sCode)
    sCode = re.sub(r">1", 'lToken[nLastToken+1]["sValue"]', sCode)
    sCode = re.sub(r"<1", 'lToken[nTokenOffset]["sValue"]', sCode)
    return sCode


def genTokenLines (sTokenLine, dDef, dDecl):
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
        if sTokBlock.startswith("({") and sTokBlock.endswith("})") and sTokBlock[1:-1] in dDef:
            sTokBlock = "(" + dDef[sTokBlock[1:-1]] + ")"
        elif sTokBlock.startswith("{") and sTokBlock.endswith("}") and sTokBlock in dDef:
            sTokBlock = dDef[sTokBlock]
        if ( (sTokBlock.startswith("[") and sTokBlock.endswith("]")) or (sTokBlock.startswith("([") and sTokBlock.endswith("])")) ):
            # multiple token
            bSelectedGroup = sTokBlock.startswith("(") and sTokBlock.endswith(")")
            if bSelectedGroup:
                sTokBlock = sTokBlock[1:-1]
            lToken = createTokenList(sTokBlock, dDecl)
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


def createTokenList (sTokBlock, dDeclensions):
    "return a list of tokens from a block of tokens"
    lToken = []
    for sToken in sTokBlock[1:-1].split("|"):
        if "+" in sToken and not sToken.startswith("+"):
            for sCode in dDeclensions:
                if sToken.endswith(sCode):
                    sToken = sToken[:-len(sCode)]
                    lToken.append(sToken)
                    for sSuffix in dDeclensions[sCode]:
                        lToken.append(sToken+sSuffix)
                    break
        else:
            lToken.append(sToken)
    return lToken


def createRule (iLine, sRuleName, sTokenLine, iActionBlock, sActions, nPriority, dOptPriority, dDef, dDecl):
    "generator: create rule as list"
    # print(iLine, "//", sRuleName, "//", sTokenLine, "//", sActions, "//", nPriority)
    if sTokenLine.startswith("!!") and sTokenLine.endswith("¡¡"):
        # antipattern
        sTokenLine = sTokenLine[2:-2].strip()
        if sRuleName not in dANTIPATTERNS:
            dANTIPATTERNS[sRuleName]= []
        for lToken in genTokenLines(sTokenLine, dDef, dDecl):
            dANTIPATTERNS[sRuleName].append(lToken)
    else:
        # pattern
        for lToken in genTokenLines(sTokenLine, dDef, dDecl):
            if sRuleName in dANTIPATTERNS and lToken in dANTIPATTERNS[sRuleName]:
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
            for iAction, sAction in enumerate(sActions.split(" <<- ")):
                sAction = sAction.strip()
                if sAction:
                    sActionId = sRuleName + "__b" + str(iActionBlock) + "_a" + str(iAction)
                    aAction = createAction(sActionId, sAction, nPriority, dOptPriority, len(lToken), dPos)
                    if aAction:
                        sActionName = storeAction(sActionId, aAction)
                        lResult = list(lToken)
                        lResult.extend(["##"+str(iLine), sActionName])
                        #if iLine == 13341:
                        #    print("  ".join(lToken))
                        #    print(sActionId, aAction)
                        yield lResult
                    else:
                        print(" # Error on action at line:", iLine)
                        print(sTokenLine, "\n", sActions)


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
    if re.search(r"[.]\w+[(]|sugg\w+[(]|\(\\[0-9]|\[[0-9]", sText):
        print("# Warning at line " + sActionId + ":  This message looks like code. Line should probably begin with =")
        print(sText)


def createAction (sActionId, sAction, nPriority, dOptPriority, nToken, dPos):
    "create action rule as a list"
    # Option
    sOption = False
    m = re.match("/(\\w+)/", sAction)
    if m:
        sOption = m.group(1)
        sAction = sAction[m.end():].strip()
    if nPriority == -1:
        nPriority = dOptPriority.get(sOption, 4)

    # valid action?
    m = re.search(r"(?P<action>[-=~/!>])(?P<start>-?\d+\.?|)(?P<end>:\.?-?\d+|)(?P<casing>:|)>>", sAction)
    if not m:
        print(" # Error. No action found at: ", sActionId)
        return None

    # Condition
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = changeReferenceToken(sCondition, dPos)
        sCondition = createFunction("cond", sCondition)
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
            print(" # Error. Wrong selection on tokens.", sActionId)
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
        iMsg = sAction.find(" # ")
        if iMsg == -1:
            sMsg = "# Error. Error message not found."
            sURL = ""
            print(sMsg + " Action id: " + sActionId)
        else:
            sMsg = sAction[iMsg+3:].strip()
            sAction = sAction[:iMsg].strip()
            sURL = ""
            mURL = re.search("[|] *(https?://.*)", sMsg)
            if mURL:
                sURL = mURL.group(1).strip()
                sMsg = sMsg[:mURL.start(0)].strip()
            checkTokenNumbers(sMsg, sActionId, nToken)
            if sMsg[0:1] == "=":
                sMsg = createFunction("msg", sMsg, True)
            else:
                checkIfThereIsCode(sMsg, sActionId)

    # checking consistancy
    checkTokenNumbers(sAction, sActionId, nToken)

    if cAction == ">":
        ## no action, break loop if condition is False
        return [sOption, sCondition, cAction, ""]

    if not sAction and cAction != "!":
        print("# Error in action at line " + sActionId + ":  This action is empty.")

    if sAction[0:1] != "=" and cAction != "=":
        checkIfThereIsCode(sAction, sActionId)

    if cAction == "-":
        ## error detected --> suggestion
        if sAction[0:1] == "=":
            sAction = createFunction("sugg", sAction, True)
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print("# Error in action at line " + sActionId + ":  The message is empty.")
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction, cStartLimit, cEndLimit, bCaseSensitivity, nPriority, sMsg, sURL]
    if cAction == "~":
        ## text processor
        if sAction[0:1] == "=":
            sAction = createFunction("tp", sAction, True)
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction, bCaseSensitivity]
    if cAction in "!/":
        ## tags
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction]
    if cAction == "=":
        ## disambiguator
        if "define(" in sAction and not re.search(r"define\(\\-?\d+ *, *\[.*\] *\)", sAction):
            print("# Error in action at line " + sActionId + ": second argument for <define> must be a list of strings")
        sAction = createFunction("da", sAction)
        return [sOption, sCondition, cAction, sAction]
    print(" # Unknown action.", sActionId)
    return None


def make (lRule, sLang, dDef, dDecl, dOptPriority):
    "compile rules, returns a dictionary of values"
    # for clarity purpose, don’t create any file here

    # removing comments, zeroing empty lines, creating definitions, storing tests, merging rule lines
    print("  parsing rules...")
    lTokenLine = []
    sActions = ""
    nPriority = -1
    dAllGraph = {}
    sGraphName = ""
    iActionBlock = 0
    aRuleName = set()

    for i, sLine in lRule:
        sLine = sLine.rstrip()
        if "\t" in sLine:
            # tabulation not allowed
            print("Error. Tabulation at line: ", i)
            exit()
        elif sLine.startswith("@@@@GRAPH: "):
            # rules graph call
            m = re.match(r"@@@@GRAPH: *(\w+)", sLine.strip())
            if m:
                sGraphName = m.group(1)
                if sGraphName in dAllGraph:
                    print("Error at line " + i + ". Graph name <" + sGraphName + "> already exists.")
                    exit()
                dAllGraph[sGraphName] = []
            else:
                print("Error. Graph name not found at line", i)
                exit()
        elif sLine.startswith("__") and sLine.endswith("__"):
            # new rule group
            m = re.match("__(\\w+)(!\\d|)__", sLine)
            if m:
                sRuleName = m.group(1)
                if sRuleName in aRuleName:
                    print("Error at line " + str(i) + ". Rule name <" + sRuleName + "> already exists.")
                    exit()
                aRuleName.add(sRuleName)
                iActionBlock = 1
                nPriority = int(m.group(2)[1:]) if m.group(2)  else -1
            else:
                print("Syntax error in rule group: ", sLine, " -- line:", i)
                exit()
        elif re.search("^    +<<- ", sLine) or (sLine.startswith("        ") and not sLine.startswith("        ||")) \
                or re.search("^    +#", sLine) or re.search(r"[-=~/!>](?:-?\d\.?(?::\.?-?\d+|)|)>> ", sLine) :
            # actions
            sActions += " " + sLine.strip()
        elif re.match("[  ]*$", sLine):
            # empty line to end merging
            if not lTokenLine:
                continue
            if not sActions:
                print("Error. No action found at line:", i)
                exit()
            if not sGraphName:
                print("Error. All rules must belong to a named graph. Line: ", i)
                exit()
            for j, sTokenLine in lTokenLine:
                dAllGraph[sGraphName].append((j, sRuleName, sTokenLine, iActionBlock, sActions, nPriority))
            lTokenLine.clear()
            sActions = ""
            iActionBlock += 1
        elif sLine.startswith("    "):
            # tokens
            sLine = sLine.strip()
            if sLine.startswith("||"):
                iPrevLine, sPrevLine = lTokenLine[-1]
                lTokenLine[-1] = [iPrevLine, sPrevLine + " " + sLine[2:]]
            else:
                lTokenLine.append([i, sLine])
        else:
            print("Unknown line:")
            print(sLine)

    # processing rules
    print("  preparing rules...")
    for sGraphName, lRuleLine in dAllGraph.items():
        print("{:>8,} rules in {:<24} ".format(len(lRuleLine), "<"+sGraphName+">"), end="")
        lPreparedRule = []
        for i, sRuleGroup, sTokenLine, iActionBlock, sActions, nPriority in lRuleLine:
            for aRule in createRule(i, sRuleGroup, sTokenLine, iActionBlock, sActions, nPriority, dOptPriority, dDef, dDecl):
                lPreparedRule.append(aRule)
        # Graph creation
        oDARG = darg.DARG(lPreparedRule, sLang)
        dAllGraph[sGraphName] = oDARG.createGraph()
        # Debugging
        if False:
            print("\nRULES:")
            for e in lPreparedRule:
                if e[-2] == "##2211":
                    print(e)
        if False:
            print("\nGRAPH:", sGraphName)
            for k, v in dAllGraph[sGraphName].items():
                print(k, "\t", v)

    # creating file with all functions callable by rules
    print("  creating callables for graph rules...")
    sPyCallables = ""
    sJSCallables = ""
    for sFuncName, sReturn in dFUNCTIONS.items():
        if sFuncName.startswith("_g_cond_"): # condition
            sParams = "lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, dTags, sSentence, sSentence0"
        elif sFuncName.startswith("g_msg_"): # message
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
        sPyCallables += "def {} ({}):\n".format(sFuncName, sParams)
        sPyCallables += "    return " + sReturn + "\n"
        # JavaScript
        sJSCallables += "    {}: function ({})".format(sFuncName, sParams) + " {\n"
        sJSCallables += "        return " + jsconv.py2js(sReturn) + ";\n"
        sJSCallables += "    },\n"

    # Debugging
    if False:
        print("\nActions:")
        for sActionName, aAction in dACTIONS.items():
            print(sActionName, aAction)
        print("\nFunctions:")
        print(sPyCallables)

    # Result
    return {
        "graph_callables": sPyCallables,
        "graph_callablesJS": sJSCallables,
        "rules_graphs": str(dAllGraph),
        "rules_graphsJS": str(dAllGraph),
        "rules_actions": str(dACTIONS),
        "rules_actionsJS": jsconv.pyActionsToString(dACTIONS)
    }
