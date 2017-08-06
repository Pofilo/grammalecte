// Grammar checker engine

"use strict";

${string}
${regex}
${map}


if (typeof(require) !== 'undefined') {
    var helpers = require("resource://grammalecte/helpers.js");
    var gc_options = require("resource://grammalecte/${lang}/gc_options.js");
    var gc_rules = require("resource://grammalecte/${lang}/gc_rules.js");
    var cregex = require("resource://grammalecte/${lang}/cregex.js");
    var text = require("resource://grammalecte/text.js");
}


function capitalizeArray (aArray) {
    // can’t map on user defined function??
    let aNew = [];
    for (let i = 0; i < aArray.length; i = i + 1) {
        aNew[i] = aArray[i].gl_toCapitalize();
    }
    return aNew;
}


// data
let _sAppContext = "";                                  // what software is running
let _dOptions = null;
let _aIgnoredRules = new Set();
let _oDict = null;
let _dAnalyses = new Map();                             // cache for data from dictionary


var gc_engine = {

    //// Informations

    lang: "${lang}",
    locales: ${loc},
    pkg: "${implname}",
    name: "${name}",
    version: "${version}",
    author: "${author}",

    //// Parsing

    parse: function (sText, sCountry="${country_default}", bDebug=false, bContext=false) {
        // analyses the paragraph sText and returns list of errors
        let dErrors;
        let errs;
        let sAlt = sText;
        let dDA = new Map();        // Disamnbiguator
        let dPriority = new Map();  // Key = position; value = priority
        let sNew = "";

        // parse paragraph
        try {
            [sNew, dErrors] = this._proofread(sText, sAlt, 0, true, dDA, dPriority, sCountry, bDebug, bContext);
            if (sNew) {
                sText = sNew;
            }
        }
        catch (e) {
            helpers.logerror(e);
        }

        // cleanup
        if (sText.includes(" ")) {
            sText = sText.replace(/ /g, ' '); // nbsp
        }
        if (sText.includes(" ")) {
            sText = sText.replace(/ /g, ' '); // snbsp
        }
        if (sText.includes("'")) {
            sText = sText.replace(/'/g, "’");
        }
        if (sText.includes("‑")) {
            sText = sText.replace(/‑/g, "-"); // nobreakdash
        }

        // parse sentence
        for (let [iStart, iEnd] of this._getSentenceBoundaries(sText)) {
            if (4 < (iEnd - iStart) < 2000) {
                dDA.clear();
                //helpers.echo(sText.slice(iStart, iEnd));
                try {
                    [, errs] = this._proofread(sText.slice(iStart, iEnd), sAlt.slice(iStart, iEnd), iStart, false, dDA, dPriority, sCountry, bDebug, bContext);
                    dErrors.gl_update(errs);
                }
                catch (e) {
                    helpers.logerror(e);
                }
            }
        }
        return Array.from(dErrors.values());
    },

    _zEndOfSentence: new RegExp ('([.?!:;…][ .?!… »”")]*|.$)', "g"),
    _zBeginOfParagraph: new RegExp ("^[-  –—.,;?!…]*", "ig"),
    _zEndOfParagraph: new RegExp ("[-  .,;?!…–—]*$", "ig"),

    _getSentenceBoundaries: function* (sText) {
        let mBeginOfSentence = this._zBeginOfParagraph.exec(sText);
        let iStart = this._zBeginOfParagraph.lastIndex;
        let m;
        while ((m = this._zEndOfSentence.exec(sText)) !== null) {
            yield [iStart, this._zEndOfSentence.lastIndex];
            iStart = this._zEndOfSentence.lastIndex;
        }
    },

    _proofread: function (s, sx, nOffset, bParagraph, dDA, dPriority, sCountry, bDebug, bContext) {
        let dErrs = new Map();
        let bChange = false;
        let bIdRule = option('idrule');
        let m;
        let bCondMemo;
        let nErrorStart;

        for (let [sOption, lRuleGroup] of this._getRules(bParagraph)) {
            if (!sOption || option(sOption)) {
                for (let [zRegex, bUppercase, sLineId, sRuleId, nPriority, lActions, lGroups, lNegLookBefore] of lRuleGroup) {
                    if (!_aIgnoredRules.has(sRuleId)) {
                        while ((m = zRegex.gl_exec2(s, lGroups, lNegLookBefore)) !== null) {
                            bCondMemo = null;
                            /*if (bDebug) {
                                helpers.echo(">>>> Rule # " + sLineId + " - Text: " + s + " opt: "+ sOption);
                            }*/
                            for (let [sFuncCond, cActionType, sWhat, ...eAct] of lActions) {
                            // action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                                try {
                                    //helpers.echo(oEvalFunc[sFuncCond]);
                                    bCondMemo = (!sFuncCond || oEvalFunc[sFuncCond](s, sx, m, dDA, sCountry, bCondMemo));
                                    if (bCondMemo) {
                                        switch (cActionType) {
                                            case "-":
                                                // grammar error
                                                //helpers.echo("-> error detected in " + sLineId + "\nzRegex: " + zRegex.source);
                                                nErrorStart = nOffset + m.start[eAct[0]];
                                                if (!dErrs.has(nErrorStart) || nPriority > dPriority.get(nErrorStart)) {
                                                    dErrs.set(nErrorStart, this._createError(s, sx, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bIdRule, sOption, bContext));
                                                    dPriority.set(nErrorStart, nPriority);
                                                }
                                                break;
                                            case "~":
                                                // text processor
                                                //helpers.echo("-> text processor by " + sLineId + "\nzRegex: " + zRegex.source);
                                                s = this._rewrite(s, sWhat, eAct[0], m, bUppercase);
                                                bChange = true;
                                                if (bDebug) {
                                                    helpers.echo("~ " + s + "  -- " + m[eAct[0]] + "  # " + sLineId);
                                                }
                                                break;
                                            case "=":
                                                // disambiguation
                                                //helpers.echo("-> disambiguation by " + sLineId + "\nzRegex: " + zRegex.source);
                                                oEvalFunc[sWhat](s, m, dDA);
                                                if (bDebug) {
                                                    helpers.echo("= " + m[0] + "  # " + sLineId + "\nDA: " + dDA.gl_toString());
                                                }
                                                break;
                                            case ">":
                                                // we do nothing, this test is just a condition to apply all following actions
                                                break;
                                            default:
                                                helpers.echo("# error: unknown action at " + sLineId);
                                        }
                                    } else {
                                        if (cActionType == ">") {
                                            break;
                                        }
                                    }
                                }
                                catch (e) {
                                    helpers.echo(s);
                                    helpers.echo("# line id: " + sLineId + "\n# rule id: " + sRuleId);
                                    helpers.logerror(e);
                                }
                            }
                        }
                    }
                }
            }
        }
        if (bChange) {
            return [s, dErrs];
        }
        return [false, dErrs];
    },

    _createError: function (s, sx, sRepl, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bIdRule, sOption, bContext) {
        let oErr = {};
        oErr["nStart"] = nOffset + m.start[iGroup];
        oErr["nEnd"] = nOffset + m.end[iGroup];
        oErr["sLineId"] = sLineId;
        oErr["sRuleId"] = sRuleId;
        oErr["sType"] = (sOption) ? sOption : "notype";
        // suggestions
        if (sRepl.slice(0,1) === "=") {
            let sugg = oEvalFunc[sRepl.slice(1)](s, m);
            if (sugg) {
                if (bUppercase && m[iGroup].slice(0,1).gl_isUpperCase()) {
                    oErr["aSuggestions"] = capitalizeArray(sugg.split("|"));
                } else {
                    oErr["aSuggestions"] = sugg.split("|");
                }
            } else {
                oErr["aSuggestions"] = [];
            }
        } else if (sRepl == "_") {
            oErr["aSuggestions"] = [];
        } else {
            if (bUppercase && m[iGroup].slice(0,1).gl_isUpperCase()) {
                oErr["aSuggestions"] = capitalizeArray(sRepl.gl_expand(m).split("|"));
            } else {
                oErr["aSuggestions"] = sRepl.gl_expand(m).split("|");
            }
        }
        // Message
        let sMessage = "";
        if (sMsg.slice(0,1) === "=") {
            sMessage = oEvalFunc[sMsg.slice(1)](s, m);
        } else {
            sMessage = sMsg.gl_expand(m);
        }
        if (bIdRule) {
            sMessage += " ##" + sLineId + " #" + sRuleId;
        }
        oErr["sMessage"] = sMessage;
        // URL
        oErr["URL"] = sURL || "";
        // Context
        if (bContext) {
            oErr["sUnderlined"] = sx.slice(m.start[iGroup], m.end[iGroup]);
            oErr["sBefore"] = sx.slice(Math.max(0, m.start[iGroup]-80), m.start[iGroup]);
            oErr["sAfter"] = sx.slice(m.end[iGroup], m.end[iGroup]+80);
        }
        return oErr;
    },

    _rewrite: function (s, sRepl, iGroup, m, bUppercase) {
        // text processor: write sRepl in s at iGroup position"
        let ln = m.end[iGroup] - m.start[iGroup];
        let sNew = "";
        if (sRepl === "*") {
            sNew = " ".repeat(ln);
        } else if (sRepl === ">" || sRepl === "_" || sRepl === "~") {
            sNew = sRepl + " ".repeat(ln-1);
        } else if (sRepl === "@") {
            sNew = "@".repeat(ln);
        } else if (sRepl.slice(0,1) === "=") {
            sNew = oEvalFunc[sRepl.slice(1)](s, m);
            sNew = sNew + " ".repeat(ln-sNew.length);
            if (bUppercase && m[iGroup].slice(0,1).gl_isUpperCase()) {
                sNew = sNew.gl_toCapitalize();
            }
        } else {
            sNew = sRepl.gl_expand(m);
            sNew = sNew + " ".repeat(ln-sNew.length);
        }
        //helpers.echo("\n"+s+"\nstart: "+m.start[iGroup]+" end:"+m.end[iGroup])
        return s.slice(0, m.start[iGroup]) + sNew + s.slice(m.end[iGroup]);
    },

    // Actions on rules

    ignoreRule: function (sRuleId) {
        _aIgnoredRules.add(sRuleId);
    },

    resetIgnoreRules: function () {
        _aIgnoredRules.clear();
    },

    reactivateRule: function (sRuleId) {
        _aIgnoredRules.delete(sRuleId);
    },

    listRules: function* (sFilter=null) {
        // generator: returns tuple (sOption, sLineId, sRuleId)
        try {
            for (let [sOption, lRuleGroup] of this._getRules(true)) {
                for (let [,, sLineId, sRuleId,,] of lRuleGroup) {
                    if (!sFilter || sRuleId.test(sFilter)) {
                        yield [sOption, sLineId, sRuleId];
                    }
                }
            }
            for (let [sOption, lRuleGroup] of this._getRules(false)) {
                for (let [,, sLineId, sRuleId,,] of lRuleGroup) {
                    if (!sFilter || sRuleId.test(sFilter)) {
                        yield [sOption, sLineId, sRuleId];
                    }
                }
            }
        }
        catch (e) {
            helpers.logerror(e);
        }
    },

    _getRules: function (bParagraph) {
        if (!bParagraph) {
            return gc_rules.lSentenceRules;
        }
        return gc_rules.lParagraphRules;
    },

    //// Initialization

    load: function (sContext="JavaScript", sPath="") {
        try {
            if (typeof(require) !== 'undefined') {
                var ibdawg = require("resource://grammalecte/ibdawg.js");
                _oDict = new ibdawg.IBDAWG("${dic_name}.json");
            } else {
                _oDict = new IBDAWG("${dic_name}.json", sPath);
            }
            _sAppContext = sContext;
            _dOptions = gc_options.getOptions(sContext).gl_shallowCopy();     // duplication necessary, to be able to reset to default
        }
        catch (e) {
            helpers.logerror(e);
        }
    },

    getDictionary: function () {
        return _oDict;
    },

    //// Options

    setOption: function (sOpt, bVal) {
        if (_dOptions.has(sOpt)) {
            _dOptions.set(sOpt, bVal);
        }
    },

    setOptions: function (dOpt) {
        _dOptions.gl_updateOnlyExistingKeys(dOpt);
    },

    getOptions: function () {
        return _dOptions;
    },

    getDefaultOptions: function () {
        return gc_options.getOptions(_sAppContext).gl_shallowCopy();
    },

    resetOptions: function () {
        _dOptions = gc_options.getOptions(_sAppContext).gl_shallowCopy();
    }
};


//////// Common functions

function option (sOpt) {
    // return true if option sOpt is active
    return _dOptions.get(sOpt);
}

function displayInfo (dDA, aWord) {
    // for debugging: info of word
    if (!aWord) {
        helpers.echo("> nothing to find");
        return true;
    }
    if (!_dAnalyses.has(aWord[1]) && !_storeMorphFromFSA(aWord[1])) {
        helpers.echo("> not in FSA");
        return true;
    }
    if (dDA.has(aWord[0])) {
        helpers.echo("DA: " + dDA.get(aWord[0]));
    }
    helpers.echo("FSA: " + _dAnalyses.get(aWord[1]));
    return true;
}

function _storeMorphFromFSA (sWord) {
    // retrieves morphologies list from _oDict -> _dAnalyses
    //helpers.echo("register: "+sWord + " " + _oDict.getMorph(sWord).toString())
    _dAnalyses.set(sWord, _oDict.getMorph(sWord));
    return !!_dAnalyses.get(sWord);
}

function morph (dDA, aWord, sPattern, bStrict=true, bNoWord=false) {
    // analyse a tuple (position, word), return true if sPattern in morphologies (disambiguation on)
    if (!aWord) {
        //helpers.echo("morph: noword, returns " + bNoWord);
        return bNoWord;
    }
    //helpers.echo("aWord: "+aWord.toString());
    if (!_dAnalyses.has(aWord[1]) && !_storeMorphFromFSA(aWord[1])) {
        return false;
    }
    let lMorph = dDA.has(aWord[0]) ? dDA.get(aWord[0]) : _dAnalyses.get(aWord[1]);
    //helpers.echo("lMorph: "+lMorph.toString());
    if (lMorph.length === 0) {
        return false;
    }
    //helpers.echo("***");
    if (bStrict) {
        return lMorph.every(s  =>  (s.search(sPattern) !== -1));
    }
    return lMorph.some(s  =>  (s.search(sPattern) !== -1));
}

function morphex (dDA, aWord, sPattern, sNegPattern, bNoWord=false) {
    // analyse a tuple (position, word), returns true if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation on)
    if (!aWord) {
        //helpers.echo("morph: noword, returns " + bNoWord);
        return bNoWord;
    }
    //helpers.echo("aWord: "+aWord.toString());
    if (!_dAnalyses.has(aWord[1]) && !_storeMorphFromFSA(aWord[1])) {
        return false;
    }
    let lMorph = dDA.has(aWord[0]) ? dDA.get(aWord[0]) : _dAnalyses.get(aWord[1]);
    //helpers.echo("lMorph: "+lMorph.toString());
    if (lMorph.length === 0) {
        return false;
    }
    //helpers.echo("***");
    // check negative condition
    if (lMorph.some(s  =>  (s.search(sNegPattern) !== -1))) {
        return false;
    }
    // search sPattern
    return lMorph.some(s  =>  (s.search(sPattern) !== -1));
}

function analyse (sWord, sPattern, bStrict=true) {
    // analyse a word, return true if sPattern in morphologies (disambiguation off)
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return false;
    }
    if (bStrict) {
        return _dAnalyses.get(sWord).every(s  =>  (s.search(sPattern) !== -1));
    }
    return _dAnalyses.get(sWord).some(s  =>  (s.search(sPattern) !== -1));
}

function analysex (sWord, sPattern, sNegPattern) {
    // analyse a word, returns True if not sNegPattern in word morphologies and sPattern in word morphologies (disambiguation off)
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return false;
    }
    // check negative condition
    if (_dAnalyses.get(sWord).some(s  =>  (s.search(sNegPattern) !== -1))) {
        return false;
    }
    // search sPattern
    return _dAnalyses.get(sWord).some(s  =>  (s.search(sPattern) !== -1));
}

function stem (sWord) {
    // returns a list of sWord's stems
    if (!sWord) {
        return [];
    }
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return [];
    }
    return _dAnalyses.get(sWord).map( s => s.slice(1, s.indexOf(" ")) );
}


//// functions to get text outside pattern scope

// warning: check compile_rules.py to understand how it works

function nextword (s, iStart, n) {
    // get the nth word of the input string or empty string
    let z = new RegExp("^(?: +[a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ%_-]+){" + (n-1).toString() + "} +([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ%_-]+)", "ig");
    let m = z.exec(s.slice(iStart));
    if (!m) {
        return null;
    }
    return [iStart + z.lastIndex - m[1].length, m[1]];
}

function prevword (s, iEnd, n) {
    // get the (-)nth word of the input string or empty string
    let z = new RegExp("([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ%_-]+) +(?:[a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ%_-]+ +){" + (n-1).toString() + "}$", "i");
    let m = z.exec(s.slice(0, iEnd));
    if (!m) {
        return null;
    }
    return [m.index, m[1]];
}

function nextword1 (s, iStart) {
    // get next word (optimization)
    let _zNextWord = new RegExp ("^ +([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ_][a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ_-]*)", "ig");
    let m = _zNextWord.exec(s.slice(iStart));
    if (!m) {
        return null;
    }
    return [iStart + _zNextWord.lastIndex - m[1].length, m[1]];
}

const _zPrevWord = new RegExp ("([a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ_][a-zà-öA-Zø-ÿÀ-Ö0-9Ø-ßĀ-ʯﬁ-ﬆ_-]*) +$", "i");

function prevword1 (s, iEnd) {
    // get previous word (optimization)
    let m = _zPrevWord.exec(s.slice(0, iEnd));
    if (!m) {
        return null;
    }
    return [m.index, m[1]];
}

function look (s, zPattern, zNegPattern=null) {
    // seek zPattern in s (before/after/fulltext), if antipattern zNegPattern not in s
    try {
        if (zNegPattern && zNegPattern.test(s)) {
            return false;
        }
        return zPattern.test(s);
    }
    catch (e) {
        helpers.logerror(e);
    }
    return false;
}

function look_chk1 (dDA, s, nOffset, zPattern, sPatternGroup1, sNegPatternGroup1=null) {
    // returns True if s has pattern zPattern and m.group(1) has pattern sPatternGroup1
    let m = zPattern.gl_exec2(s, null);
    if (!m) {
        return false;
    }
    try {
        let sWord = m[1];
        let nPos = m.start[1] + nOffset;
        if (sNegPatternGroup1) {
            return morphex(dDA, [nPos, sWord], sPatternGroup1, sNegPatternGroup1);
        } 
        return morph(dDA, [nPos, sWord], sPatternGroup1, false);
    }
    catch (e) {
        helpers.logerror(e);
        return false;
    }
}


//////// Disambiguator

function select (dDA, nPos, sWord, sPattern, lDefault=null) {
    if (!sWord) {
        return true;
    }
    if (dDA.has(nPos)) {
        return true;
    }
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return true;
    }
    if (_dAnalyses.get(sWord).length === 1) {
        return true;
    }
    let lSelect = _dAnalyses.get(sWord).filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != _dAnalyses.get(sWord).length) {
            dDA.set(nPos, lSelect);
        }
    } else if (lDefault) {
        dDA.set(nPos, lDefaul);
    }
    return true;
}

function exclude (dDA, nPos, sWord, sPattern, lDefault=null) {
    if (!sWord) {
        return true;
    }
    if (dDA.has(nPos)) {
        return true;
    }
    if (!_dAnalyses.has(sWord) && !_storeMorphFromFSA(sWord)) {
        return true;
    }
    if (_dAnalyses.get(sWord).length === 1) {
        return true;
    }
    let lSelect = _dAnalyses.get(sWord).filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != _dAnalyses.get(sWord).length) {
            dDA.set(nPos, lSelect);
        }
    } else if (lDefault) {
        dDA.set(nPos, lDefault);
    }
    return true;
}

function define (dDA, nPos, lMorph) {
    dDA.set(nPos, lMorph);
    return true;
}


//////// GRAMMAR CHECKER PLUGINS

${pluginsJS}


${callablesJS}



if (typeof(exports) !== 'undefined') {
    exports.lang = gc_engine.lang;
    exports.locales = gc_engine.locales;
    exports.pkg = gc_engine.pkg;
    exports.name = gc_engine.name;
    exports.version = gc_engine.version;
    exports.author = gc_engine.author;
    exports.parse = gc_engine.parse;
    exports._zEndOfSentence = gc_engine._zEndOfSentence;
    exports._zBeginOfParagraph = gc_engine._zBeginOfParagraph;
    exports._zEndOfParagraph = gc_engine._zEndOfParagraph;
    exports._getSentenceBoundaries = gc_engine._getSentenceBoundaries;
    exports._proofread = gc_engine._proofread;
    exports._createError = gc_engine._createError;
    exports._rewrite = gc_engine._rewrite;
    exports.ignoreRule = gc_engine.ignoreRule;
    exports.resetIgnoreRules = gc_engine.resetIgnoreRules;
    exports.reactivateRule = gc_engine.reactivateRule;
    exports.listRules = gc_engine.listRules;
    exports._getRules = gc_engine._getRules;
    exports.load = gc_engine.load;
    exports.getDictionary = gc_engine.getDictionary;
    exports.setOption = gc_engine.setOption;
    exports.setOptions = gc_engine.setOptions;
    exports.getOptions = gc_engine.getOptions;
    exports.getDefaultOptions = gc_engine.getDefaultOptions;
    exports.resetOptions = gc_engine.resetOptions;
}
