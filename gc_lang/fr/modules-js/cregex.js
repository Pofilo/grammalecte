//// Grammalecte - Compiled regular expressions


///// Lemme
const zLemma = new RegExp("^>([a-zà-öø-ÿ0-9Ā-ʯ][a-zà-öø-ÿ0-9Ā-ʯ-]+)");

///// Masculin / féminin / singulier / pluriel
const zGender = new RegExp(":[mfe]");
const zNumber = new RegExp(":[spi]");

///// Nom et adjectif
const zNA = new RegExp(":[NA]");

//// nombre
const zNAs = new RegExp(":[NA].*:s");
const zNAp = new RegExp(":[NA].*:p");
const zNAi = new RegExp(":[NA].*:i");
const zNAsi = new RegExp(":[NA].*:[si]");
const zNApi = new RegExp(":[NA].*:[pi]");

//// genre
const zNAm = new RegExp(":[NA].*:m");
const zNAf = new RegExp(":[NA].*:f");
const zNAe = new RegExp(":[NA].*:e");
const zNAme = new RegExp(":[NA].*:[me]");
const zNAfe = new RegExp(":[NA].*:[fe]");

//// nombre et genre
// singuilier
const zNAms = new RegExp(":[NA].*:m.*:s");
const zNAfs = new RegExp(":[NA].*:f.*:s");
const zNAes = new RegExp(":[NA].*:e.*:s");
const zNAmes = new RegExp(":[NA].*:[me].*:s");
const zNAfes = new RegExp(":[NA].*:[fe].*:s");

// singulier et invariable
const zNAmsi = new RegExp(":[NA].*:m.*:[si]");
const zNAfsi = new RegExp(":[NA].*:f.*:[si]");
const zNAesi = new RegExp(":[NA].*:e.*:[si]");
const zNAmesi = new RegExp(":[NA].*:[me].*:[si]");
const zNAfesi = new RegExp(":[NA].*:[fe].*:[si]");

// pluriel
const zNAmp = new RegExp(":[NA].*:m.*:p");
const zNAfp = new RegExp(":[NA].*:f.*:p");
const zNAep = new RegExp(":[NA].*:e.*:p");
const zNAmep = new RegExp(":[NA].*:[me].*:p");
const zNAfep = new RegExp(":[NA].*:[me].*:p");

// pluriel et invariable
const zNAmpi = new RegExp(":[NA].*:m.*:[pi]");
const zNAfpi = new RegExp(":[NA].*:f.*:[pi]");
const zNAepi = new RegExp(":[NA].*:e.*:[pi]");
const zNAmepi = new RegExp(":[NA].*:[me].*:[pi]");
const zNAfepi = new RegExp(":[NA].*:[fe].*:[pi]");

//// Divers
const zAD = new RegExp(":[AB]");

///// Verbe
const zVconj = new RegExp(":[123][sp]");
const zVconj123 = new RegExp(":V[123].*:[123][sp]");

///// Nom | Adjectif | Verbe
const zNVconj = new RegExp(":(?:N|[123][sp])");
const zNAVconj = new RegExp(":(?:N|A|[123][sp])");

///// Spécifique
const zNnotA = new RegExp(":N(?!:A)");
const zPNnotA = new RegExp(":(?:N(?!:A)|Q)");

///// Noms propres
const zNP = new RegExp(":(?:M[12P]|T)");
const zNPm = new RegExp(":(?:M[12P]|T):m");
const zNPf = new RegExp(":(?:M[12P]|T):f");
const zNPe = new RegExp(":(?:M[12P]|T):e");


///// FONCTIONS

function getLemmaOfMorph (sMorph) {
    return zLemma.exec(sMorph)[1];
}

function checkAgreement (l1, l2) {
    // check number agreement
    if (!mbInv(l1) && !mbInv(l2)) {
        if (mbSg(l1) && !mbSg(l2)) {
            return false;
        }
        if (mbPl(l1) && !mbPl(l2)) {
            return false;
        }
    }
    // check gender agreement
    if (mbEpi(l1) || mbEpi(l2)) {
        return true;
    }
    if (mbMas(l1) && !mbMas(l2)) {
        return false;
    }
    if (mbFem(l1) && !mbFem(l2)) {
        return false;
    }
    return true;
}

function checkConjVerb (lMorph, sReqConj) {
    return lMorph.some(s  =>  s.includes(sReqConj));
}

function getGender (lMorph) {
    // returns gender of word (':m', ':f', ':e' or empty string).
    let sGender = "";
    for (let sMorph of lMorph) {
        let m = zGender.exec(sMorph);
        if (m) {
            if (!sGender) {
                sGender = m[0];
            } else if (sGender != m[0]) {
                return ":e";
            }
        }
    }
    return sGender;
}

function getNumber (lMorph) {
    // returns number of word (':s', ':p', ':i' or empty string).
    let sNumber = "";
    for (let sMorph of lMorph) {
        let m = zNumber.exec(sWord);
        if (m) {
            if (!sNumber) {
                sNumber = m[0];
            } else if (sNumber != m[0]) {
                return ":i";
            }
        }
    }
    return sNumber;
}

// NOTE :  isWhat (lMorph)    returns true   if lMorph contains nothing else than What
//         mbWhat (lMorph)    returns true   if lMorph contains What at least once

//// isXXX = it’s certain

function isNom (lMorph) {
    return lMorph.every(s  =>  s.includes(":N"));
}

function isNomNotAdj (lMorph) {
    return lMorph.every(s  =>  zNnotA.test(s));
}

function isAdj (lMorph) {
    return lMorph.every(s  =>  s.includes(":A"));
}

function isNomAdj (lMorph) {
    return lMorph.every(s  =>  zNA.test(s));
}

function isNomVconj (lMorph) {
    return lMorph.every(s  =>  zNVconj.test(s));
}

function isInv (lMorph) {
    return lMorph.every(s  =>  s.includes(":i"));
}
function isSg (lMorph) {
    return lMorph.every(s  =>  s.includes(":s"));
}
function isPl (lMorph) {
    return lMorph.every(s  =>  s.includes(":p"));
}
function isEpi (lMorph) {
    return lMorph.every(s  =>  s.includes(":e"));
}
function isMas (lMorph) {
    return lMorph.every(s  =>  s.includes(":m"));
}
function isFem (lMorph) {
    return lMorph.every(s  =>  s.includes(":f"));
}


//// mbXXX = MAYBE XXX

function mbNom (lMorph) {
    return lMorph.some(s  =>  s.includes(":N"));
}

function mbAdj (lMorph) {
    return lMorph.some(s  =>  s.includes(":A"));
}

function mbAdjNb (lMorph) {
    return lMorph.some(s  =>  zAD.test(s));
}

function mbNomAdj (lMorph) {
    return lMorph.some(s  =>  zNA.test(s));
}

function mbNomNotAdj (lMorph) {
    let b = false;
    for (let s of lMorph) {
        if (s.includes(":A")) {
            return false;
        }
        if (s.includes(":N")) {
            b = true;
        }
    }
    return b;
}

function mbPpasNomNotAdj (lMorph) {
    return lMorph.some(s  =>  zPNnotA.test(s));
}

function mbVconj (lMorph) {
    return lMorph.some(s  =>  zVconj.test(s));
}

function mbVconj123 (lMorph) {
    return lMorph.some(s  =>  zVconj123.test(s));
}

function mbMG (lMorph) {
    return lMorph.some(s  =>  s.includes(":G"));
}

function mbInv (lMorph) {
    return lMorph.some(s  =>  s.includes(":i"));
}
function mbSg (lMorph) {
    return lMorph.some(s  =>  s.includes(":s"));
}
function mbPl (lMorph) {
    return lMorph.some(s  =>  s.includes(":p"));
}
function mbEpi (lMorph) {
    return lMorph.some(s  =>  s.includes(":e"));
}
function mbMas (lMorph) {
    return lMorph.some(s  =>  s.includes(":m"));
}
function mbFem (lMorph) {
    return lMorph.some(s  =>  s.includes(":f"));
}

function mbNpr (lMorph) {
    return lMorph.some(s  =>  zNP.test(s));
}

function mbNprMasNotFem (lMorph) {
    if (lMorph.some(s  =>  zNPf.test(s))) {
        return false;
    }
    return lMorph.some(s  =>  zNPm.test(s));
}



exports.getLemmaOfMorph = getLemmaOfMorph;
exports.checkAgreement = checkAgreement;
exports.checkConjVerb = checkConjVerb;
exports.getGender = getGender;
exports.getNumber = getNumber;
exports.isNom = isNom;
exports.isNomNotAdj = isNomNotAdj;
exports.isAdj = isAdj;
exports.isNomAdj = isNomAdj;
exports.isNomVconj = isNomVconj;
exports.isInv = isInv;
exports.isSg = isSg;
exports.isPl = isPl;
exports.isEpi = isEpi;
exports.isMas = isMas;
exports.isFem = isFem;
exports.mbNom = mbNom;
exports.mbAdj = mbAdj;
exports.mbAdjNb = mbAdjNb;
exports.mbNomAdj = mbNomAdj;
exports.mbNomNotAdj = mbNomNotAdj;
exports.mbPpasNomNotAdj = mbPpasNomNotAdj;
exports.mbVconj = mbVconj;
exports.mbVconj123 = mbVconj123;
exports.mbMG = mbMG;
exports.mbInv = mbInv;
exports.mbSg = mbSg;
exports.mbPl = mbPl;
exports.mbEpi = mbEpi;
exports.mbMas = mbMas;
exports.mbFem = mbFem;
exports.mbNpr = mbNpr;
exports.mbNprMasNotFem = mbNprMasNotFem;
