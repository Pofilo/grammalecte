// GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

/* jshint esversion:6 */
/* jslint esversion:6 */

function g_morphVC (dToken, sPattern, sNegPattern="") {
    let nEnd = dToken["sValue"].lastIndexOf("-");
    if (dToken["sValue"].includes("-t-")) {
        nEnd = nEnd - 2;
    }
    return g_morph(dToken, sPattern, sNegPattern, 0, nEnd, false);
}

function rewriteSubject (s1, s2) {
    // s1 is supposed to be prn/patr/npr (M[12P])
    if (s2 == "lui") {
        return "ils";
    }
    if (s2 == "moi") {
        return "nous";
    }
    if (s2 == "toi") {
        return "vous";
    }
    if (s2 == "nous") {
        return "nous";
    }
    if (s2 == "vous") {
        return "vous";
    }
    if (s2 == "eux") {
        return "ils";
    }
    if (s2 == "elle" || s2 == "elles") {
        if (cregex.mbNprMasNotFem(_oSpellChecker.getMorph(s1))) {
            return "ils";
        }
        // si épicène, indéterminable, mais OSEF, le féminin l’emporte
        return "elles";
    }
    return s1 + " et " + s2;
}

function apposition (sWord1, sWord2) {
    // returns true if nom + nom (no agreement required)
    return sWord2.length < 2 || (cregex.mbNomNotAdj(_oSpellChecker.getMorph(sWord2)) && cregex.mbPpasNomNotAdj(_oSpellChecker.getMorph(sWord1)));
}

function isAmbiguousNAV (sWord) {
    // words which are nom|adj and verb are ambiguous (except être and avoir)
    let lMorph = _oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0) {
        return false;
    }
    if (!cregex.mbNomAdj(lMorph) || sWord == "est") {
        return false;
    }
    if (cregex.mbVconj(lMorph) && !cregex.mbMG(lMorph)) {
        return true;
    }
    return false;
}

function isAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj) {
    //// use it if sWord1 won’t be a verb; word2 is assumed to be true via isAmbiguousNAV
    let lMorph2 = _oSpellChecker.getMorph(sWord2);
    if (lMorph2.length === 0) {
        return false;
    }
    if (cregex.checkConjVerb(lMorph2, sReqMorphConj)) {
        // verb word2 is ok
        return false;
    }
    let lMorph1 = _oSpellChecker.getMorph(sWord1);
    if (lMorph1.length === 0) {
        return false;
    }
    if (cregex.checkAgreement(lMorph1, lMorph2) && (cregex.mbAdj(lMorph2) || cregex.mbAdj(lMorph1))) {
        return false;
    }
    return true;
}

function isVeryAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj, bLastHopeCond) {
    //// use it if sWord1 can be also a verb; word2 is assumed to be true via isAmbiguousNAV
    let lMorph2 = _oSpellChecker.getMorph(sWord2);
    if (lMorph2.length === 0) {
        return false;
    }
    if (cregex.checkConjVerb(lMorph2, sReqMorphConj)) {
        // verb word2 is ok
        return false;
    }
    let lMorph1 = _oSpellChecker.getMorph(sWord1);
    if (lMorph1.length === 0) {
        return false;
    }
    if (cregex.checkAgreement(lMorph1, lMorph2) && (cregex.mbAdj(lMorph2) || cregex.mbAdjNb(lMorph1))) {
        return false;
    }
    // now, we know there no agreement, and conjugation is also wrong
    if (cregex.isNomAdj(lMorph1)) {
        return true;
    }
    //if cregex.isNomAdjVerb(lMorph1): # considered true
    if (bLastHopeCond) {
        return true;
    }
    return false;
}

function checkAgreement (sWord1, sWord2) {
    let lMorph2 = _oSpellChecker.getMorph(sWord2);
    if (lMorph2.length === 0) {
        return true;
    }
    let lMorph1 = _oSpellChecker.getMorph(sWord1);
    if (lMorph1.length === 0) {
        return true;
    }
    return cregex.checkAgreement(lMorph1, lMorph2);
}

function mbUnit (s) {
    if (/[µ\/⁰¹²³⁴⁵⁶⁷⁸⁹Ωℓ·]/.test(s)) {
        return true;
    }
    if (s.length > 1 && s.length < 16 && s.slice(0, 1).gl_isLowerCase() && (!s.slice(1).gl_isLowerCase() || /[0-9]/.test(s))) {
        return true;
    }
    return false;
}


// Exceptions

const aREGULARPLURAL = new Set(["abricot", "amarante", "aubergine", "acajou", "anthracite", "brique", "caca", "café",
                                "carotte", "cerise", "chataigne", "corail", "citron", "crème", "grave", "groseille",
                                "jonquille", "marron", "olive", "pervenche", "prune", "sable"]);
const aSHOULDBEVERB = new Set(["aller", "manger"]);
