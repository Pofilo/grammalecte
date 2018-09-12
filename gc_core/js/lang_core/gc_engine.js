// Grammar checker engine
/*jslint esversion: 6*/
/*global console,require,exports*/

"use strict";

${string}
${regex}
${map}


if (typeof(require) !== 'undefined') {
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
        aNew[i] = aArray[i].gl_toCapitalize();
    }
    return aNew;
}


// data
let _sAppContext = "";                                  // what software is running
let _dOptions = null;
let _oSpellChecker = null;
let _oTokenizer = null;
let _aIgnoredRules = new Set();



var gc_engine = {

    //// Informations

    lang: "${lang}",
    locales: ${loc},
    pkg: "${implname}",
    name: "${name}",
    version: "${version}",
    author: "${author}",

    //// Initialization

    load: function (sContext="JavaScript", sPath="") {
        try {
            if (typeof(require) !== 'undefined') {
                var spellchecker = require("resource://grammalecte/graphspell/spellchecker.js");
                _oSpellChecker = new spellchecker.SpellChecker("${lang}", "", "${dic_main_filename_js}", "${dic_extended_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            } else {
                _oSpellChecker = new SpellChecker("${lang}", sPath, "${dic_main_filename_js}", "${dic_extended_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            }
            _sAppContext = sContext;
            _dOptions = gc_options.getOptions(sContext).gl_shallowCopy();     // duplication necessary, to be able to reset to default
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

    parse: function (sText, sCountry="${country_default}", bDebug=false, dOptions=null, bContext=false) {
        let oText = new TextParser(sText);
        return oText.parse(sCountry, bDebug, dOptions, bContext);
    },

    _zEndOfSentence: new RegExp ('([.?!:;…][ .?!… »”")]*|.$)', "g"),
    _zBeginOfParagraph: new RegExp ("^[-  –—.,;?!…]*", "ig"),
    _zEndOfParagraph: new RegExp ("[-  .,;?!…–—]*$", "ig"),

    getSentenceBoundaries: function* (sText) {
        let mBeginOfSentence = this._zBeginOfParagraph.exec(sText);
        let iStart = this._zBeginOfParagraph.lastIndex;
        let m;
        while ((m = this._zEndOfSentence.exec(sText)) !== null) {
            yield [iStart, this._zEndOfSentence.lastIndex];
            iStart = this._zEndOfSentence.lastIndex;
        }
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
        this.dTokenPos = new Map();
        this.dTags = new Map();
        this.dError = new Map();
        this.dErrorPriority = new Map();  // Key = position; value = priority
    }

    asString () {
        let s = "===== TEXT =====\n"
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

    parse (sCountry="${country_default}", bDebug=false, dOptions=null, bContext=false) {
        // analyses the paragraph sText and returns list of errors
        let dOpt = dOptions || _dOptions;
        let bShowRuleId = option('idrule');
        // parse paragraph
        try {
            this.parseText(this.sText, this.sText0, true, 0, sCountry, dOpt, bShowRuleId, bDebug, bContext);
        }
        catch (e) {
            console.error(e);
        }

        // cleanup
        if (this.sText.includes(" ")) {
            this.sText = this.sText.replace(/ /g, ' '); // nbsp
        }
        if (this.sText.includes(" ")) {
            this.sText = this.sText.replace(/ /g, ' '); // snbsp
        }
        if (this.sText.includes("'")) {
            this.sText = this.sText.replace(/'/g, "’");
        }
        if (this.sText.includes("‑")) {
            this.sText = this.sText.replace(/‑/g, "-"); // nobreakdash
        }

        // parse sentence
        for (let [iStart, iEnd] of gc_engine.getSentenceBoundaries(this.sText)) {
            try {
                this.sSentence = this.sText.slice(iStart, iEnd);
                this.sSentence0 = this.sText0.slice(iStart, iEnd);
                this.nOffsetWithinParagraph = iStart;
                this.lToken = Array.from(_oTokenizer.genTokens(this.sSentence, true));
                this.dTokenPos.clear();
                for (let dToken of this.lToken) {
                    if (dToken["sType"] != "INFO") {
                        this.dTokenPos.set(dToken["nStart"], dToken);
                    }
                }
                this.parseText(this.sSentence, this.sSentence0, false, iStart, sCountry, dOpt, bShowRuleId, bDebug, bContext);
            }
            catch (e) {
                console.error(e);
            }
        }
        return Array.from(this.dError.values());
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
                                                    console.log("= " + m[0] + "  # " + sLineId + "\nDA: " + dDA.gl_toString());
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
        for (let dToken of lNewToken) {
            if (this.dTokenPos.gl_get(dToken["nStart"], {}).hasOwnProperty("lMorph")) {
                dToken["lMorph"] = this.dTokenPos.get(dToken["nStart"])["lMorph"];
            }
            if (this.dTokenPos.gl_get(dToken["nStart"], {}).hasOwnProperty("aTags")) {
                dToken["aTags"] = this.dTokenPos.get(dToken["nStart"])["aTags"];
            }
        }
        this.lToken = lNewToken;
        this.dTokenPos.clear();
        for (let dToken of this.lToken) {
            if (dToken["sType"] != "INFO") {
                this.dTokenPos.set(dToken["nStart"], dToken);
            }
        }
        if (bDebug) {
            console.log("UPDATE:");
            console.log(this.asString());
        }
    }

    * _getNextPointers (dToken, dGraph, dPointer, bDebug=false) {
        // generator: return nodes where <dToken> “values” match <dNode> arcs
        try {
            let dNode = dPointer["dNode"];
            let iNode1 = dPointer["iNode1"];
            let bTokenFound = false;
            // token value
            if (dNode.hasOwnProperty(dToken["sValue"])) {
                if (bDebug) {
                    console.log("  MATCH: " + dToken["sValue"]);
                }
                yield { "iNode1": iNode1, "dNode": dGraph[dNode[dToken["sValue"]]] };
                bTokenFound = true;
            }
            if (dToken["sValue"].slice(0,2).gl_isTitle()) { // we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
                let sValue = dToken["sValue"].toLowerCase();
                if (dNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iNode1": iNode1, "dNode": dGraph[dNode[sValue]] };
                    bTokenFound = true;
                }
            }
            else if (dToken["sValue"].gl_isUpperCase()) {
                let sValue = dToken["sValue"].toLowerCase();
                if (dNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iNode1": iNode1, "dNode": dGraph[dNode[sValue]] };
                    bTokenFound = true;
                }
                sValue = dToken["sValue"].gl_toCapitalize();
                if (dNode.hasOwnProperty(sValue)) {
                    if (bDebug) {
                        console.log("  MATCH: " + sValue);
                    }
                    yield { "iNode1": iNode1, "dNode": dGraph[dNode[sValue]] };
                    bTokenFound = true;
                }
            }
            // regex value arcs
            if (dToken["sType"] != "INFO"  &&  dToken["sType"] != "PUNC"  &&  dToken["sType"] != "SIGN") {
                if (dNode.hasOwnProperty("<re_value>")) {
                    for (let sRegex in dNode["<re_value>"]) {
                        if (!sRegex.includes("¬")) {
                            // no anti-pattern
                            if (dToken["sValue"].search(sRegex) !== -1) {
                                if (bDebug) {
                                    console.log("  MATCH: ~" + sRegex);
                                }
                                yield { "iNode1": iNode1, "dNode": dGraph[dNode["<re_value>"][sRegex]] };
                                bTokenFound = true;
                            }
                        } else {
                            // there is an anti-pattern
                            let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                            if (sNegPattern && dToken["sValue"].search(sNegPattern) !== -1) {
                                continue;
                            }
                            if (!sPattern || dToken["sValue"].search(sPattern) !== -1) {
                                if (bDebug) {
                                    console.log("  MATCH: ~" + sRegex);
                                }
                                yield { "iNode1": iNode1, "dNode": dGraph[dNode["<re_value>"][sRegex]] };
                                bTokenFound = true;
                            }
                        }
                    }
                }
            }
            // analysable tokens
            if (dToken["sType"].slice(0,4) == "WORD") {
                // token lemmas
                if (dNode.hasOwnProperty("<lemmas>")) {
                    for (let sLemma of _oSpellChecker.getLemma(dToken["sValue"])) {
                        if (dNode["<lemmas>"].hasOwnProperty(sLemma)) {
                            if (bDebug) {
                                console.log("  MATCH: >" + sLemma);
                            }
                            yield { "iNode1": iNode1, "dNode": dGraph[dNode["<lemmas>"][sLemma]] };
                            bTokenFound = true;
                        }
                    }
                }
                // regex morph arcs
                if (dNode.hasOwnProperty("<re_morph>")) {
                    let lMorph = (dToken.hasOwnProperty("lMorph")) ? dToken["lMorph"] : _oSpellChecker.getMorph(dToken["sValue"]);
                    for (let sRegex in dNode["<re_morph>"]) {
                        if (!sRegex.includes("¬")) {
                            // no anti-pattern
                            if (lMorph.some(sMorph  =>  (sMorph.search(sRegex) !== -1))) {
                                if (bDebug) {
                                    console.log("  MATCH: @" + sRegex);
                                }
                                yield { "iNode1": iNode1, "dNode": dGraph[dNode["<re_morph>"][sRegex]] };
                                bTokenFound = true;
                            }
                        } else {
                            // there is an anti-pattern
                            let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                            if (sNegPattern == "*") {
                                // all morphologies must match with <sPattern>
                                if (sPattern) {
                                    if (lMorph.length > 0  &&  lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1))) {
                                        if (bDebug) {
                                            console.log("  MATCH: @" + sRegex);
                                        }
                                        yield { "iNode1": iNode1, "dNode": dGraph[dNode["<re_morph>"][sRegex]] };
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
                                    yield { "iNode1": iNode1, "dNode": dGraph[dNode["<re_morph>"][sRegex]] };
                                    bTokenFound = true;
                                }
                            }
                        }
                    }
                }
            }
            // token tags
            if (dToken.hasOwnProperty("aTags") && dNode.hasOwnProperty("<tags>")) {
                for (let sTag in dToken["aTags"]) {
                    if (dNode["<tags>"].hasOwnProperty(sTag)) {
                        if (bDebug) {
                            console.log("  MATCH: /" + sTag);
                        }
                        yield { "iNode1": iNode1, "dNode": dGraph[dNode["<tags>"][sTag]] };
                        bTokenFound = true;
                    }
                }
            }
            // meta arc (for token type)
            if (dNode.hasOwnProperty("<meta>")) {
                for (let sMeta in dNode["<meta>"]) {
                    // no regex here, we just search if <dNode["sType"]> exists within <sMeta>
                    if (sMeta == "*" || dToken["sType"] == sMeta) {
                        if (bDebug) {
                            console.log("  MATCH: *" + sMeta);
                        }
                        yield { "iNode1": iNode1, "dNode": dGraph[dNode["<meta>"][sMeta]] };
                        bTokenFound = true;
                    }
                    else if (sMeta.includes("¬")) {
                        if (!sMeta.includes(dToken["sType"])) {
                            if (bDebug) {
                                console.log("  MATCH: *" + sMeta);
                            }
                            yield { "iNode1": iNode1, "dNode": dGraph[dNode["<meta>"][sMeta]] };
                            bTokenFound = true;
                        }
                    }
                }
            }
            if (!bTokenFound  &&  dPointer.hasOwnProperty("bKeep")) {
                yield dPointer;
            }
            // JUMP
            // Warning! Recurssion!
            if (dNode.hasOwnProperty("<>")) {
                let dPointer2 = { "iNode1": iNode1, "dNode": dGraph[dNode["<>"]], "bKeep": true };
                yield* this._getNextPointers(dToken, dGraph, dPointer2, bDebug);
            }
        }
        catch (e) {
            console.error(e);
        }
    }

    parseGraph (dGraph, sCountry="${country_default}", dOptions=null, bShowRuleId=false, bDebug=false, bContext=false) {
        // parse graph with tokens from the text and execute actions encountered
        let lPointer = [];
        let bTagAndRewrite = false;
        try {
            for (let [iToken, dToken] of this.lToken.entries()) {
                if (bDebug) {
                    console.log("TOKEN: " + dToken["sValue"]);
                }
                // check arcs for each existing pointer
                let lNextPointer = [];
                for (let dPointer of lPointer) {
                    lNextPointer.push(...this._getNextPointers(dToken, dGraph, dPointer, bDebug));
                }
                lPointer = lNextPointer;
                // check arcs of first nodes
                lPointer.push(...this._getNextPointers(dToken, dGraph, { "iNode1": iToken, "dNode": dGraph[0] }, bDebug));
                // check if there is rules to check for each pointer
                for (let dPointer of lPointer) {
                    if (dPointer["dNode"].hasOwnProperty("<rules>")) {
                        let bChange = this._executeActions(dGraph, dPointer["dNode"]["<rules>"], dPointer["iNode1"]-1, iToken, dOptions, sCountry, bShowRuleId, bDebug, bContext);
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
            console.log(this);
        }
        return this.sSentence;
    }

    _executeActions (dGraph, dNode, nTokenOffset, nLastToken, dOptions, sCountry, bShowRuleId, bDebug, bContext) {
        // execute actions found in the DARG
        let bChange = false;
        for (let [sLineId, nextNodeKey] of Object.entries(dNode)) {
            let bCondMemo = null;
            for (let sRuleId of dGraph[nextNodeKey]) {
                try {
                    if (bDebug) {
                        console.log("   >TRY: " + sRuleId + " " + sLineId);
                    }
                    let [sOption, sFuncCond, cActionType, sWhat, ...eAct] = gc_rules_graph.dRule[sRuleId];
                    // Suggestion    [ option, condition, "-", replacement/suggestion/action, iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, sURL ]
                    // TextProcessor [ option, condition, "~", replacement/suggestion/action, iTokenStart, iTokenEnd, bCaseSvty ]
                    // Disambiguator [ option, condition, "=", replacement/suggestion/action ]
                    // Tag           [ option, condition, "/", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    // Immunity      [ option, condition, "%", "",                            iTokenStart, iTokenEnd ]
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
                                        this.dErrorPriority[nErrorStart] = nPriority;
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
                            else if (cActionType == "%") {
                                // immunity
                                if (bDebug) {
                                    console.log("    IMMUNITY: " + _rules_graph.dRule[sRuleId]);
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
            sMessage += "  ## " + sLineId + " # " + sRuleId;
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
            sMessage += " ## " + sLineId + " # " + sRuleId;
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
        else if (sRepl === ">" || sRepl === "_" || sRepl === "~") {
            sNew = sRepl + " ".repeat(ln-1);
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
        let dTokenMerger = null;
        for (let [iToken, dToken] of this.lToken.entries()) {
            let bKeepToken = true;
            if (dToken["sType"] != "INFO") {
                if (nMergeUntil && iToken <= nMergeUntil) {
                    dTokenMerger["sValue"] += " ".repeat(dToken["nStart"] - dTokenMerger["nEnd"]) + dToken["sValue"];
                    dTokenMerger["nEnd"] = dToken["nEnd"];
                    if (bDebug) {
                        console.log("  MERGED TOKEN: " + dTokenMerger["sValue"]);
                    }
                    bKeepToken = false;
                }
                if (dToken.hasOwnProperty("nMergeUntil")) {
                    if (iToken > nMergeUntil) { // this token is not already merged with a previous token
                        dTokenMerger = dToken;
                    }
                    if (dToken["nMergeUntil"] > nMergeUntil) {
                        nMergeUntil = dToken["nMergeUntil"];
                    }
                    delete dToken["nMergeUntil"];
                }
                else if (dToken.hasOwnProperty("bToRemove")) {
                    if (bDebug) {
                        console.log("  REMOVED: " + dToken["sValue"]);
                    }
                    this.sSentence = this.sSentence.slice(0, dToken["nStart"]) + " ".repeat(dToken["nEnd"] - dToken["nStart"]) + this.sSentence.slice(dToken["nEnd"]);
                    bKeepToken = false;
                }
            }
            //
            if (bKeepToken) {
                lNewToken.push(dToken);
                if (dToken.hasOwnProperty("sNewValue")) {
                    // rewrite token and sentence
                    if (bDebug) {
                        console.log(dToken["sValue"] + " -> " + dToken["sNewValue"]);
                    }
                    dToken["sRealValue"] = dToken["sValue"];
                    dToken["sValue"] = dToken["sNewValue"];
                    let nDiffLen = dToken["sRealValue"].length - dToken["sNewValue"].length;
                    let sNewRepl = (nDiffLen >= 0) ? dToken["sNewValue"] + " ".repeat(nDiffLen) : dToken["sNewValue"].slice(0, dToken["sRealValue"].length);
                    this.sSentence = this.sSentence.slice(0,dToken["nStart"]) + sNewRepl + this.sSentence.slice(dToken["nEnd"]);
                    delete dToken["sNewValue"];
                }
            }
            else {
                try {
                    this.dTokenPos.delete(dToken["nStart"]);
                }
                catch (e) {
                    console.log(this.asString());
                    console.log(dToken);
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

function look_chk1 (dTokenPos, s, nOffset, sPattern, sPatternGroup1, sNegPatternGroup1="") {
    // returns True if s has pattern sPattern and m.group(1) has pattern sPatternGroup1
    let zPattern = createRegExp(sPattern);
    let m = zPattern.gl_exec2(s, null);
    if (!m) {
        return false;
    }
    try {
        let sWord = m[1];
        let nPos = m.start[1] + nOffset;
        return morph(dTokenPos, [nPos, sWord], sPatternGroup1, sNegPatternGroup1);
    }
    catch (e) {
        console.error(e);
        return false;
    }
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

function g_value (dToken, sValues, nLeft=null, nRight=null) {
    // test if <dToken['sValue']> is in sValues (each value should be separated with |)
    let sValue = (nLeft === null) ? "|"+dToken["sValue"]+"|" : "|"+dToken["sValue"].slice(nLeft, nRight)+"|";
    if (sValues.includes(sValues)) {
        return true;
    }
    if (dToken["sValue"].slice(0,2).gl_isTitle()) { // we test only 2 first chars, to make valid words such as "Laissez-les", "Passe-partout".
        if (sValues.includes(sValue.toLowerCase())) {
            return true;
        }
    }
    else if (dToken["sValue"].gl_isUpperCase()) {
        //if sValue.lower() in sValues:
        //    return true;
        sValue = "|"+sValue.slice(1).gl_toCapitalize();
        if (sValues.includes(sValue)) {
            return true;
        }
    }
    return false;
}

function g_morph (dToken, sPattern, sNegPattern="", nLeft=null, nRight=null, bMemorizeMorph=true) {
    // analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies
    let lMorph;
    if (dToken.hasOwnProperty("lMorph")) {
        lMorph = dToken["lMorph"];
    }
    else {
        if (nLeft !== null) {
            lMorph = _oSpellChecker.getMorph(dToken["sValue"].slice(nLeft, nRight));
            if (bMemorizeMorph) {
                dToken["lMorph"] = lMorph;
            }
        } else {
            lMorph = _oSpellChecker.getMorph(dToken["sValue"]);
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

function g_analyse (dToken, sPattern, sNegPattern="", nLeft=null, nRight=null, bMemorizeMorph=true) {
    // analyse a token, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies
    let lMorph;
    if (nLeft !== null) {
        lMorph = _oSpellChecker.getMorph(dToken["sValue"].slice(nLeft, nRight));
        if (bMemorizeMorph) {
            dToken["lMorph"] = lMorph;
        }
    } else {
        lMorph = _oSpellChecker.getMorph(dToken["sValue"]);
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

function g_merged_analyse (dToken1, dToken2, cMerger, sPattern, sNegPattern="", bSetMorph=true) {
    // merge two token values, return True if <sNegPattern> not in morphologies and <sPattern> in morphologies (disambiguation off)
    let lMorph = _oSpellChecker.getMorph(dToken1["sValue"] + cMerger + dToken2["sValue"]);
    if (lMorph.length == 0) {
        return false;
    }
    // check negative condition
    if (sNegPattern) {
        if (sNegPattern == "*") {
            // all morph must match sPattern
            let bResult = lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1));
            if (bResult && bSetMorph) {
                dToken1["lMorph"] = lMorph;
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
        dToken1["lMorph"] = lMorph;
    }
    return bResult;
}

function g_tag_before (dToken, dTags, sTag) {
    if (!dTags.has(sTag)) {
        return false;
    }
    if (dToken["i"] > dTags.get(sTag)[0]) {
        return true;
    }
    return false;
}

function g_tag_after (dToken, dTags, sTag) {
    if (!dTags.has(sTag)) {
        return false;
    }
    if (dToken["i"] < dTags.get(sTag)[1]) {
        return true;
    }
    return false;
}

function g_tag (dToken, sTag) {
    return dToken.hasOwnProperty("aTags") && dToken["aTags"].has(sTag);
}

function g_space_between_tokens (dToken1, dToken2, nMin, nMax=null) {
    let nSpace = dToken2["nStart"] - dToken1["nEnd"]
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
    if (dTokenPos.has(nPos)) {
        return true;
    }
    let lMorph = _oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            dTokenPos.set(nPos, lSelect);
        }
    } else if (lDefault) {
        dTokenPos.set(nPos, lDefaul);
    }
    return true;
}

function exclude (dTokenPos, nPos, sWord, sPattern, lDefault=null) {
    if (!sWord) {
        return true;
    }
    if (dTokenPos.has(nPos)) {
        return true;
    }
    let lMorph = _oSpellChecker.getMorph(sWord);
    if (lMorph.length === 0  ||  lMorph.length === 1) {
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect.length > 0) {
        if (lSelect.length != lMorph.length) {
            dTokenPos.set(nPos, lSelect);
        }
    } else if (lDefault) {
        dTokenPos.set(nPos, lDefault);
    }
    return true;
}

function define (dTokenPos, nPos, lMorph) {
    dTokenPos.set(nPos, lMorph);
    return true;
}


//// Disambiguation for graph rules

function g_select (dToken, sPattern, lDefault=null) {
    // select morphologies for <dToken> according to <sPattern>, always return true
    let lMorph = (dToken.hasOwnProperty("lMorph")) ? dToken["lMorph"] : _oSpellChecker.getMorph(dToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        if (lDefault) {
            dToken["lMorph"] = lDefault;
        }
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) !== -1 );
    if (lSelect) {
        if (lSelect.length != lMorph.length) {
            dToken["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        dToken["lMorph"] = lDefault;
    }
    return true;
}

function g_exclude (dToken, sPattern, lDefault=null) {
    // select morphologies for <dToken> according to <sPattern>, always return true
    let lMorph = (dToken.hasOwnProperty("lMorph")) ? dToken["lMorph"] : _oSpellChecker.getMorph(dToken["sValue"]);
    if (lMorph.length === 0  || lMorph.length === 1) {
        if (lDefault) {
            dToken["lMorph"] = lDefault;
        }
        return true;
    }
    let lSelect = lMorph.filter( sMorph => sMorph.search(sPattern) === -1 );
    if (lSelect) {
        if (lSelect.length != lMorph.length) {
            dToken["lMorph"] = lSelect;
        }
    } else if (lDefault) {
        dToken["lMorph"] = lDefault;
    }
    return true;
}

function g_define (dToken, lMorph) {
    // set morphologies of <dToken>, always return true
    dToken["lMorph"] = lMorph;
    return true;
}

function g_define_from (dToken, nLeft=null, nRight=null) {
    if (nLeft !== null) {
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"].slice(nLeft, nRight));
    } else {
        dToken["lMorph"] = _oSpellChecker.getMorph(dToken["sValue"]);
    }
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
    exports.getSpellChecker = gc_engine.getSpellChecker;
    // sentence
    exports._zEndOfSentence = gc_engine._zEndOfSentence;
    exports._zBeginOfParagraph = gc_engine._zBeginOfParagraph;
    exports._zEndOfParagraph = gc_engine._zEndOfParagraph;
    exports.getSentenceBoundaries = gc_engine.getSentenceBoundaries;
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
