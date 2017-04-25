//// GRAMMAR CHECKING ENGINE PLUGIN: Parsing functions for French language

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
        // We don’t check if word exists in _dAnalyses, for it is assumed it has been done before
        if (cr.mbNprMasNotFem(_dAnalyses._get(s1, ""))) {
            return "ils";
        }
        // si épicène, indéterminable, mais OSEF, le féminin l’emporte
        return "elles";
    }
    return s1 + " et " + s2;
}

function apposition (sWord1, sWord2) {
    // returns true if nom + nom (no agreement required)
    // We don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    return cr.mbNomNotAdj(_dAnalyses._get(sWord2, "")) && cr.mbPpasNomNotAdj(_dAnalyses._get(sWord1, ""));
}

function isAmbiguousNAV (sWord) {
    // words which are nom|adj and verb are ambiguous (except être and avoir)
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return false;
    }
    if (!cr.mbNomAdj(_dAnalyses._get(sWord, "")) || sWord == "est") {
        return false;
    }
    if (cr.mbVconj(_dAnalyses._get(sWord, "")) && !cr.mbMG(_dAnalyses._get(sWord, ""))) {
        return true;
    }
    return false;
}

function isAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj) {
    //// use it if sWord1 won’t be a verb; word2 is assumed to be true via isAmbiguousNAV
    // We don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let a2 = _dAnalyses._get(sWord2, null);
    if (!a2 || a2.length === 0) {
        return false;
    }
    if (cr.checkConjVerb(a2, sReqMorphConj)) {
        // verb word2 is ok
        return false;
    }
    let a1 = _dAnalyses._get(sWord1, null);
    if (!a1 || a1.length === 0) {
        return false;
    }
    if (cr.checkAgreement(a1, a2) && (cr.mbAdj(a2) || cr.mbAdj(a1))) {
        return false;
    }
    return true;
}

function isVeryAmbiguousAndWrong (sWord1, sWord2, sReqMorphNA, sReqMorphConj, bLastHopeCond) {
    //// use it if sWord1 can be also a verb; word2 is assumed to be true via isAmbiguousNAV
    // We don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let a2 = _dAnalyses._get(sWord2, null)
    if (!a2 || a2.length === 0) {
        return false;
    }
    if (cr.checkConjVerb(a2, sReqMorphConj)) {
        // verb word2 is ok
        return false;
    }
    let a1 = _dAnalyses._get(sWord1, null);
    if (!a1 || a1.length === 0) {
        return false;
    }
    if (cr.checkAgreement(a1, a2) && (cr.mbAdj(a2) || cr.mbAdjNb(a1))) {
        return false;
    }
    // now, we know there no agreement, and conjugation is also wrong
    if (cr.isNomAdj(a1)) {
        return true;
    }
    //if cr.isNomAdjVerb(a1): # considered true
    if (bLastHopeCond) {
        return true;
    }
    return false;
}

function checkAgreement (sWord1, sWord2) {
    // We don’t check if word exists in _dAnalyses, for it is assumed it has been done before
    let a2 = _dAnalyses._get(sWord2, null)
    if (!a2 || a2.length === 0) {
        return true;
    }
    let a1 = _dAnalyses._get(sWord1, null);
    if (!a1 || a1.length === 0) {
        return true;
    }
    return cr.checkAgreement(a1, a2);
}

function mbUnit (s) {
    if (/[µ\/⁰¹²³⁴⁵⁶⁷⁸⁹Ωℓ·]/.test(s)) {
        return true;
    }
    if (s.length > 1 && s.length < 16 && s.slice(0, 1)._isLowerCase() && (!s.slice(1)._isLowerCase() || /[0-9]/.test(s))) {
        return true;
    }
    return false;
}


//// Syntagmes

const _zEndOfNG1 = new RegExp ("^ *$|^ +(?:, +|)(?:n(?:’|e |o(?:u?s|tre) )|l(?:’|e(?:urs?|s|) |a )|j(?:’|e )|m(?:’|es? |a |on )|t(?:’|es? |a |u )|s(?:’|es? |a )|c(?:’|e(?:t|tte|s|) )|ç(?:a |’)|ils? |vo(?:u?s|tre) )");
const _zEndOfNG2 = new RegExp ("^ +([a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ][a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ-]+)");
const _zEndOfNG3 = new RegExp ("^ *, +([a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ][a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ-]+)");

function isEndOfNG (dDA, s, iOffset) {
    if (_zEndOfNG1.test(s)) {
        return true;
    }
    let m = _zEndOfNG2._exec2(s, ["$"]);
    if (m && morphex(dDA, [iOffset+m.start[1], m[1]], ":[VR]", ":[NAQP]")) {
        return true;
    }
    m = _zEndOfNG3._exec2(s, ["$"]);
    if (m && !morph(dDA, [iOffset+m.start[1], m[1]], ":[NA]", false)) {
        return true;
    }
    return false;
}


const _zNextIsNotCOD1 = new RegExp ("^ *,");
const _zNextIsNotCOD2 = new RegExp ("^ +(?:[mtsnj](e +|’)|[nv]ous |tu |ils? |elles? )");
const _zNextIsNotCOD3 = new RegExp ("^ +([a-zéèî][a-zà-öA-Zø-ÿÀ-ÖØ-ßĀ-ʯ-]+)");

function isNextNotCOD (dDA, s, iOffset) {
    if (_zNextIsNotCOD1.test(s) || _zNextIsNotCOD2.test(s)) {
        return true;
    }
    let m = _zNextIsNotCOD3._exec2(s, ["$"]);
    if (m && morphex(dDA, [iOffset+m.start[1], m[1]], ":[123][sp]", ":[DM]")) {
        return true;
    }
    return false;
}


const _zNextIsVerb1 = new RegExp ("^ +[nmts](?:e |’)");
const _zNextIsVerb2 = new RegExp ("^ +([a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ][a-zà-öA-Zø-ÿÀ-Ö0-9_Ø-ßĀ-ʯ-]+)");

function isNextVerb (dDA, s, iOffset) {
    if (_zNextIsVerb1.test(s)) {
        return true;
    }
    let m = _zNextIsVerb2._exec2(s, ["$"]);
    if (m && morph(dDA, [iOffset+m.start[1], m[1]], ":[123][sp]", false)) {
        return true;
    }
    return false;
}


//// Exceptions

const aREGULARPLURAL = new Set(["abricot", "amarante", "aubergine", "acajou", "anthracite", "brique", "caca", "café",
                                "carotte", "cerise", "chataigne", "corail", "citron", "crème", "grave", "groseille",
                                "jonquille", "marron", "olive", "pervenche", "prune", "sable"]);
const aSHOULDBEVERB = new Set(["aller", "manger"]);
