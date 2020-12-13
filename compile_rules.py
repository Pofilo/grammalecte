"""
Grammalecte: compile rules
"""

import re
import os
import traceback
import json
import colorsys
import time
import hashlib

import compile_rules_js_convert as jsconv
import compile_rules_graph as crg


dDEFINITIONS = {}
dDECLENSIONS = {}
lFUNCTIONS = []

aRULESET = set()     # set of rule-ids to check if there is several rules with the same id

dJSREGEXES = {}

sWORDLIMITLEFT  = r"(?<![\w.,–-])"   # r"(?<![-.,—])\b"  seems slower
sWORDLIMITRIGHT = r"(?![\w–-])"      # r"\b(?!-—)"       seems slower


def convertRGBToInteger (r, g, b):
    "rbg (int, int, int) -> int"
    return (r & 255) << 16 | (g & 255) << 8 | (b & 255)


def convertHSLToRBG (h, s, l):
    "hsl (int, int, int) -> [int, int, int]"
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return [round(r*255), round(g*255), round(b*255)]


def createColors (dColor):
    "dictionary of colors {color_name: [h, s, l]} -> returns dictionary of colors as dictionaries of color types"
    dColorType = {
        "aHSL": {},     # dictionary of colors as HSL list
        "sCSS": {},     # dictionary of colors as strings for HTML/CSS (example: hsl(0, 50%, 50%))
        "aRGB": {},     # dictionary of colors as RGB list
        "nInt": {}      # dictionary of colors as integer values (for Writer)
    }
    for sKey, aHSL in dColor.items():
        dColorType["aHSL"][sKey] = aHSL
        dColorType["sCSS"][sKey] = "hsl({}, {}%, {}%)".format(*aHSL)
        dColorType["aRGB"][sKey] = convertHSLToRBG(*aHSL)
        dColorType["nInt"][sKey] = convertRGBToInteger(*dColorType["aRGB"][sKey])
    return dColorType


def prepareFunction (s):
    "convert simple rule syntax to a string of Python code"
    s = s.replace("__also__", "bCondMemo")
    s = s.replace("__else__", "not bCondMemo")
    s = s.replace("sContext", "_sAppContext")
    s = re.sub(r"\bstart\(\)", 'before("^ *$|, *$")', s)
    s = re.sub(r"\brealstart\(\)", 'before("^ *$")', s)
    s = re.sub(r"\bstart0\(\)", 'before0("^ *$|, *$")', s)
    s = re.sub(r"\brealstart0\(\)", 'before0("^ *$")', s)
    s = re.sub(r"\bend\(\)", 'after("^ *$|^,")', s)
    s = re.sub(r"\brealend\(\)", 'after("^ *$")', s)
    s = re.sub(r"\bend0\(\)", 'after0("^ *$|^,")', s)
    s = re.sub(r"\brealend0\(\)", 'after0("^ *$")', s)
    s = re.sub(r"\bselect[(][\\](\d+)", '\\1(dTokenPos, m.start(\\1), m.group(\\1)', s)
    s = re.sub(r"\bdefine[(][\\](\d+)", 'define(dTokenPos, m.start(\\1)', s)
    s = re.sub(r"\b(morph|info)[(][\\](\d+)", '\\1((m.start(\\2), m.group(\\2))', s)
    s = re.sub(r"\b(morph|info)[(]", '\\1(dTokenPos, ', s)
    s = re.sub(r"\b(sugg\w+|switch\w+)\(@", '\\1(m.group(i[4])', s)
    s = re.sub(r"\bword\(\s*1\b", 'nextword1(sSentence, m.end()', s)                                # word(1)
    s = re.sub(r"\bword\(\s*-1\b", 'prevword1(sSentence, m.start()', s)                             # word(-1)
    s = re.sub(r"\bword\(\s*(\d)", 'nextword(sSentence, m.end(), \\1', s)                           # word(n)
    s = re.sub(r"\bword\(\s*-(\d)", 'prevword(sSentence, m.start(), \\1', s)                        # word(-n)
    s = re.sub(r"\bbefore\(\s*", 'look(sSentence[:m.start()], ', s)                                 # before(sSentence)
    s = re.sub(r"\bafter\(\s*", 'look(sSentence[m.end():], ', s)                                    # after(sSentence)
    s = re.sub(r"\btextarea\(\s*", 'look(sSentence, ', s)                                           # textarea(sSentence)
    s = re.sub(r"/0", 'sSentence0[m.start():m.end()]', s)                                           # /0
    s = re.sub(r"\bbefore0\(\s*", 'look(sSentence0[:m.start()], ', s)                               # before0(sSentence)
    s = re.sub(r"\bafter0\(\s*", 'look(sSentence0[m.end():], ', s)                                  # after0(sSentence)
    s = re.sub(r"\btextarea0\(\s*", 'look(sSentence0, ', s)                                         # textarea0(sSentence)
    s = re.sub(r"\bspell *[(]", '_oSpellChecker.isValid(', s)
    s = re.sub(r"[\\](\d+)", 'm.group(\\1)', s)
    return s


def uppercase (sText, sLang):
    "(flag i is not enough): converts regex to uppercase regex: 'foo' becomes '[Ff][Oo][Oo]', but 'Bar' becomes 'B[Aa][Rr]'."
    sUp = ""
    nState = 0
    for i, c in enumerate(sText):
        if c == "[":
            nState = 1
        if nState == 1 and c == "]":
            nState = 0
        if c == "<" and i > 3 and sText[i-3:i] == "(?P":
            nState = 2
        if nState == 2 and c == ">":
            nState = 0
        if c == "?" and i > 0 and sText[i-1:i] == "(" and sText[i+1:i+2] != ":":
            nState = 5
        if nState == 5 and c == ")":
            nState = 0
        if c.isalpha() and c.islower() and nState == 0:
            if c == "i" and sLang in ("tr", "az"):
                sUp += "[İ" + c + "]"
            else:
                sUp += "[" + c.upper() + c + "]"
        elif c.isalpha() and c.islower() and nState == 1 and sText[i+1:i+2] != "-":
            if sText[i-1:i] == "-" and sText[i-2:i-1].islower():  # [a-z] -> [a-zA-Z]
                sUp += c + sText[i-2:i-1].upper() + "-" + c.upper()
            elif c == "i" and sLang in ("tr", "az"):
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
    "returns the number of groups in <sRegex>"
    try:
        return re.compile(sRegex).groups
    except re.error:
        traceback.print_exc()
        print(sRegex)
    return 0


def createRule (s, nLineId, sLang, bParagraph, dOptPriority):
    "returns rule as list [option name, regex, bCaseInsensitive, identifier, list of actions]"
    global dJSREGEXES

    sLineId = f"#{nLineId}" + ("p" if bParagraph else "s")
    sRuleId = sLineId

    #### GRAPH CALL
    if s.startswith("@@@@"):
        if bParagraph:
            print("Error. Graph call can be made only after the first pass (sentence by sentence)")
            exit()
        return ["@@@@", s[4:], sLineId]

    #### OPTIONS
    sOption = ""            # empty string or [a-z0-9]+ name
    nPriority = 4           # Default is 4, value must be between 0 and 9
    tGroups = None          # code for groups positioning (only useful for JavaScript)
    cCaseMode = 'i'         # i: case insensitive,  s: case sensitive,  u: uppercasing allowed
    cWordLimitLeft = '['    # [: word limit, <: no specific limit
    cWordLimitRight = ']'   # ]: word limit, >: no specific limit
    m = re.match("^__(?P<borders_and_case>[\\[<]\\w[\\]>])(?P<option>/[a-zA-Z0-9]+|)(?P<ruleid>\\(\\w+\\))(?P<priority>![0-9]|)__ *", s)
    if m:
        cWordLimitLeft = m.group('borders_and_case')[0]
        cCaseMode = m.group('borders_and_case')[1]
        cWordLimitRight = m.group('borders_and_case')[2]
        sOption = m.group('option')[1:]  if m.group('option')  else ""
        sRuleId =  m.group('ruleid')[1:-1]
        if sRuleId in aRULESET:
            print(f"# Error. Several rules have the same id: {sRuleId}")
            exit()
        aRULESET.add(sRuleId)
        nPriority = dOptPriority.get(sOption, 4)
        if m.group('priority'):
            nPriority = int(m.group('priority')[1:])
        s = s[m.end(0):]
    else:
        print(f"# Warning. Rule wrongly shaped at line: {sLineId}")
        exit()

    #### REGEX TRIGGER
    i = s.find(" <<-")
    if i == -1:
        print(f"# Error: no condition at line {sLineId}")
        return None
    sRegex = s[:i].strip()
    s = s[i+4:]

    # JS groups positioning codes
    m = re.search("@@\\S+", sRegex)
    if m:
        tGroups = jsconv.groupsPositioningCodeToList(sRegex[m.start()+2:])
        sRegex = sRegex[:m.start()].strip()
    # JS regex
    m = re.search("<js>.+</js>i?", sRegex)
    if m:
        dJSREGEXES[sLineId] = m.group(0)
        sRegex = sRegex[:m.start()].strip()
    if "<js>" in sRegex or "</js>" in sRegex:
        print(f"# Error: JavaScript regex not delimited at line {sLineId}")
        return None

    # quotes ?
    if sRegex.startswith('"') and sRegex.endswith('"'):
        sRegex = sRegex[1:-1]

    ## definitions
    for sDef, sRepl in dDEFINITIONS.items():
        sRegex = sRegex.replace(sDef, sRepl)

    ## count number of groups (must be done before modifying the regex)
    nGroup = countGroupInRegex(sRegex)
    if nGroup > 0:
        if not tGroups:
            print(f"# Warning: groups positioning code for JavaScript should be defined at line {sLineId}")
        else:
            if nGroup != len(tGroups):
                print(f"# Error: groups positioning code irrelevant at line {sLineId}")

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
        print(f"# Unknown case mode [{cCaseMode}] at line {sLineId}")

    ## check regex
    try:
        re.compile(sRegex)
    except re.error:
        print(f"# Regex error at line {sLineId}")
        print(sRegex)
        return None
    ## groups in non grouping parenthesis
    for _ in re.finditer(r"\(\?:[^)]*\([\[\w -]", sRegex):
        print(f"# Warning: groups inside non grouping parenthesis in regex at line {sLineId}")

    #### PARSE ACTIONS
    lActions = []
    nAction = 1
    for sAction in s.split(" <<- "):
        t = createAction(sLineId, sRuleId + "_" + str(nAction), sAction, nGroup)
        nAction += 1
        if t:
            lActions.append(t)
    if not lActions:
        return None

    return [sOption, sRegex, bCaseInsensitive, sLineId, sRuleId, nPriority, lActions, tGroups]


def checkReferenceNumbers (sText, sActionId, nToken):
    "check if token references in <sText> greater than <nToken> (debugging)"
    for x in re.finditer(r"\\(\d+)", sText):
        if int(x.group(1)) > nToken:
            print(f"# Error in token index at line {sLineId} / {sActionId} ({nToken} tokens only)")
            print(sText)


def checkIfThereIsCode (sText, sLineId, sActionId):
    "check if there is code in <sText> (debugging)"
    if re.search(r"[.]\w+[(]|sugg\w+[(]|\(\\[0-9]|\[(?:[0-9]:|:)", sText):
        print(f"# Warning at line {sLineId} / {sActionId}:  This message looks like code. Line should probably begin with =")
        print(sText)


def createAction (sLineId, sActionId, sAction, nGroup):
    "returns an action to perform as a tuple (condition, action type, action[, iGroup [, message, URL ]])"
    m = re.search(r"([-~=>])(\d*|)>>", sAction)
    if not m:
        print(f"# No action at line {sLineId} / {sActionId}")
        return None

    #### CONDITION
    sCondition = sAction[:m.start()].strip()
    if sCondition:
        sCondition = prepareFunction(sCondition)
        lFUNCTIONS.append(("_c_"+sActionId, sCondition))
        checkReferenceNumbers(sCondition, sActionId, nGroup)
        if ".match" in sCondition:
            print(f"# Error at line {sLineId} / {sActionId}. JS compatibility. Don't use .match() in condition, use .search()")
        sCondition = "_c_"+sActionId
    else:
        sCondition = None

    #### iGroup / positioning
    iGroup = int(m.group(2)) if m.group(2) else 0
    if iGroup > nGroup:
        print(f"# Error. Selected group > group number in regex at line {sLineId} / {sActionId}")

    #### ACTION
    sAction = sAction[m.end():].strip()
    cAction = m.group(1)
    if cAction == "-":
        ## error
        iMsg = sAction.find(" && ")
        if iMsg == -1:
            sMsg = "# Error. Error message not found."
            sURL = ""
            print(f"# No message. Id: {sLineId} / {sActionId}")
        else:
            sMsg = sAction[iMsg+4:].strip()
            sAction = sAction[:iMsg].strip()
            sURL = ""
            mURL = re.search("[|] *(https?://.*)", sMsg)
            if mURL:
                sURL = mURL.group(1).strip()
                sMsg = sMsg[:mURL.start(0)].strip()
            checkReferenceNumbers(sMsg, sActionId, nGroup)
            if sMsg[0:1] == "=":
                sMsg = prepareFunction(sMsg[1:])
                lFUNCTIONS.append(("_m_"+sActionId, sMsg))
                sMsg = "=_m_"+sActionId
            else:
                checkIfThereIsCode(sMsg, sLineId, sActionId)

    checkReferenceNumbers(sAction, sActionId, nGroup)
    if sAction[0:1] == "=" or cAction == "=":
        sAction = prepareFunction(sAction)
        sAction = sAction.replace("m.group(i[4])", "m.group("+str(iGroup)+")")
    else:
        checkIfThereIsCode(sAction, sLineId, sActionId)

    if cAction == ">":
        ## no action, break loop if condition is False
        return [sCondition, cAction, ""]

    if not sAction:
        print(f"# Error in action at line {sLineId} / {sActionId}:  This action is empty.")
        return None

    if cAction == "-":
        ## error detected --> suggestion
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("_s_"+sActionId, sAction[1:]))
            sAction = "=_s_"+sActionId
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        if not sMsg:
            print(f"# Error in action at line {sLineId} / {sActionId}:  the message is empty.")
        return [sCondition, cAction, sAction, iGroup, sMsg, sURL]
    if cAction == "~":
        ## text processor
        if sAction[0:1] == "=":
            lFUNCTIONS.append(("_p_"+sActionId, sAction[1:]))
            sAction = "=_p_"+sActionId
        elif sAction.startswith('"') and sAction.endswith('"'):
            sAction = sAction[1:-1]
        return [sCondition, cAction, sAction, iGroup]
    if cAction == "=":
        ## disambiguator
        if sAction[0:1] == "=":
            sAction = sAction[1:]
        lFUNCTIONS.append(("_d_"+sActionId, sAction))
        sAction = "_d_"+sActionId
        return [sCondition, cAction, sAction]
    print(f"# Unknown action at line {sLineId} / {sActionId}")
    return None


def _calcRulesStats (lRules):
    "count rules and actions"
    d = {'=':0, '~': 0, '-': 0, '>': 0}
    for aRule in lRules:
        if aRule[0] != "@@@@":
            for aAction in aRule[6]:
                d[aAction[1]] = d[aAction[1]] + 1
    return (d, len(lRules))


def displayStats (lParagraphRules, lSentenceRules):
    "display rules numbers"
    print("               {:>18} {:>18} {:>18} {:>18}".format("DISAMBIGUATOR", "TEXT PROCESSOR", "GRAMMAR CHECKING", "REGEX"))
    d, nRule = _calcRulesStats(lParagraphRules)
    print("    paragraph: {:>10} actions {:>10} actions {:>10} actions  in {:>8} rules".format(d['='], d['~'], d['-'], nRule))
    d, nRule = _calcRulesStats(lSentenceRules)
    print("    sentence:  {:>10} actions {:>10} actions {:>10} actions  in {:>8} rules".format(d['='], d['~'], d['-'], nRule))


def mergeRulesByOption (lRules):
    "returns a list of tuples [option, list of rules] keeping the rules order"
    lFinal = []
    lTemp = []
    sOption = None
    for aRule in lRules:
        if aRule[0] != sOption:
            if sOption is not None:
                lFinal.append([sOption, lTemp])
            # new tuple
            sOption = aRule[0]
            lTemp = []
        lTemp.append(aRule[1:])
    lFinal.append([sOption, lTemp])
    return lFinal


def createRulesAsString (lRules):
    "create rules as a string of arrays (to be bundled in a JSON string)"
    sArray = "[\n"
    for sOption, aRuleGroup in lRules:
        sArray += f'  ["{sOption}", [\n'
        for aRule in aRuleGroup:
            sArray += f'    {aRule},\n'
        sArray += "  ]],\n"
    sArray += "]"
    return sArray


def prepareOptions (lOptionLines):
    "returns a dictionary with data about options"
    sLang = ""
    sDefaultUILang = ""
    lStructOpt = []
    lOpt = []
    lOptColor = []
    dColor = {}
    dOptLabel = {}
    dOptPriority = {}
    for sLine in lOptionLines:
        sLine = sLine.strip()
        if sLine.startswith("OPTGROUP/"):
            m = re.match("OPTGROUP/([a-z0-9]+):(.+)$", sLine)
            lStructOpt.append( [m.group(1), list(map(str.split, m.group(2).split(",")))] )
        elif sLine.startswith("OPTSOFTWARE:"):
            lOpt = [ [s, {}]  for s in sLine[12:].strip().split() ]  # don’t use tuples (s, {}), because unknown to JS
        elif sLine.startswith("OPT/"):
            m = re.match("OPT/([a-z0-9]+):(.+)$", sLine)
            for i, sOpt in enumerate(m.group(2).split()):
                lOpt[i][1][m.group(1)] = sOpt in ("True", "true", "Yes", "yes")
        elif sLine.startswith("OPTCOLORTHEME:"):
            lOptColor = [ [s, {}]  for s in sLine[14:].strip().split() ]  # don’t use tuples (s, {}), because unknown to JS
        elif sLine.startswith("OPTCOLOR/"):
            m = re.match("OPTCOLOR/([a-z0-9]+):(.+)$", sLine)
            for i, sColor in enumerate(m.group(2).split()):
                lOptColor[i][1][m.group(1)] = sColor
        elif sLine.startswith("COLOR/"):
            m = re.match("COLOR/([a-zA-Z0-9_]+):(.+)$", sLine)
            dColor[m.group(1)] = [ int(s) for s in m.group(2).strip().split(",") ]
        elif sLine.startswith("OPTPRIORITY/"):
            m = re.match("OPTPRIORITY/([a-z0-9]+): *([0-9])$", sLine)
            dOptPriority[m.group(1)] = int(m.group(2))
        elif sLine.startswith("OPTLANG/"):
            m = re.match("OPTLANG/([a-z][a-z](?:_[A-Z][A-Z]|)):(.+)$", sLine)
            sLang = m.group(1)[:2]
            dOptLabel[sLang] = { "__optiontitle__": m.group(2).strip() }
        elif sLine.startswith("OPTDEFAULTUILANG:"):
            m = re.match("OPTDEFAULTUILANG: *([a-z][a-z](?:_[A-Z][A-Z]|))$", sLine)
            sDefaultUILang = m.group(1)[:2]
        elif sLine.startswith("OPTLABEL/"):
            m = re.match("OPTLABEL/([a-z0-9]+):(.+)$", sLine)
            dOptLabel[sLang][m.group(1)] = list(map(str.strip, m.group(2).split("|")))  if "|" in m.group(2)  else  [m.group(2).strip(), ""]
        else:
            print("# Error. Wrong option line in:\n  ")
            print(sLine)
    print("  options defined for: " + ", ".join([ t[0] for t in lOpt ]))
    dOptions = {
        "lStructOpt": lStructOpt, "dOptLabel": dOptLabel, "sDefaultUILang": sDefaultUILang, \
        "dColorType": createColors(dColor), "dOptColor": { s: d  for s, d in lOptColor }
    }
    dOptions.update({ "dOpt"+k: v  for k, v in lOpt })
    return dOptions, dOptPriority


def printBookmark (nLevel, sComment, nLine):
    "print bookmark within the rules file"
    print("  {:>6}:  {}".format(nLine, "  " * nLevel + sComment))


def make (spLang, sLang, bUseCache=None):
    "compile rules, returns a dictionary of values"
    # for clarity purpose, don’t create any file here (except cache)

    dCacheVars = None

    if os.path.isfile("_build/data_cache.json"):
        print("> data cache found")
        sJSON = open("_build/data_cache.json", "r", encoding="utf-8").read()
        dCacheVars = json.loads(sJSON)
        sBuildDate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(dCacheVars.get("fBuildTime", 0)))
        if bUseCache:
            print("> use cache (no rebuild asked)")
            print("  build made at: " + sBuildDate)
            return dCacheVars

    print("> read rules file...")
    try:
        sFileContent = open(spLang + "/rules.grx", 'r', encoding="utf-8").read()
    except OSError:
        print(f"# Error. Rules file in project <{sLang}> not found.")
        exit()

    # calculate hash of loaded file
    xHasher = hashlib.new("sha3_512")
    xHasher.update(sFileContent.encode("utf-8"))
    sFileHash = xHasher.hexdigest()

    if dCacheVars and bUseCache != False and sFileHash == dCacheVars.get("sFileHash", ""):
        # if <bUseCache> is None or True, we can use the cache
        print("> cache hash identical to file hash, use cache")
        print("  build made at: " + sBuildDate)
        return dCacheVars

    # removing comments, zeroing empty lines, creating definitions, storing tests, merging rule lines
    print("  parsing rules...")
    fBuildTime = time.time()
    lRuleLine = []
    lTest = []
    lOpt = []
    bGraph = False
    lGraphRule = []

    for i, sLine in enumerate(sFileContent.split("\n"), 1):
        if sLine.startswith('#END'):
            # arbitrary end
            printBookmark(0, "BREAK BY #END", i)
            break
        elif sLine.startswith(("#", "    ##")):
            # comment
            pass
        elif sLine.startswith("DEF:"):
            # definition
            m = re.match("DEF: +([a-zA-Z_][a-zA-Z_0-9]*) +(.+)$", sLine.strip())
            if m:
                dDEFINITIONS["{"+m.group(1)+"}"] = m.group(2)
            else:
                print("# Error in definition: ", end="")
                print(sLine.strip())
        elif sLine.startswith("DECL:"):
            # declensions
            m = re.match(r"DECL: +(\+\w+) (.+)$", sLine.strip())
            if m:
                dDECLENSIONS[m.group(1)] = m.group(2).strip().split()
            else:
                print("Error in declension list: ", end="")
                print(sLine.strip())
        elif sLine.startswith("TEST:"):
            # test
            lTest.append("{:<8}".format(i) + "  " + sLine[5:].strip())
        elif sLine.startswith("TODO:"):
            # todo
            pass
        elif sLine.startswith(("OPTGROUP/", "OPTSOFTWARE:", "OPT/", \
                                "COLOR/", "OPTCOLORTHEME:", "OPTCOLOR/", \
                                "OPTLANG/", "OPTDEFAULTUILANG:", \
                                "OPTLABEL/", "OPTPRIORITY/")):
            # options
            lOpt.append(sLine)
        elif sLine.startswith("!!"):
            # bookmark
            m = re.match("!!+", sLine)
            nExMk = len(m.group(0))
            if sLine[nExMk:].strip():
                printBookmark(nExMk-2, sLine[nExMk:-3].strip(), i)
        # Graph rules
        elif sLine.startswith("@@@@GRAPH:"):
            # rules graph call
            m = re.match(r"@@@@GRAPH: *(\w+)", sLine.strip())
            if m:
                printBookmark(0, "GRAPH: " + m.group(1), i)
                lRuleLine.append([i, "@@@@"+m.group(1)])
                lGraphRule.append([i, sLine])
                bGraph = True
            else:
                print("Graph error at line", i)
        elif sLine.startswith(("@@@@END_GRAPH", "@@@@ENDGRAPH")):
            #lGraphRule.append([i, sLine])
            printBookmark(0, "ENDGRAPH", i)
            bGraph = False
        elif re.match("@@@@ *$", sLine):
            pass
        elif bGraph:
            lGraphRule.append([i, sLine])
        # Regex rules
        elif re.match("[  \t]*$", sLine):
            # empty line
            pass
        elif sLine.startswith("    "):
            # rule (continuation)
            lRuleLine[-1][1] += " " + sLine.strip()
        else:
            # new rule
            lRuleLine.append([i, sLine.strip()])

    # generating options files
    print("  parsing options...")
    dOptions, dOptPriority = prepareOptions(lOpt)

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
                        lParagraphRulesJS.append(jsconv.pyRuleToJS(aRule, dJSREGEXES, sWORDLIMITLEFT))
                    else:
                        lSentenceRules.append(aRule)
                        lSentenceRulesJS.append(jsconv.pyRuleToJS(aRule, dJSREGEXES, sWORDLIMITLEFT))

    # creating file with all functions callable by rules
    print("  creating callables for regex rules...")
    sPyCallables = ""
    sJSCallables = ""
    for sFuncName, sReturn in lFUNCTIONS:
        if sFuncName.startswith("_c_"): # condition
            sParams = "sSentence, sSentence0, m, dTokenPos, sCountry, bCondMemo"
        elif sFuncName.startswith("_m_"): # message
            sParams = "sSentence, m"
        elif sFuncName.startswith("_s_"): # suggestion
            sParams = "sSentence, m"
        elif sFuncName.startswith("_p_"): # preprocessor
            sParams = "sSentence, m"
        elif sFuncName.startswith("_d_"): # disambiguator
            sParams = "sSentence, m, dTokenPos"
        else:
            print(f"# Unknown function type in <{sFuncName}>")
            continue
        # Python
        sPyCallables += f"def {sFuncName} ({sParams}):\n"
        sPyCallables += f"    return {sReturn}\n"
        # JavaScript
        sJSCallables += f"    {sFuncName}: function ({sParams}) {{\n"
        sJSCallables += "        return " + jsconv.py2js(sReturn) + ";\n"
        sJSCallables += "    },\n"

    displayStats(lParagraphRules, lSentenceRules)

    dVars = {
        "fBuildTime": fBuildTime,
        "sFileHash": sFileHash,
        "callables": sPyCallables,
        "callablesJS": sJSCallables,
        "gctests": sGCTests,
        "gctestsJS": sGCTestsJS,
        "paragraph_rules": createRulesAsString(mergeRulesByOption(lParagraphRules)),
        "sentence_rules": createRulesAsString(mergeRulesByOption(lSentenceRules)),
        "paragraph_rules_JS": jsconv.writeRulesToJSArray(mergeRulesByOption(lParagraphRulesJS)),
        "sentence_rules_JS": jsconv.writeRulesToJSArray(mergeRulesByOption(lSentenceRulesJS))
    }
    dVars.update(dOptions)

    # compile graph rules
    dVars2 = crg.make(lGraphRule, sLang, dDEFINITIONS, dDECLENSIONS, dOptPriority)
    dVars.update(dVars2)

    with open("_build/data_cache.json", "w", encoding="utf-8") as hDst:
        hDst.write(json.dumps(dVars, ensure_ascii=False))
    return dVars
