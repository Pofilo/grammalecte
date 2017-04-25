#!python3
# -*- coding: UTF-8 -*-


dSimilarChars = {
    "a": "aàâáä",
    "à": "aàâáä",
    "â": "aàâáä",
    "á": "aàâáä",
    "ä": "aàâáä",
    "c": "cç",
    "ç": "cç",
    "e": "eéêèë",
    "é": "eéêèë",
    "ê": "eéêèë",
    "è": "eéêèë",
    "ë": "eéêèë",
    "i": "iîïíì",
    "î": "iîïíì",
    "ï": "iîïíì",
    "í": "iîïíì",
    "ì": "iîïíì",
    "o": "oôóòö",
    "ô": "oôóòö",
    "ó": "oôóòö",
    "ò": "oôóòö",
    "ö": "oôóòö",
    "u": "uûùüú",
    "û": "uûùüú",
    "ù": "uûùüú",
    "ü": "uûùüú",
    "ú": "uûùüú",
}

## No stemming

def noStemming (sFlex, sStem):
    return sStem

def rebuildWord (sFlex, cmd1, cmd2):
    if cmd1 == "_":
        return sFlex
    n, c = cmd1.split(":")
    s = s[:n] + c + s[n:]
    if cmd2 == "_":
        return s
    n, c = cmd2.split(":")
    return s[:n] + c + s[n:]

    
## Define affixes for stemming

# Note: 48 is the ASCII code for "0"


# Suffix only
def defineSuffixCode (sFlex, sStem):
    """ Returns a string defining how to get stem from flexion
            "n(sfx)"
        with n: a char with numeric meaning, "0" = 0, "1" = 1, ... ":" = 10, etc. (See ASCII table.) Says how many letters to strip from flexion.
             sfx [optional]: string to add on flexion
        Examples:
            "0": strips nothing, adds nothing
            "1er": strips 1 letter, adds "er"
            "2": strips 2 letters, adds nothing
    """
    if sFlex == sStem:
        return "0"
    jSfx = 0
    for i in range(min(len(sFlex), len(sStem))):
        if sFlex[i] != sStem[i]:
            break
        jSfx += 1
    return chr(len(sFlex)-jSfx+48) + sStem[jSfx:]  

def getStemFromSuffixCode (sFlex, sSfxCode):
    if sSfxCode == "0":
        return sFlex
    return sFlex[:-(ord(sSfxCode[0])-48)] + sSfxCode[1:]  if sSfxCode[0] != '0'  else sFlex + sSfxCode[1:]


# Prefix and suffix
def defineAffixCode (sFlex, sStem):
    """ Returns a string defining how to get stem from flexion. Examples:
            "0" if stem = flexion
            "stem" if no common substring
            "n(pfx)/m(sfx)"
        with n and m: chars with numeric meaning, "0" = 0, "1" = 1, ... ":" = 10, etc. (See ASCII table.) Says how many letters to strip from flexion.
            pfx [optional]: string to add before the flexion 
            sfx [optional]: string to add after the flexion
    """
    if sFlex == sStem:
        return "0"
    # is stem a substring of flexion?
    n = sFlex.find(sStem)
    if n >= 0:
        return "{}/{}".format(chr(n+48), chr(len(sFlex)-(len(sStem)+n)+48))
    # no, so we are looking for common substring
    sSubs = longestCommonSubstring(sFlex, sStem)
    if len(sSubs) > 1:
        iPos = sStem.find(sSubs)
        sPfx = sStem[:iPos]
        sSfx = sStem[iPos+len(sSubs):]
        n = sFlex.find(sSubs)
        m = len(sFlex) - (len(sSubs)+n)
        sAff = "{}/".format(chr(n+48))  if not sPfx  else "{}{}/".format(chr(n+48), sPfx)
        sAff += chr(m+48)  if not sSfx  else "{}{}".format(chr(m+48), sSfx)
        return sAff
    return sStem

def longestCommonSubstring (s1, s2):
    # http://en.wikipedia.org/wiki/Longest_common_substring_problem
    # http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Longest_common_substring
    M = [ [0]*(1+len(s2)) for i in range(1+len(s1)) ]
    longest, x_longest = 0, 0
    for x in range(1, 1+len(s1)):
        for y in range(1, 1+len(s2)):
            if s1[x-1] == s2[y-1]:
                M[x][y] = M[x-1][y-1] + 1
                if M[x][y] > longest:
                    longest = M[x][y]
                    x_longest = x
            else:
                M[x][y] = 0
    return s1[x_longest-longest : x_longest]

def getStemFromAffixCode (sFlex, sAffCode):
    if sAffCode == "0":
        return sFlex
    if '/' not in sAffCode:
        return "# error #"
    sPfxCode, sSfxCode = sAffCode.split('/')
    sFlex = sPfxCode[1:] + sFlex[(ord(sPfxCode[0])-48):] 
    return sFlex[:-(ord(sSfxCode[0])-48)] + sSfxCode[1:]  if sSfxCode[0] != '0'  else sFlex + sSfxCode[1:]

