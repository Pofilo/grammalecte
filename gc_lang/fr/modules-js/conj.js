// Grammalecte - Conjugueur
// License: GPL 3

"use strict";

${map}


let helpers = null; // module not loaded in Firefox content script

let _oData = {};
let _lVtyp = null;
let _lTags = null;
let _dPatternConj = {};
let _dVerb = {};


if (typeof(exports) !== 'undefined') {
    // used within Grammalecte library
    helpers = require("resource://grammalecte/helpers.js");
    _oData = JSON.parse(helpers.loadFile("resource://grammalecte/fr/conj_data.json"));
    _lVtyp = _oData.lVtyp;
    _lTags = _oData.lTags;
    _dPatternConj = _oData.dPatternConj;
    _dVerb = _oData.dVerb;
} else {
    // used within Firefox content script (conjugation panel).
    // can’t load JSON from here, so we do it in ui.js and send it here.
    self.port.on("provideConjData", function (sData) {
        _oData = JSON.parse(sData);
        _lVtyp = _oData.lVtyp;
        _lTags = _oData.lTags;
        _dPatternConj = _oData.dPatternConj;
        _dVerb = _oData.dVerb;
    });
}


const _zStartVoy = new RegExp("^[aeéiouœê]");
const _zNeedTeuph = new RegExp("[tdc]$");

const _dProSuj = new Map ([ [":1s", "je"], [":1ś", "je"], [":2s", "tu"], [":3s", "il"], [":1p", "nous"], [":2p", "vous"], [":3p", "ils"] ]);
const _dProObj = new Map ([ [":1s", "me "], [":1ś", "me "], [":2s", "te "], [":3s", "se "], [":1p", "nous "], [":2p", "vous "], [":3p", "se "] ]);
const _dProObjEl = new Map ([ [":1s", "m’"], [":1ś", "m’"], [":2s", "t’"], [":3s", "s’"], [":1p", "nous "], [":2p", "vous "], [":3p", "s’"] ]);
const _dImpePro = new Map ([ [":2s", "-toi"], [":1p", "-nous"], [":2p", "-vous"] ]);
const _dImpeProNeg = new Map ([ [":2s", "ne te "], [":1p", "ne nous "], [":2p", "ne vous "] ]);
const _dImpeProEn = new Map ([ [":2s", "-t’en"], [":1p", "-nous-en"], [":2p", "-vous-en"] ]);
const _dImpeProNegEn = new Map ([ [":2s", "ne t’en "], [":1p", "ne nous en "], [":2p", "ne vous en "] ]);

const _dGroup = new Map ([ ["0", "auxiliaire"], ["1", "1ᵉʳ groupe"], ["2", "2ᵉ groupe"], ["3", "3ᵉ groupe"] ]);

const _dTenseIdx = new Map ([ [":PQ", 0], [":Ip", 1], [":Iq", 2], [":Is", 3], [":If", 4], [":K", 5], [":Sp", 6], [":Sq", 7], [":E", 8] ]);


function isVerb (sVerb) {
    return _dVerb.hasOwnProperty(sVerb);
}

function getConj (sVerb, sTense, sWho) {
    // returns conjugation (can be an empty string)
    if (!_dVerb.hasOwnProperty(sVerb)) {
        return null;
    }
    if (!_dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx.get(sTense)]].hasOwnProperty(sWho)) {
        return "";
    }
    return _modifyStringWithSuffixCode(sVerb, _dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx.get(sTense)]][sWho]);
}

function hasConj (sVerb, sTense, sWho) {
    // returns false if no conjugation (also if empty) else true
    if (!_dVerb.hasOwnProperty(sVerb)) {
        return false;
    }
    if (_dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx.get(sTense)]].hasOwnProperty(sWho)
            && _dPatternConj[sTense][_lTags[_dVerb[sVerb][1]][_dTenseIdx.get(sTense)]][sWho]) {
        return true;
    }
    return false;
}

function getVtyp (sVerb) {
    // returns raw informations about sVerb
    if (!_dVerb.hasOwnProperty(sVerb)) {
        return null;
    }
    return _lVtyp[_dVerb[sVerb][0]];
}

function getSimil (sWord, sMorph, sFilter=null) {
    if (!sMorph.includes(":V")) {
        return new Set();
    }
    let sInfi = sMorph.slice(1, sMorph.indexOf(" "));
    let tTags = _getTags(sInfi);
    let aSugg = new Set();
    if (sMorph.includes(":Q") || sMorph.includes(":Y")) {
        // we suggest conjugated forms
        if (sMorph.includes(":V1")) {
            aSugg.add(sInfi);
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":2p"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":1s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":3s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Iq", ":3p"));
        } else if (sMorph.includes(":V2")) {
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":1s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"));
        } else if (sMorph.includes(":V3")) {
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":1s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Ip", ":3s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Is", ":1s"));
            aSugg.add(_getConjWithTags(sInfi, tTags, ":Is", ":3s"));
        } else if (isMorph.includes(":V0a")) {
            aSugg.add("eus");
            aSugg.add("eut");
        } else {
            aSugg.add("étais");
            aSugg.add("était");
        }
        aSugg.delete("");
    } else {
        // we suggest past participles
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q1"));
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q2"));
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q3"));
        aSugg.add(_getConjWithTags(sInfi, tTags, ":PQ", ":Q4"));
        aSugg.delete("");
        // if there is only one past participle (epi inv), unreliable.
        if (aSugg.size === 1) {
            aSugg.clear();
        }
        if (sMorph.includes(":V1")) {
            aSugg.add(sInfi);
        }
    }
    return aSugg;
}


function _getTags (sVerb) {
    // returns tuple of tags (usable with functions _getConjWithTags and _hasConjWithTags)
    if (!_dVerb.hasOwnProperty(sVerb)) {
        return null;
    }
    return _lTags[_dVerb[sVerb][1]];
}

function _getConjWithTags (sVerb, tTags, sTense, sWho) {
    // returns conjugation (can be an empty string)
    if (!_dPatternConj[sTense][tTags[_dTenseIdx.get(sTense)]].hasOwnProperty(sWho)) {
        return "";
    }
    return _modifyStringWithSuffixCode(sVerb, _dPatternConj[sTense][tTags[_dTenseIdx.get(sTense)]][sWho]);
}

function _hasConjWithTags (tTags, sTense, sWho) {
    // returns false if no conjugation (also if empty) else true
    if (_dPatternConj[sTense][tTags[_dTenseIdx.get(sTense)]].hasOwnProperty(sWho)
            && _dPatternConj[sTense][tTags[_dTenseIdx.get(sTense)]][sWho]) {
        return true;
    }
    return false;
}

function _modifyStringWithSuffixCode (sWord, sSfx) {
    // returns sWord modified by sSfx
    if (sSfx === "") {
        return "";
    }
    if (sSfx === "0") {
        return sWord;
    }
    try {
        if (sSfx[0] !== '0') {
            return sWord.slice(0, -(sSfx.charCodeAt(0)-48)) + sSfx.slice(1); // 48 is the ASCII code for "0"
        } else {
            return sWord + sSfx.slice(1);
        }
    }
    catch (e) {
        console.log(e);
        return "## erreur, code : " + sSfx + " ##";
    }
}


class Verb {

    constructor (sVerb) {
        if (typeof sVerb !== "string" || sVerb === "") {
            throw new TypeError ("The value should be a non-empty string");
        }
        this.sVerb = sVerb;
        this.sVerbAux = "";
        this._sRawInfo = getVtyp(this.sVerb);
        this.sInfo = this._readableInfo(this._sRawInfo);
        this._tTags = _getTags(sVerb);
        this._tTagsAux = _getTags(this.sVerbAux);
        this.bProWithEn = (this._sRawInfo[5] === "e");
        this.dConj = new Map ([
            [":Y", new Map ([
                ["label", "Infinitif"],
                [":Y", sVerb]
            ])],
            [":PQ", new Map ([
                ["label", "Participes passés et présent"],
                [":Q1", _getConjWithTags(sVerb, this._tTags, ":PQ", ":Q1")],
                [":Q2", _getConjWithTags(sVerb, this._tTags, ":PQ", ":Q2")],
                [":Q3", _getConjWithTags(sVerb, this._tTags, ":PQ", ":Q3")],
                [":Q4", _getConjWithTags(sVerb, this._tTags, ":PQ", ":Q4")],
                [":P", _getConjWithTags(sVerb, this._tTags, ":PQ", ":P")]
            ])],
            [":Ip", new Map ([
                ["label", "Présent"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":Ip", ":1s")],
                [":1ś", _getConjWithTags(sVerb, this._tTags, ":Ip", ":1ś")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":Ip", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":Ip", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":Ip", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":Ip", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":Ip", ":3p")]
            ])],
            [":Iq", new Map ([
                ["label", "Imparfait"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":Iq", ":1s")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":Iq", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":Iq", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":Iq", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":Iq", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":Iq", ":3p")]
            ])],
            [":Is", new Map ([
                ["label", "Passé simple"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":Is", ":1s")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":Is", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":Is", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":Is", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":Is", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":Is", ":3p")]
            ])],
            [":If", new Map ([
                ["label", "Futur"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":If", ":1s")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":If", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":If", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":If", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":If", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":If", ":3p")]
            ])],
            [":Sp", new Map ([
                ["label", "Présent subjonctif"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":Sp", ":1s")],
                [":1ś", _getConjWithTags(sVerb, this._tTags, ":Sp", ":1ś")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":Sp", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":Sp", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":Sp", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":Sp", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":Sp", ":3p")]
            ])],
            [":Sq", new Map ([
                ["label", "Imparfait subjonctif"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":Sq", ":1s")],
                [":1ś", _getConjWithTags(sVerb, this._tTags, ":Sq", ":1ś")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":Sq", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":Sq", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":Sq", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":Sq", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":Sq", ":3p")]
            ])],
            [":K", new Map ([
                ["label", "Conditionnel"],
                [":1s", _getConjWithTags(sVerb, this._tTags, ":K", ":1s")],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":K", ":2s")],
                [":3s", _getConjWithTags(sVerb, this._tTags, ":K", ":3s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":K", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":K", ":2p")],
                [":3p", _getConjWithTags(sVerb, this._tTags, ":K", ":3p")]
            ])],
            [":E", new Map ([
                ["label", "Impératif"],
                [":2s", _getConjWithTags(sVerb, this._tTags, ":E", ":2s")],
                [":1p", _getConjWithTags(sVerb, this._tTags, ":E", ":1p")],
                [":2p", _getConjWithTags(sVerb, this._tTags, ":E", ":2p")]
            ])]
        ]);
    };

    _readableInfo () {
        // returns readable infos
        this.sVerbAux = (this._sRawInfo.slice(7,8) == "e") ? "être" : "avoir";
        let sGroup = _dGroup.get(this._sRawInfo[0]);
        let sInfo = "";
        if (this._sRawInfo.slice(3,4) == "t") {
            sInfo = "transitif";
        } else if (this._sRawInfo.slice(4,5) == "n") {
            sInfo = "transitif indirect";
        } else if (this._sRawInfo.slice(2,3) == "i") {
            sInfo = "intransitif";
        } else if (this._sRawInfo.slice(5,6) == "r") {
            sInfo = "pronominal réciproque";
        } else if (this._sRawInfo.slice(5,6) == "p") {
            sInfo = "pronominal";
        }
        if ( ["q", "u", "v", "e"].includes(this._sRawInfo.slice(5,6)) ) {
            sInfo = sInfo + " (+ usage pronominal)";
        }
        if (this._sRawInfo.slice(6,7) == "m") {
            sInfo = sInfo + " impersonnel";
        }
        if (sInfo === "") {
            sInfo = "# erreur - code : " + this._sRawInfo;
        }
        return sGroup + " · " + sInfo;
    };

    infinitif (bPro, bNeg, bTpsCo, bInt, bFem) {
        let sInfi;
        if (bTpsCo) {
            sInfi = (bPro) ? "être" : this.sVerbAux;
        } else {
            sInfi = this.sVerb;
        }
        if (bPro) {
            if (this.bProWithEn) {
                sInfi = "s’en " + sInfi;
            } else {
                sInfi = (_zStartVoy.test(sInfi)) ? "s’" + sInfi : "se " + sInfi;
            }
        }
        if (bNeg) {
            sInfi = "ne pas " + sInfi;
        }
        if (bTpsCo) {
            sInfi += " " + this._seekPpas(bPro, bFem, (this._sRawInfo[5] == "r"));
        }
        if (bInt) {
            sInfi += " … ?";
        }
        return sInfi;
    };

    participePasse (sWho) {
        return this.dConj.get(":PQ").get(sWho);
    };

    participePresent (bPro, bNeg, bTpsCo, bInt, bFem) {
        if (!this.dConj.get(":PQ").get(":P")) {
            return "";
        }
        let sPartPre;
        if (bTpsCo) {
            sPartPre = (!bPro) ? _getConjWithTags(this.sVerbAux, this._tTagsAux, ":PQ", ":P") : getConj("être", ":PQ", ":P");
        } else {
            sPartPre = this.dConj.get(":PQ").get(":P");
        }
        if (sPartPre === "") {
            return "";
        }
        let bEli = _zStartVoy.test(sPartPre);
        if (bPro) {
            if (this.bProWithEn) {
                sPartPre = "s’en " + sPartPre;
            } else {
                sPartPre = (bEli) ? "s’" + sPartPre : "se " + sPartPre;
            }
        }
        if (bNeg) {
            sPartPre = (bEli && !bPro) ? "n’" + sPartPre + " pas" : "ne " + sPartPre + " pas";
        }
        if (bTpsCo) {
            sPartPre += " " + this._seekPpas(bPro, bFem, this._sRawInfo[5] == "r");
        }
        if (bInt) {
            sPartPre += " … ?";
        }
        return sPartPre;
    };

    conjugue (sTemps, sWho, bPro, bNeg, bTpsCo, bInt, bFem) {
        if (!this.dConj.get(sTemps).get(sWho)) {
            return "";
        }
        let sConj;
        if (!bTpsCo && bInt && sWho == ":1s" && this.dConj.get(sTemps)._get(":1ś", false)) {
            sWho = ":1ś";
        }
        if (bTpsCo) {
            sConj = (!bPro) ? _getConjWithTags(this.sVerbAux, this._tTagsAux, sTemps, sWho) : getConj("être", sTemps, sWho);
        } else {
            sConj = this.dConj.get(sTemps).get(sWho);
        }
        if (sConj === "") {
            return "";
        }
        let bEli = _zStartVoy.test(sConj);
        if (bPro) {
            if (!this.bProWithEn) {
                sConj = (bEli) ? _dProObjEl.get(sWho) + sConj : _dProObj.get(sWho) + sConj;
            } else {
                sConj = _dProObjEl.get(sWho) + "en " + sConj;
            }
        }
        if (bNeg) {
            sConj = (bEli && !bPro) ? "n’" + sConj : "ne " + sConj;
        }
        if (bInt) {
            if (sWho == ":3s" && !_zNeedTeuph.test(sConj)) {
                sConj += "-t";
            }
            sConj += "-" + this._getPronom(sWho, bFem);
        } else {
            if (sWho == ":1s" && bEli && !bNeg && !bPro) {
                sConj = "j’" + sConj;
            } else {
                sConj = this._getPronom(sWho, bFem) + " " + sConj;
            }
        }
        if (bNeg) {
            sConj += " pas";
        }
        if (bTpsCo) {
            sConj += " " + this._seekPpas(bPro, bFem, sWho.endsWith("p") || this._sRawInfo[5] == "r");
        }
        if (bInt) {
            sConj += " … ?";
        }
        return sConj;
    };

    _getPronom (sWho, bFem) {
        if (sWho == ":3s") {
            if (this._sRawInfo[5] == "r") {
                return "on";
            } else if (bFem) {
                return "elle";
            }
        } else if (sWho == ":3p" && bFem) {
            return "elles";
        }
        return _dProSuj.get(sWho);
    };

    imperatif (sWho, bPro, bNeg, bTpsCo, bFem) {
        if (!this.dConj.get(":E").get(sWho)) {
            return "";
        }
        let sImpe;
        if (bTpsCo) {
            sImpe = (!bPro) ? _getConjWithTags(this.sVerbAux, this._tTagsAux, ":E", sWho) : getConj("être", ":E", sWho);
        } else {
            sImpe = this.dConj.get(":E").get(sWho);
        }
        if (sImpe === "") {
            return "";
        }
        let bEli = _zStartVoy.test(sImpe);
        if (bNeg) {
            if (bPro) {
                if (!this.bProWithEn) {
                    sImpe = (bEli && sWho == ":2s") ? "ne t’" + sImpe + " pas" : _dImpeProNeg.get(sWho) + sImpe + " pas";
                } else {
                    sImpe = _dImpeProNegEn.get(sWho) + sImpe + " pas";
                }
            } else {
                sImpe = (bEli) ? "n’" + sImpe + " pas" : "ne " + sImpe + " pas";
            }
        } else if (bPro) {
            sImpe = (this.bProWithEn) ? sImpe + _dImpeProEn.get(sWho) : sImpe + _dImpePro.get(sWho);
        }
        if (bTpsCo) {
            return sImpe + " " + this._seekPpas(bPro, bFem, sWho.endsWith("p") || this._sRawInfo[5] == "r");
        }
        return sImpe;
    };

    _seekPpas (bPro, bFem, bPlur) {
        if (!bPro && this.sVerbAux == "avoir") {
            return this.dConj.get(":PQ").get(":Q1");
        }
        if (!bFem) {
            return (bPlur && this.dConj.get(":PQ").get(":Q2")) ? this.dConj.get(":PQ").get(":Q2") : this.dConj.get(":PQ").get(":Q1");
        }
        if (!bPlur) {
            return (this.dConj.get(":PQ").get(":Q3")) ? this.dConj.get(":PQ").get(":Q3") : this.dConj.get(":PQ").get(":Q1");
        }
        return (this.dConj.get(":PQ").get(":Q4")) ? this.dConj.get(":PQ").get(":Q4") : this.dConj.get(":PQ").get(":Q1");
    }
}

if (typeof(exports) !== 'undefined') {
    // Used for Grammalecte library.
    // In content scripts, these variable are directly reachable
    exports.Verb = Verb;
    exports.isVerb = isVerb;
    exports.getConj = getConj;
    exports.hasConj = hasConj;
    exports.getVtyp = getVtyp;
    exports.getSimil = getSimil;
    exports._getTags = _getTags;
    exports._hasConjWithTags = _hasConjWithTags;
    exports._getConjWithTags = _getConjWithTags;
}
