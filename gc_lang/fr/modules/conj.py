# Grammalecte - Conjugueur
# License: GPL 3

import re
import traceback

from .conj_data import lVtyp as _lVtyp
from .conj_data import lTags as _lTags
from .conj_data import dPatternConj as _dPatternConj
from .conj_data import dVerb as _dVerb


_zStartVoy = re.compile("^[aeéiouœê]")
_zNeedTeuph = re.compile("[tdc]$")
#_zNEEDACCENTWITHJE = re.compile("[^i]e$")

_dProSuj = { ":1s": "je", ":1ś": "je", ":2s": "tu", ":3s": "il", ":1p": "nous", ":2p": "vous", ":3p": "ils" }
_dProObj = { ":1s": "me ", ":1ś": "me ", ":2s": "te ", ":3s": "se ", ":1p": "nous ", ":2p": "vous ", ":3p": "se " }
_dProObjEl = { ":1s": "m’", ":1ś": "m’", ":2s": "t’", ":3s": "s’", ":1p": "nous ", ":2p": "vous ", ":3p": "s’" }
_dImpePro = { ":2s": "-toi", ":1p": "-nous", ":2p": "-vous" }
_dImpeProNeg = { ":2s": "ne te ", ":1p": "ne nous ", ":2p": "ne vous " }
_dImpeProEn = { ":2s": "-t’en", ":1p": "-nous-en", ":2p": "-vous-en" }
_dImpeProNegEn = { ":2s": "ne t’en ", ":1p": "ne nous en ", ":2p": "ne vous en " }

_dGroup = { "0": "auxiliaire", "1": "1ᵉʳ groupe", "2": "2ᵉ groupe", "3": "3ᵉ groupe" }

_dTenseIdx = { ":PQ": 0, ":Ip": 1, ":Iq": 2, ":Is": 3, ":If": 4, ":K": 5, ":Sp": 6, ":Sq": 7, ":E": 8 }



def isVerb (s):
    return s in _dVerb


def getConj (sVerb, sTense, sWho):
    "returns conjugation (can be an empty string)"
    if sVerb not in _dVerb:
        return None
    return _modifyStringWithSuffixCode(sVerb, _dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx[sTense]]].get(sWho, ""))


def hasConj (sVerb, sTense, sWho):
    "returns False if no conjugation (also if empty) else True"
    if sVerb not in _dVerb:
        return False
    if _dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx[sTense]]].get(sWho, False):
        return True
    return False


def getVtyp (sVerb):
    "returns raw informations about sVerb"
    if sVerb not in _dVerb:
        return None
    return _lVtyp[_dVerb[sVerb][0]]


def getSimil (sWord, sMorph):
    if ":V" not in sMorph:
        return set()
    sInfi = sMorph[1:sMorph.find(" ")]
    tTags = _getTags(sInfi)
    aSugg = set()
    if ":Q" in sMorph:
        # we suggest conjugated forms
        if ":V1" in sMorph:
            aSugg.add(sInfi)
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":2p"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":1s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":3s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":3p"))
        elif ":V2" in sMorph:
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":1s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"))
        elif ":V3" in sMorph:
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":1s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Is", ":1s"))
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Is", ":3s"))
        elif ":V0a" in sMorph:
            aSugg.add("eus")
            aSugg.add("eut")
        else:
            aSugg.add("étais")
            aSugg.add("était")
        aSugg.discard("")
    else:
        # we suggest past participles
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q1"))
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q2"))
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q3"))
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q4"))
        aSugg.discard("")
        # if there is only one past participle (epi inv), unreliable.
        if len(aSugg) == 1:
            aSugg.clear()
    return aSugg


def _getTags (sVerb):
    "returns tuple of tags (usable with functions _getConjWithTags and _hasConjWithTags)"
    if sVerb not in _dVerb:
        return None
    return _lTags[_dVerb[sVerb][1]]


def _getConjWithTags (sVerb, tTags, sTense, sWho):
    "returns conjugation (can be an empty string)"
    return _modifyStringWithSuffixCode(sVerb, _dPatternConj[sTense][tTags[_dTenseIdx[sTense]]].get(sWho, ""))


def _hasConjWithTags (tTags, sTense, sWho):
    "returns False if no conjugation (also if empty) else True"
    if _dPatternConj[sTense][tTags[_dTenseIdx[sTense]]].get(sWho, False):
        return True
    return False


def _modifyStringWithSuffixCode (sWord, sSfx):
    "returns sWord modified by sSfx"
    if not sSfx:
        return ""
    if sSfx == "0":
        return sWord
    try:
        return sWord[:-(ord(sSfx[0])-48)] + sSfx[1:]  if sSfx[0] != '0'  else  sWord + sSfx[1:]  # 48 is the ASCII code for "0"
    except:
        return "## erreur, code : " + str(sSfx) + " ##"
        


class Verb ():
    def __init__ (self, sVerb):
        if not isinstance(sVerb, str):
            raise TypeError
        if not sVerb:
            raise ValueError

        self.sVerb = sVerb
        self.sVerbAux = ""
        self._sRawInfo = getVtyp(self.sVerb)
        self.sInfo = self._readableInfo()
        self.bProWithEn = (self._sRawInfo[5] == "e")
        self._tTags = _getTags(sVerb)
        self._tTagsAux = _getTags(self.sVerbAux)

        self.dConj = {
            ":Y": {
                "label": "Infinitif",
                ":Y": sVerb,
            },
            ":PQ": {
                "label": "Participes passés et présent",
                ":Q1": _getConjWithTags(sVerb, self._tTags, ":PQ", ":Q1"),
                ":Q2": _getConjWithTags(sVerb, self._tTags, ":PQ", ":Q2"),
                ":Q3": _getConjWithTags(sVerb, self._tTags, ":PQ", ":Q3"),
                ":Q4": _getConjWithTags(sVerb, self._tTags, ":PQ", ":Q4"),
                ":P": _getConjWithTags(sVerb, self._tTags, ":PQ", ":P"),
            },
            ":Ip": {
                "label": "Présent",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":Ip", ":1s"),
                ":1ś": _getConjWithTags(sVerb, self._tTags, ":Ip", ":1ś"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":Ip", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":Ip", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":Ip", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":Ip", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":Ip", ":3p"),
            },
            ":Iq": {
                "label": "Imparfait",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":Iq", ":1s"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":Iq", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":Iq", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":Iq", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":Iq", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":Iq", ":3p"),
            },
            ":Is": {
                "label": "Passé simple",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":Is", ":1s"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":Is", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":Is", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":Is", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":Is", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":Is", ":3p"),
            },
            ":If": {
                "label": "Futur",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":If", ":1s"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":If", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":If", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":If", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":If", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":If", ":3p"),
            },
            ":Sp": {
                "label": "Présent subjonctif",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":Sp", ":1s"),
                ":1ś": _getConjWithTags(sVerb, self._tTags, ":Sp", ":1ś"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":Sp", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":Sp", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":Sp", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":Sp", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":Sp", ":3p"),
            },
            ":Sq": {
                "label": "Imparfait subjonctif",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":Sq", ":1s"),
                ":1ś": _getConjWithTags(sVerb, self._tTags, ":Sq", ":1ś"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":Sq", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":Sq", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":Sq", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":Sq", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":Sq", ":3p"),
            },
            ":K": {
                "label": "Conditionnel",
                ":1s": _getConjWithTags(sVerb, self._tTags, ":K", ":1s"),
                ":2s": _getConjWithTags(sVerb, self._tTags, ":K", ":2s"),
                ":3s": _getConjWithTags(sVerb, self._tTags, ":K", ":3s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":K", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":K", ":2p"),
                ":3p": _getConjWithTags(sVerb, self._tTags, ":K", ":3p"),
            },
            ":E": {
                "label": "Impératif",
                ":2s": _getConjWithTags(sVerb, self._tTags, ":E", ":2s"),
                ":1p": _getConjWithTags(sVerb, self._tTags, ":E", ":1p"),
                ":2p": _getConjWithTags(sVerb, self._tTags, ":E", ":2p"),
            },
        }

    def _readableInfo (self):
        "returns readable infos about sVerb"
        try:
            if not self._sRawInfo:
                return "verbe inconnu"
            if self._sRawInfo[7:8] == "e":
                self.sVerbAux = "être"
            else:
                self.sVerbAux = "avoir"
            sGroup = _dGroup.get(self._sRawInfo[0], "# erreur ")
            s = ""
            if self._sRawInfo[3:4] == "t":
                s = "transitif"
            elif self._sRawInfo[4:5] == "n":
                s = "transitif indirect"
            elif self._sRawInfo[2:3] == "i":
                s = "intransitif"
            elif self._sRawInfo[5:6] == "r":
                s = "pronominal réciproque"
            elif self._sRawInfo[5:6] == "p":
                s = "pronominal"
            if self._sRawInfo[5:6] == "q" or self._sRawInfo[5:6] == "e":
                s = s + " (+ usage pronominal)"
            if self._sRawInfo[6:7] == "m":
                s = s + " impersonnel"
            if not s:
                s = "# erreur - code : " + self._sRawInfo
            return sGroup + " · " + s
        except:
            traceback.print_exc()
            return "# erreur"

    def infinitif (self, bPro, bNeg, bTpsCo, bInt, bFem):
        try:
            if bTpsCo:
                sInfi = self.sVerbAux  if not bPro  else  "être"
            else:
                sInfi = self.sVerb
            if bPro:
                if self.bProWithEn:
                    sInfi = "s’en " + sInfi
                else:
                    sInfi = "s’" + sInfi  if _zStartVoy.search(sInfi)  else  "se " + sInfi
            if bNeg:
                sInfi = "ne pas " + sInfi
            if bTpsCo:
                sInfi += " " + self._seekPpas(bPro, bFem, self._sRawInfo[5] == "r")
            if bInt:
                sInfi += " … ?"
            return sInfi
        except:
            traceback.print_exc()
            return "# erreur"

    def participePasse (self, sWho):
        try:
            return self.dConj[":PQ"][sWho]
        except:
            traceback.print_exc()
            return "# erreur"

    def participePresent (self, bPro, bNeg, bTpsCo, bInt, bFem):
        try:
            if not self.dConj[":PQ"][":P"]:
                return ""
            if bTpsCo:
                s = _getConjWithTags(self.sVerbAux, self._tTagsAux, ":PQ", ":P")  if not bPro  else  getConj("être", ":PQ", ":P")
            else:
                s = self.dConj[":PQ"][":P"]
            if not s:
                return ""
            bEli = True  if _zStartVoy.search(s)  else  False
            if bPro:
                if self.bProWithEn:
                    s = "s’en " + s
                else:
                    s = "s’" + s  if bEli  else  "se " + s
            if bNeg:
                if bEli and not bPro:
                    s = "n’" + s + " pas"
                else:
                    s = "ne " + s + " pas"
            if bTpsCo:
                s += " " + self._seekPpas(bPro, bFem, self._sRawInfo[5] == "r")
            if bInt:
                s += " … ?"
            return s
        except:
            traceback.print_exc()
            return "# erreur"

    def conjugue (self, sTemps, sWho, bPro, bNeg, bTpsCo, bInt, bFem):
        try:
            if not self.dConj[sTemps][sWho]:
                return ""
            if not bTpsCo and bInt and sWho == ":1s" and self.dConj[sTemps].get(":1ś", False):
                sWho = ":1ś"
            if bTpsCo:
                s = _getConjWithTags(self.sVerbAux, self._tTagsAux, sTemps, sWho)  if not bPro  else  getConj("être", sTemps, sWho)
            else:
                s = self.dConj[sTemps][sWho]
            if not s:
                return ""
            bEli = True  if _zStartVoy.search(s)  else  False
            if bPro:
                if not self.bProWithEn:
                    s = _dProObjEl[sWho] + s  if bEli  else _dProObj[sWho] + s
                else:
                    s = _dProObjEl[sWho] + "en " + s
            if bNeg:
                s = "n’" + s  if bEli and not bPro  else  "ne " + s
            if bInt:
                if sWho == ":3s" and not _zNeedTeuph.search(s):
                    s += "-t"
                s += "-" + self._getPronom(sWho, bFem)
            else:
                if sWho == ":1s" and bEli and not bNeg and not bPro:
                    s = "j’" + s
                else:
                    s = self._getPronom(sWho, bFem) + " " + s
            if bNeg:
                s += " pas"
            if bTpsCo:
                s += " " + self._seekPpas(bPro, bFem, sWho.endswith("p") or self._sRawInfo[5] == "r")
            if bInt:
                s += " … ?"
            return s
        except:
            traceback.print_exc()
            return "# erreur"

    def _getPronom (self, sWho, bFem):
        try:
            if sWho == ":3s":
                if self._sRawInfo[5] == "r":
                    return "on"
                elif bFem:
                    return "elle"
            elif sWho == ":3p" and bFem:
                return "elles"
            return _dProSuj[sWho]
        except:
            traceback.print_exc()
            return "# erreur"

    def imperatif (self, sWho, bPro, bNeg, bTpsCo, bFem):
        try:
            if not self.dConj[":E"][sWho]:
                return ""
            if bTpsCo:
                s = _getConjWithTags(self.sVerbAux, self._tTagsAux, ":E", sWho)  if not bPro  else  getConj(u"être", ":E", sWho)
            else:
                s = self.dConj[":E"][sWho]
            if not s:
                return ""
            bEli = True  if _zStartVoy.search(s)  else  False
            if bNeg:
                if bPro:
                    if not self.bProWithEn:
                        if bEli and sWho == ":2s":
                            s = "ne t’" + s + " pas"
                        else:
                            s = _dImpeProNeg[sWho] + s + " pas"
                    else:
                        s = _dImpeProNegEn[sWho] + s + " pas"
                else:
                    s = "n’" + s + " pas"  if bEli  else  "ne " + s + " pas"
            elif bPro:
                s = s + _dImpeProEn[sWho]  if self.bProWithEn  else  s + _dImpePro[sWho]
            if bTpsCo:
                return s + " " + self._seekPpas(bPro, bFem, sWho.endswith("p") or self._sRawInfo[5] == "r")
            return s
        except:
            traceback.print_exc()
            return "# erreur"

    def _seekPpas (self, bPro, bFem, bPlur):
        try:
            if not bPro and self.sVerbAux == "avoir":
                return self.dConj[":PQ"][":Q1"]
            if not bFem:
                return self.dConj[":PQ"][":Q2"]  if bPlur and self.dConj[":PQ"][":Q2"]  else  self.dConj[":PQ"][":Q1"]
            if not bPlur:
                return self.dConj[":PQ"][":Q3"]  if self.dConj[":PQ"][":Q3"]  else  self.dConj[":PQ"][":Q1"]
            return self.dConj[":PQ"][":Q4"]  if self.dConj[":PQ"][":Q4"]  else  self.dConj[":PQ"][":Q1"]
        except:
            traceback.print_exc()
            return "# erreur"
