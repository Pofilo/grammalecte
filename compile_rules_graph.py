# Create a Direct Acyclic Rule Graph (DARG)

import re
import traceback
import json
import datg


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
    s = re.sub(r"(select|exclude)[(][\\](\d+)", '\\1(lToken[\\2]', s)
    s = re.sub(r"define[(][\\](\d+)", 'define(lToken[\\1]', s)
    s = re.sub(r"(morph|morphex|displayInfo)[(][\\](\d+)", '\\1(lToken[\\2])', s)
    s = re.sub(r"token\(\s*(\d)", 'nextToken(\\1', s)                                       # token(n)
    s = re.sub(r"token\(\s*-(\d)", 'prevToken(\\1', s)                                      # token(-n)
    s = re.sub(r"before\(\s*", 'look(s[:m.start()], ', s)                                   # before(s)
    s = re.sub(r"after\(\s*", 'look(s[m.end():], ', s)                                      # after(s)
    s = re.sub(r"textarea\(\s*", 'look(s, ', s)                                             # textarea(s)
    s = re.sub(r"before_chk1\(\s*", 'look_chk1(dDA, s[:m.start()], 0, ', s)                 # before_chk1(s)
    s = re.sub(r"after_chk1\(\s*", 'look_chk1(dDA, s[m.end():], m.end(), ', s)              # after_chk1(s)
    s = re.sub(r"textarea_chk1\(\s*", 'look_chk1(dDA, s, 0, ', s)                           # textarea_chk1(s)
    s = re.sub(r"isEndOfNG\(\s*\)", 'isEndOfNG(dDA, s[m.end():], m.end())', s)              # isEndOfNG(s)
    s = re.sub(r"isNextNotCOD\(\s*\)", 'isNextNotCOD(dDA, s[m.end():], m.end())', s)        # isNextNotCOD(s)
    s = re.sub(r"isNextVerb\(\s*\)", 'isNextVerb(dDA, s[m.end():], m.end())', s)            # isNextVerb(s)
    s = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', s)
    s = re.sub(r"[\\](\d+)", 'lToken[\\1]', s)
    return s


def changeReferenceToken (s, dPos):
    for i in range(len(dPos), 0, -1):
        s = s.replace("\\"+str(i), "\\"+dPos[i])
    return s


def createRule (iLine, sRuleName, sTokenLine, sActions, nPriority):
    # print(iLine, "//", sRuleName, "//", sTokenLine, "//", sActions, "//", nPriority)
    lToken = sTokenLine.split()

    # Calculate positions
    dPos = {}
    nGroup = 0
    for i, sToken in enumerate(lToken):
        if sToken.startswith("(") and sToken.endswith(")"):
            lToken[i] = sToken[1:-1]
            nGroup += 1
            dPos[nGroup] = i

    # Parse actions
    for nAction, sAction in enumerate(sActions.split(" <<- ")):
        if sAction.strip():
            sActionId = sRuleName + "_a" + str(nAction)
            sCondition, tAction = createAction(sActionId, sAction, nGroup, nPriority, dPos)
            if tAction:
                dACTIONS[sActionId] = tAction
                lResult = list(lToken)
                lResult.extend(["##"+str(iLine), sRuleName, sCondition, sActionId])
                yield lResult


def createAction (sIdAction, sAction, nGroup, nPriority, dPos):
    m = re.search("([-~=])(\\d+|)(:\\d+|)>> ", sAction)
    if not m:
        print(" # Error. No action found at: ", sIdAction)
        print("   ==", sAction, "==")
        return None, None
    # Condition
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = prepareFunction(sCondition)
        sCondition = changeReferenceToken(sCondition, dPos)    
        lFUNCTIONS.append(("gc_"+sIdAction, sCondition))
        sCondition = "gc_"+sIdAction
    else:
        sCondition = ""
    # Action
    cAction = m.group(1)
    sAction = sAction[m.end():].strip()
    sAction = changeReferenceToken(sAction, dPos)
    iStartAction = int(m.group(2))  if m.group(2)  else 0
    iEndAction = int(m.group(3)[1:])  if m.group(3)  else iStartAction
    if nGroup:
        iStartAction = dPos[iStartAction]
        iEndAction = dPos[iEndAction]

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
                lFUNCTIONS.append(("gm_"+sIdAction, sMsg))
                for x in re.finditer("group[(](\d+)[)]", sMsg):
                    if int(x.group(1)) > nGroup:
                        print("# Error in groups in message at line " + sIdAction + " ("+str(nGroup)+" groups only)")
                sMsg = "=m_"+sIdAction
            else:
                for x in re.finditer(r"\\(\d+)", sMsg):
                    if int(x.group(1)) > nGroup:
                        print("# Error in groups in message at line " + sIdAction + " ("+str(nGroup)+" groups only)")
                if re.search("[.]\\w+[(]", sMsg):
                    print("# Error in message at line " + sIdAction + ":  This message looks like code. Line should begin with =")
            
    if sAction[0:1] == "=" or cAction == "=":
        if "define" in sAction and not re.search(r"define\(\\\d+ *, *\[.*\] *\)", sAction):
            print("# Error in action at line " + sIdAction + ": second argument for define must be a list of strings")
        sAction = prepareFunction(sAction)
        for x in re.finditer("group[(](\d+)[)]", sAction):
            if int(x.group(1)) > nGroup:
                print("# Error in groups in replacement at line " + sIdAction + " ("+str(nGroup)+" groups only)")
    else:
        for x in re.finditer(r"\\(\d+)", sAction):
            if int(x.group(1)) > nGroup:
                print("# Error in groups in replacement at line " + sIdAction + " ("+str(nGroup)+" groups only)")
        if re.search("[.]\\w+[(]|sugg\\w+[(]", sAction):
            print("# Error in action at line " + sIdAction + ":  This action looks like code. Line should begin with =")

    if cAction == "-":
        ## error detected --> suggestion
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("gs_"+sIdAction, sAction[1:]))
            sAction = "=gs_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print("# Error in action at line " + sIdAction + ":  The message is empty.")
        return [sCondition, (cAction, sAction, iStartAction, iEndAction, nPriority, sMsg, sURL)]
    elif cAction == "~":
        ## text processor
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("gp_"+sIdAction, sAction[1:]))
            sAction = "=gp_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sCondition, (cAction, sAction, iStartAction, iEndAction)]
    elif cAction == "=":
        ## disambiguator
        if sAction[0:1] == "=":
            sAction = sAction[1:]
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        lFUNCTIONS.append(("gd_"+sIdAction, sAction))
        sAction = "gd_"+sIdAction
        return [sCondition, (cAction, sAction)]
    elif cAction == ">":
        ## no action, break loop if condition is False
        return [sCondition, (cAction, "")]
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
            lTest.append("{:<8}".format(i) + "  " + sLine[5:].strip())
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

    oDATG = datg.DATG(lPreparedRule, sLang)
    oRuleGraph = oDATG.createGraph()

    # Result
    d = {
        "g_callables": None,
        "g_gctests": None,
        "graph_rules": None,
    }

    return d


