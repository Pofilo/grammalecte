// GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

/* jshint esversion:6 */
/* jslint esversion:6 */

function g_morphVC (oToken, sPattern, sNegPattern="") {
    let nEnd = oToken["sValue"].lastIndexOf("-");
    if (oToken["sValue"].gl_count("-") > 1) {
        if (oToken["sValue"].includes("-t-")) {
            nEnd = nEnd - 2;
        }
        else if (oToken["sValue"].search(/-l(?:es?|a)-(?:[mt]oi|nous|leur)$|(?:[nv]ous|lui|leur)-en$/) != -1) {
            nEnd = oToken["sValue"].slice(0,nEnd).lastIndexOf("-");
        }
    }
    return g_morph(oToken, sPattern, sNegPattern, 0, nEnd, false);
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

function g_checkAgreement (oToken1, oToken2, bNotOnlyNames=true) {
    // check agreement between <oToken1> and <oToken2>
    let lMorph1 = oToken1.hasOwnProperty("lMorph") ? oToken1["lMorph"] : _oSpellChecker.getMorph(oToken1["sValue"]);
    if (lMorph1.length === 0) {
        return true;
    }
    let lMorph2 = oToken2.hasOwnProperty("lMorph") ? oToken2["lMorph"] : _oSpellChecker.getMorph(oToken2["sValue"]);
    if (lMorph2.length === 0) {
        return true;
    }
    if (bNotOnlyNames && !(cregex.mbAdj(lMorph2) || cregex.mbAdjNb(lMorph1))) {
        return false;
    }
    return cregex.checkAgreement(lMorph1, lMorph2);
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
