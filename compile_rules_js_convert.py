# Convert Python code to JavaScript code

import copy
import re
import json


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
    sCode = sCode.replace(".isdigit", ".gl_isDigit")
    sCode = sCode.replace(".isupper", ".gl_isUpperCase")
    sCode = sCode.replace(".islower", ".gl_isLowerCase")
    sCode = sCode.replace(".istitle", ".gl_isTitle")
    sCode = sCode.replace(".capitalize", ".gl_toCapitalize")
    sCode = sCode.replace(".strip", ".gl_trim")
    sCode = sCode.replace(".lstrip", ".gl_trimLeft")
    sCode = sCode.replace(".rstrip", ".gl_trimRight")
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
    sCode = re.sub('m\\.group\\((\\d+)\\) +in +(a[a-zA-Z]+)', "\\2.has(m[\\1])", sCode)
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
    lRuleJS = copy.deepcopy(lRule)
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
