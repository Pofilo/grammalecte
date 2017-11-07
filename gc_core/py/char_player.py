# list of similar chars
# useful for suggestion mechanism

import re


_xTransChars = str.maketrans({
    'à': 'a',  'é': 'e',  'î': 'i',  'ô': 'o',  'û': 'u',  'ÿ': 'y',
    'â': 'a',  'è': 'e',  'ï': 'i',  'ö': 'o',  'ù': 'u',  'ŷ': 'y',
    'ä': 'a',  'ê': 'e',  'í': 'i',  'ó': 'o',  'ü': 'u',  'ý': 'y',
    'á': 'a',  'ë': 'e',  'ì': 'i',  'ò': 'o',  'ú': 'u',  'ỳ': 'y',
    'ā': 'a',  'ē': 'e',  'ī': 'i',  'ō': 'o',  'ū': 'u',  'ȳ': 'y',
    'ñ': 'n',
    'œ': 'oe',  'æ': 'ae', 
})

def cleanWord (sWord):
    "word simplication before calculating distance between words"
    return sWord.lower().translate(_xTransChars).replace("eau", "o").replace("au", "o")


def distanceDamerauLevenshtein (s1, s2):
    "distance of Damerau-Levenshtein between <s1> and <s2>"
    # https://fr.wikipedia.org/wiki/Distance_de_Damerau-Levenshtein
    d = {}
    nLen1 = len(s1)
    nLen2 = len(s2)
    for i in range(-1, nLen1+1):
        d[i, -1] = i + 1
    for j in range(-1, nLen2+1):
        d[-1, j] = j + 1
    for i in range(nLen1):
        for j in range(nLen2):
            nCost = 0  if s1[i] == s2[j]  else 1
            d[i, j] = min(
                d[i-1, j]   + 1,        # Deletion
                d[i,   j-1] + 1,        # Insertion
                d[i-1, j-1] + nCost,    # Substitution
            )
            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[i, j] = min(d[i, j], d[i-2, j-2] + nCost)     # Transposition
    return d[nLen1-1, nLen2-1]


def showDistance (s1, s2):
    s1b = cleanWord(s1);
    s2b = cleanWord(s2);
    print(f"Distance: {s1} / {s2} = {distanceDamerauLevenshtein(s1, s2)}")
    print(f"Distance: {s1b} / {s2b} = {distanceDamerauLevenshtein(s1b, s2b)}")


def distanceSift4 (s1, s2, nMaxOffset=5):
    "implementation of general Sift4."
    # https://siderite.blogspot.com/2014/11/super-fast-and-accurate-string-distance.html
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    nLen1, nLen2 = len(s1), len(s2)
    i1, i2 = 0, 0   # Cursors for each string
    nLargestCS = 0  # Largest common substring
    nLocalCS = 0    # Local common substring
    nTrans = 0      # Number of transpositions ('ab' vs 'ba')
    lOffset = []    # Offset pair array, for computing the transpositions
 
    while i1 < nLen1 and i2 < nLen2:
        if s1[i1] == s2[i2]:
            nLocalCS += 1
            # Check if current match is a transposition
            bTrans = False
            i = 0
            while i < len(lOffset):
                t = lOffset[i]
                if i1 <= t[0] or i2 <= t[1]:
                    bTrans = abs(i2-i1) >= abs(t[1] - t[0])
                    if bTrans:
                        nTrans += 1
                    elif not t[2]:
                        t[2] = True
                        nTrans += 1
                    break
                elif i1 > t[1] and i2 > t[0]:
                    del lOffset[i]
                else:
                    i += 1
            lOffset.append([i1, i2, bTrans])
        else:
            nLargestCS += nLocalCS
            nLocalCS = 0
            if i1 != i2:
                i1 = i2 = min(i1, i2)
            for i in range(nMaxOffset):
                if i1 + i >= nLen1 and i2 + i >= nLen2:
                    break
                elif i1 + i < nLen1 and s1[i1+i] == s2[i2]:
                    i1 += i - 1
                    i2 -= 1
                    break
                elif i2 + i < nLen2 and s1[i1] == s2[i2+i]:
                    i2 += i - 1
                    i1 -= 1
                    break
        i1 += 1
        i2 += 1
        if i1 >= nLen1 or i2 >= nLen2:
            nLargestCS += nLocalCS
            nLocalCS = 0
            i1 = i2 = min(i1, i2)
    nLargestCS += nLocalCS
    return round(max(nLen1, nLen2) - nLargestCS + nTrans)


# Method: Remove Useless Chars

_dVovels = {
    'a': '',  'e': '',  'i': '',  'o': '',  'u': '',  'y': '',
    'à': '',  'é': '',  'î': '',  'ô': '',  'û': '',  'ÿ': '',
    'â': '',  'è': '',  'ï': '',  'ö': '',  'ù': '',  'ŷ': '',
    'ä': '',  'ê': '',  'í': '',  'ó': '',  'ü': '',  'ý': '',
    'á': '',  'ë': '',  'ì': '',  'ò': '',  'ú': '',  'ỳ': '',
    'ā': '',  'ē': '',  'ī': '',  'ō': '',  'ū': '',  'ȳ': '',
    'h': '',  'œ': '',  'æ': ''
 }

_xTransVovels = str.maketrans(_dVovels)


aVovels = frozenset(_dVovels.keys())


def shrinkWord (sWord):
    "remove vovels and h"
    return sWord[0:1].replace("h", "") + sWord[1:].translate(_xTransVovels)


# Similar chars

d1to1 = {
    "1": "liîLIÎ",
    "2": "zZ",
    "3": "eéèêEÉÈÊ",
    "4": "aàâAÀÂ",
    "5": "sgSG",
    "6": "bdgBDG",
    "7": "ltLT",
    "8": "bB",
    "9": "gbdGBD",
    "0": "oôOÔ",

    "a": "aàâáäæ",
    "A": "AÀÂÁÄÆ",
    "à": "aàâáäæ",
    "À": "AÀÂÁÄÆ",
    "â": "aàâáäæ",
    "Â": "AÀÂÁÄÆ",
    "á": "aàâáäæ",
    "Á": "AÀÂÁÄÆ",
    "ä": "aàâáäæ",
    "Ä": "AÀÂÁÄÆ",

    "æ": "æéa",
    "Æ": "ÆÉA",

    "c": "cçskqśŝ",
    "C": "CÇSKQŚŜ",
    "ç": "cçskqśŝ",
    "Ç": "CÇSKQŚŜ",

    "e": "eéèêëœ",
    "E": "EÉÈÊËŒ",
    "é": "eéèêëœ",
    "É": "EÉÈÊËŒ",
    "ê": "eéèêëœ",
    "Ê": "EÉÈÊËŒ",
    "è": "eéèêëœ",
    "È": "EÉÈÊËŒ",
    "ë": "eéèêëœ",
    "Ë": "EÉÈÊËŒ",

    "g": "gj",
    "G": "GJ",
    
    "i": "iîïyíìÿ",
    "I": "IÎÏYÍÌŸ",
    "î": "iîïyíìÿ",
    "Î": "IÎÏYÍÌŸ",
    "ï": "iîïyíìÿ",
    "Ï": "IÎÏYÍÌŸ",
    "í": "iîïyíìÿ",
    "Í": "IÎÏYÍÌŸ",
    "ì": "iîïyíìÿ",
    "Ì": "IÎÏYÍÌŸ",

    "j": "jg",
    "J": "JG",

    "k": "kcq",
    "K": "KCQ",

    "n": "nñ",
    "N": "NÑ",

    "o": "oôóòöœ",
    "O": "OÔÓÒÖŒ",
    "ô": "oôóòöœ",
    "Ô": "OÔÓÒÖŒ",
    "ó": "oôóòöœ",
    "Ó": "OÔÓÒÖŒ",
    "ò": "oôóòöœ",
    "Ò": "OÔÓÒÖŒ",
    "ö": "oôóòöœ",
    "Ö": "OÔÓÒÖŒ",

    "œ": "œoôeéèêë",
    "Œ": "ŒOÔEÉÈÊË",

    "q": "qck",
    "Q": "QCK",

    "s": "sśŝcç",
    "S": "SŚŜCÇ",
    "ś": "sśŝcç",
    "Ś": "SŚŜCÇ",
    "ŝ": "sśŝcç",
    "Ŝ": "SŚŜCÇ",

    "u": "uûùüú",
    "U": "UÛÙÜÚ",
    "û": "uûùüú",
    "Û": "UÛÙÜÚ",
    "ù": "uûùüú",
    "Ù": "UÛÙÜÚ",
    "ü": "uûùüú",
    "Ü": "UÛÙÜÚ",
    "ú": "uûùüú",
    "Ú": "UÛÙÜÚ",

    "v": "vw",
    "V": "VW",

    "w": "wv",
    "W": "WV",

    "x": "xck",
    "X": "XCK",

    "y": "yÿiîŷýỳ",
    "Y": "YŸIÎŶÝỲ",
    "ÿ": "yÿiîŷýỳ",
    "Ÿ": "YŸIÎŶÝỲ",
    "ŷ": "yÿiîŷýỳ",
    "Ŷ": "YŸIÎŶÝỲ",
    "ý": "yÿiîŷýỳ",
    "Ý": "YŸIÎŶÝỲ",
    "ỳ": "yÿiîŷýỳ",
    "Ỳ": "YŸIÎŶÝỲ",

    "z": "zs",
    "Z": "ZS",
}

d1toX = {
    "æ": ("ae",),
    "Æ": ("AE",),
    "b": ("bb",),
    "B": ("BB",),
    "c": ("cc", "ss", "qu", "ch"),
    "C": ("CC", "SS", "QU", "CH"),
    "ç": ("ss", "cc", "qh", "ch"),
    "Ç": ("SS", "CC", "QH", "CH"),
    "d": ("dd",),
    "D": ("DD",),
    "f": ("ff", "ph"),
    "F": ("FF", "PH"),
    "g": ("gu", "ge", "gg", "gh"),
    "G": ("GU", "GE", "GG", "GH"),
    "i": ("ii",),
    "I": ("II",),
    "j": ("jj", "dj"),
    "J": ("JJ", "DJ"),
    "k": ("qu", "ck", "ch", "cu", "kk", "kh"),
    "K": ("QU", "CK", "CH", "CU", "KK", "KH"),
    "l": ("ll",),
    "L": ("LL",),
    "m": ("mm", "mn"),
    "M": ("MM", "MN"),
    "n": ("nn", "nm", "mn"),
    "N": ("NN", "NM", "MN"),
    "o": ("au", "eau"),
    "O": ("AU", "EAU"),
    "œ": ("oe", "eu"),
    "Œ": ("OE", "EU"),
    "p": ("pp", "ph"),
    "P": ("PP", "PH"),
    "q": ("qu", "ch", "cq", "ck", "kk"),
    "Q": ("QU", "CH", "CQ", "CK", "KK"),
    "r": ("rr",),
    "R": ("RR",),
    "s": ("ss", "sh"),
    "S": ("SS", "SH"),
    "t": ("tt", "th"),
    "T": ("TT", "TH"),
    "x": ("cc", "ct", "xx"),
    "X": ("CC", "CT", "XX"),
    "z": ("ss", "zh"),
    "Z": ("SS", "ZH"),
}

d2toX = {
    "an": ("en",),
    "AN": ("EN",),
    "au": ("eau", "o", "ô"),
    "AU": ("EAU", "O", "Ô"),
    "en": ("an",),
    "EN": ("AN",),
    "ai": ("ei", "é", "è", "ê", "ë"),
    "AI": ("EI", "É", "È", "Ê", "Ë"),
    "ei": ("ai", "é", "è", "ê", "ë"),
    "EI": ("AI", "É", "È", "Ê", "Ë"),
    "ch": ("sh", "c", "ss"),
    "CH": ("SH", "C", "SS"),
    "ct": ("x", "cc"),
    "CT": ("X", "CC"),
    "oa": ("oi",),
    "OA": ("OI",),
    "oi": ("oa", "oie"),
    "OI": ("OA", "OIE"),
    "qu": ("q", "cq", "ck", "c", "k"),
    "QU": ("Q", "CQ", "CK", "C", "K"),
    "ss": ("c", "ç"),
    "SS": ("C", "Ç"),
}


# End of word

dFinal1 = {
    "a": ("as", "at", "ant", "ah"),
    "A": ("AS", "AT", "ANT", "AH"),
    "c": ("ch",),
    "C": ("CH",),
    "e": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait", "ent", "eh"),
    "E": ("ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT", "ENT", "EH"),
    "é": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "É": ("ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"),
    "è": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "È": ("ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"),
    "ê": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "Ê": ("ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"),
    "ë": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "Ë": ("ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"),
    "g": ("gh",),
    "G": ("GH",),
    "i": ("is", "it", "ie", "in"),
    "I": ("IS", "IT", "IE", "IN"),
    "n": ("nt", "nd", "ns", "nh"),
    "N": ("NT", "ND", "NS", "NH"),
    "o": ("aut", "ot", "os"),
    "O": ("AUT", "OT", "OS"),
    "ô": ("aut", "ot", "os"),
    "Ô": ("AUT", "OT", "OS"),
    "ö": ("aut", "ot", "os"),
    "Ö": ("AUT", "OT", "OS"),
    "p": ("ph",),
    "P": ("PH",),
    "s": ("sh",),
    "S": ("SH",),
    "t": ("th",),
    "T": ("TH",),
    "u": ("ut", "us", "uh"),
    "U": ("UT", "US", "UH"),
}

dFinal2 = {
    "ai": ("aient", "ais", "et"),
    "AI": ("AIENT", "AIS", "ET"),
    "an": ("ant", "ent"),
    "AN": ("ANT", "ENT"),
    "en": ("ent", "ant"),
    "EN": ("ENT", "ANT"),
    "ei": ("ait", "ais"),
    "EI": ("AIT", "AIS"),
    "on": ("ons", "ont"),
    "ON": ("ONS", "ONT"),
    "oi": ("ois", "oit", "oix"),
    "OI": ("OIS", "OIT", "OIX"),
}


# Préfixes et suffixes

aPfx1 = frozenset([
    "anti", "archi", "contre", "hyper", "mé", "méta", "im", "in", "ir", "par", "proto",
    "pseudo", "pré", "re", "ré", "sans", "sous", "supra", "sur", "ultra"
])
aPfx2 = frozenset([
    "belgo", "franco", "génito", "gynéco", "médico", "russo"
])


_zMotAvecPronom = re.compile("^(?i)(\\w+)(-(?:t-|)(?:ils?|elles?|on|je|tu|nous|vous))$")

def cut (sWord):
    "returns a tuple of strings (prefix, trimed_word, suffix)"
    m = _zMotAvecPronom.search(sWord)
    if m:
        return ("", m.group(1), m.group(2))
    return ("", sWord, "")


# Other functions

def filterSugg (aSugg):
    "exclude suggestions"
    return filter(lambda sSugg: not sSugg.endswith(("è", "È")), aSugg)
