# list of similar chars
# useful for suggestion mechanism


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


def clearWord (sWord):
    "remove vovels and h"
    return sWord[0:1].replace("h", "") + sWord[1:].translate(_xTransVovels)


# Similar chars

d1to1 = {
    "1": "li",
    "2": "z",
    "3": "e",
    "4": "aà",
    "5": "sg",
    "6": "bdg",
    "7": "lt",
    "8": "b",
    "9": "gbd",
    "0": "o",

    "a": "aàâáäæ",
    "à": "aàâáäæ",
    "â": "aàâáäæ",
    "á": "aàâáäæ",
    "ä": "aàâáäæ",

    "æ": "æéa",

    "c": "cçskqśŝ",
    "ç": "cçskqśŝ",

    "e": "eéèêëœ",
    "é": "eéèêëœ",
    "ê": "eéèêëœ",
    "è": "eéèêëœ",
    "ë": "eéèêëœ",

    "g": "gj",
    
    "i": "iîïyíìÿ",
    "î": "iîïyíìÿ",
    "ï": "iîïyíìÿ",
    "í": "iîïyíìÿ",
    "ì": "iîïyíìÿ",

    "j": "jg",

    "k": "kcq",

    "n": "nñ",

    "o": "oôóòöœ",
    "ô": "oôóòöœ",
    "ó": "oôóòöœ",
    "ò": "oôóòöœ",
    "ö": "oôóòöœ",

    "œ": "œoôeéèêë",

    "q": "qck",

    "s": "sśŝcç",
    "ś": "sśŝcç",
    "ŝ": "sśŝcç",

    "u": "uûùüú",
    "û": "uûùüú",
    "ù": "uûùüú",
    "ü": "uûùüú",
    "ú": "uûùüú",

    "v": "vw",

    "w": "wv",

    "x": "xck",

    "y": "yÿiîŷýỳ",
    "ÿ": "yÿiîŷýỳ",
    "ŷ": "yÿiîŷýỳ",
    "ý": "yÿiîŷýỳ",
    "ỳ": "yÿiîŷýỳ",

    "z": "zs",
}

d1toX = {
    "æ": ("ae",),
    "b": ("bb",),
    "c": ("cc", "ss", "qu", "ch"),
    "ç": ("ss", "cc", "qh", "ch"),
    "d": ("dd",),
    "f": ("ff", "ph"),
    "g": ("gu", "ge", "gg", "gh"),
    "i": ("ii",),
    "j": ("jj", "dj"),
    "k": ("qu", "ck", "ch", "cu", "kk", "kh"),
    "l": ("ll",),
    "m": ("mm", "mn"),
    "n": ("nn", "nm", "mn"),
    "o": ("au", "eau", "aut"),
    "œ": ("oe", "eu"),
    "p": ("pp", "ph"),
    "q": ("qu", "ch", "cq", "ck", "kk"),
    "r": ("rr",),
    "s": ("ss", "sh"),
    "t": ("tt", "th"),
    "x": ("cc", "ct", "xx"),
    "z": ("ss", "zh")
}

d2toX = {
    "an": ("en",),
    "en": ("an",),
    "ai": ("ei", "é", "è", "ê", "ë"),
    "ei": ("ai", "é", "è", "ê", "ë"),
    "ch": ("sh", "c", "ss"),
    "ct": ("x", "cc"),
    "oa": ("oi",),
    "oi": ("oa", "oie"),
    "qu": ("q", "cq", "ck", "c", "k"),
    "ss": ("c", "ç"),
}


# End of word

dFinal1 = {
    "a": ("as", "at", "ant", "ah"),
    "c": ("ch",),
    "e": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait", "ent", "eh"),
    "é": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "è": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "ê": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "ë": ("et", "er", "ets", "ée", "ez", "ai", "ais", "ait"),
    "g": ("gh",),
    "i": ("is", "it", "ie", "in"),
    "n": ("nt", "nd", "ns", "nh"),
    "o": ("aut", "ot", "os"),
    "ô": ("aut", "ot", "os"),
    "ö": ("aut", "ot", "os"),
    "p": ("ph",),
    "s": ("sh",),
    "t": ("th",),
    "u": ("ut", "us", "uh"),
}

dFinal2 = {
    "ai": ("aient", "ais", "et"),
    "an": ("ant", "ent"),
    "en": ("ent", "ant"),
    "ei": ("ait", "ais"),
    "on": ("ons", "ont"),
    "oi": ("ois", "oit", "oix"),
}


# Préfixes

aPfx1 = frozenset([
    "anti", "archi", "contre", "hyper", "mé", "méta", "im", "in", "ir", "par", "proto",
    "pseudo", "pré", "re", "ré", "sans", "sous", "supra", "sur", "ultra"
])
aPfx2 = frozenset([
    "belgo", "franco", "génito", "gynéco", "médico", "russo"
])
