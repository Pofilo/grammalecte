// Spellchecker
// Wrapper for the IBDAWG class.
// Useful to check several dictionaries at once.

// To avoid iterating over a pile of dictionaries, it is assumed that 3 are enough:
// - the main dictionary, bundled with the package
// - the extended dictionary
// - the community dictionary, added by an organization
// - the personal dictionary, created by the user for its own convenience


"use strict";


if (typeof(require) !== 'undefined') {
    var ibdawg = require("resource://grammalecte/graphspell/ibdawg.js");
    var tokenizer = require("resource://grammalecte/graphspell/tokenizer.js");
}


${map}


const dDefaultDictionaries = new Map([
    ["fr", "fr.json"],
    ["en", "en.json"]
]);


class SpellChecker {

    constructor (sLangCode, sPath="", mainDic="", extentedDic="", communityDic="", personalDic="") {
        // returns true if the main dictionary is loaded
        this.sLangCode = sLangCode;
        if (!mainDic) {
            mainDic = dDefaultDictionaries.gl_get(sLangCode, "");
        }
        this.oMainDic = this._loadDictionary(mainDic, sPath, true);
        this.oExtendedDic = this._loadDictionary(extentedDic, sPath);
        this.oCommunityDic = this._loadDictionary(communityDic, sPath);
        this.oPersonalDic = this._loadDictionary(personalDic, sPath);
        this.oTokenizer = null;
    }

    _loadDictionary (dictionary, sPath, bNecessary=false) {
        // returns an IBDAWG object
        if (!dictionary) {
            return null;
        }
        try {
            if (typeof(ibdawg) !== 'undefined') {
                return new ibdawg.IBDAWG(dictionary);  // dictionary can be a filename or a JSON object
            } else {
                return new IBDAWG(dictionary, sPath);  // dictionary can be a filename or a JSON object
            }
        }
        catch (e) {
            let sfDictionary = (typeof(dictionary) == "string") ? dictionary : dictionary.sLangName + "/" + dictionary.sFileName;
            if (bNecessary) {
                throw "Error: <" + sfDictionary + "> not loaded. " + e.message;
            }
            console.log("Error: <" + sfDictionary + "> not loaded.")
            console.log(e.message);
            return null;
        }
    }

    loadTokenizer () {
        if (typeof(tokenizer) !== 'undefined') {
            this.oTokenizer = new tokenizer.Tokenizer(this.sLangCode);
        } else {
            this.oTokenizer = new Tokenizer(this.sLangCode);
        }
    }

    getTokenizer () {
        if (!this.oTokenizer) {
            this.loadTokenizer();
        }
        return this.oTokenizer;
    }

    setMainDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oMainDic = this._loadDictionary(dictionary);
        return Boolean(this.oMainDic);
    }

    setExtendedDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oExtendedDic = this._loadDictionary(dictionary);
        return Boolean(this.oExtendedDic);
    }

    setCommunityDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oCommunityDic = this._loadDictionary(dictionary);
        return Boolean(this.oCommunityDic);
    }

    setPersonalDictionary (dictionary) {
        // returns true if the dictionary is loaded
        this.oPersonalDic = this._loadDictionary(dictionary);
        return Boolean(this.oPersonalDic);
    }

    // parse text functions

    parseParagraph (sText) {
        if (!this.oTokenizer) {
            this.loadTokenizer();
        }
        let aSpellErr = [];
        for (let oToken of this.oTokenizer.genTokens(sText)) {
            if (oToken.sType === 'WORD' && !this.isValidToken(oToken.sValue)) {
                aSpellErr.push(oToken);
            }
        }
        return aSpellErr;
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
        if (this.oCommunityDic && this.oCommunityDic.isValidToken(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.isValidToken(sToken)) {
            return true;
        }
        return false;
    }

    isValid (sWord) {
        // checks if sWord is valid (different casing tested if the first letter is a capital)
        if (this.oMainDic.isValid(sWord)) {
            return true;
        }
        if (this.oExtendedDic && this.oExtendedDic.isValid(sWord)) {
            return true;
        }
        if (this.oCommunityDic && this.oCommunityDic.isValid(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.isValid(sWord)) {
            return true;
        }
        return false;
    }

    lookup (sWord) {
        // checks if sWord is in dictionary as is (strict verification)
        if (this.oMainDic.lookup(sWord)) {
            return true;
        }
        if (this.oExtendedDic && this.oExtendedDic.lookup(sWord)) {
            return true;
        }
        if (this.oCommunityDic && this.oCommunityDic.lookup(sToken)) {
            return true;
        }
        if (this.oPersonalDic && this.oPersonalDic.lookup(sWord)) {
            return true;
        }
        return false;
    }

    getMorph (sWord) {
        // retrieves morphologies list, different casing allowed
        let lResult = this.oMainDic.getMorph(sWord);
        if (this.oExtendedDic) {
            lResult.push(...this.oExtendedDic.getMorph(sWord));
        }
        if (this.oCommunityDic) {
            lResult.push(...this.oCommunityDic.getMorph(sWord));
        }
        if (this.oPersonalDic) {
            lResult.push(...this.oPersonalDic.getMorph(sWord));
        }
        return lResult;
    }

    * suggest (sWord, nSuggLimit=10) {
        // generator: returns 1, 2 or 3 lists of suggestions
        yield this.oMainDic.suggest(sWord, nSuggLimit);
        if (this.oExtendedDic) {
            yield this.oExtendedDic.suggest(sWord, nSuggLimit);
        }
        if (this.oCommunityDic) {
            yield this.oCommunityDic.suggest(sWord, nSuggLimit);
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
        if (this.oCommunityDic) {
            yield* this.oCommunityDic.select(sPattern);
        }
        if (this.oPersonalDic) {
            yield* this.oPersonalDic.select(sPattern);
        }
    }
}

if (typeof(exports) !== 'undefined') {
    exports.SpellChecker = SpellChecker;
}
