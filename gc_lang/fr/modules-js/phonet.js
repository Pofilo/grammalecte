// Grammalecte - Suggestion phonétique

const helpers = require("resource://grammalecte/helpers.js");
const echo = helpers.echo;

const oData = JSON.parse(helpers.loadFile("resource://grammalecte/fr/phonet_data.json"));

const _dWord = helpers.objectToMap(oData.dWord);
const _lSet = oData.lSet;
const _dMorph = helpers.objectToMap(oData.dMorph);



function hasSimil (sWord, sPattern=null) {
    // return True if there is list of words phonetically similar to sWord
    if (!sWord) {
        return false;
    }
    if (_dWord.has(sWord)) {
        if (sPattern) {
            return getSimil(sWord).some(sSimil => _dMorph.gl_get(sSimil, []).some(sMorph => sMorph.search(sPattern) >= 0));
        }
        return true;
    }
    if (sWord.slice(0,1).gl_isUpperCase()) {
        sWord = sWord.toLowerCase();
        if (_dWord.has(sWord)) {
            if (sPattern) {
                return getSimil(sWord).some(sSimil => _dMorph.gl_get(sSimil, []).some(sMorph => sMorph.search(sPattern) >= 0));
            }
            return true;
        }
    }
    return false;
}

function getSimil (sWord) {
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
}

function selectSimil (sWord, sPattern) {
    // return list of words phonetically similar to sWord and whom POS is matching sPattern
    if (!sPattern) {
        return new Set(getSimil(sWord));
    }
    let aSelect = new Set();
    for (let sSimil of getSimil(sWord)) {
        for (let sMorph of _dMorph.gl_get(sSimil, [])) {
            if (sMorph.search(sPattern) >= 0) {
                aSelect.add(sSimil);
            }
        }
    }
    return aSelect;
}


if (typeof(exports) !== 'undefined') {
    exports.hasSimil = hasSimil;
    exports.getSimil = getSimil;
    exports.selectSimil = selectSimil;
}
