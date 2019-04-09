#! python3
#
# Metagraphe
#
# By Olivier R. - 2013

import re


# Dictionnaire des caractères pour la phonétique
PHMAP = str.maketrans({ 'à': 'a',  'â': 'a',  'ä': 'a',  'å': 'a',  'ā': 'a',
                        'ç': 'S',
                        'é': 'é',  'è': 'é',  'ê': 'é',  'ë': 'é',  'ē': 'é',
                        'î': 'i',  'ï': 'i',  'ī': 'i',
                        'ñ': 'ni',
                        'ô': 'o',  'ö': 'o',  'ō': 'o',
                        'ù': 'u',  'û': 'u',  'ü': 'u',  'ū': 'u',
                        'ÿ': 'i',
                        'æ': 'é' })

def getPhonex (s, sMorph):
    "returns a simplified phonetic string"
    if re.match("[A-Z0-9]{2,}$", s):
        return s
    elif len(s) == 1:
        return s.lower().translate(PHMAP)
    else:
        s = s.lower().translate(PHMAP)
        s = re.sub("sc(?=[eéiy])", "S", s)
        s = re.sub("x[cs](?=[eéiy])", "kS", s)
        s = re.sub("c(?=[eéiy])", "S", s)
        s = re.sub("c(?=[auoœ])", "k", s)
        s = re.sub("ge(?=[ao])", "j", s)
        s = re.sub("g(?=[ieéy])", "j", s)
        s = re.sub("gue", "ge", s)
        s = re.sub("am(?=[bp])", "â", s)
        s = re.sub("om(?=[bpt])", "ô", s)
        s = re.sub("omp(?=t)", "ô", s)
        s = re.sub("[iy]m(?=[bp])", "1", s)
        s = re.sub("eill", "éY", s)
        s = re.sub("aill", "aY", s)
        s = re.sub("[ae]y(?=[aeéi])", "éY", s)
        s = re.sub("^s", "S", s)
        s = re.sub("(?<=[aeioéu])s(?=[aeioéu])", "z", s)
        if sMorph.startswith("v"):
            s = re.sub("aient$", "é", s)
            s = re.sub("ent$", "", s)
            s = re.sub("ant$", "â", s)
            s = re.sub("a[st]$", "a", s)
            s = re.sub("ai[ets]$", "é", s)
            s = re.sub("ez$", "é", s)
            s = re.sub("on[st]?$", "ô", s)
            s = re.sub("es?$", "", s)
            s = re.sub("ée?s?$", "é", s)
            s = re.sub("ie?s?$", "i", s)
            s = re.sub("ue?s?$", "u", s)
            s = re.sub("ui[ts]$", "ui", s)
            s = re.sub("aut$", "o", s)
            s = re.sub("ut$", "u", s)
            s = re.sub("it?s?$", "i", s)
        if sMorph.startswith("nom") or sMorph.startswith("adj"):
            if "pl" in sMorph:
                s = re.sub("[sx]$", "", s)
        s = re.sub("tion$", "Siô", s)
        s = re.sub("ent$", "â", s)
        s = re.sub("eux$", "2", s)
        s = re.sub("eaux$", "o", s)
        s = re.sub("e[rt]$", "é", s)
        s = re.sub("[ea]ine$", "én", s)
        s = re.sub("at$", "a", s)
        s = re.sub("on(?=[bcdfghjklmpqrsStvwxz])", "ô", s)
        s = re.sub("an[st]?$", "â", s)
        s = re.sub("an(?=[bcdfghjklmpqrsStvwxz])", "â", s)
        s = re.sub("iens?$", "i1", s)
        s = re.sub("(?<!i)ens?$", "â", s)
        s = re.sub("en(?=[bcdfghjklmpqrsStvwxz])", "â", s)
        s = re.sub("uns?$", "1", s)
        s = re.sub("un(?=[bcdfghjklmpqrsStvwxz])", "1", s)
        s = re.sub("ins?$", "1", s)
        s = re.sub("a?in(?=[bcdfghjklmpqrsStvwxz])", "1", s)
        s = re.sub("œu?", "2", s)
        s = re.sub("eux?$", "2", s)
        s = re.sub("eu(?=[bcdfghjklmpqrsStvwxz])", "2", s)
        s = re.sub("e(?=ss|tt|rr|ll|ff)", "é", s)
        s = re.sub("enne$", "én", s)
        s = re.sub("e?au", "o", s)
        s = re.sub("che$", "ç", s)
        s = re.sub("[ae]i", "é", s)
        s = s.replace("ou", "û")
        s = s.replace("ss", "S")
        s = s.replace("dj", "j")
        s = s.replace("th", "t")
        s = re.sub("[qc]u?", "k", s)
        s = s.replace("ch", "k")
        s = s.replace("ph", "f")
        s = s.replace("h", "")
        s = s.replace("y", "i")
        s = s.replace("æ", "é")
        s = s.replace("x", "ks")
        if len(s) > 3: s = re.sub("es$", "", s)
        if len(s) > 2: s = re.sub("e$", "", s)
        s = re.sub("(\\w)\\1", "\\1", s)
    return s

def getGraphix (s):
    "returns a simplified spelling"
    return ''


def getMetagraphe (s, sMorph):
    return (getPhonex(s, sMorph), getGraphix(s))
