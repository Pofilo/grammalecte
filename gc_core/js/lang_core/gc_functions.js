// JavaScript
// Grammar checker engine functions

${string}
${regex}
${map}


if (typeof(process) !== 'undefined') {
    var gc_options = require("./gc_options.js");
}


let _sAppContext = "JavaScript";        // what software is running
let _oSpellChecker = null;


//////// Common functions

function option (sOpt) {
    // return true if option sOpt is active
    return gc_options.dOptions.gl_get(sOpt, false);
}

function echo (x) {
    console.log(x);
    return true;
}

var re = {
    search: function (sRegex, sText) {
        if (sRegex.startsWith("(?i)")) {
            return sText.search(new RegExp(sRegex.slice(4), "i")) !== -1;
        } else {
            return sText.search(sRegex) !== -1;
        }
    },

    createRegExp: function (sRegex) {
        if (sRegex.startsWith("(?i)")) {
            return new RegExp(sRegex.slice(4), "i");
        } else {
            return new RegExp(sRegex);
        }
    }
}


//////// functions to get text outside pattern scope

// warning: check compile_rules.py to understand how it works

function nextword (s, iStart, n) {
    // get the nth word of the input string or empty string
    let z = new RegExp("^(?: +[a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ%_-]+){" + (n-1).toString() + "} +([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ%_-]+)", "ig");
    let m = z.exec(s.slice(iStart));
    if (!m) {
        return null;
    }
    return [iStart + z.lastIndex - m[1].length, m[1]];
}

function prevword (s, iEnd, n) {
    // get the (-)nth word of the input string or empty string
    let z = new RegExp("([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ%_-]+) +(?:[a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ%_-]+ +){" + (n-1).toString() + "}$", "i");
    let m = z.exec(s.slice(0, iEnd));
    if (!m) {
        return null;
    }
    return [m.index, m[1]];
}

function nextword1 (s, iStart) {
    // get next word (optimization)
    let _zNextWord = new RegExp ("^ +([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ_][a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ_-]*)", "ig");
    let m = _zNextWord.exec(s.slice(iStart));
    if (!m) {
        return null;
    }
    return [iStart + _zNextWord.lastIndex - m[1].length, m[1]];
}

const _zPrevWord = new RegExp ("([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ_][a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬀ-ﬆᴀ-ᶿ_-]*) +$", "i");

function prevword1 (s, iEnd) {
    // get previous word (optimization)
    let m = _zPrevWord.exec(s.slice(0, iEnd));
    if (!m) {
        return null;
    }
    return [m.index, m[1]];
}

function look (s, sPattern, sNegPattern=null) {
    // seek sPattern in s (before/after/fulltext), if antipattern sNegPattern not in s
    try {
        if (sNegPattern && re.search(sNegPattern, s)) {
            return false;
        }
        return re.search(sPattern, s);
    }
    catch (e) {
        console.error(e);
    }
    return false;
}


//////// Analyse groups for regex rules

function info (dTokenPos, aWord) {
    // for debugging: info of word
    if (!aWord) {
        console.log("> nothing to find");
        return true;
    }
    let lMorph = gc_engine.oSpellChecker.getMorph(aWord[1]);
    if (lMorph.length === 0) {
        console.log("> not in dictionary");
        return true;
    }
    if (dTokenPos.has(aWord[0])) {
        console.log("DA: " + dTokenPos.get(aWord[0]));
    }
    console.log("FSA: " + lMorph);
    return true;
}

function morph (dTokenPos, aWord, sPattern, sNegPattern, bNoWord=false) {
    // analyse a tuple (position, word), returns true if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)
    if (!aWord) {
        return bNoWord;
    }
    let lMorph = (dTokenPos.has(aWord[0])  &&  dTokenPos.get(aWord[0]))["lMorph"] ? dTokenPos.get(aWord[0])["lMorph"] : gc_engine.oSpellChecker.getMorph(aWord[1]);
    if (lMorph.length === 0) {
        return false;
    }
    if (sNegPattern) {
        // check negative condition
        if (sNegPattern === "*") {
            // all morph must match sPattern
            return lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
        }
        else {
            if (lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                return false;
            }
        }
    }
    // search sPattern
    return lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1));
}

function analyse (sWord, sPattern, sNegPattern) {
    // analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)
    let lMorph = gc_engine.oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0) {
        return false;
    }
    if (sNegPattern) {
        // check negative condition
        if (sNegPattern === "*") {
            // all morph must match sPattern
            return lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
        }
        else {
            if (lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                return false;
            }
        }
    }
    // search sPattern
    return lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1));
}


//// Analyse tokens for graph rules

function g_value (oToken, sValues, nLeft=null, nRight=null) {
    // test if <oToken['sValue']> is in sValues (each value should be separated with |)
    let sValue = (nLeft === null) ? "|"+oToken["sValue"]+"|" : "|"+oToken["sValue"].slice(nLeft, nRight)+"|";
    if (sValues.includes(sValue)) {
        return true;
    }
    if (oToken["sValue"].slice(0,2).gl_isTitle()) { // we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
        if (sValues.includes(sValue.toLowerCase())) {
            return true;
        }
    }
    else if (oToken["sValue"].gl_isUpperCase()) {
        //if sValue.lower() in sValues:
        //    return true;
        sValue = "|"+sValue.slice(1).gl_toCapitalize();
        if (sValues.includes(sValue)) {
            return true;
        }
        sValue = sValue.toLowerCase();
        if (sValues.includes(sValue)) {
            return true;
        }
    }
    return false;
}

function g_morph (oToken, sPattern, sNegPattern="", nLeft=null, nRight=null, bMemorizeMorph=true) {
    // analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies
    let lMorph;
    if (oToken.hasOwnProperty("lMorph")) {
        lMorph = oToken["lMorph"];
    }
    else {
        if (nLeft !== null) {
            let sValue = (nRight !== null) ? oToken["sValue"].slice(nLeft, nRight) : oToken["sValue"].slice(nLeft);
            lMorph = gc_engine.oSpellChecker.getMorph(sValue);
            if (bMemorizeMorph) {
                oToken["lMorph"] = lMorph;
            }
        } else {
            lMorph = gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
        }
    }
    if (lMorph.length == 0) {
        return false;
    }
    // check negative condition
    if (sNegPattern) {
        if (sNegPattern == "*") {
            // all morph must match sPattern
            return lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
        }
        else {
            if (lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                return false;
            }
        }
    }
    // search sPattern
    return lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1));
}

function g_morph0 (oToken, sPattern, sNegPattern="", nLeft=null, nRight=null, bMemorizeMorph=true) {
    // analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies
    let lMorph;
    if (nLeft !== null) {
        let sValue = (nRight !== null) ? oToken["sValue"].slice(nLeft, nRight) : oToken["sValue"].slice(nLeft);
        lMorph = gc_engine.oSpellChecker.getMorph(sValue);
        if (bMemorizeMorph) {
            oToken["lMorph"] = lMorph;
        }
    } else {
        lMorph = gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
    }
    if (lMorph.length == 0) {
        return false;
    }
    // check negative condition
    if (sNegPattern) {
        if (sNegPattern == "*") {
            // all morph must match sPattern
            return lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
        }
        else {
            if (lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                return false;
            }
        }
    }
    // search sPattern
    return lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1));
}

function g_merged_analyse (oToken1, oToken2, cMerger, sPattern, sNegPattern="", bSetMorph=true) {
    // merge two token values, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)
    let lMorph = gc_engine.oSpellChecker.getMorph(oToken1["sValue"] + cMerger + oToken2["sValue"]);
    if (lMorph.length == 0) {
        return false;
    }
    // check negative condition
    if (sNegPattern) {
        if (sNegPattern == "*") {
            // all morph must match sPattern
            let bResult = lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
            if (bResult && bSetMorph) {
                oToken1["lMorph"] = lMorph;
            }
            return bResult;
        }
        else {
            if (lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                return false;
            }
        }
    }
    // search sPattern
    let bResult = lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1));
    if (bResult && bSetMorph) {
        oToken1["lMorph"] = lMorph;
    }
    return bResult;
}

function g_tagbefore (oToken, dTags, sTag) {
    if (!dTags.has(sTag)) {
        return false;
    }
    if (oToken["i"] > dTags.get(sTag)[0]) {
        return true;
    }
    return false;
}

function g_tagafter (oToken, dTags, sTag) {
    if (!dTags.has(sTag)) {
        return false;
    }
    if (oToken["i"] < dTags.get(sTag)[1]) {
        return true;
    }
    return false;
}

function g_tag (oToken, sTag) {
    return oToken.hasOwnProperty("aTags") && oToken["aTags"].has(sTag);
}

function g_meta (oToken, sType) {
    return oToken["sType"] == sType;
}

function g_space (oToken1, oToken2, nMin, nMax=null) {
    let nSpace = oToken2["nStart"] - oToken1["nEnd"]
    if (nSpace < nMin) {
        return false;
    }
    if (nMax !== null && nSpace > nMax) {
        return false;
    }
    return true;
}

function g_token (lToken, i) {
    if (i < 0) {
        return lToken[0];
    }
    if (i >= lToken.length) {
        return lToken[lToken.length-1];
    }
    return lToken[i];
}


//////// Disambiguator for regex rules

function select (dTokenPos, nPos, sWord, sPattern) {
    if (!sWord) {
        return true;
    }
    if (!dTokenPos.has(nPos)) {
        console.log("Error. There should be a token at this position: ", nPos);
        return true;
    }
    let lMorph = gc_engine.oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect.length > 0 && lSelect.length != lMorph.length) {
        dTokenPos.get(nPos)["lMorph"] = lSelect;
    }
    return true;
}

function exclude (dTokenPos, nPos, sWord, sPattern) {
    if (!sWord) {
        return true;
    }
    if (!dTokenPos.has(nPos)) {
        console.log("Error. There should be a token at this position: ", nPos);
        return true;
    }
    let lMorph = gc_engine.oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0 && lSelect.length != lMorph.length) {
        dTokenPos.get(nPos)["lMorph"] = lSelect;
    }
    return true;
}

function define (dTokenPos, nPos, sMorphs) {
    dTokenPos.get(nPos)["lMorph"] = sMorphs.split("|");
    return true;
}


//// Disambiguation for graph rules

function g_select (oToken, sPattern) {
    // select morphologies for <oToken> according to <sPattern>, always return true
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect.length > 0 && lSelect.length != lMorph.length) {
        oToken["lMorph"] = lSelect;
    }
    return true;
}

function g_exclude (oToken, sPattern) {
    // select morphologies for <oToken> according to <sPattern>, always return true
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0 && lSelect.length != lMorph.length) {
        oToken["lMorph"] = lSelect;
    }
    return true;
}

function g_addmorph (oToken, sNewMorph) {
    // Disambiguation: add a morphology to a token
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
    lMorph.push(...sNewMorph.split("|"));
    oToken["lMorph"] = lMorph;
    return true;
}

function g_rewrite (oToken, sToReplace, sReplace) {
    // Disambiguation: rewrite morphologies
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
    oToken["lMorph"] = lMorph.map(s => s.replace(sToReplace, sReplace));
    return true;
}

function g_define (oToken, sMorphs) {
    // set morphologies of <oToken>, always return true
    oToken["lMorph"] = sMorphs.split("|");
    return true;
}

function g_definefrom (oToken, nLeft=null, nRight=null) {
    let sValue = oToken["sValue"];
    if (nLeft !== null) {
        sValue = (nRight !== null) ? sValue.slice(nLeft, nRight) : sValue.slice(nLeft);
    }
    oToken["lMorph"] = gc_engine.oSpellChecker.getMorph(sValue);
    return true;
}

function g_setmeta (oToken, sType) {
    // Disambiguation: change type of token
    oToken["sType"] = sType;
    return true;
}



//////// GRAMMAR CHECKER PLUGINS

${pluginsJS}


// generated code, do not edit
var gc_functions = {

    load: function (sContext, oSpellChecker) {
        _sAppContext = sContext
        _oSpellChecker = oSpellChecker
    },

    // callables for regex rules
${callablesJS}

    // callables for graph rules
${graph_callablesJS}
}


if (typeof(exports) !== 'undefined') {
    exports.load = gc_functions.load;
}
