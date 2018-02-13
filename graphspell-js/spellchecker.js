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
    ["fr", "fr.bdic"],
    ["en", "en.bdic"]
]);


class Spellchecker {

    constructor (sLangCode, sfMainDic="", sfExtendedDic="", sfPersonalDic="") {
        // returns true if the main dictionary is loaded
        this.sLangCode = sLangCode;
        if (sfMainDic === "") {
            sfMainDic = dDefaultDictionaries.gl_get(sLangCode, "");
        }
        this.oMainDic = this._loadDictionary(sfMainDic);
        this.oExtendedDic = this._loadDictionary(sfExtendedDic);
        this.oPersonalDic = this._loadDictionary(sfPersonalDic);
        return bool(this.oMainDic);
    }

    _loadDictionary (sfDictionary) {
        // returns an IBDAWG object
        if (sfDictionary === "") {
            return null;
        }
        try {
            return ibdawg.IBDAWG(sfDictionary);
        }
        catch (e) {
            console.log("Error: <" + sDicName + "> not loaded.");
            console.log(e.message);
            return null;
        }
    }

    setMainDictionary (sfDictionary) {
        // returns true if the dictionary is loaded
        this.oMainDic = this._loadDictionary(sfDictionary);
        return bool(this.oMainDic);
    }

    setExtendedDictionary (sfDictionary) {
        // returns true if the dictionary is loaded
        this.oExtendedDic = this._loadDictionary(sfDictionary);
        return bool(this.oExtendedDic);
    }

    setPersonalDictionary (sfDictionary) {
        // returns true if the dictionary is loaded
        this.oPersonalDic = this._loadDictionary(sfDictionary);
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