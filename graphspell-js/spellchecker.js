// Spellchecker
// Wrapper for the IBDAWG class.
// Useful to check several dictionaries at once.

// To avoid iterating over a pile of dictionaries, it is assumed that 3 are enough:
// - the main dictionary, bundled with the package
// - the extended dictionary, added by an organization
// - the personal dictionary, created by the user for its own convenience


"use strict";


if (typeof(require) !== 'undefined') {
    var ibdawg = require("resource://grammalecte/graphspell/ibdawg.js");
}


${map}


const dDefaultDictionaries = new Map([
    ["fr", "fr.json"],
    ["en", "en.json"]
]);


class Spellchecker {

    constructor (sLangCode, mainDic=null, extentedDic=null, personalDic=null, sPath="") {
        // returns true if the main dictionary is loaded
        this.sLangCode = sLangCode;
        console.log(sLangCode);
        console.log(mainDic);
        if (mainDic === null) {
            mainDic = dDefaultDictionaries.gl_get(sLangCode, "");
        }
        this.oMainDic = this._loadDictionary(mainDic, sPath, true);
        this.oExtendedDic = this._loadDictionary(extentedDic, sPath);
        this.oPersonalDic = this._loadDictionary(personalDic, sPath);
    }

    _loadDictionary (dictionary, sPath, bNecessary=false) {
        // returns an IBDAWG object
        if (dictionary === null) {
            return null;
        }
        try {
        	if (typeof(require) !== 'undefined') {
        		console.log(">>>> <resource:>");
                return new ibdawg.IBDAWG(dictionary);  // dictionary can be a filename or a JSON object
            } else {
            	console.log(">>>> no <resource:>");
                return new IBDAWG(dictionary, sPath);  // dictionary can be a filename or a JSON object
            }
        }
        catch (e) {
        	if (bNecessary) {
        		throw e.message;
        	}
            console.log(e.message);
            return null;
        }
    }

    setMainDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oMainDic = this._loadDictionary(dictionary);
        return bool(this.oMainDic);
    }

    setExtendedDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oExtendedDic = this._loadDictionary(dictionary);
        return bool(this.oExtendedDic);
    }

    setPersonalDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oPersonalDic = this._loadDictionary(dictionary);
        return bool(this.oPersonalDic);
    }

    // IBDAWG functions

    isValidToken (sToken) {
        // checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)
        if (this.oMainDic.isValidToken(sToken)) {
            return true;
        }
        if (this.oExtendedDic && this.oExtendedDic.isValidToken(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.isValidToken(sToken)) {
            return true;
        }
        return false;
    }

    isValid (sWord) {
        // checks if sWord is valid (different casing tested if the first letter is a capital)
        if (this.oMainDic.isValid(sToken)) {
            return true;
        }
        if (this.oExtendedDic && this.oExtendedDic.isValid(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.isValid(sToken)) {
            return true;
        }
        return false;
    }

    lookup (sWord) {
        // checks if sWord is in dictionary as is (strict verification)
        if (this.oMainDic.lookup(sToken)) {
            return true;
        }
        if (this.oExtendedDic && this.oExtendedDic.lookup(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.lookup(sToken)) {
            return true;
        }
        return false;
    }

    getMorph (sWord) {
        // retrieves morphologies list, different casing allowed
        let lResult = this.oMainDic.getMorph(sToken);
        if (this.oExtendedDic) {
            lResult.extends(this.oExtendedDic.getMorph(sToken));
        }
        if (this.oPersonalDic) {
            lResult.extends(this.oPersonalDic.getMorph(sToken));
        }
        return lResult;
    }

    * suggest (sWord, nSuggLimit=10) {
        // generator: returns 1,2 or 3 lists of suggestions
        yield this.oMainDic.suggest(sWord, nSuggLimit);
        if (this.oExtendedDic) {
            yield this.oExtendedDic.suggest(sWord, nSuggLimit);
        }
        if (this.oPersonalDic) {
            yield this.oPersonalDic.suggest(sWord, nSuggLimit);
        }
    }

    * select (sPattern="") {
        // generator: returns all entries which morphology fits <sPattern>
        yield* this.oMainDic.select(sPattern)
        if (this.oExtendedDic) {
            yield* this.oExtendedDic.select(sPattern);
        }
        if (this.oPersonalDic) {
            yield* this.oPersonalDic.select(sPattern);
        }
    }
}

if (typeof(exports) !== 'undefined') {
    exports.Spellchecker = Spellchecker;
}
