# Create a Direct Acyclic Rule Graph (DARG)

import re
import traceback
import json
import darg


dDEF = {}
dACTIONS = {}
lFUNCTIONS = []


def prepareFunction (s):
    s = s.replace("__also__", "bCondMemo")
    s = s.replace("__else__", "not bCondMemo")
    s = re.sub(r"isStart *\(\)", 'before(["<START>", ","])', s)
    s = re.sub(r"isRealStart *\(\)", 'before(["<START>"])', s)
    s = re.sub(r"isStart0 *\(\)", 'before0(["<START>", ","])', s)
    s = re.sub(r"isRealStart0 *\(\)", 'before0(["<START>"])', s)
    s = re.sub(r"isEnd *\(\)", 'after(["<END>", ","])', s)
    s = re.sub(r"isRealEnd *\(\)", 'after(["<END>"])', s)
    s = re.sub(r"isEnd0 *\(\)", 'after0(["<END>", ","])', s)
    s = re.sub(r"isRealEnd0 *\(\)", 'after0(["<END>"])', s)
    s = re.sub(r"(select|exclude|define)[(][\\](\d+)", 'g_\\1(lToken[\\2+nTokenOffset]', s)
    s = re.sub(r"(morph|displayInfo)[(]\\(\d+)", 'g_\\1(lToken[\\2+nTokenOffset]', s)
    s = re.sub(r"token\(\s*(\d)", 'nextToken(\\1', s)                                       # token(n)
    s = re.sub(r"token\(\s*-(\d)", 'prevToken(\\1', s)                                      # token(-n)
    s = re.sub(r"before\(\s*", 'look(s[:m.start()], ', s)                                   # before(s)
    s = re.sub(r"after\(\s*", 'look(s[m.end():], ', s)                                      # after(s)
    s = re.sub(r"textarea\(\s*", 'look(s, ', s)                                             # textarea(s)
    s = re.sub(r"before_chk1\(\s*", 'look_chk1(dDA, s[:m.start()], 0, ', s)                 # before_chk1(s)
    s = re.sub(r"after_chk1\(\s*", 'look_chk1(dDA, s[m.end():], m.end(), ', s)              # after_chk1(s)
    s = re.sub(r"textarea_chk1\(\s*", 'look_chk1(dDA, s, 0, ', s)                           # textarea_chk1(s)
    #s = re.sub(r"isEndOfNG\(\s*\)", 'isEndOfNG(dDA, s[m.end():], m.end())', s)              # isEndOfNG(s)
    #s = re.sub(r"isNextNotCOD\(\s*\)", 'isNextNotCOD(dDA, s[m.end():], m.end())', s)        # isNextNotCOD(s)
    #s = re.sub(r"isNextVerb\(\s*\)", 'isNextVerb(dDA, s[m.end():], m.end())', s)            # isNextVerb(s)
    s = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', s)
    s = re.sub(r"[\\](\d+)", 'lToken[\\1]', s)
    return s


def genTokenLines (sTokenLine):
    "tokenize a string and return a list of lines of tokens"
    lToken = sTokenLine.split()
    lTokenLines = None
    for i, sToken in enumerate(lToken):
        if sToken.startswith("{") and sToken.endswith("}") and sToken in dDEF:
            lToken[i] = dDEF[sToken]
        if ( (sToken.startswith("[") and sToken.endswith("]")) or (sToken.startswith("([") and sToken.endswith("])")) ):
            bSelectedGroup = sToken.startswith("(") and sToken.endswith(")")
            if bSelectedGroup:
                sToken = sToken[1:-1]
            # multiple token
            if not lTokenLines:
                lTokenLines = [ [s]  for s  in sToken[1:-1].split("|") ]
            else:
                lNewTemp = []
                for aRule in lTokenLines:
                    lElem = sToken[1:-1].split("|")
                    sElem1 = lElem.pop(0)
                    if bSelectedGroup:
                        sElem1 = "(" + sElem1 + ")"
                    for sElem in lElem:
                        if bSelectedGroup:
                            sElem = "(" + sElem + ")"
                        aNew = list(aRule)
                        aNew.append(sElem)
                        lNewTemp.append(aNew)
                    aRule.append(sElem1)
                lTokenLines.extend(lNewTemp)
        else:
            # simple token
            if not lTokenLines:
                lTokenLines = [[sToken]]
            else:
                for aRule in lTokenLines:
                    aRule.append(sToken)
    for aRule in lTokenLines:
        yield aRule


def createRule (iLine, sRuleName, sTokenLine, sActions, nPriority):
    # print(iLine, "//", sRuleName, "//", sTokenLine, "//", sActions, "//", nPriority)
    for lToken in genTokenLines(sTokenLine):
        # Calculate positions
        dPos = {}   # key: iGroup, value: iToken
        iGroup = 0
        for i, sToken in enumerate(lToken):
            if sToken.startswith("(") and sToken.endswith(")"):
                lToken[i] = sToken[1:-1]
                iGroup += 1
                dPos[iGroup] = i + 1    # we add 1, for we count tokens from 1 to n (not from 0)

        # Parse actions
        for nAction, sAction in enumerate(sActions.split(" <<- ")):
            if sAction.strip():
                sActionId = sRuleName + "_a" + str(nAction)
                aAction = createAction(sActionId, sAction, nPriority, len(lToken), dPos)
                if aAction:
                    dACTIONS[sActionId] = aAction
                    lResult = list(lToken)
                    lResult.extend(["##"+str(iLine), sActionId])
                    yield lResult


def changeReferenceToken (s, dPos):
    for i in range(len(dPos), 0, -1):
        s = s.replace("\\"+str(i), "\\"+str(dPos[i]))
    return s


def createAction (sIdAction, sAction, nPriority, nToken, dPos):
    m = re.search("(?P<action>[-~=])(?P<start>\\d+|)(?P<end>:\\d+|)>> ", sAction)
    if not m:
        print(" # Error. No action found at: ", sIdAction)
        print("   ==", sAction, "==")
        return None
    # Condition
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = prepareFunction(sCondition)
        sCondition = changeReferenceToken(sCondition, dPos)    
        lFUNCTIONS.append(("g_c_"+sIdAction, sCondition))
        sCondition = "g_c_"+sIdAction
    else:
        sCondition = ""
    # Action
    cAction = m.group("action")
    sAction = sAction[m.end():].strip()
    sAction = changeReferenceToken(sAction, dPos)
    if not m.group("start"):
        iStartAction = 1
        iEndAction = nToken
    else:
        iStartAction = int(m.group("start"))
        iEndAction = int(m.group("end")[1:])  if m.group("end")  else iStartAction
    if dPos:
        try:
            iStartAction = dPos[iStartAction]
            iEndAction = dPos[iEndAction]
        except:
            print("# Error. Wrong groups in: " + sIdAction)

    if cAction == "-":
        ## error
        iMsg = sAction.find(" # ")
        if iMsg == -1:
            sMsg = "# Error. Error message not found."
            sURL = ""
            print(sMsg + " Action id: " + sIdAction)
        else:
            sMsg = sAction[iMsg+3:].strip()
            sAction = sAction[:iMsg].strip()
            sURL = ""
            mURL = re.search("[|] *(https?://.*)", sMsg)
            if mURL:
                sURL = mURL.group(1).strip()
                sMsg = sMsg[:mURL.start(0)].strip()
            if sMsg[0:1] == "=":
                sMsg = prepareFunction(sMsg[1:])
                lFUNCTIONS.append(("g_m_"+sIdAction, sMsg))
                for x in re.finditer("group[(](\\d+)[)]", sMsg):
                    if int(x.group(1)) > nToken:
                        print("# Error in token index in message at line " + sIdAction + " ("+str(nToken)+" tokens only)")
                sMsg = "=g_m_"+sIdAction
            else:
                for x in re.finditer(r"\\(\d+)", sMsg):
                    if int(x.group(1)) > nToken:
                        print("# Error in token index in message at line " + sIdAction + " ("+str(nToken)+" tokens only)")
                if re.search("[.]\\w+[(]", sMsg):
                    print("# Error in message at line " + sIdAction + ":  This message looks like code. Line should begin with =")
            
    if sAction[0:1] == "=" or cAction == "=":
        if "define" in sAction and not re.search(r"define\(\\\d+ *, *\[.*\] *\)", sAction):
            print("# Error in action at line " + sIdAction + ": second argument for define must be a list of strings")
        sAction = prepareFunction(sAction)
        for x in re.finditer("group[(](\\d+)[)]", sAction):
            if int(x.group(1)) > nToken:
                print("# Error in token index in replacement at line " + sIdAction + " ("+str(nToken)+" tokens only)")
    else:
        for x in re.finditer(r"\\(\d+)", sAction):
            if int(x.group(1)) > nToken:
                print("# Error in token index in replacement at line " + sIdAction + " ("+str(nToken)+" tokens only)")
        if re.search("[.]\\w+[(]|sugg\\w+[(]", sAction):
            print("# Error in action at line " + sIdAction + ":  This action looks like code. Line should begin with =")

    if cAction == "-":
        ## error detected --> suggestion
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("g_s_"+sIdAction, sAction[1:]))
            sAction = "=g_s_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print("# Error in action at line " + sIdAction + ":  The message is empty.")
        return [sCondition, cAction, sAction, iStartAction, iEndAction, nPriority, sMsg, sURL]
    elif cAction == "~":
        ## text processor
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("g_p_"+sIdAction, sAction[1:]))
            sAction = "=g_p_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sCondition, cAction, sAction, iStartAction, iEndAction]
    elif cAction == "=":
        ## disambiguator
        if sAction[0:1] == "=":
            sAction = sAction[1:]
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        lFUNCTIONS.append(("g_d_"+sIdAction, sAction))
        sAction = "g_d_"+sIdAction
        return [sCondition, cAction, sAction]
    elif cAction == ">":
        ## no action, break loop if condition is False
        return [sCondition, cAction, ""]
    else:
        print("# Unknown action at line " + sIdAction)
        return None


def make (spLang, sLang, bJavaScript):
    "compile rules, returns a dictionary of values"
    # for clarity purpose, don’t create any file here

    print("> read graph rules file...")
    try:
        lRules = open(spLang + "/rules_graph.grx", 'r', encoding="utf-8").readlines()
    except:
        print("Error. Rules file in project [" + sLang + "] not found.")
        exit()

    # removing comments, zeroing empty lines, creating definitions, storing tests, merging rule lines
    print("  parsing rules...")
    global dDEF
    lLine = []
    lRuleLine = []
    lTest = []
    lOpt = []
    lTokenLine = []
    sActions = ""
    nPriority = 4

    for i, sLine in enumerate(lRules, 1):
        sLine = sLine.rstrip()
        if "\t" in sLine:
            print("Error. Tabulation at line: ", i)
            break
        if sLine.startswith('#END'):
            printBookmark(0, "BREAK BY #END", i)
            break
        elif sLine.startswith("#"):
            pass
        elif sLine.startswith("DEF:"):
            m = re.match("DEF: +([a-zA-Z_][a-zA-Z_0-9]*) +(.+)$", sLine.strip())
            if m:
                dDEF["{"+m.group(1)+"}"] = m.group(2)
            else:
                print("Error in definition: ", end="")
                print(sLine.strip())
        elif sLine.startswith("TEST:"):
            lTest.append("g{:<7}".format(i) + "  " + sLine[5:].strip())
        elif sLine.startswith("TODO:"):
            pass
        elif sLine.startswith("!!"):
            m = re.search("^!!+", sLine)
            nExMk = len(m.group(0))
            if sLine[nExMk:].strip():
                printBookmark(nExMk-2, sLine[nExMk:].strip(), i)
        elif sLine.startswith("__") and sLine.endswith("__"):
            # new rule group
            m = re.match("__(\\w+)(!\\d|)__", sLine)
            if m:
                sRuleName = m.group(1)
                nPriority = int(m.group(2)[1:]) if m.group(2)  else 4
            else:
                print("Error at rule group: ", sLine, " -- line:", i)
                break
        elif re.match("[  ]*$", sLine):
            # empty line to end merging
            for i, sTokenLine in lTokenLine:
                lRuleLine.append((i, sRuleName, sTokenLine, sActions, nPriority))
            lTokenLine = []
            sActions = ""
            sRuleName = ""
            nPriority = 4
        elif sLine.startswith(("        ")):
            # actions
            sActions += " " + sLine.strip()
        else:
            lTokenLine.append([i, sLine.strip()])

    # tests
    print("  list tests...")
    sGCTests = "\n".join(lTest)
    sGCTestsJS = '{ "aData2": ' + json.dumps(lTest, ensure_ascii=False) + " }\n"

    # processing rules
    print("  preparing rules...")
    lPreparedRule = []
    for i, sRuleGroup, sTokenLine, sActions, nPriority in lRuleLine:
        for lRule in createRule(i, sRuleGroup, sTokenLine, sActions, nPriority):
            lPreparedRule.append(lRule)

    # Graph creation
    for e in lPreparedRule:
        print(e)

    oDARG = darg.DARG(lPreparedRule, sLang)
    oRuleGraph = oDARG.createGraph()

    # creating file with all functions callable by rules
    print("  creating callables...")
    sPyCallables = "# generated code, do not edit\n"
    #sJSCallables = "// generated code, do not edit\nconst oEvalFunc = {\n"
    for sFuncName, sReturn in lFUNCTIONS:
        if sFuncName.startswith("g_c_"): # condition
            sParams = "lToken, nTokenOffset, sCountry, bCondMemo"
        elif sFuncName.startswith("g_m_"): # message
            sParams = "lToken, nTokenOffset"
        elif sFuncName.startswith("g_s_"): # suggestion
            sParams = "lToken, nTokenOffset"
        elif sFuncName.startswith("g_p_"): # preprocessor
            sParams = "lToken"
        elif sFuncName.startswith("g_d_"): # disambiguator
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

    for sActionName, aAction in dACTIONS.items():
        print(sActionName, aAction)

    # Result
    d = {
        "graph_callables": sPyCallables,
        "graph_gctests": sGCTests,
        "rules_graph": oRuleGraph,
        "rules_actions": dACTIONS
    }

    return d


