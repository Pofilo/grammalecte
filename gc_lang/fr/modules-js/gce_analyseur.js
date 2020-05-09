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
