//// GRAMMAR CHECKING ENGINE PLUGIN: Suggestion mechanisms

if (typeof(exports) !== 'undefined') {
    var conj = require("resource://grammalecte/fr/conj.js");
    var mfsp = require("resource://grammalecte/fr/mfsp.js");
    var phonet = require("resource://grammalecte/fr/phonet.js");
}


//// verbs

function suggVerb (sFlex, sWho, funcSugg2=null) {
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    for (let sStem of stem(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            // we get the tense
            let aTense = new Set();
            for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
                let m;
                let zVerb = new RegExp (sStem+" .*?(:(?:Y|I[pqsf]|S[pq]|K))", "g");
                while (m = zVerb.exec(sMorph)) {
                    // stem must be used in regex to prevent confusion between different verbs (e.g. sauras has 2 stems: savoir and saurer)
                    if (m) {
                        if (m[1] === ":Y") {
                            aTense.add(":Ip");
                            aTense.add(":Iq");
                            aTense.add(":Is");
                        } else if (m[1] === ":P") {
                            aTense.add(":Ip");
                        } else {
                            aTense.add(m[1]);
                        }
                    }
                }
            }
            for (let sTense of aTense) {
                if (sWho === ":1ś" && !conj._hasConjWithTags(tTags, sTense, ":1ś")) {
                    sWho = ":1s";
                }
                if (conj._hasConjWithTags(tTags, sTense, sWho)) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, sTense, sWho));
                }
            }
        }
    }
    if (funcSugg2) {
        let aSugg2 = funcSugg2(sFlex);
        if (aSugg2.size > 0) {
            aSugg.add(aSugg2);
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbPpas (sFlex, sWhat=null) {
    let aSugg = new Set();
    for (let sStem of stem(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            if (!sWhat) {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"));
                aSugg.delete("");
            } else if (sWhat === ":m:s") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
            } else if (sWhat === ":m:p") {
                if (conj._hasConjWithTags(tTags, ":PQ", ":Q2")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
                }
            } else if (sWhat === ":f:s") {
                if (conj._hasConjWithTags(tTags, ":PQ", ":Q3")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
                }
            } else if (sWhat === ":f:p") {
                if (conj._hasConjWithTags(tTags, ":PQ", ":Q4")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
                }
            } else if (sWhat === ":s") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q3"));
                aSugg.delete("");
            } else if (sWhat === ":p") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q2"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q4"));
                aSugg.delete("");
            } else {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":PQ", ":Q1"));
            }
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbTense (sFlex, sTense, sWho) {
    let aSugg = new Set();
    for (let sStem of stem(sFlex)) {
        if (conj.hasConj(sStem, sTense, sWho)) {
            aSugg.add(conj.getConj(sStem, sTense, sWho));
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbImpe (sFlex) {
    let aSugg = new Set();
    for (let sStem of stem(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            if (conj._hasConjWithTags(tTags, ":E", ":2s")) {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":2s"));
            }
            if (conj._hasConjWithTags(tTags, ":E", ":1p")) {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":1p"));
            }
            if (conj._hasConjWithTags(tTags, ":E", ":2p")) {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":E", ":2p"));
            }
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbInfi (sFlex) {
    //return stem(sFlex).join("|");
    return [ for (sStem of stem(sFlex)) if (conj.isVerb(sStem)) sStem ].join("|");
}


const _dQuiEst = new Map ([
    ["je", ":1s"], ["j’", ":1s"], ["j’en", ":1s"], ["j’y", ":1s"],
    ["tu", ":2s"], ["il", ":3s"], ["on", ":3s"], ["elle", ":3s"],
    ["nous", ":1p"], ["vous", ":2p"], ["ils", ":3p"], ["elles", ":3p"]
]);
const _lIndicatif = [":Ip", ":Iq", ":Is", ":If"];
const _lSubjonctif = [":Sp", ":Sq"];

function suggVerbMode (sFlex, cMode, sSuj) {
    let lMode;
    if (cMode == ":I") {
        lMode = _lIndicatif;
    } else if (cMode == ":S") {
        lMode = _lSubjonctif;
    } else if (cMode.startsWith(":I") || cMode.startsWith(":S")) {
        lMode = [cMode];
    } else {
        return "";
    }
    let sWho = _dQuiEst.gl_get(sSuj.toLowerCase(), null);
    if (!sWho) {
        if (sSuj[0].gl_isLowerCase()) { // pas un pronom, ni un nom propre
            return "";
        }
        sWho = ":3s";
    }
    let aSugg = new Set();
    for (let sStem of stem(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            for (let sTense of lMode) {
                if (conj._hasConjWithTags(tTags, sTense, sWho)) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, sTense, sWho));
                }
            }
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

//// Nouns and adjectives

function suggPlur (sFlex, sWordToAgree=null) {
    // returns plural forms assuming sFlex is singular
    if (sWordToAgree) {
        if (!_dAnalyses.has(sWordToAgree) && !_storeMorphFromFSA(sWordToAgree)) {
            return "";
        }
        let sGender = cregex.getGender(_dAnalyses.gl_get(sWordToAgree, []));
        if (sGender == ":m") {
            return suggMasPlur(sFlex);
        } else if (sGender == ":f") {
            return suggFemPlur(sFlex);
        }
    }
    let aSugg = new Set();
    if (!sFlex.includes("-")) {
        if (sFlex.endsWith("l")) {
            if (sFlex.endsWith("al") && sFlex.length > 2 && _oDict.isValid(sFlex.slice(0,-1)+"ux")) {
                aSugg.add(sFlex.slice(0,-1)+"ux");
            }
            if (sFlex.endsWith("ail") && sFlex.length > 3 && _oDict.isValid(sFlex.slice(0,-2)+"ux")) {
                aSugg.add(sFlex.slice(0,-2)+"ux");
            }
        }
        if (_oDict.isValid(sFlex+"s")) {
            aSugg.add(sFlex+"s");
        }
        if (_oDict.isValid(sFlex+"x")) {
            aSugg.add(sFlex+"x");
        }
    }
    if (mfsp.hasMiscPlural(sFlex)) {
        mfsp.getMiscPlural(sFlex).forEach(function(x) { aSugg.add(x); });
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggSing (sFlex) {
    // returns singular forms assuming sFlex is plural
    if (sFlex.includes("-")) {
        return "";
    }
    let aSugg = new Set();
    if (sFlex.endsWith("ux")) {
        if (_oDict.isValid(sFlex.slice(0,-2)+"l")) {
            aSugg.add(sFlex.slice(0,-2)+"l");
        }
        if (_oDict.isValid(sFlex.slice(0,-2)+"il")) {
            aSugg.add(sFlex.slice(0,-2)+"il");
        }
    }
    if (_oDict.isValid(sFlex.slice(0,-1))) {
        aSugg.add(sFlex.slice(0,-1));
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggMasSing (sFlex, bSuggSimil=false) {
    // returns masculine singular forms
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":m") || sMorph.includes(":e")) {
                aSugg.add(suggSing(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isFemForm(sStem)) {
                    mfsp.getMasForm(sStem, false).forEach(function(x) { aSugg.add(x); });
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":PQ", ":Q1") && conj.hasConj(sVerb, ":PQ", ":Q3")) {
                // We also check if the verb has a feminine form.
                // If not, we consider it’s better to not suggest the masculine one, as it can be considered invariable.
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q1"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":m:[si]")) {
            aSugg.add(e);
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggMasPlur (sFlex, bSuggSimil=false) {
    // returns masculine plural forms
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":m") || sMorph.includes(":e")) {
                aSugg.add(suggPlur(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isFemForm(sStem)) {
                    mfsp.getMasForm(sStem, true).forEach(function(x) { aSugg.add(x); });
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":PQ", ":Q2")) {
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q2"));
            } else if (conj.hasConj(sVerb, ":PQ", ":Q1")) {
                let sSugg = conj.getConj(sVerb, ":PQ", ":Q1");
                // it is necessary to filter these flexions, like “succédé” or “agi” that are not masculine plural
                if (sSugg.endsWith("s")) {
                    aSugg.add(sSugg);
                }
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":m:[pi]")) {
            aSugg.add(e);
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}


function suggFemSing (sFlex, bSuggSimil=false) {
    // returns feminine singular forms
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":f") || sMorph.includes(":e")) {
                aSugg.add(suggSing(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isFemForm(sStem)) {
                    aSugg.add(sStem);
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":PQ", ":Q3")) {
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q3"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":f:[si]")) {
            aSugg.add(e);
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggFemPlur (sFlex, bSuggSimil=false) {
    // returns feminine plural forms
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":f") || sMorph.includes(":e")) {
                aSugg.add(suggPlur(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isFemForm(sStem)) {
                    aSugg.add(sStem+"s");
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":PQ", ":Q4")) {
                aSugg.add(conj.getConj(sVerb, ":PQ", ":Q4"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":f:[pi]")) {
            aSugg.add(e);
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function hasFemForm (sFlex) {
    for (let sStem of stem(sFlex)) {
        if (mfsp.isFemForm(sStem) || conj.hasConj(sStem, ":PQ", ":Q3")) {
            return true;
        }
    }
    if (phonet.hasSimil(sFlex, ":f")) {
        return true;
    }
    return false;
}

function hasMasForm (sFlex) {
    for (let sStem of stem(sFlex)) {
        if (mfsp.isFemForm(sStem) || conj.hasConj(sStem, ":PQ", ":Q1")) {
            // what has a feminine form also has a masculine form
            return true;
        }
    }
    if (phonet.hasSimil(sFlex, ":m")) {
        return true;
    }
    return false;
}

function switchGender (sFlex, bPlur=null) {
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let aSugg = new Set();
    if (bPlur === null) {
        for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
            if (sMorph.includes(":f")) {
                if (sMorph.includes(":s")) {
                    aSugg.add(suggMasSing(sFlex));
                } else if (sMorph.includes(":p")) {
                    aSugg.add(suggMasPlur(sFlex));
                }
            } else if (sMorph.includes(":m")) {
                if (sMorph.includes(":s")) {
                    aSugg.add(suggFemSing(sFlex));
                } else if (sMorph.includes(":p")) {
                    aSugg.add(suggFemPlur(sFlex));
                } else {
                    aSugg.add(suggFemSing(sFlex));
                    aSugg.add(suggFemPlur(sFlex));
                }
            }
        }
    } else if (bPlur) {
        for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
            if (sMorph.includes(":f")) {
                aSugg.add(suggMasPlur(sFlex));
            } else if (sMorph.includes(":m")) {
                aSugg.add(suggFemPlur(sFlex));
            }
        }
    } else {
        for (let sMorph of _dAnalyses.gl_get(sFlex, [])) {
            if (sMorph.includes(":f")) {
                aSugg.add(suggMasSing(sFlex));
            } else if (sMorph.includes(":m")) {
                aSugg.add(suggFemSing(sFlex));
            }
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function switchPlural (sFlex) {
    let aSugg = new Set();
    for (let sMorph of _dAnalyses.gl_get(sFlex, [])) { // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
        if (sMorph.includes(":s")) {
            aSugg.add(suggPlur(sFlex));
        } else if (sMorph.includes(":p")) {
            aSugg.add(suggSing(sFlex));
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function hasSimil (sWord, sPattern=null) {
    return phonet.hasSimil(sWord, sPattern);
}

function suggSimil (sWord, sPattern) {
    // return list of words phonetically similar to sWord and whom POS is matching sPattern
    let aSugg = phonet.selectSimil(sWord, sPattern);
    for (let sMorph of _dAnalyses.gl_get(sWord, [])) {
        for (let e of conj.getSimil(sWord, sMorph, sPattern)) {
            aSugg.add(e); 
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggCeOrCet (sWord) {
    if (/^[aeéèêiouyâîï]/i.test(sWord)) {
        return "cet";
    }
    if (sWord[0] == "h" || sWord[0] == "H") {
        return "ce|cet";
    }
    return "ce";
}

function suggLesLa (sWord) {
    // we don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    if (_dAnalyses.gl_get(sWord, []).some(s  =>  s.includes(":p"))) {
        return "les|la";
    }
    return "la";
}

function formatNumber (s) {
    let nLen = s.length;
    if (nLen < 4 ) {
        return s;
    }
    let sRes = "";
    // nombre ordinaire
    let nEnd = nLen;
    while (nEnd > 0) {
        let nStart = Math.max(nEnd-3, 0);
        sRes = sRes ? s.slice(nStart, nEnd) + " " + sRes : sRes = s.slice(nStart, nEnd);
        nEnd = nEnd - 3;
    }
    // binaire
    if (/^[01]+$/.test(s)) {
        nEnd = nLen;
        let sBin = "";
        while (nEnd > 0) {
            let nStart = Math.max(nEnd-4, 0);
            sBin = sBin ? s.slice(nStart, nEnd) + " " + sBin : sBin = s.slice(nStart, nEnd);
            nEnd = nEnd - 4;
        }
        sRes += "|" + sBin;
    }
    // numéros de téléphone
    if (nLen == 10) {
        if (s.startsWith("0")) {
            sRes += "|" + s.slice(0,2) + " " + s.slice(2,4) + " " + s.slice(4,6) + " " + s.slice(6,8) + " " + s.slice(8);   // téléphone français
            if (s[1] == "4" && (s[2]=="7" || s[2]=="8" || s[2]=="9")) {
                sRes += "|" + s.slice(0,4) + " " + s.slice(4,6) + " " + s.slice(6,8) + " " + s.slice(8);    // mobile belge
            }
            sRes += "|" + s.slice(0,3) + " " + s.slice(3,6) + " " + s.slice(6,8) + " " + s.slice(8);        // téléphone suisse
        }
        sRes += "|" + s.slice(0,4) + " " + s.slice(4,7) + "-" + s.slice(7);                                 // téléphone canadien ou américain
    } else if (nLen == 9 && s.startsWith("0")) {
        sRes += "|" + s.slice(0,3) + " " + s.slice(3,5) + " " + s.slice(5,7) + " " + s.slice(7,9);          // fixe belge 1
        sRes += "|" + s.slice(0,2) + " " + s.slice(2,5) + " " + s.slice(5,7) + " " + s.slice(7,9);          // fixe belge 2
    }
    return sRes;
}

function formatNF (s) {
    try {
        let m = /NF[  -]?(C|E|P|Q|S|X|Z|EN(?:[  -]ISO|))[  -]?([0-9]+(?:[\/‑-][0-9]+|))/i.exec(s);
        if (!m) {
            return "";
        }
        return "NF " + m[1].toUpperCase().replace(/ /g, " ").replace(/-/g, " ") + " " + m[2].replace(/\//g, "‑").replace(/-/g, "‑");
    }
    catch (e) {
        helpers.logerror(e);
        return "# erreur #";
    }
}

function undoLigature (c) {
    if (c == "ﬁ") {
        return "fi";
    } else if (c == "ﬂ") {
        return "fl";
    } else if (c == "ﬀ") {
        return "ff";
    } else if (c == "ﬃ") {
        return "ffi";
    } else if (c == "ﬄ") {
        return "ffl";
    } else if (c == "ﬅ") {
        return "ft";
    } else if (c == "ﬆ") {
        return "st";
    }
    return "_";
}
