"""
Convert Python code and regexes to JavaScript code
"""

import copy
import re
import json


def py2js (sCode):
    "convert Python code to JavaScript code"
    # Python strings
    sCode = sCode.replace(' ', ' ')
    sCode = sCode.replace('(r"', '("')
    sCode = sCode.replace("(r'", "('")
    sCode = sCode.replace(' r"', ' "')
    sCode = sCode.replace(" r'", " '")
    sCode = sCode.replace(',r"', ',"')
    sCode = sCode.replace(",r'", ",'")
    # operators
    sCode = sCode.replace(" and ", " && ")
    sCode = sCode.replace(" or ", " || ")
    sCode = re.sub("\\bnot\\b", "!", sCode)
    #sCode = re.sub("(.+) if (.+) else (.+)", "(\\2) ? \\1 : \\3", sCode)
    # boolean
    sCode = sCode.replace("False", "false")
    sCode = sCode.replace("True", "true")
    sCode = sCode.replace("None", "null")
    sCode = sCode.replace("bool", "Boolean")
    # methods
    sCode = sCode.replace("_oSpellChecker", "gc_engine.oSpellChecker")
    sCode = sCode.replace(".__len__()", ".length")
    sCode = sCode.replace(".endswith", ".endsWith")
    sCode = sCode.replace(".find", ".indexOf")
    sCode = sCode.replace(".startswith", ".startsWith")
    sCode = sCode.replace(".lower", ".toLowerCase")
    sCode = sCode.replace(".upper", ".toUpperCase")
    sCode = sCode.replace(".isdigit", ".gl_isDigit")
    sCode = sCode.replace(".isupper", ".gl_isUpperCase")
    sCode = sCode.replace(".islower", ".gl_isLowerCase")
    sCode = sCode.replace(".istitle", ".gl_isTitle")
    sCode = sCode.replace(".isalpha", ".gl_isAlpha")
    sCode = sCode.replace(".capitalize", ".gl_toCapitalize")
    sCode = sCode.replace(".strip", ".gl_trim")
    sCode = sCode.replace(".lstrip", ".gl_trimLeft")
    sCode = sCode.replace(".rstrip", ".gl_trimRight")
    sCode = sCode.replace('.replace("."', r".replace(/\./g")
    sCode = sCode.replace('.replace("..."', r".replace(/\.\.\./g")
    sCode = re.sub(r'.replace\("([^"]+)" ?,', ".replace(/\\1/g,", sCode)

    # regex
    sCode = re.sub('m\\.group\\((\\d+)\\) +in +(a[a-zA-Z]+)', "\\2.has(m[\\1])", sCode)
    sCode = re.sub('(lToken\\S+) +in +(a[a-zA-Z]+)', "\\2.has(\\1)", sCode)
    # slices
    sCode = sCode.replace("[:m.start()]", ".slice(0,m.index)")
    sCode = sCode.replace("[m.end():]", ".slice(m.end[0])")
    sCode = sCode.replace("[m.start():m.end()]", ".slice(m.index, m.end[0])")
    sCode = sCode.replace('[lToken[nLastToken]["nEnd"]:]', '.slice(lToken[nLastToken]["nEnd"])')
    sCode = sCode.replace('[:lToken[1+nTokenOffset]["nStart"]]', '.slice(0,lToken[1+nTokenOffset]["nStart"])')
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
    sCode = re.sub("\\((m\\.start\\[\\d+\\], m\\[\\d+\\])\\)", "[\\1]", sCode)
    # regex
    sCode = sCode.replace(r"[\\w", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆᴀ-ᶿ")
    sCode = sCode.replace(r"\\w", "[a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆᴀ-ᶿ]")
    return sCode


def regex2js (sRegex, sWORDLIMITLEFT):
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


def pyRuleToJS (lRule, dJSREGEXES, sWORDLIMITLEFT):
    "modify Python rules -> JS rules"
    lRuleJS = copy.deepcopy(lRule)
    # graph rules
    if lRuleJS[0] == "@@@@":
        return lRuleJS
    del lRule[-1] # tGroups positioning codes are useless for Python
    # error messages
    for aAction in lRuleJS[6]:
        if aAction[1] == "-":
            aAction[2] = aAction[2].replace(" ", " ") # nbsp --> nnbsp
            aAction[4] = aAction[4].replace("« ", "« ").replace(" »", " »").replace(" :", " :").replace(" :", " :")
    # js regexes
    lRuleJS[1], lNegLookBehindRegex = regex2js(dJSREGEXES.get(lRuleJS[3], lRuleJS[1]), sWORDLIMITLEFT)
    lRuleJS.append(lNegLookBehindRegex)
    return lRuleJS


def writeRulesToJSArray (lRules):
    "create rules as a string of arrays (to be bundled in a JSON string)"
    sArray = "[\n"
    for sOption, aRuleGroup in lRules:
        sArray += f'  ["{sOption}", [\n'
        if sOption != "@@@@":
            for sRegex, bCaseInsensitive, sLineId, sRuleId, nPriority, lActions, aGroups, aNegLookBehindRegex in aRuleGroup:
                sCaseSensitive = "true" if bCaseInsensitive  else "false"
                sActions = json.dumps(lActions, ensure_ascii=False)
                sGroups = json.dumps(aGroups, ensure_ascii=False)
                sNLBRegex = json.dumps(aNegLookBehindRegex, ensure_ascii=False)
                sArray += f'    [{sRegex}, {sCaseSensitive}, "{sLineId}", "{sRuleId}", {nPriority}, {sActions}, {sGroups}, {sNLBRegex}],\n'
        else:
            for aRule in aRuleGroup:
                sArray += f'    {aRule},\n'
        sArray += "  ]],\n"
    sArray += "]"
    return sArray


def groupsPositioningCodeToList (sGroupsPositioningCode):
    "convert <sGroupsPositioningCode> to a list of codes (numbers or strings)"
    if not sGroupsPositioningCode:
        return None
    return [ int(sCode)  if sCode.isdigit() or (sCode[0:1] == "-" and sCode[1:].isdigit())  else sCode \
             for sCode in sGroupsPositioningCode.split(",") ]


def pyActionsToString (dActions):
    "returns dictionary as string (nbsp -> nnbsp, True -> true, etc.)"
    for _, aValue in dActions.items():
        if aValue[3] == "-":
            aValue[4] = aValue[4].replace(" ", " ") # nbsp --> nnbsp
            aValue[11] = aValue[11].replace("« ", "« ").replace(" »", " »").replace(" :", " :").replace(" :", " :")
    return str(dActions).replace("True", "true").replace("False", "false")
