// Grammalecte - Suggestion phonétique

if (typeof(exports) !== 'undefined') {
    var helpers = require("resource://grammalecte/helpers.js");
}


const _oData = JSON.parse(helpers.loadFile("resource://grammalecte/fr/phonet_data.json"));
const _dWord = helpers.objectToMap(_oData.dWord);
const _lSet = _oData.lSet;
const _dMorph = helpers.objectToMap(_oData.dMorph);


var phonet = {
    hasSimil: function (sWord, sPattern=null) {
        // return True if there is list of words phonetically similar to sWord
        if (!sWord) {
            return false;
        }
        if (_dWord.has(sWord)) {
            if (sPattern) {
                return this.getSimil(sWord).some(sSimil => _dMorph.gl_get(sSimil, []).some(sMorph => sMorph.search(sPattern) >= 0));
            }
            return true;
        }
        if (sWord.slice(0,1).gl_isUpperCase()) {
            sWord = sWord.toLowerCase();
            if (_dWord.has(sWord)) {
                if (sPattern) {
                    return this.getSimil(sWord).some(sSimil => _dMorph.gl_get(sSimil, []).some(sMorph => sMorph.search(sPattern) >= 0));
                }
                return true;
            }
        }
        return false;
    },

    getSimil: function (sWord) {
        // return list of words phonetically similar to sWord
        if (!sWord) {
            return [];
        }
        if (_dWord.has(sWord)) {
            return _lSet[_dWord.get(sWord)];
        }
        if (sWord.slice(0,1).gl_isUpperCase()) {
            sWord = sWord.toLowerCase();
            if (_dWord.has(sWord)) {
                return _lSet[_dWord.get(sWord)];
            }
        }
        return [];
    },

    selectSimil: function (sWord, sPattern) {
        // return list of words phonetically similar to sWord and whom POS is matching sPattern
        if (!sPattern) {
            return new Set(this.getSimil(sWord));
        }
        let aSelect = new Set();
        for (let sSimil of this.getSimil(sWord)) {
            for (let sMorph of _dMorph.gl_get(sSimil, [])) {
                if (sMorph.search(sPattern) >= 0) {
                    aSelect.add(sSimil);
                }
            }
        }
        return aSelect;
    }
}


if (typeof(exports) !== 'undefined') {
    exports.hasSimil = phonet.hasSimil;
    exports.getSimil = phonet.getSimil;
    exports.selectSimil = phonet.selectSimil;
}
