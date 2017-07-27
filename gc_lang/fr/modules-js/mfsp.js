// Grammalecte

"use strict";

const helpers = require("resource://grammalecte/helpers.js");
const echo = helpers.echo;

const oData = JSON.parse(helpers.loadFile("resource://grammalecte/fr/mfsp_data.json"));

// list of affix codes
const _lTagMiscPlur = oData.lTagMiscPlur;
const _lTagMasForm = oData.lTagMasForm;

// dictionary of words with uncommon plurals (-x, -ux, english, latin and italian plurals) and tags to generate them
const _dMiscPlur = helpers.objectToMap(oData.dMiscPlur);

// dictionary of feminine forms and tags to generate masculine forms (singular and plural)
const _dMasForm = helpers.objectToMap(oData.dMasForm);



function isFemForm (sWord) {
    // returns True if sWord exists in _dMasForm
    return _dMasForm.has(sWord);
}

function getMasForm (sWord, bPlur) {
    // returns masculine form with feminine form
    if (_dMasForm.has(sWord)) {
        return [ for (sTag of _whatSuffixCodes(sWord, bPlur))  _modifyStringWithSuffixCode(sWord, sTag) ];
    }
    return [];
}

function hasMiscPlural (sWord) {
    // returns True if sWord exists in dMiscPlur
    return _dMiscPlur.has(sWord);
}

function getMiscPlural (sWord) {
    // returns plural form with singular form
    if (_dMiscPlur.has(sWord)) {
        return [ for (sTag of _lTagMiscPlur[_dMiscPlur.get(sWord)].split("|"))  _modifyStringWithSuffixCode(sWord, sTag) ];
    }
    return [];
}

function _whatSuffixCodes (sWord, bPlur) {
    // necessary only for dMasFW
    let sSfx = _lTagMasForm[_dMasForm.get(sWord)];
    if (sSfx.includes("/")) {
        if (bPlur) {
            return sSfx.slice(sSfx.indexOf("/")+1).split("|");
        }
        return sSfx.slice(0, sSfx.indexOf("/")).split("|");
    }
    return sSfx.split("|");
}

function _modifyStringWithSuffixCode (sWord, sSfx) {
    // returns sWord modified by sSfx
    if (!sWord) {
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


if (typeof(exports) !== 'undefined') {
    exports.isFemForm = isFemForm;
    exports.getMasForm = getMasForm;
    exports.hasMiscPlural = hasMiscPlural;
    exports.getMiscPlural = getMiscPlural;
}
