// Grammalecte

"use strict";

const helpers = require("resource://grammalecte/helpers.js");

const _oData = JSON.parse(helpers.loadFile("resource://grammalecte/fr/mfsp_data.json"));

// list of affix codes
const _lTagMiscPlur = _oData.lTagMiscPlur;
const _lTagMasForm = _oData.lTagMasForm;

// dictionary of words with uncommon plurals (-x, -ux, english, latin and italian plurals) and tags to generate them
const _dMiscPlur = helpers.objectToMap(_oData.dMiscPlur);

// dictionary of feminine forms and tags to generate masculine forms (singular and plural)
const _dMasForm = helpers.objectToMap(_oData.dMasForm);


var mfsp = {
    isFemForm: function (sWord) {
        // returns True if sWord exists in _dMasForm
        return _dMasForm.has(sWord);
    },

    getMasForm: function (sWord, bPlur) {
        // returns masculine form with feminine form
        if (_dMasForm.has(sWord)) {
            return [ for (sTag of this._whatSuffixCode(sWord, bPlur))  this._modifyStringWithSuffixCode(sWord, sTag) ];
        }
        return [];
    },

    hasMiscPlural: function (sWord) {
        // returns True if sWord exists in dMiscPlur
        return _dMiscPlur.has(sWord);
    },

    getMiscPlural: function (sWord) {
        // returns plural form with singular form
        if (_dMiscPlur.has(sWord)) {
            return [ for (sTag of _lTagMiscPlur[_dMiscPlur.get(sWord)].split("|"))  this._modifyStringWithSuffixCode(sWord, sTag) ];
        }
        return [];
    },

    _whatSuffixCode: function (sWord, bPlur) {
        // necessary only for dMasFW
        let sSfx = _lTagMasForm[_dMasForm.get(sWord)];
        if (sSfx.includes("/")) {
            if (bPlur) {
                return sSfx.slice(sSfx.indexOf("/")+1).split("|");
            }
            return sSfx.slice(0, sSfx.indexOf("/")).split("|");
        }
        return sSfx.split("|");
    },

    _modifyStringWithSuffixCode: function (sWord, sSfx) {
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
}


if (typeof(exports) !== 'undefined') {
    exports.isFemForm = mfsp.isFemForm;
    exports.getMasForm = mfsp.getMasForm;
    exports.hasMiscPlural = mfsp.hasMiscPlural;
    exports.getMiscPlural = mfsp.getMiscPlural;
    exports._whatSuffixCode = mfsp._whatSuffixCode;
    exports._modifyStringWithSuffixCode = mfsp._modifyStringWithSuffixCode;
}
