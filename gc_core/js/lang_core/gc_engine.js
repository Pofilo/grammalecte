// Grammar checker engine

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global require, exports, console */

"use strict";


${string}
${regex}
${map}


if (typeof(process) !== 'undefined') {
    // NodeJS
    var spellchecker = require("../graphspell/spellchecker.js");
    var gc_functions = require("./gc_functions.js");
    var gc_options = require("./gc_options.js");
    var gc_rules = require("./gc_rules.js");
    var gc_rules_graph = require("./gc_rules_graph.js");
    var cregex = require("./cregex.js");
    var text = require("../text.js");
}


function capitalizeArray (aArray) {
    // can’t map on user defined function??
    let aNew = [];
    for (let i = 0; i < aArray.length; i = i + 1) {
        aNew[i] = aArray[i].slice(0,1).toUpperCase() + aArray[i].slice(1);
    }
    return aNew;
}


var gc_engine = {

    //// Informations

    lang: "${lang}",
    locales: ${loc},
    pkg: "${implname}",
    name: "${name}",
    version: "${version}",
    author: "${author}",

    //// Tools
    oSpellChecker: null,
    oTokenizer: null,

    //// Data
    aIgnoredRules: new Set(),
    oOptionsColors: null,

    //// Initialization

    load: function (sContext="JavaScript", sColorType="aRGB", sPath="") {
        try {
            if (typeof(process) !== 'undefined') {
                this.oSpellChecker = new spellchecker.SpellChecker("${lang}", "", "${dic_main_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            } else {
                this.oSpellChecker = new SpellChecker("${lang}", sPath, "${dic_main_filename_js}", "${dic_community_filename_js}", "${dic_personal_filename_js}");
            }
            this.oSpellChecker.activateStorage();
            this.oTokenizer = this.oSpellChecker.getTokenizer();
            gc_functions.load(sContext, this.oSpellChecker);
            gc_options.load(sContext)
            this.oOptionsColors = gc_options.getOptionsColors(sContext, sColorType);
        }
        catch (e) {
            console.error(e);
        }
    },

    getSpellChecker: function () {
        return this.oSpellChecker;
    },

    //// Rules

    getRules: function (bParagraph) {
        if (!bParagraph) {
            return gc_rules.lSentenceRules;
        }
        return gc_rules.lParagraphRules;
    },

    ignoreRule: function (sRuleId) {
        this.aIgnoredRules.add(sRuleId);
    },

    resetIgnoreRules: function () {
        this.aIgnoredRules.clear();
    },

    reactivateRule: function (sRuleId) {
        this.aIgnoredRules.delete(sRuleId);
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
        gc_options.setOption(sOpt, bVal);
    },

    setOptions: function (dOpt) {
        gc_options.setOptions(dOpt);
    },

    getOptions: function () {
        return gc_options.getOptions();
    },

    getDefaultOptions: function () {
        return gc_options.getDefaultOptions();
    },

    resetOptions: function () {
        gc_options.resetOptions();
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
        let dOpt = dOptions || gc_options.dOptions;
        let bShowRuleId = option('idrule');
        // parse paragraph
        try {
            this.parseText(this.sText, this.sText0, true, 0, sCountry, dOpt, bShowRuleId, bDebug, bContext);
        }
        catch (e) {
            console.error(e);
        }
        this.lTokens = null;
        this.lTokens0 = null;
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
                this.lTokens = Array.from(gc_engine.oTokenizer.genTokens(this.sSentence, true));
                this.dTokenPos.clear();
                for (let dToken of this.lTokens) {
                    if (dToken["sType"] != "INFO") {
                        this.dTokenPos.set(dToken["nStart"], dToken);
                    }
                }
                if (bFullInfo) {
                    this.lTokens0 = Array.from(this.lTokens);
                    // the list of tokens is duplicated, to keep tokens from being deleted when analysis
                }
                this.parseText(this.sSentence, this.sSentence0, false, iStart, sCountry, dOpt, bShowRuleId, bDebug, bContext);
                if (bFullInfo) {
                    for (let oToken of this.lTokens0) {
                        gc_engine.oSpellChecker.setLabelsOnToken(oToken);
                    }
                    lSentences.push({
                        "nStart": iStart,
                        "nEnd": iEnd,
                        "sSentence": this.sSentence0,
                        "lTokens": this.lTokens0,
                        "lGrammarErrors": Array.from(this.dSentenceError.values())
                    });
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
        if (sText.includes("‐")) {
            sText = sText.replace(/‐/g, "-"); // Hyphen (U+2010)
        }
        if (sText.includes("‑")) {
            sText = sText.replace(/‑/g, "-"); // Non-Breaking Hyphen (U+2011)
        }
        if (sText.includes("@@")) {
            sText = sText.replace(/@@+/g, (sMatch, nOffest, sSource) => { return " ".repeat(sMatch.length) });
            // function as replacement: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/replace
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
                    if (!gc_engine.aIgnoredRules.has(sRuleId)) {
                        while ((m = zRegex.gl_exec2(sText, lGroups, lNegLookBefore)) !== null) {
                            let bCondMemo = null;
                            for (let [sFuncCond, cActionType, sAction, ...eAct] of lActions) {
                                // action in lActions: [ condition, action type, replacement/suggestion/action[, iGroup[, message, URL]] ]
                                try {
                                    bCondMemo = (!sFuncCond || gc_functions[sFuncCond](sText, sText0, m, this.dTokenPos, sCountry, bCondMemo));
                                    if (bCondMemo) {
                                        switch (cActionType) {
                                            case "-":
                                                // grammar error
                                                //console.log("-> error detected in " + sLineId + "\nzRegex: " + zRegex.source);
                                                let nErrorStart = nOffset + m.start[eAct[0]];
                                                if (!this.dError.has(nErrorStart) || nPriority > this.dErrorPriority.get(nErrorStart)) {
                                                    this.dError.set(nErrorStart, this._createErrorFromRegex(sText, sText0, sAction, nOffset, m, eAct[0], sLineId, sRuleId, bUppercase, eAct[1], eAct[2], bShowRuleId, sOption, bContext));
                                                    this.dErrorPriority.set(nErrorStart, nPriority);
                                                    this.dSentenceError.set(nErrorStart, this.dError.get(nErrorStart));
                                                }
                                                break;
                                            case "~":
                                                // text processor
                                                //console.log("-> text processor by " + sLineId + "\nzRegex: " + zRegex.source);
                                                sText = this.rewriteText(sText, sAction, eAct[0], m, bUppercase);
                                                bChange = true;
                                                if (bDebug) {
                                                    console.log("~ " + sText + "  -- " + m[eAct[0]] + "  # " + sLineId);
                                                }
                                                break;
                                            case "=":
                                                // disambiguation
                                                //console.log("-> disambiguation by " + sLineId + "\nzRegex: " + zRegex.source);
                                                gc_functions[sAction](sText, m, this.dTokenPos);
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
        let lNewToken = Array.from(gc_engine.oTokenizer.genTokens(sSentence, true));
        for (let oToken of lNewToken) {
            if (this.dTokenPos.gl_get(oToken["nStart"], {}).hasOwnProperty("lMorph")) {
                oToken["lMorph"] = this.dTokenPos.get(oToken["nStart"])["lMorph"];
            }
            if (this.dTokenPos.gl_get(oToken["nStart"], {}).hasOwnProperty("aTags")) {
                oToken["aTags"] = this.dTokenPos.get(oToken["nStart"])["aTags"];
            }
        }
        this.lTokens = lNewToken;
        this.dTokenPos.clear();
        for (let oToken of this.lTokens) {
            if (oToken["sType"] != "INFO") {
                this.dTokenPos.set(oToken["nStart"], oToken);
            }
        }
        if (bDebug) {
            console.log("UPDATE:");
            console.log(this.asString());
        }
    }

    * _getNextNodes (oGraph, oToken, oNode, bKeep=false) {
        // generator: return matches where <oToken> “values” match <oNode> arcs
        try {
            let bTokenFound = false;
            // token value
            if (oNode.hasOwnProperty(oToken["sValue"])) {
                yield [" ", oToken["sValue"], oNode[oToken["sValue"]]];
                bTokenFound = true;
            }
            if (oToken["sValue"].slice(0,2).gl_isTitle()) {
                let sValue = oToken["sValue"].toLowerCase();
                if (oNode.hasOwnProperty(sValue)) {
                    yield [" ", sValue, oNode[sValue]];
                    bTokenFound = true;
                }
            }
            else if (oToken["sValue"].gl_isUpperCase()) {
                let sValue = oToken["sValue"].toLowerCase();
                if (oNode.hasOwnProperty(sValue)) {
                    yield [" ", sValue, oNode[sValue]];
                    bTokenFound = true;
                }
                sValue = oToken["sValue"].gl_toCapitalize();
                if (oNode.hasOwnProperty(sValue)) {
                    yield [" ", sValue, oNode[sValue]];
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
                                yield ["~", sRegex, oNode["<re_value>"][sRegex]];
                                bTokenFound = true;
                            }
                        } else {
                            // there is an anti-pattern
                            let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                            if (sNegPattern && oToken["sValue"].search(sNegPattern) !== -1) {
                                continue;
                            }
                            if (!sPattern || oToken["sValue"].search(sPattern) !== -1) {
                                yield ["~", sRegex, oNode["<re_value>"][sRegex]];
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
                    for (let sLemma of gc_engine.oSpellChecker.getLemma(oToken["sValue"])) {
                        if (oNode["<lemmas>"].hasOwnProperty(sLemma)) {
                            yield [">", sLemma, oNode["<lemmas>"][sLemma]];
                            bTokenFound = true;
                        }
                    }
                }
                // phonetic similarity
                if (oNode.hasOwnProperty("<phonet>")) {
                    for (let sPhonet in oNode["<phonet>"]) {
                        if (sPhonet.endsWith("!")) {
                            let sPhon = sPhonet.slice(0,-1);
                            if (oToken["sValue"] == sPhon) {
                                continue;
                            }
                            if (oToken["sValue"].slice(0,1).gl_isUpperCase()) {
                                if (oToken["sValue"].toLowerCase() == sPhon) {
                                    continue;
                                }
                                if (oToken["sValue"].gl_isUpperCase() && oToken["sValue"].gl_toCapitalize() == sPhon) {
                                    continue;
                                }
                            }
                        }
                        if (phonet.isSimilAs(oToken["sValue"], sPhonet.gl_trimRight("!"))) {
                            yield ["#", sPhonet, oNode["<phonet>"][sPhonet]];
                            bTokenFound = true;
                        }
                    }
                }
                // morph arcs
                if (oNode.hasOwnProperty("<morph>")) {
                    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
                    if (lMorph.length > 0) {
                        for (let sSearch in oNode["<morph>"]) {
                            if (!sSearch.includes("¬")) {
                                // no anti-pattern
                                if (lMorph.some(sMorph  =>  (sMorph.includes(sSearch)))) {
                                    yield ["$", sSearch, oNode["<morph>"][sSearch]];
                                    bTokenFound = true;
                                }
                            } else {
                                // there is an anti-pattern
                                let [sPattern, sNegPattern] = sSearch.split("¬", 2);
                                if (sNegPattern == "*") {
                                    // all morphologies must match with <sPattern>
                                    if (sPattern) {
                                        if (lMorph.every(sMorph  =>  (sMorph.includes(sPattern)))) {
                                            yield ["$", sSearch, oNode["<morph>"][sSearch]];
                                            bTokenFound = true;
                                        }
                                    }
                                } else {
                                    if (sNegPattern  &&  lMorph.some(sMorph  =>  (sMorph.includes(sNegPattern)))) {
                                        continue;
                                    }
                                    if (!sPattern  ||  lMorph.some(sMorph  =>  (sMorph.includes(sPattern)))) {
                                        yield ["$", sSearch, oNode["<morph>"][sSearch]];
                                        bTokenFound = true;
                                    }
                                }
                            }
                        }
                    }
                }
                // regex morph arcs
                if (oNode.hasOwnProperty("<re_morph>")) {
                    let lMorph = (oToken.hasOwnProperty("lMorph")) ? oToken["lMorph"] : gc_engine.oSpellChecker.getMorph(oToken["sValue"]);
                    if (lMorph.length > 0) {
                        for (let sRegex in oNode["<re_morph>"]) {
                            if (!sRegex.includes("¬")) {
                                // no anti-pattern
                                if (lMorph.some(sMorph  =>  (sMorph.search(sRegex) !== -1))) {
                                    yield ["@", sRegex, oNode["<re_morph>"][sRegex]];
                                    bTokenFound = true;
                                }
                            } else {
                                // there is an anti-pattern
                                let [sPattern, sNegPattern] = sRegex.split("¬", 2);
                                if (sNegPattern == "*") {
                                    // all morphologies must match with <sPattern>
                                    if (sPattern) {
                                        if (lMorph.every(sMorph  =>  (sMorph.search(sPattern) !== -1))) {
                                            yield ["@", sRegex, oNode["<re_morph>"][sRegex]];
                                            bTokenFound = true;
                                        }
                                    }
                                } else {
                                    if (sNegPattern  &&  lMorph.some(sMorph  =>  (sMorph.search(sNegPattern) !== -1))) {
                                        continue;
                                    }
                                    if (!sPattern  ||  lMorph.some(sMorph  =>  (sMorph.search(sPattern) !== -1))) {
                                        yield ["@", sRegex, oNode["<re_morph>"][sRegex]];
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
                        yield ["/", sTag, oNode["<tags>"][sTag]];
                        bTokenFound = true;
                    }
                }
            }
            // meta arc (for token type)
            if (oNode.hasOwnProperty("<meta>")) {
                for (let sMeta in oNode["<meta>"]) {
                    // no regex here, we just search if <oNode["sType"]> exists within <sMeta>
                    if (sMeta == "*" || oToken["sType"] == sMeta) {
                        yield ["*", sMeta, oNode["<meta>"][sMeta]];
                        bTokenFound = true;
                    }
                    else if (sMeta.includes("¬")) {
                        if (!sMeta.includes(oToken["sType"])) {
                            yield ["*", sMeta, oNode["<meta>"][sMeta]];
                            bTokenFound = true;
                        }
                    }
                }
            }
            if (!bTokenFound && bKeep) {
                yield [null, "", -1];
            }
            // JUMP
            // Warning! Recurssion!
            if (oNode.hasOwnProperty("<>")) {
                yield* this._getNextNodes(oGraph, oToken, oGraph[oNode["<>"]], bKeep=true);
            }
        }
        catch (e) {
            console.error(e);
        }
    }

    parseGraph (oGraph, sCountry="${country_default}", dOptions=null, bShowRuleId=false, bDebug=false, bContext=false) {
        // parse graph with tokens from the text and execute actions encountered
        let lPointers = [];
        let bTagAndRewrite = false;
        try {
            for (let [iToken, oToken] of this.lTokens.entries()) {
                if (bDebug) {
                    console.log("TOKEN: " + oToken["sValue"]);
                }
                // check arcs for each existing pointer
                let lNextPointers = [];
                for (let oPointer of lPointers) {
                    if (oPointer["nMultiEnd"] != -1) {
                        if (oToken["i"] <= oPointer["nMultiEnd"]) {
                            lNextPointers.push(oPointer);
                        }
                        if (oToken["i"] != oPointer["nMultiEnd"]) {
                            continue;
                        }
                    }
                    for (let [cNodeType, sMatch, iNode] of this._getNextNodes(oGraph, oToken, oGraph[oPointer["iNode"]])) {
                        if (cNodeType === null) {
                            lNextPointers.push(oPointer);
                            continue;
                        }
                        if (bDebug) {
                            console.log("  MATCH: " + cNodeType + sMatch);
                        }
                        let nMultiEnd = (cNodeType != "&") ? -1 : dToken["nMultiStartTo"];
                        lNextPointers.push({ "iToken1": oPointer["iToken1"], "iNode": iNode, "nMultiEnd": nMultiEnd });
                    }
                }
                lPointers = lNextPointers;
                // check arcs of first nodes
                for (let [cNodeType, sMatch, iNode] of this._getNextNodes(oGraph, oToken, oGraph[0])) {
                    if (cNodeType === null) {
                        continue;
                    }
                    if (bDebug) {
                        console.log("  MATCH: " + cNodeType + sMatch);
                    }
                    let nMultiEnd = (cNodeType != "&") ? -1 : dToken["nMultiStartTo"];
                    lPointers.push({ "iToken1": iToken, "iNode": iNode, "nMultiEnd": nMultiEnd });
                }
                // check if there is rules to check for each pointer
                for (let oPointer of lPointers) {
                    if (oPointer["nMultiEnd"] != -1) {
                        if (oToken["i"] < oPointer["nMultiEnd"]) {
                            continue;
                        }
                        if (oToken["i"] == oPointer["nMultiEnd"]) {
                            oPointer["nMultiEnd"] = -1;
                        }
                    }
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
                    let [_, sOption, sFuncCond, cActionType, sAction, ...eAct] = gc_rules_graph.dRule[sRuleId];
                    // Suggestion    [ option, condition, "-", replacement/suggestion/action, iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, iURL ]
                    // TextProcessor [ option, condition, "~", replacement/suggestion/action, iTokenStart, iTokenEnd, bCaseSvty ]
                    // Disambiguator [ option, condition, "=", replacement/suggestion/action ]
                    // Tag           [ option, condition, "/", replacement/suggestion/action, iTokenStart, iTokenEnd ]
                    // Immunity      [ option, condition, "!", "",                            iTokenStart, iTokenEnd ]
                    // Immunity      [ option, condition, "&", "",                            iTokenStart, iTokenEnd ]
                    // Test          [ option, condition, ">", "" ]
                    if (!sOption || dOptions.gl_get(sOption, false)) {
                        bCondMemo = !sFuncCond || gc_functions[sFuncCond](this.lTokens, nTokenOffset, nLastToken, sCountry, bCondMemo, this.dTags, this.sSentence, this.sSentence0);
                        if (bCondMemo) {
                            if (cActionType == "-") {
                                // grammar error
                                let [iTokenStart, iTokenEnd, cStartLimit, cEndLimit, bCaseSvty, nPriority, sMessage, iURL] = eAct;
                                let nTokenErrorStart = (iTokenStart > 0) ? nTokenOffset + iTokenStart : nLastToken + iTokenStart;
                                if (!this.lTokens[nTokenErrorStart].hasOwnProperty("sImmunity") || (this.lTokens[nTokenErrorStart]["sImmunity"] != "*" && !this.lTokens[nTokenErrorStart]["sImmunity"].includes(sOption))) {
                                    let nTokenErrorEnd = (iTokenEnd > 0) ? nTokenOffset + iTokenEnd : nLastToken + iTokenEnd;
                                    let nErrorStart = this.nOffsetWithinParagraph + ((cStartLimit == "<") ? this.lTokens[nTokenErrorStart]["nStart"] : this.lTokens[nTokenErrorStart]["nEnd"]);
                                    let nErrorEnd = this.nOffsetWithinParagraph + ((cEndLimit == ">") ? this.lTokens[nTokenErrorEnd]["nEnd"] : this.lTokens[nTokenErrorEnd]["nStart"]);
                                    if (!this.dError.has(nErrorStart) || nPriority > this.dErrorPriority.gl_get(nErrorStart, -1)) {
                                        this.dError.set(nErrorStart, this._createErrorFromTokens(sAction, nTokenOffset, nLastToken, nTokenErrorStart, nErrorStart, nErrorEnd, sLineId, sRuleId, bCaseSvty,
                                                                                                 sMessage, gc_rules_graph.dURL[iURL], bShowRuleId, sOption, bContext));
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
                                this._tagAndPrepareTokenForRewriting(sAction, nTokenStart, nTokenEnd, nTokenOffset, nLastToken, eAct[2], bDebug);
                                bChange = true;
                                if (bDebug) {
                                    console.log(`    TEXT_PROCESSOR: [${this.lTokens[nTokenStart]["sValue"]}:${this.lTokens[nTokenEnd]["sValue"]}]  > ${sAction}`);
                                }
                            }
                            else if (cActionType == "=") {
                                // disambiguation
                                gc_functions[sAction](this.lTokens, nTokenOffset, nLastToken);
                                if (bDebug) {
                                    console.log(`    DISAMBIGUATOR: (${sAction})  [${this.lTokens[nTokenOffset+1]["sValue"]}:${this.lTokens[nLastToken]["sValue"]}]`);
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
                                    if (this.lTokens[i].hasOwnProperty("aTags")) {
                                        this.lTokens[i]["aTags"].add(...sAction.split("|"))
                                    } else {
                                        this.lTokens[i]["aTags"] = new Set(sAction.split("|"));
                                    }
                                }
                                if (bDebug) {
                                    console.log(`    TAG:  ${sAction} > [${this.lTokens[nTokenStart]["sValue"]}:${this.lTokens[nTokenEnd]["sValue"]}]`);
                                }
                                for (let sTag of sAction.split("|")) {
                                    if (!this.dTags.has(sTag)) {
                                        this.dTags.set(sTag, [nTokenStart, nTokenEnd]);
                                    } else {
                                        this.dTags.set(sTag, [Math.min(nTokenStart, this.dTags.get(sTag)[0]), Math.max(nTokenEnd, this.dTags.get(sTag)[1])]);
                                    }
                                }
                            }
                            else if (cActionType == "!") {
                                // immunity
                                if (bDebug) {
                                    console.log("    IMMUNITY: " + sLineId + " / " + sRuleId);
                                }
                                let nTokenStart = (eAct[0] > 0) ? nTokenOffset + eAct[0] : nLastToken + eAct[0];
                                let nTokenEnd = (eAct[1] > 0) ? nTokenOffset + eAct[1] : nLastToken + eAct[1];
                                let sImmunity = sAction || "*";
                                if (nTokenEnd - nTokenStart == 0) {
                                    this.lTokens[nTokenStart]["sImmunity"] = sImmunity;
                                    let nErrorStart = this.nOffsetWithinParagraph + this.lTokens[nTokenStart]["nStart"];
                                    if (this.dError.has(nErrorStart)) {
                                        this.dError.delete(nErrorStart);
                                    }
                                } else {
                                    for (let i = nTokenStart;  i <= nTokenEnd;  i++) {
                                        this.lTokens[i]["sImmunity"] = sImmunity;
                                        let nErrorStart = this.nOffsetWithinParagraph + this.lTokens[i]["nStart"];
                                        if (this.dError.has(nErrorStart)) {
                                            this.dError.delete(nErrorStart);
                                        }
                                    }
                                }
                            }
                            else if (cActionType == "#") {
                                // multi-tokens
                                let nTokenStart = (eAct[0] > 0) ? nTokenOffset + eAct[0] : nLastToken + eAct[0];
                                let nTokenEnd = (eAct[1] > 0) ? nTokenOffset + eAct[1] : nLastToken + eAct[1];
                                let oMultiToken = {
                                    "nTokenStart": nTokenStart,
                                    "nTokenEnd": nTokenEnd,
                                    "lTokens": this.lTokens.slice(nTokenStart, nTokenEnd+1),
                                    "lMorph": (sAction) ? sAction.split("|") : [":HM"]
                                }
                                this.lTokens[nTokenStart]["nMultiStartTo"] = nTokenEnd
                                this.lTokens[nTokenEnd]["nMultiEndFrom"] = nTokenStart
                                this.lTokens[nTokenStart]["dMultiToken"] = dMultiToken
                                this.lTokens[nTokenEnd]["dMultiToken"] = dMultiToken
                            }
                            else {
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

    _createErrorFromRegex (sText, sText0, sSugg, nOffset, m, iGroup, sLineId, sRuleId, bCaseSvty, sMsg, sURL, bShowRuleId, sOption, bContext) {
        let nStart = nOffset + m.start[iGroup];
        let nEnd = nOffset + m.end[iGroup];
        // suggestions
        let lSugg = [];
        if (sSugg.startsWith("=")) {
            sSugg = gc_functions[sSugg.slice(1)](sText, m);
            lSugg = (sSugg) ? sSugg.replace(/ /g, " ").split("|") : [];
        } else if (sSugg == "_") {
            lSugg = [];
        } else {
            lSugg = sSugg.gl_expand(m).replace(/ /g, " ").split("|");
        }
        if (bCaseSvty && lSugg.length > 0 && m[iGroup].slice(0,1).gl_isUpperCase()) {
            lSugg = (m[iGroup].gl_isUpperCase()) ? lSugg.map((s) => s.toUpperCase()) : capitalizeArray(lSugg);
        }
        // Message
        let sMessage = (sMsg.startsWith("=")) ? gc_functions[sMsg.slice(1)](sText, m) : sMsg.gl_expand(m);
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
            sSugg = gc_functions[sSugg.slice(1)](this.lTokens, nTokenOffset, nLastToken);
            lSugg = (sSugg) ? sSugg.replace(/ /g, " ").split("|") : [];
        } else if (sSugg == "_") {
            lSugg = [];
        } else {
            lSugg = this._expand(sSugg, nTokenOffset, nLastToken).replace(/ /g, " ").split("|");
        }
        if (bCaseSvty && lSugg.length > 0 && this.lTokens[iFirstToken]["sValue"].slice(0,1).gl_isUpperCase()) {
            lSugg = (this.sSentence.slice(nStart, nEnd).gl_isUpperCase()) ? lSugg.map((s) => s.toUpperCase()) : capitalizeArray(lSugg);
        }
        // Message
        let sMessage = (sMsg.startsWith("=")) ? gc_functions[sMsg.slice(1)](this.lTokens, nTokenOffset, nLastToken) : this._expand(sMsg, nTokenOffset, nLastToken);
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
            "aColor": gc_engine.oOptionsColors[sOption],
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
                sText = sText.replace(m[0], this.lTokens[nLastToken+parseInt(m[1],10)+1]["sValue"]);
            } else {
                sText = sText.replace(m[0], this.lTokens[nTokenOffset+parseInt(m[1],10)]["sValue"]);
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
            sNew = gc_functions[sRepl.slice(1)](sText, m);
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

    _tagAndPrepareTokenForRewriting (sAction, nTokenRewriteStart, nTokenRewriteEnd, nTokenOffset, nLastToken, bCaseSvty, bDebug) {
        // text processor: rewrite tokens between <nTokenRewriteStart> and <nTokenRewriteEnd> position
        if (sAction === "*") {
            // purge text
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                this.lTokens[nTokenRewriteStart]["bToRemove"] = true;
            } else {
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    this.lTokens[i]["bToRemove"] = true;
                }
            }
        }
        else if (sAction === "␣") {
            // merge tokens
            this.lTokens[nTokenRewriteStart]["nMergeUntil"] = nTokenRewriteEnd;
        }
        else if (sAction.startsWith("␣")) {
            sAction = this._expand(sAction, nTokenOffset, nLastToken);
            this.lTokens[nTokenRewriteStart]["nMergeUntil"] = nTokenRewriteEnd;
            this.lTokens[nTokenRewriteStart]["sMergedValue"] = sAction.slice(1);
        }
        else if (sAction === "_") {
            // neutralized token
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                this.lTokens[nTokenRewriteStart]["sNewValue"] = "_";
            } else {
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    this.lTokens[i]["sNewValue"] = "_";
                }
            }
        }
        else {
            if (sAction.startsWith("=")) {
                sAction = gc_functions[sAction.slice(1)](this.lTokens, nTokenOffset, nLastToken);
            } else {
                sAction = this._expand(sAction, nTokenOffset, nLastToken);
            }
            let bUppercase = bCaseSvty && this.lTokens[nTokenRewriteStart]["sValue"].slice(0,1).gl_isUpperCase();
            if (nTokenRewriteEnd - nTokenRewriteStart == 0) {
                // one token
                if (bUppercase) {
                    sAction = sAction.gl_toCapitalize();
                }
                this.lTokens[nTokenRewriteStart]["sNewValue"] = sAction;
            }
            else {
                // several tokens
                let lTokenValue = sAction.split("|");
                if (lTokenValue.length != (nTokenRewriteEnd - nTokenRewriteStart + 1)) {
                    if (bDebug) {
                        console.log("Error. Text processor: number of replacements != number of tokens.");
                    }
                    return;
                }
                let j = 0;
                for (let i = nTokenRewriteStart;  i <= nTokenRewriteEnd;  i++) {
                    let sValue = lTokenValue[j];
                    if (!sValue || sValue === "*") {
                        this.lTokens[i]["bToRemove"] = true;
                    } else {
                        if (bUppercase) {
                            sValue = sValue.gl_toCapitalize();
                        }
                        this.lTokens[i]["sNewValue"] = sValue;
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
        for (let [iToken, oToken] of this.lTokens.entries()) {
            let bKeepToken = true;
            if (oToken["sType"] != "INFO") {
                if (nMergeUntil && iToken <= nMergeUntil) {
                    oMergingToken["sValue"] += " ".repeat(oToken["nStart"] - oMergingToken["nEnd"]) + oToken["sValue"];
                    oMergingToken["nEnd"] = oToken["nEnd"];
                    if (bDebug) {
                        console.log("  MERGED TOKEN: " + oMergingToken["sValue"]);
                    }
                    oToken["bMerged"] = true;
                    bKeepToken = false;
                    if (iToken == nMergeUntil && oMergingToken.hasOwnProperty("sMergedValue")) {
                        oMergingToken["sValue"] = oMergingToken["sMergedValue"];
                        let sSpaceFiller = " ".repeat(oToken["nEnd"] - oMergingToken["nStart"] - oMergingToken["sMergedValue"].length);
                        this.sSentence = this.sSentence.slice(0, oMergingToken["nStart"]) + oMergingToken["sMergedValue"] + sSpaceFiller + this.sSentence.slice(oToken["nEnd"]);
                    }
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
        }
        if (bDebug) {
            console.log("  TEXT REWRITED: " + this.sSentence);
        }
        this.lTokens.length = 0;
        this.lTokens = lNewToken;
    }
};


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
