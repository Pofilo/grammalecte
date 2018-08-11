"""
Grammalecte: compile rules
Create a Direct Acyclic Rule Graphs (DARGs)
"""

import re
import traceback
import json

import darg


dACTIONS = {}
dFUNCTIONS = {}
dFUNCNAME = {}


def createFunction (sType, sActionId, sCode, bStartWithEqual=False):
    "create a function (stored in dFUNCTIONS) and return function name"
    sCode = prepareFunction(sCode)
    if sActionId not in dFUNCNAME:
        dFUNCNAME[sActionId] = {}
    if sCode not in dFUNCNAME[sActionId]:
        dFUNCNAME[sActionId][sCode] = len(dFUNCNAME[sActionId])+1
    sFuncName = "_g_" + sType + "_" + sActionId + "_" + str(dFUNCNAME[sActionId][sCode])
    dFUNCTIONS[sFuncName] = sCode
    return sFuncName  if not bStartWithEqual  else "="+sFuncName


def prepareFunction (s):
    "convert simple rule syntax to a string of Python code"
    if s[0:1] == "=":
        s = s[1:]
    s = s.replace("__also__", "bCondMemo")
    s = s.replace("__else__", "not bCondMemo")
    s = s.replace("sContext", "_sAppContext")
    s = re.sub(r"(morph|morphVC|analyse|value|displayInfo)[(]\\(\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', s)
    s = re.sub(r"(morph|morphVC|analyse|value|displayInfo)[(]\\-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', s)
    s = re.sub(r"(select|exclude|define|define_from)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2]', s)
    s = re.sub(r"(select|exclude|define|define_from)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1]', s)
    s = re.sub(r"(tag_before|tag_after)[(][\\](\d+)", 'g_\\1(lToken[nTokenOffset+\\2], dTags', s)
    s = re.sub(r"(tag_before|tag_after)[(][\\]-(\d+)", 'g_\\1(lToken[nLastToken-\\2+1], dTags', s)
    s = re.sub(r"space_after[(][\\](\d+)", 'g_space_between_tokens(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', s)
    s = re.sub(r"space_after[(][\\]-(\d+)", 'g_space_between_tokens(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', s)
    s = re.sub(r"analyse_with_next[(][\\](\d+)", 'g_merged_analyse(lToken[nTokenOffset+\\1], lToken[nTokenOffset+\\1+1]', s)
    s = re.sub(r"analyse_with_next[(][\\]-(\d+)", 'g_merged_analyse(lToken[nLastToken-\\1+1], lToken[nLastToken-\\1+2]', s)
    s = re.sub(r"(morph|analyse|value)\(>1", 'g_\\1(lToken[nLastToken+1]', s)                       # next token
    s = re.sub(r"(morph|analyse|value)\(<1", 'g_\\1(lToken[nTokenOffset]', s)                       # previous token
    s = re.sub(r"(morph|analyse|value)\(>(\d+)", 'g_\\1(g_token(lToken, nLastToken+\\2)', s)          # next token
    s = re.sub(r"(morph|analyse|value)\(<(\d+)", 'g_\\1(g_token(lToken, nTokenOffset+1-\\2)', s)      # previous token
    s = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', s)
    s = re.sub(r"\bbefore\(\s*", 'look(sSentence[:lToken[1+nTokenOffset]["nStart"]], ', s)          # before(s)
    s = re.sub(r"\bafter\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', s)                 # after(s)
    s = re.sub(r"\bbefore0\(\s*", 'look(sSentence0[:lToken[1+nTokenOffset]["nStart"]], ', s)        # before0(s)
    s = re.sub(r"\bafter0\(\s*", 'look(sSentence[lToken[nLastToken]["nEnd"]:], ', s)                # after0(s)
    s = re.sub(r"[\\](\d+)", 'lToken[nTokenOffset+\\1]["sValue"]', s)
    s = re.sub(r"[\\]-(\d+)", 'lToken[nLastToken-\\1+1]["sValue"]', s)
    return s


def genTokenLines (sTokenLine, dDef):
    "tokenize a string and return a list of lines of tokens"
    lToken = sTokenLine.split()
    lTokenLines = None
    for sToken in lToken:
        # optional token?
        bNullPossible = sToken.startswith("?") and sToken.endswith("¿")
        if bNullPossible:
            sToken = sToken[1:-1]
        # token with definition?
        if sToken.startswith("({") and sToken.endswith("})") and sToken[1:-1] in dDef:
            sToken = "(" + dDef[sToken[1:-1]] + ")"
        elif sToken.startswith("{") and sToken.endswith("}") and sToken in dDef:
            sToken = dDef[sToken]
        if ( (sToken.startswith("[") and sToken.endswith("]")) or (sToken.startswith("([") and sToken.endswith("])")) ):
            # multiple token
            bSelectedGroup = sToken.startswith("(") and sToken.endswith(")")
            if bSelectedGroup:
                sToken = sToken[1:-1]
            lNewToken = sToken[1:-1].split("|")
            if not lTokenLines:
                lTokenLines = [ ["("+s+")"]  for s  in lNewToken ]  if bSelectedGroup  else [ [s]  for s  in lNewToken ]
                if bNullPossible:
                    lTokenLines.extend([ []  for i  in range(len(lNewToken)+1) ])
            else:
                lNewTemp = []
                if bNullPossible:
                    for aRule in lTokenLines:
                        for sElem in lNewToken:
                            aNewRule = list(aRule)
                            aNewRule.append(sElem)
                            lNewTemp.append(aNewRule)
                else:
                    sElem1 = lNewToken.pop(0)
                    for aRule in lTokenLines:
                        for sElem in lNewToken:
                            aNewRule = list(aRule)
                            aNewRule.append("(" + sElem + ")"  if bSelectedGroup  else sElem)
                            lNewTemp.append(aNewRule)
                        aRule.append("(" + sElem1 + ")"  if bSelectedGroup  else sElem1)
                lTokenLines.extend(lNewTemp)
        else:
            # simple token
            if not lTokenLines:
                lTokenLines = [[sToken], []]  if bNullPossible  else [[sToken]]
            else:
                if bNullPossible:
                    lNewTemp = []
                    for aRule in lTokenLines:
                        lNew = list(aRule)
                        lNew.append(sToken)
                        lNewTemp.append(lNew)
                    lTokenLines.extend(lNewTemp)
                else:
                    for aRule in lTokenLines:
                        aRule.append(sToken)
    for aRule in lTokenLines:
        yield aRule


def createRule (iLine, sRuleName, sTokenLine, iActionBlock, sActions, nPriority, dOptPriority, dDef):
    "generator: create rule as list"
    # print(iLine, "//", sRuleName, "//", sTokenLine, "//", sActions, "//", nPriority)
    for lToken in genTokenLines(sTokenLine, dDef):
        # Calculate positions
        dPos = {}   # key: iGroup, value: iToken
        iGroup = 0
        #if iLine == 3971: # debug
        #    print(lToken)
        for i, sToken in enumerate(lToken):
            if sToken.startswith("(") and sToken.endswith(")"):
                lToken[i] = sToken[1:-1]
                iGroup += 1
                dPos[iGroup] = i + 1    # we add 1, for we count tokens from 1 to n (not from 0)

        # Parse actions
        for iAction, sAction in enumerate(sActions.split(" <<- ")):
            sAction = sAction.strip()
            if sAction:
                sActionId = sRuleName + "__b" + str(iActionBlock) + "_a" + str(iAction) + "_" + str(len(lToken))
                aAction = createAction(sActionId, sAction, nPriority, dOptPriority, len(lToken), dPos)
                if aAction:
                    dACTIONS[sActionId] = aAction
                    lResult = list(lToken)
                    lResult.extend(["##"+str(iLine), sActionId])
                    yield lResult
                else:
                    print(" # Error on action at line:", iLine)
                    print(sTokenLine, "\n", sActions)


def changeReferenceToken (sText, dPos):
    "change group reference in <sText> with values in <dPos>"
    for i in range(len(dPos), 0, -1):
        sText = sText.replace("\\"+str(i), "\\"+str(dPos[i]))
    return sText


def checkTokenNumbers (sText, sActionId, nToken):
    "check if token references in <sText> greater than <nToken> (debugging)"
    for x in re.finditer(r"\\(\d+)", sText):
        if int(x.group(1)) > nToken:
            print("# Error in token index at line " + sActionId + " ("+str(nToken)+" tokens only)")
            print(sText)


def checkIfThereIsCode (sText, sActionId):
    "check if there is code in <sText> (debugging)"
    if re.search("[.]\\w+[(]|sugg\\w+[(]|\\([0-9]|\\[[0-9]", sText):
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
    m = re.search(r"(?P<action>[-~=/%>])(?P<start>-?\d+\.?|)(?P<end>:\.?-?\d+|)(?P<casing>:|)>>", sAction)
    if not m:
        print(" # Error. No action found at: ", sActionId)
        return None

    # Condition
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = changeReferenceToken(sCondition, dPos)
        sCondition = createFunction("cond", sActionId, sCondition)
    else:
        sCondition = ""

    # Case sensitivity
    bCaseSensitivity = False if m.group("casing") == ":" else True

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
        try:
            iStartAction = dPos.get(iStartAction, iStartAction)
            if iEndAction:
                iEndAction = dPos.get(iEndAction, iEndAction)
        except:
            print("# Error. Wrong groups in: " + sActionId)
            print("  iStartAction:", iStartAction, "iEndAction:", iEndAction)
            print(" ", dPos)
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
                sMsg = createFunction("msg", sActionId, sMsg, True)
            else:
                checkIfThereIsCode(sMsg, sActionId)

    # checking consistancy
    checkTokenNumbers(sAction, sActionId, nToken)

    if cAction == ">":
        ## no action, break loop if condition is False
        return [sOption, sCondition, cAction, ""]

    if not sAction and cAction != "%":
        print("# Error in action at line " + sActionId + ":  This action is empty.")

    if sAction[0:1] != "=" and cAction != "=":
        checkIfThereIsCode(sAction, sActionId)

    if cAction == "-":
        ## error detected --> suggestion
        if sAction[0:1] == "=":
            sAction = createFunction("sugg", sActionId, sAction, True)
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print("# Error in action at line " + sActionId + ":  The message is empty.")
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction, cStartLimit, cEndLimit, bCaseSensitivity, nPriority, sMsg, sURL]
    elif cAction == "~":
        ## text processor
        if sAction[0:1] == "=":
            sAction = createFunction("tp", sActionId, sAction, True)
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction, bCaseSensitivity]
    elif cAction == "%" or cAction == "/":
        ## tags
        return [sOption, sCondition, cAction, sAction, iStartAction, iEndAction]
    elif cAction == "=":
        ## disambiguator
        if "define(" in sAction and not re.search(r"define\(\\\d+ *, *\[.*\] *\)", sAction):
            print("# Error in action at line " + sActionId + ": second argument for <define> must be a list of strings")
        sAction = createFunction("da", sActionId, sAction)
        return [sOption, sCondition, cAction, sAction]
    else:
        print(" # Unknown action.", sActionId)
        return None


def make (lRule, dDef, sLang, dOptPriority, bJavaScript):
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
                    print("Error. Graph name " + sGraphName + " already exists.")
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
                iActionBlock = 1
                nPriority = int(m.group(2)[1:]) if m.group(2)  else -1
            else:
                print("Syntax error in rule group: ", sLine, " -- line:", i)
                exit()
        elif re.search("^    +<<- ", sLine) or (sLine.startswith("        ") and not sLine.startswith("        ||")) \
                or re.search("^    +#", sLine) or re.search(r"[-~=>/%](?:-?\d\.?(?::\.?-?\d+|)|)>> ", sLine) :
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
        lPreparedRule = []
        for i, sRuleGroup, sTokenLine, iActionBlock, sActions, nPriority in lRuleLine:
            for lRule in createRule(i, sRuleGroup, sTokenLine, iActionBlock, sActions, nPriority, dOptPriority, dDef):
                lPreparedRule.append(lRule)
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
    print("  creating callables...")
    sPyCallables = "# generated code, do not edit\n"
    #sJSCallables = "// generated code, do not edit\nconst oEvalFunc = {\n"
    for sFuncName, sReturn in dFUNCTIONS.items():
        if sFuncName.startswith("_g_cond_"): # condition
            sParams = "lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, dTags, sSentence, sSentence0"
        elif sFuncName.startswith("g_msg_"): # message
            sParams = "lToken, nTokenOffset"
        elif sFuncName.startswith("_g_sugg_"): # suggestion
            sParams = "lToken, nTokenOffset, nLastToken"
        elif sFuncName.startswith("_g_tp_"): # text preprocessor
            sParams = "lToken, nTokenOffset"
        elif sFuncName.startswith("_g_da_"): # disambiguator
            sParams = "lToken, nTokenOffset"
        else:
            print("# Unknown function type in [" + sFuncName + "]")
            continue
        sPyCallables += "def {} ({}):\n".format(sFuncName, sParams)
        sPyCallables += "    return " + sReturn + "\n"
        #sJSCallables += "    {}: function ({})".format(sFuncName, sParams) + " {\n"
        #sJSCallables += "        return " + jsconv.py2js(sReturn) + ";\n"
        #sJSCallables += "    },\n"
    #sJSCallables += "}\n"

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
        "rules_graphs": dAllGraph,
        "rules_actions": dACTIONS
    }
