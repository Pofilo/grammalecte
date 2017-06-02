
import re
import sys
import traceback
import copy
import json
from distutils import file_util


dDEF = {}
lFUNCTIONS = []

aRULESET = set()     # set of rule-ids to check if there is several rules with the same id
nRULEWITHOUTNAME = 0

dJSREGEXES = {}

sWORDLIMITLEFT  = r"(?<![\w.,–-])"   # r"(?<![-.,—])\b"  seems slower
sWORDLIMITRIGHT = r"(?![\w–-])"      # r"\b(?!-—)"       seems slower


def prepareFunction (s):
    s = s.replace("__also__", "bCondMemo")
    s = s.replace("__else__", "not bCondMemo")
    s = re.sub(r"isStart *\(\)", 'before("^ *$|, *$")', s)
    s = re.sub(r"isRealStart *\(\)", 'before("^ *$")', s)
    s = re.sub(r"isStart0 *\(\)", 'before0("^ *$|, *$")', s)
    s = re.sub(r"isRealStart0 *\(\)", 'before0("^ *$")', s)
    s = re.sub(r"isEnd *\(\)", 'after("^ *$|^,")', s)
    s = re.sub(r"isRealEnd *\(\)", 'after("^ *$")', s)
    s = re.sub(r"isEnd0 *\(\)", 'after0("^ *$|^,")', s)
    s = re.sub(r"isRealEnd0 *\(\)", 'after0("^ *$")', s)
    s = re.sub(r"(select|exclude)[(][\\](\d+)", '\\1(dDA, m.start(\\2), m.group(\\2)', s)
    s = re.sub(r"define[(][\\](\d+)", 'define(dDA, m.start(\\1)', s)
    s = re.sub(r"(morph|morphex|displayInfo)[(][\\](\d+)", '\\1((m.start(\\2), m.group(\\2))', s)
    s = re.sub(r"(morph|morphex|displayInfo)[(]", '\\1(dDA, ', s)
    s = re.sub(r"(sugg\w+|switch\w+)\(@", '\\1(m.group(i[4])', s)
    s = re.sub(r"word\(\s*1\b", 'nextword1(s, m.end()', s)                                  # word(1)
    s = re.sub(r"word\(\s*-1\b", 'prevword1(s, m.start()', s)                               # word(-1)
    s = re.sub(r"word\(\s*(\d)", 'nextword(s, m.end(), \\1', s)                             # word(n)
    s = re.sub(r"word\(\s*-(\d)", 'prevword(s, m.start(), \\1', s)                          # word(-n)
    s = re.sub(r"before\(\s*", 'look(s[:m.start()], ', s)                                   # before(s)
    s = re.sub(r"after\(\s*", 'look(s[m.end():], ', s)                                      # after(s)
    s = re.sub(r"textarea\(\s*", 'look(s, ', s)                                             # textarea(s)
    s = re.sub(r"before_chk1\(\s*", 'look_chk1(dDA, s[:m.start()], 0, ', s)                 # before_chk1(s)
    s = re.sub(r"after_chk1\(\s*", 'look_chk1(dDA, s[m.end():], m.end(), ', s)              # after_chk1(s)
    s = re.sub(r"textarea_chk1\(\s*", 'look_chk1(dDA, s, 0, ', s)                           # textarea_chk1(s)
    s = re.sub(r"/0", 'sx[m.start():m.end()]', s)                                           # /0
    s = re.sub(r"before0\(\s*", 'look(sx[:m.start()], ', s)                                 # before0(s)
    s = re.sub(r"after0\(\s*", 'look(sx[m.end():], ', s)                                    # after0(s)
    s = re.sub(r"textarea0\(\s*", 'look(sx, ', s)                                           # textarea0(s)
    s = re.sub(r"before0_chk1\(\s*", 'look_chk1(dDA, sx[:m.start()], 0, ', s)               # before0_chk1(s)
    s = re.sub(r"after0_chk1\(\s*", 'look_chk1(dDA, sx[m.end():], m.end(), ', s)            # after0_chk1(s)
    s = re.sub(r"textarea0_chk1\(\s*", 'look_chk1(dDA, sx, 0, ', s)                         # textarea0_chk1(s)
    s = re.sub(r"isEndOfNG\(\s*\)", 'isEndOfNG(dDA, s[m.end():], m.end())', s)              # isEndOfNG(s)
    s = re.sub(r"isNextNotCOD\(\s*\)", 'isNextNotCOD(dDA, s[m.end():], m.end())', s)        # isNextNotCOD(s)
    s = re.sub(r"isNextVerb\(\s*\)", 'isNextVerb(dDA, s[m.end():], m.end())', s)            # isNextVerb(s)
    s = re.sub(r"\bspell *[(]", '_oDict.isValid(', s)
    s = re.sub(r"[\\](\d+)", 'm.group(\\1)', s)
    return s


def py2js (sCode):
    "convert Python code to JavaScript code"
    # Python 2.x unicode strings
    sCode = re.sub('\\b[ur]"', '"', sCode)
    sCode = re.sub("\\b[ur]'", "'", sCode)
    # operators
    sCode = sCode.replace(" and ", " && ")
    sCode = sCode.replace(" or ", " || ")
    sCode = re.sub("\\bnot\\b", "!", sCode)
    sCode = re.sub("(.+) if (.+) else (.+)", "(\\2) ? \\1 : \\3", sCode)
    # boolean
    sCode = sCode.replace("False", "false")
    sCode = sCode.replace("True", "true")
    sCode = sCode.replace("bool", "Boolean")
    # methods
    sCode = sCode.replace(".__len__()", ".length")
    sCode = sCode.replace(".endswith", ".endsWith")
    sCode = sCode.replace(".find", ".indexOf")
    sCode = sCode.replace(".startswith", ".startsWith")
    sCode = sCode.replace(".lower", ".toLowerCase")
    sCode = sCode.replace(".upper", ".toUpperCase")
    sCode = sCode.replace(".isdigit", "._isDigit")
    sCode = sCode.replace(".isupper", "._isUpperCase")
    sCode = sCode.replace(".islower", "._isLowerCase")
    sCode = sCode.replace(".istitle", "._isTitle")
    sCode = sCode.replace(".capitalize", "._toCapitalize")
    sCode = sCode.replace(".strip", "._trim")
    sCode = sCode.replace(".lstrip", "._trimLeft")
    sCode = sCode.replace(".rstrip", "._trimRight")
    sCode = sCode.replace('.replace("."', ".replace(/\./g")
    sCode = sCode.replace('.replace("..."', ".replace(/\.\.\./g")
    sCode = re.sub('.replace\("([^"]+)" ?,', ".replace(/\\1/g,", sCode)
    # regex
    sCode = re.sub('re.search\("([^"]+)", *(m.group\(\\d\))\)', "(\\2.search(/\\1/) >= 0)", sCode)
    sCode = re.sub(".search\\(/\\(\\?i\\)([^/]+)/\\) >= 0\\)", ".search(/\\1/i) >= 0)", sCode)
    sCode = re.sub('(look\\(sx?[][.a-z:()]*), "\\(\\?i\\)([^"]+)"', "\\1, /\\2/i", sCode)
    sCode = re.sub('(look\\(sx?[][.a-z:()]*), "([^"]+)"', "\\1, /\\2/", sCode)
    sCode = re.sub('(look_chk1\\(dDA, sx?[][.a-z:()]*, [0-9a-z.()]+), "\\(\\?i\\)([^"]+)"', "\\1, /\\2/i", sCode)
    sCode = re.sub('(look_chk1\\(dDA, sx?[][.a-z:()]*, [0-9a-z.()]+), "([^"]+)"', "\\1, /\\2/i", sCode)
    sCode = sCode.replace("(?<!-)", "")  # todo
    # slices
    sCode = sCode.replace("[:m.start()]", ".slice(0,m.index)")
    sCode = sCode.replace("[m.end():]", ".slice(m.end[0])")
    sCode = sCode.replace("[m.start():m.end()]", ".slice(m.index, m.end[0])")
    sCode = re.sub("\\[(-?\\d+):(-?\\d+)\\]", ".slice(\\1,\\2)", sCode)
    sCode = re.sub("\\[(-?\\d+):\\]", ".slice(\\1)", sCode)
    sCode = re.sub("\\[:(-?\\d+)\\]", ".slice(0,\\1)", sCode)
    # regex matches
    sCode = sCode.replace(".end()", ".end[0]")
    sCode = sCode.replace(".start()", ".index")
    sCode = sCode.replace("m.group()", "m[0]")
    sCode = re.sub("\\.start\\((\\d+)\\)", ".start[\\1]", sCode)
    sCode = re.sub("m\\.group\\((\\d+)\\)", "m[\\1]", sCode)
    # tuples -> lists
    sCode = re.sub("\((m\.start\[\\d+\], m\[\\d+\])\)", "[\\1]", sCode)
    # regex
    sCode = sCode.replace("\w[\w-]+", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ][a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ-]+")
    sCode = sCode.replace(r"/\w/", "/[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ]/")
    sCode = sCode.replace(r"[\w-]", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ-]")
    sCode = sCode.replace(r"[\w,]", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ,]")
    return sCode


def uppercase (s, sLang):
    "(flag i is not enough): converts regex to uppercase regex: 'foo' becomes '[Ff][Oo][Oo]', but 'Bar' becomes 'B[Aa][Rr]'."
    sUp = ""
    nState = 0
    for i in range(0, len(s)):
        c = s[i]
        if c == "[":
            nState = 1
        if nState == 1 and c == "]":
            nState = 0
        if c == "<" and i > 3 and s[i-3:i] == "(?P":
            nState = 2
        if nState == 2 and c == ">":
            nState = 0
        if c == "?" and i > 0 and s[i-1:i] == "(" and s[i+1:i+2] != ":":
            nState = 5
        if nState == 5 and c == ")":
            nState = 0
        if c.isalpha() and c.islower() and nState == 0:
            if c == "i" and (sLang == "tr" or sLang == "az"):
                sUp += "[İ" + c + "]"
            else:
                sUp += "[" + c.upper() + c + "]"
        elif c.isalpha() and c.islower() and nState == 1 and s[i+1:i+2] != "-":
            if s[i-1:i] == "-" and s[i-2:i-1].islower():  # [a-z] -> [a-zA-Z]
                sUp += c + s[i-2:i-1].upper() + "-" + c.upper()
            elif c == "i" and (sLang == "tr" or sLang == "az"):
                sUp += "İ" + c
            else:
                sUp += c.upper() + c
        else:
            sUp += c
        if c == "\\":
            nState = 4
        elif nState == 4:
            nState = 0
    return sUp


def countGroupInRegex (sRegex):
    try:
        return re.compile(sRegex).groups
    except:
        traceback.print_exc()
        print(sRegex)
    return 0


def createRule (s, nIdLine, sLang, bParagraph, dOptPriority):
    "returns rule as list [option name, regex, bCaseInsensitive, identifier, list of actions]"
    global dJSREGEXES
    global nRULEWITHOUTNAME

    #### OPTIONS
    sLineId = str(nIdLine) + ("p" if bParagraph else "s")
    sRuleId = sLineId
    sOption = False         # False or [a-z0-9]+ name
    nPriority = 4           # Default is 4, value must be between 0 and 9
    tGroups = None          # code for groups positioning (only useful for JavaScript)
    cCaseMode = 'i'         # i: case insensitive,  s: case sensitive,  u: uppercasing allowed
    cWordLimitLeft = '['    # [: word limit, <: no specific limit
    cWordLimitRight = ']'   # ]: word limit, >: no specific limit
    m = re.match("^__(?P<borders_and_case>[[<]\\w[]>])(?P<option>/[a-zA-Z0-9]+|)(?P<ruleid>\\(\\w+\\)|)(?P<priority>![0-9]|)__ *", s)
    if m:
        cWordLimitLeft = m.group('borders_and_case')[0]
        cCaseMode = m.group('borders_and_case')[1]
        cWordLimitRight = m.group('borders_and_case')[2]
        sOption = m.group('option')[1:]  if m.group('option')  else False
        if m.group('ruleid'):
            sRuleId =  m.group('ruleid')[1:-1]
            if sRuleId in aRULESET:
                print("# Error. Several rules have the same id: " + sRuleId)
                exit()
            aRULESET.add(sRuleId)
        else:
            nRULEWITHOUTNAME += 1
        nPriority = dOptPriority.get(sOption, 4)
        if m.group('priority'):
            nPriority = int(m.group('priority')[1:])
        s = s[m.end(0):]
    else:
        print("# Warning. No option defined at line: " + sLineId)

    #### REGEX TRIGGER
    i = s.find(" <<-")
    if i == -1:
        print("# Error: no condition at line " + sLineId)
        return None
    sRegex = s[:i].strip()
    s = s[i+4:]
    
    # JS groups positioning codes
    m = re.search("@@\\S+", sRegex)
    if m:
        tGroups = groupsPositioningCodeToList(sRegex[m.start()+2:])
        sRegex = sRegex[:m.start()].strip()
    # JS regex
    m = re.search("<js>.+</js>i?", sRegex)
    if m:
        dJSREGEXES[sLineId] = m.group(0)
        sRegex = sRegex[:m.start()].strip()
    if "<js>" in sRegex or "</js>" in sRegex:
        print("# Error: JavaScript regex not delimited at line " + sLineId)
        return None

    # quotes ?
    if sRegex.startswith('"') and sRegex.endswith('"'):
        sRegex = sRegex[1:-1]

    ## definitions
    for sDef, sRepl in dDEF.items():
        sRegex = sRegex.replace(sDef, sRepl)

    ## count number of groups (must be done before modifying the regex)
    nGroup = countGroupInRegex(sRegex)
    if nGroup > 0:
        if not tGroups:
            print("# Warning: groups positioning code for JavaScript should be defined at line " + sLineId)
        else:
            if nGroup != len(tGroups):
                print("# Error: groups positioning code irrelevant at line " + sLineId)

    ## word limit
    if cWordLimitLeft == '[' and not sRegex.startswith(("^", '’', "'", ",")):
        sRegex = sWORDLIMITLEFT + sRegex
    if cWordLimitRight == ']' and not sRegex.endswith(("$", '’', "'", ",")):
        sRegex = sRegex + sWORDLIMITRIGHT

    ## casing mode
    if cCaseMode == "i":
        bCaseInsensitive = True
        if not sRegex.startswith("(?i)"):
            sRegex = "(?i)" + sRegex
    elif cCaseMode == "s":
        bCaseInsensitive = False
        sRegex = sRegex.replace("(?i)", "")
    elif cCaseMode == "u":
        bCaseInsensitive = False
        sRegex = sRegex.replace("(?i)", "")
        sRegex = uppercase(sRegex, sLang)
    else:
        print("# Unknown case mode [" + cCaseMode + "] at line " + sLineId)

    ## check regex
    try:
        z = re.compile(sRegex)
    except:
        print("# Regex error at line ", nIdLine)
        print(sRegex)
        traceback.print_exc()
        return None
    ## groups in non grouping parenthesis
    for x in re.finditer("\(\?:[^)]*\([[\w -]", sRegex):
        print("# Warning: groups inside non grouping parenthesis in regex at line " + sLineId)

    #### PARSE ACTIONS
    lActions = []
    nAction = 1
    for sAction in s.split(" <<- "):
        t = createAction(sRuleId + "_" + str(nAction), sAction, nGroup)
        nAction += 1
        if t:
            lActions.append(t)
    if not lActions:
        return None

    return [sOption, sRegex, bCaseInsensitive, sLineId, sRuleId, nPriority, lActions, tGroups]


def createAction (sIdAction, sAction, nGroup):
    "returns an action to perform as a tuple (condition, action type, action[, iGroup [, message, URL ]])"
    global lFUNCTIONS

    m = re.search(r"([-~=>])(\d*|)>>", sAction)
    if not m:
        print("# No action at line " + sIdAction)
        return None

    #### CONDITION
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = prepareFunction(sCondition)
        lFUNCTIONS.append(("c_"+sIdAction, sCondition))
        for x in re.finditer("[.](?:group|start|end)[(](\d+)[)]", sCondition):
            if int(x.group(1)) > nGroup:
                print("# Error in groups in condition at line " + sIdAction + " ("+str(nGroup)+" groups only)")
        if ".match" in sCondition:
            print("# Error. JS compatibility. Don't use .match() in condition, use .search()")
        sCondition = "c_"+sIdAction
    else:
        sCondition = None

    #### iGroup / positioning
    iGroup = int(m.group(2)) if m.group(2) else 0
    if iGroup > nGroup:
        print("# Selected group > group number in regex at line " + sIdAction)
    
    #### ACTION
    sAction = sAction[m.end():].strip()
    cAction = m.group(1)
    if cAction == "-":
        ## error
        iMsg = sAction.find(" # ")
        sMsg = sAction[iMsg+3:].strip()
        sAction = sAction[:iMsg].strip()
        sURL = ""
        mURL = re.search("[|] *(https?://.*)", sMsg)
        if mURL:
            sURL = mURL.group(1).strip()
            sMsg = sMsg[:mURL.start(0)].strip()
        if sMsg[0:1] == "=":
            sMsg = prepareFunction(sMsg[1:])
            lFUNCTIONS.append(("m_"+sIdAction, sMsg))
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
        sAction = sAction.replace("m.group(i[4])", "m.group("+str(iGroup)+")")
        for x in re.finditer("group[(](\d+)[)]", sAction):
            if int(x.group(1)) > nGroup:
                print("# Error in groups in replacement at line " + sIdAction + " ("+str(nGroup)+" groups only)")
    else:
        for x in re.finditer(r"\\(\d+)", sAction):
            if int(x.group(1)) > nGroup:
                print("# Error in groups in replacement at line " + sIdAction + " ("+str(nGroup)+" groups only)")
        if re.search("[.]\\w+[(]", sAction):
            print("# Error in action at line " + sIdAction + ":  This action looks like code. Line should begin with =")

    if cAction == "-":
        ## error detected --> suggestion
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("s_"+sIdAction, sAction[1:]))
            sAction = "=s_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print("# Error in action at line " + sIdAction + ":  the message is empty.")
        return [sCondition, cAction, sAction, iGroup, sMsg, sURL]
    elif cAction == "~":
        ## text processor
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("p_"+sIdAction, sAction[1:]))
            sAction = "=p_"+sIdAction
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sCondition, cAction, sAction, iGroup]
    elif cAction == "=":
        ## disambiguator
        if sAction[0:1] == "=":
            sAction = sAction[1:]
        if not sAction:
            print("# Error in action at line " + sIdAction + ":  This action is empty.")
        lFUNCTIONS.append(("d_"+sIdAction, sAction))
        sAction = "d_"+sIdAction
        return [sCondition, cAction, sAction]
    elif cAction == ">":
        ## no action, break loop if condition is False
        return [sCondition, cAction, ""]
    else:
        print("# Unknown action at line " + sIdAction)
        return None


def regex2js (sRegex):
    "converts Python regex to JS regex and returns JS regex and list of negative lookbefore assertions"
    #   Latin letters: http://unicode-table.com/fr/
    #   0-9  and  _
    #   A-Z
    #   a-z
    #   À-Ö     00C0-00D6   (upper case)
    #   Ø-ß     00D8-00DF   (upper case)
    #   à-ö     00E0-00F6   (lower case)
    #   ø-ÿ     00F8-00FF   (lower case)
    #   Ā-ʯ     0100-02AF   (mixed)
    #   -> a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯ
    bCaseInsensitive = False
    if "(?i)" in sRegex:
        sRegex = sRegex.replace("(?i)", "")
        bCaseInsensitive = True
    lNegLookBeforeRegex = []
    if sWORDLIMITLEFT in sRegex:
        sRegex = sRegex.replace(sWORDLIMITLEFT, "")
        lNegLookBeforeRegex = ["[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯ.,–-]$"]
    sRegex = sRegex.replace("[\\w", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯ")
    sRegex = sRegex.replace("\\w", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯ]")
    sRegex = sRegex.replace("[.]", r"\.")
    if not sRegex.startswith("<js>"):
        sRegex = sRegex.replace("/", r"\/")
    m = re.search(r"\(\?<!([^()]+)\)", sRegex)  # Negative lookbefore assertion should always be at the beginning of regex
    if m:
        lNegLookBeforeRegex.append(m.group(1)+"$")
        sRegex = sRegex.replace(m.group(0), "")
    if "(?<" in sRegex:
        print("# Warning. Lookbefore assertion not changed in:\n  ")
        print(sRegex)
    if sRegex.startswith("<js>"):
        sRegex = sRegex.replace('<js>', '/').replace('</js>i', '/ig').replace('</js>', '/g')
    else:
        sRegex = "/" + sRegex + "/g"
    if bCaseInsensitive and not sRegex.endswith("/ig"):
        sRegex = sRegex + "i"
    if not lNegLookBeforeRegex:
        lNegLookBeforeRegex = None
    return (sRegex, lNegLookBeforeRegex)


def pyRuleToJS (lRule):
    lRuleJS = copy.deepcopy(lRule)
    del lRule[-1] # tGroups positioning codes are useless for Python
    # error messages
    for aAction in lRuleJS[6]:
        if aAction[1] == "-":
            aAction[4] = aAction[4].replace("« ", "«&nbsp;").replace(" »", "&nbsp;»")
    # js regexes
    lRuleJS[1], lNegLookBehindRegex = regex2js( dJSREGEXES.get(lRuleJS[3], lRuleJS[1]) )
    lRuleJS.append(lNegLookBehindRegex)
    return lRuleJS


def writeRulesToJSArray (lRules):
    sArray = "[\n"
    for sOption, aRuleGroup in lRules:
        sArray += '  ["' + sOption + '", [\n'  if sOption  else  "  [false, [\n"
        for sRegex, bCaseInsensitive, sLineId, sRuleId, nPriority, lActions, aGroups, aNegLookBehindRegex in aRuleGroup:
            sArray += '    [' + sRegex + ", "
            sArray += "true, " if bCaseInsensitive  else "false, "
            sArray += '"' + sLineId + '", '
            sArray += '"' + sRuleId + '", '
            sArray += str(nPriority) + ", "
            sArray += json.dumps(lActions, ensure_ascii=False) + ", "
            sArray += json.dumps(aGroups, ensure_ascii=False) + ", "
            sArray += json.dumps(aNegLookBehindRegex, ensure_ascii=False) + "],\n"
        sArray += "  ]],\n"
    sArray += "]"
    return sArray


def groupsPositioningCodeToList (sGroupsPositioningCode):
    if not sGroupsPositioningCode:
        return None
    return [ int(sCode)  if sCode.isdigit() or (sCode[0:1] == "-" and sCode[1:].isdigit())  else sCode \
             for sCode in sGroupsPositioningCode.split(",") ]


def _calcRulesStats (lRules):
    d = {'=':0, '~': 0, '-': 0, '>': 0}
    for aRule in lRules:
        for aAction in aRule[6]:
            d[aAction[1]] = d[aAction[1]] + 1
    return (d, len(lRules))


def displayStats (lParagraphRules, lSentenceRules):
    print("  {:>18} {:>18} {:>18} {:>18}".format("DISAMBIGUATOR", "TEXT PROCESSOR", "GRAMMAR CHECKING", "REGEX"))
    d, nRule = _calcRulesStats(lParagraphRules)
    print("§ {:>10} actions {:>10} actions {:>10} actions  in {:>8} rules".format(d['='], d['~'], d['-'], nRule))
    d, nRule = _calcRulesStats(lSentenceRules)
    print("s {:>10} actions {:>10} actions {:>10} actions  in {:>8} rules".format(d['='], d['~'], d['-'], nRule))


def mergeRulesByOption (lRules):
    "returns a list of tuples [option, list of rules] keeping the rules order"
    lFinal = []
    lTemp = []
    sOption = None
    for aRule in lRules:
        if aRule[0] != sOption:
            if sOption != None:
                lFinal.append([sOption, lTemp])
            # new tuple
            sOption = aRule[0]
            lTemp = []
        lTemp.append(aRule[1:])
    lFinal.append([sOption, lTemp])
    return lFinal


def prepareOptions (lOptionLines):
    "returns a dictionary with data about options"
    sLang = ""
    lStructOpt = []
    lOpt = []
    dOptLabel = {}
    dOptPriority = {}
    for sLine in lOptionLines:
        sLine = sLine.strip()
        if sLine.startswith("OPTGROUP/"):
            m = re.match("OPTGROUP/([a-z0-9]+):(.+)$", sLine)
            lStructOpt.append( (m.group(1), list(map(str.split, m.group(2).split(",")))) )
        elif sLine.startswith("OPTSOFTWARE:"):
            lOpt = [ [s, {}]  for s in sLine[12:].strip().split() ]  # don’t use tuples (s, {}), because unknown to JS
        elif sLine.startswith("OPT/"):
            m = re.match("OPT/([a-z0-9]+):(.+)$", sLine)
            for i, sOpt in enumerate(m.group(2).split()):
                lOpt[i][1][m.group(1)] =  eval(sOpt)
        elif sLine.startswith("OPTPRIORITY/"):
            m = re.match("OPTPRIORITY/([a-z0-9]+): *([0-9])$", sLine)
            dOptPriority[m.group(1)] = int(m.group(2))
        elif sLine.startswith("OPTLANG/"):
            m = re.match("OPTLANG/([a-z][a-z](?:_[A-Z][A-Z]|)):(.+)$", sLine)
            sLang = m.group(1)[:2]
            dOptLabel[sLang] = { "__optiontitle__": m.group(2).strip() }
        elif sLine.startswith("OPTLABEL/"):
            m = re.match("OPTLABEL/([a-z0-9]+):(.+)$", sLine)
            dOptLabel[sLang][m.group(1)] = list(map(str.strip, m.group(2).split("|")))  if "|" in m.group(2)  else  [m.group(2).strip(), ""]
        else:
            print("# Error. Wrong option line in:\n  ")
            print(sLine)
    print("  options defined for: " + ", ".join([ t[0] for t in lOpt ]))
    dOptions = { "lStructOpt": lStructOpt, "dOptLabel": dOptLabel }
    dOptions.update({ "dOpt"+k: v  for k, v in lOpt })
    return dOptions, dOptPriority


def make (lRules, sLang, bJavaScript):
    "compile rules, returns a dictionary of values"
    # for clarity purpose, don’t create any file here

    # removing comments, zeroing empty lines, creating definitions, storing tests, merging rule lines
    print("  parsing rules...")
    global dDEF
    lLine = []
    lRuleLine = []
    lTest = []
    lOpt = []
    for i, sLine in enumerate(lRules, 1):
        if sLine.startswith('#END'):
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
        elif sLine.startswith(("OPTGROUP/", "OPTSOFTWARE:", "OPT/", "OPTLANG/", "OPTLABEL/", "OPTPRIORITY/")):
            lOpt.append(sLine)
        elif re.match("[  \t]*$", sLine):
            pass
        elif sLine.startswith(("    ", "\t")):
            lRuleLine[len(lRuleLine)-1][1] += " " + sLine.strip()
        else:
            lRuleLine.append([i, sLine.strip()])

    # generating options files
    print("  parsing options...")
    try:
        dOptions, dOptPriority = prepareOptions(lOpt)
    except:
        traceback.print_exc()
        exit()

    # tests
    print("  list tests...")
    sGCTests = "\n".join(lTest)
    sGCTestsJS = '{ "aData": ' + json.dumps(lTest, ensure_ascii=False) + " }\n"

    # processing
    print("  preparing rules...")
    bParagraph = True
    lParagraphRules = []
    lSentenceRules = []
    lParagraphRulesJS = []
    lSentenceRulesJS = []

    for nLine, sLine in lRuleLine:
        if sLine:
            if sLine == "[++]":
                bParagraph = False
            else:
                aRule = createRule(sLine, nLine, sLang, bParagraph, dOptPriority)
                if aRule:
                    if bParagraph:
                        lParagraphRules.append(aRule)
                        lParagraphRulesJS.append(pyRuleToJS(aRule))
                    else:
                        lSentenceRules.append(aRule)
                        lSentenceRulesJS.append(pyRuleToJS(aRule))

    # creating file with all functions callable by rules
    print("  creating callables...")
    sPyCallables = "# generated code, do not edit\n"
    sJSCallables = "// generated code, do not edit\nconst oEvalFunc = {\n"
    for sFuncName, sReturn in lFUNCTIONS:
        cType = sFuncName[0:1]
        if cType == "c": # condition
            sParams = "s, sx, m, dDA, sCountry, bCondMemo"
        elif cType == "m": # message
            sParams = "s, m"
        elif cType == "s": # suggestion
            sParams = "s, m"
        elif cType == "p": # preprocessor
            sParams = "s, m"
        elif cType == "d": # disambiguator
            sParams = "s, m, dDA"
        else:
            print("# Unknown function type in [" + sFuncName + "]")
            continue
        sPyCallables += "def {} ({}):\n".format(sFuncName, sParams)
        sPyCallables += "    return " + sReturn + "\n"
        sJSCallables += "    {}: function ({})".format(sFuncName, sParams) + " {\n"
        sJSCallables += "        return " + py2js(sReturn) + ";\n"
        sJSCallables += "    },\n"
    sJSCallables += "}\n"

    displayStats(lParagraphRules, lSentenceRules)

    print("Unnamed rules: " + str(nRULEWITHOUTNAME))

    d = { "callables": sPyCallables,
          "callablesJS": sJSCallables,
          "gctests": sGCTests,
          "gctestsJS": sGCTestsJS,
          "paragraph_rules": mergeRulesByOption(lParagraphRules),
          "sentence_rules": mergeRulesByOption(lSentenceRules),
          "paragraph_rules_JS": writeRulesToJSArray(mergeRulesByOption(lParagraphRulesJS)),
          "sentence_rules_JS": writeRulesToJSArray(mergeRulesByOption(lSentenceRulesJS)) }
    d.update(dOptions)

    return d
