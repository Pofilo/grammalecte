// GRAMMAR CHECKING ENGINE PLUGIN: Suggestion mechanisms

/* jshint esversion:6 */
/* jslint esversion:6 */
/* global require */

if (typeof(process) !== 'undefined') {
    var conj = require("./conj.js");
    var mfsp = require("./mfsp.js");
    var phonet = require("./phonet.js");
}


//// verbs

function splitVerb (sVerb) {
    // renvoie le verbe et les pronoms séparément
    let iRight = sVerb.lastIndexOf("-");
    let sSuffix = sVerb.slice(iRight);
    sVerb = sVerb.slice(0, iRight);
    if (sVerb.endsWith("-t") || sVerb.endsWith("-le") || sVerb.endsWith("-la") || sVerb.endsWith("-les") || sVerb.endsWith("-nous") || sVerb.endsWith("-vous") || sVerb.endsWith("-leur") || sVerb.endsWith("-lui")) {
        iRight = sVerb.lastIndexOf("-");
        sSuffix = sVerb.slice(iRight) + sSuffix;
        sVerb = sVerb.slice(0, iRight);
    }
    return [sVerb, sSuffix];
}

function suggVerb (sFlex, sWho, bVC=false, funcSugg2=null, ...args) {
    let sSfx;
    if (bVC) {
        [sFlex, sSfx] = splitVerb(sFlex);
    }
    let aSugg = new Set();
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            // we get the tense
            let aTense = new Set();
            for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
                let m;
                let zVerb = new RegExp (">"+sStem+"/.*?(:(?:Y|I[pqsf]|S[pq]|K|P|Q))", "g");
                while ((m = zVerb.exec(sMorph)) !== null) {
                    // stem must be used in regex to prevent confusion between different verbs (e.g. sauras has 2 stems: savoir and saurer)
                    if (m) {
                        if (m[1] === ":Y" || m[1] == ":Q") {
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
        let sSugg2 = (args.length > 0) ? funcSugg2(...args) : funcSugg2(sFlex);
        if (sSugg2.length > 0) {
            aSugg.add(sSugg2);
        }
    }
    if (aSugg.size > 0) {
        if (bVC) {
            return Array.from(aSugg).map((sSugg) => joinVerbAndSuffix(sSugg, sSfx)).join("|");
        }
        return Array.from(aSugg).join("|");
    }
    return "";
}

function joinVerbAndSuffix (sFlex, sSfx) {
    if (/^-t-/i.test(sSfx) && /[td]$/i.test(sFlex)) {
        return sFlex + sSfx.slice(2);
    }
    if (/[eac]$/i.test(sFlex)) {
        if (/^-(?:en|y)$/i.test(sSfx)) {
            return sFlex + "s" + sSfx;
        }
        if (/^-(?:ie?l|elle|on)$/i.test(sSfx)) {
            return sFlex + "-t" + sSfx;
        }
    }
    return sFlex + sSfx;
}

function suggVerbPpas (sFlex, sWhat=null) {
    let aSugg = new Set();
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            if (!sWhat) {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:p"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:s"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:p"));
                aSugg.delete("");
            } else if (sWhat === ":m:s") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
            } else if (sWhat === ":m:p") {
                if (conj._hasConjWithTags(tTags, ":Q", ":m:p")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:p"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
                }
            } else if (sWhat === ":f:s") {
                if (conj._hasConjWithTags(tTags, ":Q", ":f:s")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:s"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
                }
            } else if (sWhat === ":f:p") {
                if (conj._hasConjWithTags(tTags, ":Q", ":f:p")) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:p"));
                } else {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
                }
            } else if (sWhat === ":s") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:s"));
                aSugg.delete("");
            } else if (sWhat === ":p") {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:p"));
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":f:p"));
                aSugg.delete("");
            } else {
                aSugg.add(conj._getConjWithTags(sStem, tTags, ":Q", ":m:s"));
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
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        if (conj.hasConj(sStem, sTense, sWho)) {
            aSugg.add(conj.getConj(sStem, sTense, sWho));
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbFrom (sStem, sFlex, sWho="") {
    "conjugate <sStem> according to <sFlex> (and eventually <sWho>)"
    let aSugg = new Set();
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
        let lTenses = [ ...sMorph.matchAll(/:(?:Y|I[pqsf]|S[pq]|K|P)/g) ];
        if (sWho) {
            for (let [sTense, ] of lTenses) {
                if (conj.hasConj(sStem, sTense, sWho)) {
                    aSugg.add(conj.getConj(sStem, sTense, sWho));
                }
            }
        }
        else {
            for (let [sTense, ] of lTenses) {
                for (let [sWho, ] of [ ...sMorph.matchAll(/:(?:[123][sp]|P|Y)/g) ]) {
                    if (conj.hasConj(sStem, sTense, sWho)) {
                        aSugg.add(conj.getConj(sStem, sTense, sWho));
                    }
                }
            }
        }
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}


function suggVerbImpe (sFlex, bVC=false) {
    let sSfx;
    if (bVC) {
        [sFlex, sSfx] = splitVerb(sFlex);
    }
    let aSugg = new Set();
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
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
        if (bVC) {
            return Array.from(aSugg).map((sSugg) => joinVerbAndSuffix(sSugg, sSfx)).join("|");
        }
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggVerbInfi (sFlex) {
    return gc_engine.oSpellChecker.getLemma(sFlex).filter(sStem => conj.isVerb(sStem)).join("|");
}


const _dQuiEst = new Map ([
    ["je", ":1s"], ["j’", ":1s"], ["tu", ":2s"], ["il", ":3s"], ["on", ":3s"], ["elle", ":3s"], ["iel", ":3s"],
    ["nous", ":1p"], ["vous", ":2p"], ["ils", ":3p"], ["elles", ":3p"], ["iels", ":3p"]
]);

const _dModeSugg = new Map([ ["es", "aies"], ["aies", "es"], ["est", "ait"], ["ait", "est"] ]);

function suggVerbMode (sFlex, cMode, sSuj) {
    let lMode;
    if (cMode == ":I") {
        lMode = [":Ip", ":Iq", ":Is", ":If"];
    } else if (cMode == ":S") {
        lMode = [":Sp", ":Sq"];
    } else if (cMode.startsWith(":I") || cMode.startsWith(":S")) {
        lMode = [cMode];
    } else {
        return "";
    }
    let sWho = _dQuiEst.gl_get(sSuj.toLowerCase(), ":3s");
    let aSugg = new Set();
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        let tTags = conj._getTags(sStem);
        if (tTags) {
            for (let sTense of lMode) {
                if (conj._hasConjWithTags(tTags, sTense, sWho)) {
                    aSugg.add(conj._getConjWithTags(sStem, tTags, sTense, sWho));
                }
            }
        }
    }
    if (_dModeSugg.has(sFlex)) {
        aSugg.add(_dModeSugg.get(sFlex));
    }
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

//// Nouns and adjectives

function suggPlur (sFlex, bSelfSugg=false) {
    // returns plural forms assuming sFlex is singular
    let aSugg = new Set();
    if (sFlex.endsWith("l")) {
        if (sFlex.endsWith("al") && sFlex.length > 2 && gc_engine.oSpellChecker.isValid(sFlex.slice(0,-1)+"ux")) {
            aSugg.add(sFlex.slice(0,-1)+"ux");
        }
        if (sFlex.endsWith("ail") && sFlex.length > 3 && gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"ux")) {
            aSugg.add(sFlex.slice(0,-2)+"ux");
        }
    }
    if (sFlex.endsWith("L")) {
        if (sFlex.endsWith("AL") && sFlex.length > 2 && gc_engine.oSpellChecker.isValid(sFlex.slice(0,-1)+"UX")) {
            aSugg.add(sFlex.slice(0,-1)+"UX");
        }
        if (sFlex.endsWith("AIL") && sFlex.length > 3 && gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"UX")) {
            aSugg.add(sFlex.slice(0,-2)+"UX");
        }
    }
    if (sFlex.slice(-1).gl_isLowerCase()) {
        if (gc_engine.oSpellChecker.isValid(sFlex+"s")) {
            aSugg.add(sFlex+"s");
        }
        if (gc_engine.oSpellChecker.isValid(sFlex+"x")) {
            aSugg.add(sFlex+"x");
        }
    } else {
        if (gc_engine.oSpellChecker.isValid(sFlex+"S")) {
            aSugg.add(sFlex+"S");
        }
        if (gc_engine.oSpellChecker.isValid(sFlex+"X")) {
            aSugg.add(sFlex+"X");
        }
    }
    if (mfsp.hasMiscPlural(sFlex)) {
        mfsp.getMiscPlural(sFlex).forEach(function(x) { aSugg.add(x); });
    }
    if (aSugg.size == 0 && bSelfSugg && (sFlex.endsWith("s") || sFlex.endsWith("x") || sFlex.endsWith("S") || sFlex.endsWith("X"))) {
        aSugg.add(sFlex);
    }
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggSing (sFlex, bSelfSugg=true) {
    // returns singular forms assuming sFlex is plural
    let aSugg = new Set();
    if (sFlex.endsWith("ux")) {
        if (gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"l")) {
            aSugg.add(sFlex.slice(0,-2)+"l");
        }
        if (gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"il")) {
            aSugg.add(sFlex.slice(0,-2)+"il");
        }
    }
    if (sFlex.endsWith("UX")) {
        if (gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"L")) {
            aSugg.add(sFlex.slice(0,-2)+"L");
        }
        if (gc_engine.oSpellChecker.isValid(sFlex.slice(0,-2)+"IL")) {
            aSugg.add(sFlex.slice(0,-2)+"IL");
        }
    }
    if ((sFlex.endsWith("s") || sFlex.endsWith("x") || sFlex.endsWith("S") || sFlex.endsWith("X")) && gc_engine.oSpellChecker.isValid(sFlex.slice(0,-1))) {
        aSugg.add(sFlex.slice(0,-1));
    }
    if (bSelfSugg && aSugg.size == 0) {
        aSugg.add(sFlex);
    }
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggMasSing (sFlex, bSuggSimil=false) {
    // returns masculine singular forms
    let aSugg = new Set();
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":m") || sMorph.includes(":e")) {
                aSugg.add(suggSing(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isMasForm(sStem)) {
                    aSugg.add(sStem);
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":Q", ":m:s") && conj.hasConj(sVerb, ":Q", ":f:s")) {
                // We also check if the verb has a feminine form.
                // If not, we consider it’s better to not suggest the masculine one, as it can be considered invariable.
                aSugg.add(conj.getConj(sVerb, ":Q", ":m:s"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":m:[si]")) {
            aSugg.add(e);
        }
    }
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggMasPlur (sFlex, bSuggSimil=false) {
    // returns masculine plural forms
    let aSugg = new Set();
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":m") || sMorph.includes(":e")) {
                aSugg.add(suggPlur(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isMasForm(sStem)) {
                    aSugg.add(suggPlur(sStem, true));
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":Q", ":m:p")) {
                aSugg.add(conj.getConj(sVerb, ":Q", ":m:p"));
            } else if (conj.hasConj(sVerb, ":Q", ":m:s")) {
                let sSugg = conj.getConj(sVerb, ":Q", ":m:s");
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
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}


function suggFemSing (sFlex, bSuggSimil=false) {
    // returns feminine singular forms
    let aSugg = new Set();
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":f") || sMorph.includes(":e")) {
                aSugg.add(suggSing(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isMasForm(sStem)) {
                    mfsp.getFemForm(sStem, false).forEach(function(x) { aSugg.add(x); });
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":Q", ":f:s")) {
                aSugg.add(conj.getConj(sVerb, ":Q", ":f:s"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":f:[si]")) {
            aSugg.add(e);
        }
    }
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggFemPlur (sFlex, bSuggSimil=false) {
    // returns feminine plural forms
    let aSugg = new Set();
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
        if (!sMorph.includes(":V")) {
            // not a verb
            if (sMorph.includes(":f") || sMorph.includes(":e")) {
                aSugg.add(suggPlur(sFlex));
            } else {
                let sStem = cregex.getLemmaOfMorph(sMorph);
                if (mfsp.isMasForm(sStem)) {
                    mfsp.getFemForm(sStem, true).forEach(function(x) { aSugg.add(x); });
                }
            }
        } else {
            // a verb
            let sVerb = cregex.getLemmaOfMorph(sMorph);
            if (conj.hasConj(sVerb, ":Q", ":f:p")) {
                aSugg.add(conj.getConj(sVerb, ":Q", ":f:p"));
            }
        }
    }
    if (bSuggSimil) {
        for (let e of phonet.selectSimil(sFlex, ":f:[pi]")) {
            aSugg.add(e);
        }
    }
    aSugg.delete("");
    if (aSugg.size > 0) {
        return Array.from(aSugg).join("|");
    }
    return "";
}

function suggAgree (sFlexDst, sFlexSrc) {
    // returns suggestions for <sFlexDst> that matches agreement with <sFlexSrc>
    let lMorphSrc = gc_engine.oSpellChecker.getMorph(sFlexSrc);
    if (lMorphSrc.length === 0) {
        return "";
    }
    let [sGender, sNumber] = cregex.getGenderNumber(lMorphSrc);
    if (sGender == ":m") {
        if (sNumber == ":s") {
            return suggMasSing(sFlexDst);
        }
        else if (sNumber == ":p") {
            return suggMasPlur(sFlexDst);
        }
        return suggMasSing(sFlexDst);
    }
    else if (sGender == ":f") {
        if (sNumber == ":s") {
            return suggFemSing(sFlexDst);
        }
        else if (sNumber == ":p") {
            return suggFemPlur(sFlexDst);
        }
        return suggFemSing(sFlexDst);
    }
    else if (sGender == ":e") {
        if (sNumber == ":s") {
            return suggSing(sFlexDst);
        }
        else if (sNumber == ":p") {
            return suggPlur(sFlexDst);
        }
        return sFlexDst;
    }
    return "";
}

function g_suggAgree (oTokenDst, oTokenSrc) {
    // returns suggestions for <oTokenDst> that matches agreement with <oTokenSrc>
    let lMorphSrc = oTokenSrc.hasOwnProperty("lMorph") ? oTokenSrc["lMorph"] : gc_engine.oSpellChecker.getMorph(oTokenSrc["sValue"]);
    if (lMorphSrc.length === 0) {
        return "";
    }
    let [sGender, sNumber] = cregex.getGenderNumber(lMorphSrc);
    if (sGender == ":m") {
        if (sNumber == ":s") {
            return suggMasSing(oTokenDst["sValue"]);
        }
        else if (sNumber == ":p") {
            return suggMasPlur(oTokenDst["sValue"]);
        }
        return suggMasSing(oTokenDst["sValue"]);
    }
    else if (sGender == ":f") {
        if (sNumber == ":s") {
            return suggFemSing(oTokenDst["sValue"]);
        }
        else if (sNumber == ":p") {
            return suggFemPlur(oTokenDst["sValue"]);
        }
        return suggFemSing(oTokenDst["sValue"]);
    }
    else if (sGender == ":e") {
        if (sNumber == ":s") {
            return suggSing(oTokenDst["sValue"]);
        }
        else if (sNumber == ":p") {
            return suggPlur(oTokenDst["sValue"]);
        }
        return oTokenDst["sValue"];
    }
    return "";
}

function hasFemForm (sFlex) {
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        if (mfsp.isMasForm(sStem) || conj.hasConj(sStem, ":Q", ":f:s")) {
            return true;
        }
    }
    if (phonet.hasSimil(sFlex, ":f")) {
        return true;
    }
    return false;
}

function hasMasForm (sFlex) {
    for (let sStem of gc_engine.oSpellChecker.getLemma(sFlex)) {
        if (mfsp.isMasForm(sStem) || conj.hasConj(sStem, ":Q", ":m:s")) {
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
    let aSugg = new Set();
    if (bPlur === null) {
        for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
            if (sMorph.includes(":f")) {
                if (sMorph.includes(":s")) {
                    aSugg.add(suggMasSing(sFlex));
                } else if (sMorph.includes(":p")) {
                    aSugg.add(suggMasPlur(sFlex));
                } else {
                    aSugg.add(suggMasSing(sFlex));
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
        for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
            if (sMorph.includes(":f")) {
                aSugg.add(suggMasPlur(sFlex));
            } else if (sMorph.includes(":m")) {
                aSugg.add(suggFemPlur(sFlex));
            }
        }
    } else {
        for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
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
    for (let sMorph of gc_engine.oSpellChecker.getMorph(sFlex)) {
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

function suggSimil (sWord, sPattern=null, bSubst=false, bVC=false) {
    // return list of words phonetically similar to <sWord> and whom POS is matching <sPattern>
    let sSfx;
    if (bVC) {
        [sWord, sSfx] = splitVerb(sWord);
    }
    let aSugg = phonet.selectSimil(sWord, sPattern);
    if (aSugg.size === 0 && bSubst) {
        for (let sMorph of gc_engine.oSpellChecker.getMorph(sWord)) {
            if (sMorph.includes(":V")) {
                let sInfi = sMorph.slice(1, sMorph.indexOf("/"));
                if (sPattern) {
                    for (let sName of conj.getNamesFrom(sInfi)) {
                        if (_oSpellChecker.getMorph(sName).some(sMorph => (sMorph.search(sPattern) !== -1))) {
                            aSugg.add(sName);
                        }
                    }
                }
                else {
                    conj.getNamesFrom(sInfi).forEach(sName => aSugg.add(sName));
                }
                break;
            }
        }
    }
    if (aSugg.size > 0) {
        if (bVC) {
            return Array.from(aSugg).map((sSugg) => joinVerbAndSuffix(sSugg, sSfx)).join("|");
        }
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
    if (gc_engine.oSpellChecker.getMorph(sWord).some(s  =>  s.includes(":p"))) {
        return "les|la";
    }
    return "la";
}

function formatNumber (sNumber, bOnlySimpleFormat=false) {
    let nLen = sNumber.length;
    if (nLen < 4 ) {
        return sNumber;
    }
    let sRes = "";
    if (!sNumber.includes(",")) {
        // Nombre entier
        sRes = _formatNumber(sNumber, 3);
        if (!bOnlySimpleFormat) {
            // binaire
            if (/^[01]+$/.test(sNumber)) {
                sRes += "|" + _formatNumber(sNumber, 4);
            }
            // numéros de téléphone
            if (nLen == 10) {
                if (sNumber.startsWith("0")) {
                    sRes += "|" + _formatNumber(sNumber, 2);                                                                           // téléphone français
                    if (sNumber[1] == "4" && (sNumber[2]=="7" || sNumber[2]=="8" || sNumber[2]=="9")) {
                        sRes += "|" + sNumber.slice(0,4) + " " + sNumber.slice(4,6) + " " + sNumber.slice(6,8) + " " + sNumber.slice(8); // mobile belge
                    }
                    sRes += "|" + sNumber.slice(0,3) + " " + sNumber.slice(3,6) + " " + sNumber.slice(6,8) + " " + sNumber.slice(8);     // téléphone suisse
                }
                sRes += "|" + sNumber.slice(0,4) + " " + sNumber.slice(4,7) + "-" + sNumber.slice(7);                                   // téléphone canadien ou américain
            } else if (nLen == 9 && sNumber.startsWith("0")) {
                sRes += "|" + sNumber.slice(0,3) + " " + sNumber.slice(3,5) + " " + sNumber.slice(5,7) + " " + sNumber.slice(7,9);       // fixe belge 1
                sRes += "|" + sNumber.slice(0,2) + " " + sNumber.slice(2,5) + " " + sNumber.slice(5,7) + " " + sNumber.slice(7,9);       // fixe belge 2
            }
        }
    } else {
        // Nombre réel
        let [sInt, sFloat] = sNumber.split(",", 2);
        sRes = _formatNumber(sInt, 3) + "," + sFloat;
    }
    return sRes;
}

function _formatNumber (sNumber, nGroup=3) {
    let sRes = "";
    let nEnd = sNumber.length;
    while (nEnd > 0) {
        let nStart = Math.max(nEnd-nGroup, 0);
        sRes = sRes ? sNumber.slice(nStart, nEnd) + " " + sRes : sRes = sNumber.slice(nStart, nEnd);
        nEnd = nEnd - nGroup;
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
        console.error(e);
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


const _dNormalizedCharsForInclusiveWriting = new Map([
    ['(', '·'],  [')', '·'],
    ['.', '·'],  ['·', '·'],  ['•', '·'],
    ['–', '·'],  ['—', '·'],
    ['/', '·']
]);

function normalizeInclusiveWriting (sToken) {
    let sRes = "";
    for (let c of sToken) {
        if (_dNormalizedCharsForInclusiveWriting.has(c)) {
            sRes += _dNormalizedCharsForInclusiveWriting.get(c);
        } else {
            sRes += c;
        }
    }
    sRes = sRes.replace("èr·", "er·").replace("ÈR·", "ER·");
    return sRes;
}
