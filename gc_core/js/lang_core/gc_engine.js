// Grammar checker engine

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global require, exports, console */

"use strict";

${string}
${regex}
${map}


if(typeof(process) !== 'undefined') {
    var gc_options = require("./gc_options.js");
    var gc_rules = require("./gc_rules.js");
    var gc_rules_graph = require("./gc_rules_graph.js");
    var cregex = require("./cregex.js");
    var text = require("../text.js");
} else if (typeof(require) !== 'undefined') {
    var gc_options = require("resource://grammalecte/${lang}/gc_options.js");
    var gc_rules = require("resource://grammalecte/${lang}/gc_rules.js");
    var gc_rules_graph = require("resource://grammalecte/${lang}/gc_rules_graph.js");
    var cregex = require("resource://grammalecte/${lang}/cregex.js");
    var text = require("resource://grammalecte/text.js");
}


function capitalizeArray (aArray) {
    // can’t map on user defined function??
    let aNew = [];
    for (let i = 0; i < aArray.length; i = i + 1) {
        aNew[i] = aArray[i].slice(0,1).toUpperCase() + aArray[i].slice(1);
    }
    return aNew;
}


// data
let _sAppContext = "";                                  // what software is running
let _dOptions = null;
let _dOptionsColors = null;
let _oSpellChecker = null;
let _oTokenizer = null;
let _aIgnoredRules = new Set();


function echo (x) {
    console.log(x);
    return true;
}


var gc_engine = {

    //// Informations

    lang: "${lang}",
    locales: ${loc},
    pkg: "${implname}",
    name: "${name}",
    version: "${version}",
    author: "${author}",

    //// Initialization

    load: function (sContext="JavaScript", sColorType="aRGB", sPath="") {
        try {
            if(typeof(process) !== 'undefined') {
                var spellchecker = require("../graphspell/spellchecker.js");
                _oSpellChecker = new spellchecker.SpellChecker("${lang}", "", "${dic_main_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            } else if (typeof(require) !== 'undefined') {
                var spellchecker = require("resource://grammalecte/graphspell/spellchecker.js");
                _oSpellChecker = new spellchecker.SpellChecker("${lang}", "", "${dic_main_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            } else {
                _oSpellChecker = new SpellChecker("${lang}", sPath, "${dic_main_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            }
            _sAppContext = sContext;
            _dOptions = gc_options.getOptions(sContext).gl_shallowCopy();     // duplication necessary, to be able to reset to default
            _dOptionsColors = gc_options.getOptionsColors(sContext, sColorType);
            _oTokenizer = _oSpellChecker.getTokenizer();
            _oSpellChecker.activateStorage();
        }
        catch (e) {
            console.error(e);
        }
    },

    getSpellChecker: function () {
        return _oSpellChecker;
    },

    //// Rules

    getRules: function (bParagraph) {
        if (!bParagraph) {
            return gc_rules.lSentenceRules;
        }
        return gc_rules.lParagraphRules;
    },

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
            for (let [sOption, lRuleGroup] of this.getRules(true)) {
                for (let [,, sLineId, sRuleId,,] of lRuleGroup) {
                    if (!sFilter || sRuleId.test(sFilter)) {
                        yield [sOption, sLineId, sRuleId];
                    }
                }
            }
            for (let [sOption, lRuleGroup] of this.getRules(false)) {
                for (let [,, sLineId, sRuleId,,] of lRuleGroup) {
                    if (!sFilter || sRuleId.test(sFilter)) {
                        yield [sOption, sLineId, sRuleId];
                    }
                }
            }
        }
        catch (e) {
            console.error(e);
        }
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
    },

    //// Parsing

    parse: function (sText, sCountry="${country_default}", bDebug=false, dOptions=null, bContext=false, bFullInfo=false) {
        // init point to analyse <sText> and returns an iterable of errors or (with option <bFullInfo>) a list of sentences with tokens and errors
        let oText = new TextParser(sText);
        return oText.parse(sCountry, bDebug, dOptions, bContext, bFullInfo);
    }
};


class TextParser {

    constructor (sText) {
        this.sText = sText;
        this.sText0 = sText;
        this.sSentence = "";
        this.sSentence0 = "";
        this.nOffsetWithinParagraph = 0;
        this.lToken = [];
        this.dTokenPos = new Map();         // {position: token}
        this.dTags = new Map();             // {position: tags}
        this.dError = new Map();            // {position: error}
        this.dSentenceError = new Map();    // {position: error} (for the current sentence only)
        this.dErrorPriority = new Map();    // {position: priority of the current error}
    }

    asString () {
        let s = "===== TEXT =====\n";
        s += "sentence: " + this.sSentence0 + "\n";
        s += "now:      " + this.sSentence  + "\n";
        for (let dToken of this.lToken) {
            s += `#${dToken["i"]}\t${dToken["nStart"]}:${dToken["nEnd"]}\t${dToken["sValue"]}\t${dToken["sType"]}`;
            if (dToken.hasOwnProperty("lMorph")) {
                s += "\t" + dToken["lMorph"].toString();
            }
            if (dToken.hasOwnProperty("aTags")) {
                s += "\t" + dToken["aTags"].toString();
            }
            s += "\n";
        }
        return s;
    }

    parse (sCountry="${country_default}", bDebug=false, dOptions=null, bContext=false, bFullInfo=false) {
        // analyses <sText> and returns an iterable of errors or (with option <bFullInfo>) a list of sentences with tokens and errors
        let dOpt = dOptions || _dOptions;
        let bShowRuleId = option('idrule');
        // parse paragraph
        try {
            this.parseText(this.sText, this.sText0, true, 0, sCountry, dOpt, bShowRuleId, bDebug, bContext);
        }
        catch (e) {
            console.error(e);
        }
        let lParagraphErrors = null;
        if (bFullInfo) {
            lParagraphErrors = Array.from(this.dError.values());
            this.dSentenceError.clear();
        }
        // parse sentence
        let sText = this._getCleanText();
        let lSentences = [];
        let oSentence = null;
        for (let [iStart, iEnd] of text.getSentenceBoundaries(sText)) {
            try {
                this.sSentence = sText.slice(iStart, iEnd);
                this.sSentence0 = this.sText0.slice(iStart, iEnd);
                this.nOffsetWithinParagraph = iStart;
                this.lToken = Array.from(_oTokenizer.genTokens(this.sSentence, true));
                this.dTokenPos.clear();
                for (let dToken of this.lToken) {
                    if (dToken["sType"] != "INFO") {
                        this.dTokenPos.set(dToken["nStart"], dToken);
                    }
                }
                if (bFullInfo) {
                    oSentence = { "nStart": iStart, "nEnd": iEnd, "sSentence": this.sSentence, "lToken": Array.from(this.lToken) };
                    for (let oToken of oSentence["lToken"]) {
                        if (oToken["sType"] == "WORD") {
                            oToken["bValidToken"] = _oSpellChecker.isValidToken(oToken["sValue"]);
                        }
                    }
                    // the list of tokens is duplicated, to keep all tokens from being deleted when analysis
                }
                this.parseText(this.sSentence, this.sSentence0, false, iStart, sCountry, dOpt, bShowRuleId, bDebug, bContext);
                if (bFullInfo) {
                    oSentence["lGrammarErrors"] = Array.from(this.dSentenceError.values());
                    lSentences.push(oSentence);
                    this.dSentenceError.clear();
                }
            }
            catch (e) {
                console.error(e);
            }
        }
        if (bFullInfo) {
            // Grammar checking and sentence analysis
            return [lParagraphErrors, lSentences];
        } else {
            // Grammar checking only
            return Array.from(this.dError.values());
        }
    }

    _getCleanText () {
        let sText = this.sText;
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
        if (sText.includes("@@")) {
            sText = sText.replace(/@@+/g, "");
        }
        return sText;
    }

    parseText (sText, sText0, bParagraph, nOffset, sCountry, dOptions, bShowRuleId, bDebug, bContext) {
        let bChange = false;
        let m;

        for (let [sOption, lRuleGroup] of gc_engine.getRules(bParagraph)) {
            if (sOption == "@@@@") {
                // graph rules
                if (!bParagraph && bChange) {
                    this.update(sText, bDebug);
                    bChange = false;
                }
                for (let [sGraphName, sLineId] of lRuleGroup) {
                    if (!dOptions.has(sGraphName) || dOptions.get(sGraphName)) {
                        if (bDebug) {
                            console.log(">>>> GRAPH: " + sGraphName + " " + sLineId);
                        }
                        sText = this.parseGraph(gc_rules_graph.dAllGraph[sGraphName], sCountry, dOptions, bShowRuleId, bDebug, bContext);
                    }
                }
            }
            else if (!sOption || option(sOption)) {
                for (let [zRegex, bUppercase, sLineId, sRuleId, nPriority, lActions, lGroups, lNegLookBefore] of lRuleGroup) {
                    if (!_aIgnoredRules.has(sRuleId)) {
                        while ((m = zRegex.gl_exec2(sText, lGroups, lNegLookBefore)) !== null) {
                            let bCondMemo = null;
                            for (let [sFuncCond, cActionType, sWhat, ...eAct] of lActions) {
                                // action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                                try {
                                    bCondMemo = (!sFuncCond || oEvalFunc[sFuncCond](sText, sText0, m, this.dTokenPos, sCountry, bCondMemo));
                                    if (bCondMemo) {
                                        switch (cActionType) {
                                            case "-":
                                                // grammar error
                                                //console.log("-> error detected in " + sLineId + "\nzRegex: " + zRegex.source);
                                                let nErrorStart = nOffset + m.start[eAct[0]];
                                                if (!this.dError.has(nErrorStart) || nPriority > this.dErrorPriority.get(nErrorStart)) {
                                                    this.dError.set(nErrorStart, this._createErrorFromRegex(sText, sText0, sWhat, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bShowRuleId, sOption, bContext));
                                                    this.dErrorPriority.set(nErrorStart, nPriority);
                                                    this.dSentenceError.set(nErrorStart, this.dError.get(nErrorStart));
                                                }
                                                break;
                                            case "~":
                                                // text processor
                                                //console.log("-> text processor by " + sLineId + "\nzRegex: " + zRegex.source);
                                                sText = this.rewriteText(sText, sWhat, eAct[0], m, bUppercase);
                                                bChange = true;
                                                if (bDebug) {
                                                    console.log("~ " + sText + "  -- " + m[eAct[0]] + "  # " + sLineId);
                                                }
                                                break;
                                            case "=":
                                                // disambiguation
                                                //console.log("-> disambiguation by " + sLineId + "\nzRegex: " + zRegex.source);
                                                oEvalFunc[sWhat](sText, m, this.dTokenPos);
                                                if (bDebug) {
                                                    console.log("= " + m[0] + "  # " + sLineId, "\nDA:", this.dTokenPos);
                                                }
                                                break;
                                            case ">":
                                                // we do nothing, this test is just a condition to apply all following actions
                                                break;
                                            default:
                                                console.log("# error: unknown action at " + sLineId);
                                        }
                                    } else {
                                        if (cActionType == ">") {
                                            break;
                                        }
                                    }
                                }
                                catch (e) {
                                    console.log(sText);
                                    console.log("# line id: " + sLineId + "\n# rule id: " + sRuleId);
                                    console.error(e);
                                }
                            }
                        }
                    }
                }
            }
        }
        if (bChange) {
            if (bParagraph) {
                this.sText = sText;
            } else {
                this.sSentence = sText;
            }
        }
    }

    update (sSentence, bDebug=false) {
        // update <sSentence> and retokenize
        this.sSentence = sSentence;
        let lNewToken = Array.from(_oTokenizer.genTokens(sSentence, true));
        for (let oToken of lNewToken) {
            if (this.dTokenPos.gl_get(oToken["nStart"], {}).hasOwnProperty("lMorph")) {
                oToken["lMorph"] = this.dTokenPos.get(oToken["nStart"])["lMorph"];
            }
            if (this.dTokenPos.gl_get(oToken["nStart"], {}).hasOwnProperty("aTags")) {
                oToken["aTags"] = this.dTokenPos.get(oToken["nStart"])["aTags"];
            }
        }
        this.lToken = lNewToken;
        this.dTokenPos.clear();
        for (let oToken of this.lToken) {
            if (oToken["sType"] != "INFO") {
                this.dTokenPos.set(oToken["nStart"], oToken);
            }
        }
        if (bDebug) {
            console.log("UPDATE:");
            console.log(this.asString());
        }
    }

    * _getNextPointers (oToken, oGraph, oPointer, bDebug=false) {
        // generator: return nodes where <oToken> “values” match <oNode> arcs
        try {
            let oNode = oGraph[oPointer["iNode"]];
            let iToken1 = oPointer["iToken1"];
            let bTokenFound = false;
            // token value
            if (oNode.hasOwnProperty(oToken["sValue"])) {
                if (bDebug) {
                    console.log("  MATCH: " + oToken["sValue"]);
                }
                yield { "iToken1": iToken1, "iNode": oNode[oToken["sValue"]] };
                bTokenFound = true;
            }
            if (oToken["sValue"].slice(0,2).gl_isTitle()) { // we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
                let sValue = oToken["sValue"].toLowerCase();
                if (oNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iToken1": iToken1, "iNode": oNode[sValue] };
                    bTokenFound = true;
                }
            }
            else if (oToken["sValue"].gl_isUpperCase()) {
                let sValue = oToken["sValue"].toLowerCase();
                if (oNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iToken1": iToken1, "iNode": oNode[sValue] };
                    bTokenFound = true;
                }
                sValue = oToken["sValue"].gl_toCapitalize();
                if (oNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iToken1": iToken1, "iNode": oNode[sValue] };
                    bTokenFound = true;
                }
            }
            // regex value arcs
            if (oToken["sType"] != "INFO"  &&  oToken["sType"] != "PUNC"  &&  oToken["sType"] != "SIGN") {
                if (oNode.hasOwnProperty("<re_value>")) {
                    for (let sRegex in oNode["<re_value>"]) {
                        if (!sRegex.includes("¬")) {
                            // no anti-pattern
                            if (oToken["sValue"].search(sRegex) !== -1) {
                                if (bDebug) {
                                    console.log("  MATCH: ~" + sRegex);
                                }
                                yield { "iToken1": iToken1, "iNode": oNode["<re_value>"][sRegex] };
                                bTokenFound = true;
                            }
                        } else {
                            // there is an anti-pattern
                            let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                            if (sNegPattern && oToken["sValue"].search(sNegPattern) !== -1) {
                                continue;
                            }
                            if (!sPattern || oToken["sValue"].search(sPattern) !== -1) {
                                if (bDebug) {
                                    console.log("  MATCH: ~" + sRegex);
                                }
                                yield { "iToken1": iToken1, "iNode": oNode["<re_value>"][sRegex] };
                                bTokenFound = true;
                            }
                        }
                    }
                }
            }
            // analysable tokens
            if (oToken["sType"].slice(0,4) == "WORD") {
                // token lemmas
                if (oNode.hasOwnProperty("<lemmas>")) {
                    for (let sLemma of _oSpellChecker.getLemma(oToken["sValue"])) {
                        if (oNode["<lemmas>"].hasOwnProperty(sLemma)) {
                            if (bDebug) {
                                console.log("  MATCH: >" + sLemma);
                            }
                            yield { "iToken1": iToken1, "iNode": oNode["<lemmas>"][sLemma] };
                            bTokenFound = true;
                        }
                    }
                }
                // regex morph arcs
                if (oNode.hasOwnProperty("<re_morph>")) {
                    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : _oSpellChecker.getMorph(oToken["sValue"]);
                    if (lMorph.length > 0) {
                        for (let sRegex in oNode["<re_morph>"]) {
                            if (!sRegex.includes("¬")) {
                                // no anti-pattern
                                if (lMorph.some(sMorph  =>  (sMorph.search(sRegex) !== -1))) {
                                    if (bDebug) {
                                        console.log("  MATCH: @" + sRegex);
                                    }
                                    yield { "iToken1": iToken1, "iNode": oNode["<re_morph>"][sRegex] };
                                    bTokenFound = true;
                                }
                            } else {
                                // there is an anti-pattern
                                let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                                if (sNegPattern == "*") {
                                    // all morphologies must match with <sPattern>
                                    if (sPattern) {
                                        if (lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1))) {
                                            if (bDebug) {
                                                console.log("  MATCH: @" + sRegex);
                                            }
                                            yield { "iToken1": iToken1, "iNode": oNode["<re_morph>"][sRegex] };
                                            bTokenFound = true;
                                        }
                                    }
                                } else {
                                    if (sNegPattern  &&  lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                                        continue;
                                    }
                                    if (!sPattern  ||  lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1))) {
                                        if (bDebug) {
                                            console.log("  MATCH: @" + sRegex);
                                        }
                                        yield { "iToken1": iToken1, "iNode": oNode["<re_morph>"][sRegex] };
                                        bTokenFound = true;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            // token tags
            if (oToken.hasOwnProperty("aTags") && oNode.hasOwnProperty("<tags>")) {
                for (let sTag of oToken["aTags"]) {
                    if (oNode["<tags>"].hasOwnProperty(sTag)) {
                        if (bDebug) {
                            console.log("  MATCH: /" + sTag);
                        }
                        yield { "iToken1": iToken1, "iNode": oNode["<tags>"][sTag] };
                        bTokenFound = true;
                    }
                }
            }
            // meta arc (for token type)
            if (oNode.hasOwnProperty("<meta>")) {
                for (let sMeta in oNode["<meta>"]) {
                    // no regex here, we just search if <oNode["sType"]> exists within <sMeta>
                    if (sMeta == "*" || oToken["sType"] == sMeta) {
                        if (bDebug) {
                            console.log("  MATCH: *" + sMeta);
                        }
                        yield { "iToken1": iToken1, "iNode": oNode["<meta>"][sMeta] };
                        bTokenFound = true;
                    }
                    else if (sMeta.includes("¬")) {
                        if (!sMeta.includes(oToken["sType"])) {
                            if (bDebug) {
                                console.log("  MATCH: *" + sMeta);
                            }
                            yield { "iToken1": iToken1, "iNode": oNode["<meta>"][sMeta] };
                            bTokenFound = true;
                        }
                    }
                }
            }
            if (!bTokenFound  &&  oPointer.hasOwnProperty("bKeep")) {
                yield oPointer;
            }
            // JUMP
            // Warning! Recurssion!
            if (oNode.hasOwnProperty("<>")) {
                let oPointer2 = { "iToken1": iToken1, "iNode": oNode["<>"], "bKeep": true };
                yield* this._getNextPointers(oToken, oGraph, oPointer2, bDebug);
            }
        }
        catch (e) {
            console.error(e);
        }
    }

    parseGraph (oGraph, sCountry="${country_default}", dOptions=null, bShowRuleId=false, bDebug=false, bContext=false) {
        // parse graph with tokens from the text and execute actions encountered
        let lPointer = [];
        let bTagAndRewrite = false;
        try {
            for (let [iToken, oToken] of this.lToken.entries()) {
                if (bDebug) {
                    console.log("TOKEN: " + oToken["sValue"]);
                }
                // check arcs for each existing pointer
                let lNextPointer = [];
                for (let oPointer of lPointer) {
                    lNextPointer.push(...this._getNextPointers(oToken, oGraph, oPointer, bDebug));
                }
                lPointer = lNextPointer;
                // check arcs of first nodes
                lPointer.push(...this._getNextPointers(oToken, oGraph, { "iToken1": iToken, "iNode": 0 }, bDebug));
                // check if there is rules to check for each pointer
                for (let oPointer of lPointer) {
                    if (oGraph[oPointer["iNode"]].hasOwnProperty("<rules>")) {
                        let bChange = this._executeActions(oGraph, oGraph[oPointer["iNode"]]["<rules>"], oPointer["iToken1"]-1, iToken, dOptions, sCountry, bShowRuleId, bDebug, bContext);
                        if (bChange) {
                            bTagAndRewrite = true;
                        }
                    }
                }
            }
        } catch (e) {
            console.error(e);
        }
        if (bTagAndRewrite) {
            this.rewriteFromTags(bDebug);
        }
        if (bDebug) {
            console.log(this.asString());
        }
        return this.sSentence;
    }

    _executeActions (oGraph, oNode, nTokenOffset, nLastToken, dOptions, sCountry, bShowRuleId, bDebug, bContext) {
        // execute actions found in the DARG
        let bChange = false;
        for (let [sLineId, nextNodeKey] of Object.entries(oNode)) {
            let bCondMemo = null;
            for (let sRuleId of oGraph[nextNodeKey]) {
                try {
                    if (bDebug) {
                        console.log("   >TRY: " + sRuleId + " " + sLineId);
                    }
                    let [sOption, sFuncCond, cActionType, sWhat, ...eAct] = gc_rules_graph.dRule[sRuleId];
                    // Suggestion    [ option, condition, "-", replacement/suggestion/action, iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, sURL ]
                    // TextProcessor [ option, condition, "~", replacement/suggestion/action, iTokenStart, iTokenEnd, bCaseSvty ]
                    // Disambiguator [ option, condition, "=", replacement/suggestion/action ]
                    // Tag           [ option, condition, "/", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    // Immunity      [ option, condition, "!", "",                            iTokenStart, iTokenEnd ]
                    // Test          [ option, condition, ">", "" ]
                    if (!sOption || dOptions.gl_get(sOption, false)) {
                        bCondMemo = !sFuncCond || oEvalFunc[sFuncCond](this.lToken, nTokenOffset, nLastToken, sCountry, bCondMemo, this.dTags, this.sSentence, this.sSentence0);
                        if (bCondMemo) {
                            if (cActionType == "-") {
                                // grammar error
                                let [iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, sURL] = eAct;
                                let nTokenErrorStart = (iTokenStart > 0) ? nTokenOffset + iTokenStart : nLastToken + iTokenStart;
                                if (!this.lToken[nTokenErrorStart].hasOwnProperty("bImmune")) {
                                    let nTokenErrorEnd = (iTokenEnd > 0) ? nTokenOffset + iTokenEnd : nLastToken + iTokenEnd;
                                    let nErrorStart = this.nOffsetWithinParagraph + ((cStartLimit == "<") ? this.lToken[nTokenErrorStart]["nStart"] : this.lToken[nTokenErrorStart]["nEnd"]);
                                    let nErrorEnd = this.nOffsetWithinParagraph + ((cEndLimit == ">") ? this.lToken[nTokenErrorEnd]["nEnd"] : this.lToken[nTokenErrorEnd]["nStart"]);
                                    if (!this.dError.has(nErrorStart) || nPriority > this.dErrorPriority.gl_get(nErrorStart, -1)) {
                                        this.dError.set(nErrorStart, this._createErrorFromTokens(sWhat, nTokenOffset, nLastToken, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, bCaseSvty, sMessage, sURL, bShowRuleId, sOption, bContext));
                                        this.dErrorPriority.set(nErrorStart, nPriority);
                                        this.dSentenceError.set(nErrorStart, this.dError.get(nErrorStart));
                                        if (bDebug) {
                                            console.log("    NEW_ERROR: ",  this.dError.get(nErrorStart));
                                        }
                                    }
                                }
                            }
                            else if (cActionType == "~") {
                                // text processor
                                let nTokenStart = (eAct[0] > 0) ? nTokenOffset + eAct[0] : nLastToken + eAct[0];
                                let nTokenEnd = (eAct[1] > 0) ? nTokenOffset + eAct[1] : nLastToken + eAct[1];
                                this._tagAndPrepareTokenForRewriting(sWhat, nTokenStart, nTokenEnd, nTokenOffset, nLastToken, eAct[2], bDebug);
                                bChange = true;
                                if (bDebug) {
                                    console.log(`    TEXT_PROCESSOR: [${this.lToken[nTokenStart]["sValue"]}:${this.lToken[nTokenEnd]["sValue"]}]  > ${sWhat}`);
                                }
                            }
                            else if (cActionType == "=") {
                                // disambiguation
                                oEvalFunc[sWhat](this.lToken, nTokenOffset, nLastToken);
                                if (bDebug) {
                                    console.log(`    DISAMBIGUATOR: (${sWhat})  [${this.lToken[nTokenOffset+1]["sValue"]}:${this.lToken[nLastToken]["sValue"]}]`);
                                }
                            }
                            else if (cActionType == ">") {
                                // we do nothing, this test is just a condition to apply all following actions
                                if (bDebug) {
                                    console.log("    COND_OK");
                                }
                            }
                            else if (cActionType == "/") {
                                // Tag
                                let nTokenStart = (eAct[0] > 0) ? nTokenOffset + eAct[0] : nLastToken + eAct[0];
                                let nTokenEnd = (eAct[1] > 0) ? nTokenOffset + eAct[1] : nLastToken + eAct[1];
                                for (let i = nTokenStart; i <= nTokenEnd; i++) {
                                    if (this.lToken[i].hasOwnProperty("aTags")) {
                                        this.lToken[i]["aTags"].add(...sWhat.split("|"))
                                    } else {
                                        this.lToken[i]["aTags"] = new Set(sWhat.split("|"));
                                    }
                                }
                                if (bDebug) {
                                    console.log(`    TAG:  ${sWhat} > [${this.lToken[nTokenStart]["sValue"]}:${this.lToken[nTokenEnd]["sValue"]}]`);
                                }
                                if (!this.dTags.has(sWhat)) {
                                    this.dTags.set(sWhat, [nTokenStart, nTokenStart]);
                                } else {
                                    this.dTags.set(sWhat, [Math.min(nTokenStart, this.dTags.get(sWhat)[0]), Math.max(nTokenEnd, this.dTags.get(sWhat)[1])]);
                                }
                            }
                            else if (cActionType == "!") {
                                // immunity
                                if (bDebug) {
                                    console.log("    IMMUNITY: " + sLineId + " / " + sRuleId);
                                }
                                let nTokenStart = (eAct[0] > 0) ? nTokenOffset + eAct[0] : nLastToken + eAct[0];
                                let nTokenEnd = (eAct[1] > 0) ? nTokenOffset + eAct[1] : nLastToken + eAct[1];
                                if (nTokenEnd - nTokenStart == 0) {
                                    this.lToken[nTokenStart]["bImmune"] = true;
                                    let nErrorStart = this.nOffsetWithinParagraph + this.lToken[nTokenStart]["nStart"];
                                    if (this.dError.has(nErrorStart)) {
                                        this.dError.delete(nErrorStart);
                                    }
                                } else {
                                    for (let i = nTokenStart;  i <= nTokenEnd;  i++) {
                                        this.lToken[i]["bImmune"] = true;
                                        let nErrorStart = this.nOffsetWithinParagraph + this.lToken[i]["nStart"];
                                        if (this.dError.has(nErrorStart)) {
                                            this.dError.delete(nErrorStart);
                                        }
                                    }
                                }
                            } else {
                                console.log("# error: unknown action at " + sLineId);
                            }
                        }
                        else if (cActionType == ">") {
                            if (bDebug) {
                                console.log("    COND_BREAK");
                            }
                            break;
                        }
                    }
                }
                catch (e) {
                    console.log("Error: ", sLineId, sRuleId, this.sSentence);
                    console.error(e);
                }
            }
        }
        return bChange;
    }

    _createErrorFromRegex (sText, sText0, sSugg, nOffset, m, iGroup, sLineId, sRuleId, bUppercase, sMsg, sURL, bShowRuleId, sOption, bContext) {
        let nStart = nOffset + m.start[iGroup];
        let nEnd = nOffset + m.end[iGroup];
        // suggestions
        let lSugg = [];
        if (sSugg.startsWith("=")) {
            sSugg = oEvalFunc[sSugg.slice(1)](sText, m);
            lSugg = (sSugg) ? sSugg.split("|") : [];
        } else if (sSugg == "_") {
            lSugg = [];
        } else {
            lSugg = sSugg.gl_expand(m).split("|");
        }
        if (bUppercase && lSugg.length > 0 && m[iGroup].slice(0,1).gl_isUpperCase()) {
            lSugg = capitalizeArray(lSugg);
        }
        // Message
        let sMessage = (sMsg.startsWith("=")) ? oEvalFunc[sMsg.slice(1)](sText, m) : sMsg.gl_expand(m);
        if (bShowRuleId) {
            sMessage += "  #" + sLineId + " / " + sRuleId;
        }
        //
        return this._createError(nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext);
    }

    _createErrorFromTokens (sSugg, nTokenOffset, nLastToken, iFirstToken, nStart, nEnd, sLineId, sRuleId, bCaseSvty, sMsg, sURL, bShowRuleId, sOption, bContext) {
        // suggestions
        let lSugg = [];
        if (sSugg.startsWith("=")) {
            sSugg = oEvalFunc[sSugg.slice(1)](this.lToken, nTokenOffset, nLastToken);
            lSugg = (sSugg) ? sSugg.split("|") : [];
        } else if (sSugg == "_") {
            lSugg = [];
        } else {
            lSugg = this._expand(sSugg, nTokenOffset, nLastToken).split("|");
        }
        if (bCaseSvty && lSugg.length > 0 && this.lToken[iFirstToken]["sValue"].slice(0,1).gl_isUpperCase()) {
            lSugg = capitalizeArray(lSugg);
        }
        // Message
        let sMessage = (sMsg.startsWith("=")) ? oEvalFunc[sMsg.slice(1)](this.lToken, nTokenOffset, nLastToken) : this._expand(sMsg, nTokenOffset, nLastToken);
        if (bShowRuleId) {
            sMessage += "  #" + sLineId + " / " + sRuleId;
        }
        //
        return this._createError(nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext);
    }

    _createError (nStart, nEnd, sLineId, sRuleId, sOption, sMessage, lSugg, sURL, bContext) {
        let oErr = {
            "nStart": nStart,
            "nEnd": nEnd,
            "sLineId": sLineId,
            "sRuleId": sRuleId,
            "sType": sOption || "notype",
            "aColor": _dOptionsColors[sOption],
            "sMessage": sMessage,
            "aSuggestions": lSugg,
            "URL": sURL
        }
        if (bContext) {
            oErr['sUnderlined'] = this.sText0.slice(nStart, nEnd);
            oErr['sBefore'] = this.sText0.slice(Math.max(0,nStart-80), nStart);
            oErr['sAfter'] = this.sText0.slice(nEnd, nEnd+80);
        }
        return oErr;
    }

    _expand (sText, nTokenOffset, nLastToken) {
        let m;
        while ((m = /\\(-?[0-9]+)/.exec(sText)) !== null) {
            if (m[1].slice(0,1) == "-") {
                sText = sText.replace(m[0], this.lToken[nLastToken+parseInt(m[1],10)+1]["sValue"]);
            } else {
                sText = sText.replace(m[0], this.lToken[nTokenOffset+parseInt(m[1],10)]["sValue"]);
            }
        }
        return sText;
    }

    rewriteText (sText, sRepl, iGroup, m, bUppercase) {
        // text processor: write sRepl in sText at iGroup position"
        let ln = m.end[iGroup] - m.start[iGroup];
        let sNew = "";
        if (sRepl === "*") {
            sNew = " ".repeat(ln);
        }
        else if (sRepl === "_") {
            sNew = "_".repeat(ln);
        }
        else if (sRepl === "@") {
            sNew = "@".repeat(ln);
        }
        else if (sRepl.slice(0,1) === "=") {
            sNew = oEvalFunc[sRepl.slice(1)](sText, m);
            sNew = sNew + " ".repeat(ln-sNew.length);
            if (bUppercase && m[iGroup].slice(0,1).gl_isUpperCase()) {
                sNew = sNew.gl_toCapitalize();
            }
        } else {
            sNew = sRepl.gl_expand(m);
            sNew = sNew + " ".repeat(ln-sNew.length);
        }
        //console.log(sText+"\nstart: "+m.start[iGroup]+" end:"+m.end[iGroup]);
        return sText.slice(0, m.start[iGroup]) + sNew + sText.slice(m.end[iGroup]);
    }

    _tagAndPrepareTokenForRewriting (sWhat, nTokenRewriteStart, nTokenRewriteEnd, nTokenOffset, nLastToken, bCaseSvty, bDebug) {
        // text processor: rewrite tokens between <nTokenRewriteStart> and <nTokenRewriteEnd> position
        if (sWhat === "*") {
            // purge text
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                this.lToken[nTokenRewriteStart]["bToRemove"] = true;
            } else {
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    this.lToken[i]["bToRemove"] = true;
                }
            }
        }
        else if (sWhat === "␣") {
            // merge tokens
            this.lToken[nTokenRewriteStart]["nMergeUntil"] = nTokenRewriteEnd;
        }
        else if (sWhat === "_") {
            // neutralized token
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                this.lToken[nTokenRewriteStart]["sNewValue"] = "_";
            } else {
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    this.lToken[i]["sNewValue"] = "_";
                }
            }
        }
        else {
            if (sWhat.startsWith("=")) {
                sWhat = oEvalFunc[sWhat.slice(1)](this.lToken, nTokenOffset, nLastToken);
            } else {
                sWhat = this._expand(sWhat, nTokenOffset, nLastToken);
            }
            let bUppercase = bCaseSvty && this.lToken[nTokenRewriteStart]["sValue"].slice(0,1).gl_isUpperCase();
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                // one token
                if (bUppercase) {
                    sWhat = sWhat.gl_toCapitalize();
                }
                this.lToken[nTokenRewriteStart]["sNewValue"] = sWhat;
            }
            else {
                // several tokens
                let lTokenValue = sWhat.split("|");
                if (lTokenValue.length != (nTokenRewriteEnd - nTokenRewriteStart + 1)) {
                    console.log("Error. Text processor: number of replacements != number of tokens.");
                    return;
                }
                let j = 0;
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    let sValue = lTokenValue[j];
                    if (!sValue || sValue === "*") {
                        this.lToken[i]["bToRemove"] = true;
                    } else {
                        if (bUppercase) {
                            sValue = sValue.gl_toCapitalize();
                        }
                        this.lToken[i]["sNewValue"] = sValue;
                    }
                    j++;
                }
            }
        }
    }

    rewriteFromTags (bDebug=false) {
        // rewrite the sentence, modify tokens, purge the token list
        if (bDebug) {
            console.log("REWRITE");
        }
        let lNewToken = [];
        let nMergeUntil = 0;
        let oMergingToken = null;
        for (let [iToken, oToken] of this.lToken.entries()) {
            let bKeepToken = true;
            if (oToken["sType"] != "INFO") {
                if (nMergeUntil && iToken <= nMergeUntil) {
                    oMergingToken["sValue"] += " ".repeat(oToken["nStart"] - oMergingToken["nEnd"]) + oToken["sValue"];
                    oMergingToken["nEnd"] = oToken["nEnd"];
                    if (bDebug) {
                        console.log("  MERGED TOKEN: " + oMergingToken["sValue"]);
                    }
                    bKeepToken = false;
                }
                if (oToken.hasOwnProperty("nMergeUntil")) {
                    if (iToken > nMergeUntil) { // this token is not already merged with a previous token
                        oMergingToken = oToken;
                    }
                    if (oToken["nMergeUntil"] > nMergeUntil) {
                        nMergeUntil = oToken["nMergeUntil"];
                    }
                    delete oToken["nMergeUntil"];
                }
                else if (oToken.hasOwnProperty("bToRemove")) {
                    if (bDebug) {
                        console.log("  REMOVED: " + oToken["sValue"]);
                    }
                    this.sSentence = this.sSentence.slice(0, oToken["nStart"]) + " ".repeat(oToken["nEnd"] - oToken["nStart"]) + this.sSentence.slice(oToken["nEnd"]);
                    bKeepToken = false;
                }
            }
            //
            if (bKeepToken) {
                lNewToken.push(oToken);
                if (oToken.hasOwnProperty("sNewValue")) {
                    // rewrite token and sentence
                    if (bDebug) {
                        console.log(oToken["sValue"] + " -> " + oToken["sNewValue"]);
                    }
                    oToken["sRealValue"] = oToken["sValue"];
                    oToken["sValue"] = oToken["sNewValue"];
                    let nDiffLen = oToken["sRealValue"].length - oToken["sNewValue"].length;
                    let sNewRepl = (nDiffLen >= 0) ? oToken["sNewValue"] + " ".repeat(nDiffLen) : oToken["sNewValue"].slice(0, oToken["sRealValue"].length);
                    this.sSentence = this.sSentence.slice(0,oToken["nStart"]) + sNewRepl + this.sSentence.slice(oToken["nEnd"]);
                    delete oToken["sNewValue"];
                }
            }
            else {
                try {
                    this.dTokenPos.delete(oToken["nStart"]);
                }
                catch (e) {
                    console.log(this.asString());
                    console.log(oToken);
                }
            }
        }
        if (bDebug) {
            console.log("  TEXT REWRITED: " + this.sSentence);
        }
        this.lToken.length = 0;
        this.lToken = lNewToken;
    }
};


//////// Common functions

function option (sOpt) {
    // return true if option sOpt is active
    return _dOptions.get(sOpt);
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

function displayInfo (dTokenPos, aWord) {
    // for debugging: info of word
    if (!aWord) {
        console.log("> nothing to find");
        return true;
    }
    let lMorph = _oSpellChecker.getMorph(aWord[1]);
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
    let lMorph = (dTokenPos.has(aWord[0])  &&  dTokenPos.get(aWord[0]))["lMorph"] ? dTokenPos.get(aWord[0])["lMorph"] : _oSpellChecker.getMorph(aWord[1]);
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
    let lMorph = _oSpellChecker.getMorph(sWord);
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
            lMorph = _oSpellChecker.getMorph(sValue);
            if (bMemorizeMorph) {
                oToken["lMorph"] = lMorph;
            }
        } else {
            lMorph = _oSpellChecker.getMorph(oToken["sValue"]);
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

function g_analyse (oToken, sPattern, sNegPattern="", nLeft=null, nRight=null, bMemorizeMorph=true) {
    // analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies
    let lMorph;
    if (nLeft !== null) {
        let sValue = (nRight !== null) ? oToken["sValue"].slice(nLeft, nRight) : oToken["sValue"].slice(nLeft);
        lMorph = _oSpellChecker.getMorph(sValue);
        if (bMemorizeMorph) {
            oToken["lMorph"] = lMorph;
        }
    } else {
        lMorph = _oSpellChecker.getMorph(oToken["sValue"]);
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
    let lMorph = _oSpellChecker.getMorph(oToken1["sValue"] + cMerger + oToken2["sValue"]);
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

function g_tag_before (oToken, dTags, sTag) {
    if (!dTags.has(sTag)) {
        return false;
    }
    if (oToken["i"] > dTags.get(sTag)[0]) {
        return true;
    }
    return false;
}

function g_tag_after (oToken, dTags, sTag) {
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

function g_space_between_tokens (oToken1, oToken2, nMin, nMax=null) {
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
        return lToken[-1];
    }
    return lToken[i];
}


//////// Disambiguator

function select (dTokenPos, nPos, sWord, sPattern, lDefault=null) {
    if (!sWord) {
        return true;
    }
    if (!dTokenPos.has(nPos)) {
        console.log("Error. There should be a token at this position: ", nPos);
        return true;
    }
    let lMorph = _oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            dTokenPos.get(nPos)["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        dTokenPos.get(nPos)["lMorph"] = lDefault;
    }
    return true;
}

function exclude (dTokenPos, nPos, sWord, sPattern, lDefault=null) {
    if (!sWord) {
        return true;
    }
    if (!dTokenPos.has(nPos)) {
        console.log("Error. There should be a token at this position: ", nPos);
        return true;
    }
    let lMorph = _oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            dTokenPos.get(nPos)["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        dTokenPos.get(nPos)["lMorph"] = lDefault;
    }
    return true;
}

function define (dTokenPos, nPos, lMorph) {
    dTokenPos.get(nPos)["lMorph"] = lMorph;
    return true;
}


//// Disambiguation for graph rules

function g_select (oToken, sPattern, lDefault=null) {
    // select morphologies for <oToken> according to <sPattern>, always return true
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : _oSpellChecker.getMorph(oToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        if (lDefault) {
            oToken["lMorph"] = lDefault;
        }
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            oToken["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        oToken["lMorph"] = lDefault;
    }
    return true;
}

function g_exclude (oToken, sPattern, lDefault=null) {
    // select morphologies for <oToken> according to <sPattern>, always return true
    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : _oSpellChecker.getMorph(oToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        if (lDefault) {
            oToken["lMorph"] = lDefault;
        }
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            oToken["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        oToken["lMorph"] = lDefault;
    }
    return true;
}

function g_define (oToken, lMorph) {
    // set morphologies of <oToken>, always return true
    oToken["lMorph"] = lMorph;
    return true;
}

function g_define_from (oToken, nLeft=null, nRight=null) {
    let sValue = oToken["sValue"];
    if (nLeft !== null) {
        sValue = (nRight !== null) ? sValue.slice(nLeft, nRight) : sValue.slice(nLeft);
    }
    oToken["lMorph"] = _oSpellChecker.getMorph(sValue);
    return true;
}


//////// GRAMMAR CHECKER PLUGINS

${pluginsJS}


// generated code, do not edit
const oEvalFunc = {
    // callables for regex rules
${callablesJS}

    // callables for graph rules
${graph_callablesJS}
}


if (typeof(exports) !== 'undefined') {
    exports.lang = gc_engine.lang;
    exports.locales = gc_engine.locales;
    exports.pkg = gc_engine.pkg;
    exports.name = gc_engine.name;
    exports.version = gc_engine.version;
    exports.author = gc_engine.author;
    // init
    exports.load = gc_engine.load;
    exports.parse = gc_engine.parse;
    exports.getSpellChecker = gc_engine.getSpellChecker;
    // rules
    exports.ignoreRule = gc_engine.ignoreRule;
    exports.resetIgnoreRules = gc_engine.resetIgnoreRules;
    exports.reactivateRule = gc_engine.reactivateRule;
    exports.listRules = gc_engine.listRules;
    exports.getRules = gc_engine.getRules;
    // options
    exports.setOption = gc_engine.setOption;
    exports.setOptions = gc_engine.setOptions;
    exports.getOptions = gc_engine.getOptions;
    exports.getDefaultOptions = gc_engine.getDefaultOptions;
    exports.resetOptions = gc_engine.resetOptions;
    // other
    exports.TextParser = TextParser;
}
