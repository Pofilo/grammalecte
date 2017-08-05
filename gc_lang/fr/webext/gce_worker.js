/*
    WORKER:
    https://developer.mozilla.org/en-US/docs/Web/API/Worker
    https://developer.mozilla.org/en-US/docs/Web/API/DedicatedWorkerGlobalScope


    JavaScript sucks.
    No module available in WebExtension at the moment! :(
    No require, no import/export.

    In Worker, we have importScripts() which imports everything in this scope.

    In order to use the same base of code with XUL-addon for Thunderbird and SDK-addon for Firefox,
    all modules have been “objectified”. And while they are still imported via “require”
    in the previous extensions, they are loaded as background scripts in WebExtension sharing
    the same memory space…

    When JavaScript become a modern language, “deobjectify” the modules…

    ATM, import/export are not available by default:
    — Chrome 60 – behind the Experimental Web Platform flag in chrome:flags.
    — Firefox 54 – behind the dom.moduleScripts.enabled setting in about:config.
    — Edge 15 – behind the Experimental JavaScript Features setting in about:flags.

    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export
*/

"use strict";


console.log("GC Engine Worker [start]");
//console.log(self);

importScripts("grammalecte/helpers.js");
importScripts("grammalecte/str_transform.js");
importScripts("grammalecte/ibdawg.js");
importScripts("grammalecte/text.js");
importScripts("grammalecte/tokenizer.js");
importScripts("grammalecte/fr/conj.js");
importScripts("grammalecte/fr/mfsp.js");
importScripts("grammalecte/fr/phonet.js");
importScripts("grammalecte/fr/cregex.js");
importScripts("grammalecte/fr/gc_options.js");
importScripts("grammalecte/fr/gc_rules.js");
importScripts("grammalecte/fr/gc_engine.js");
importScripts("grammalecte/fr/lexicographe.js");
importScripts("grammalecte/tests.js");
/*
    Warning.
    Initialization can’t be completed at startup of the worker,
    for we need the path of the extension to load data stored in JSON files.
    This path is retrieved in background.js and passed with the event “init”.
*/


/*
    Message Event Object
    https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
*/
onmessage = function (e) {
    let oParam = e.data[1];
    switch (e.data[0]) {
        case "init":
            loadGrammarChecker(oParam.sExtensionPath, oParam.sOptions, oParam.sContext);
            break;
        case "parse":
            parse(oParam.sText, oParam.sCountry, oParam.bDebug, oParam.bContext);
            break;
        case "parseAndSpellcheck":
            parseAndSpellcheck(oParam.sText, oParam.sCountry, oParam.bDebug, oParam.bContext);
            break;
        case "getOptions":
            getOptions();
            break;
        case "getDefaultOptions":
            getDefaultOptions();
            break;
        case "setOptions":
            setOptions(oParam.sOptions);
            break;
        case "setOption":
            setOption(oParam.sOptName, oParam.bValue);
            break;
        case "resetOptions":
            resetOptions();
            break;
        case "fullTests":
            fullTests();
            break;
        case "getListOfTokens":
            getListOfTokens(oParam.sText);
            break;
        default:
            console.log("Unknown command: " + e.data[0]);
    }
}


let oDict = null;
let oTokenizer = null;
let oLxg = null;
let oTest = null;


function loadGrammarChecker (sExtensionPath, sGCOptions="", sContext="JavaScript") {
    try {
        console.log("Loading… Extension path: " + sExtensionPath);
        conj.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/conj_data.json"));
        phonet.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/phonet_data.json"));
        mfsp.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/mfsp_data.json"));
        console.log("Modules have been initialized…");
        gc_engine.load(sContext, sExtensionPath+"grammalecte/_dictionaries");
        oDict = gc_engine.getDictionary();
        oTest = new TestGrammarChecking(gc_engine, sExtensionPath+"/grammalecte/fr/tests_data.json");
        oLxg = new Lexicographe(oDict);
        if (sGCOptions !== "") {
            gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
        }
        oTokenizer = new Tokenizer("fr");
        tests();
        // we always retrieve options from the gc_engine, for setOptions filters obsolete options
        postMessage(["options", gc_engine.getOptions().gl_toString()]);
    }
    catch (e) {
        console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
        postMessage(["error", e.message]);
    }
}

function parse (sText, sCountry, bDebug, bContext) {
    let aGrammErr = gc_engine.parse(sText, sCountry, bDebug, bContext);
    postMessage(["grammar_errors", {aGrammErr: JSON.stringify(aGrammErr)}]);
}

function parseAndSpellcheck (sText, sCountry, bDebug, bContext) {
    let aGrammErr = gc_engine.parse(sText, sCountry, bDebug, bContext);
    let aSpellErr = oTokenizer.getSpellingErrors(sText, oDict);
    postMessage(["spelling_and_grammar_errors", {aGrammErr: JSON.stringify(aGrammErr), aSpellErr: JSON.stringify(aSpellErr)}]);
}

function getOptions () {
    postMessage(["options", gc_engine.getOptions().gl_toString()]);
}

function getDefaultOptions () {
    postMessage(["options", gc_engine.getDefaultOptions().gl_toString()]);
}

function setOptions (sGCOptions) {
    gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    postMessage(["options", gc_engine.getOptions().gl_toString()]);
}

function setOption (sOptName, bValue) {
    gc_engine.setOptions(new Map([ [sOptName, bValue] ]));
    postMessage(["options", gc_engine.getOptions().gl_toString()]);
}

function resetOptions () {
    gc_engine.resetOptions();
    postMessage(["options", gc_engine.getOptions().gl_toString()]);
}

function tests () {
    console.log(conj.getConj("devenir", ":E", ":2s"));
    console.log(mfsp.getMasForm("emmerdeuse", true));
    console.log(mfsp.getMasForm("pointilleuse", false));
    console.log(phonet.getSimil("est"));
    let aRes = gc_engine.parse("Je suit...");
    for (let oErr of aRes) {
        console.log(text.getReadableError(oErr));
    }
}

function fullTests (sGCOptions='{"nbsp":true, "esp":true, "unit":true, "num":true}') {
    if (!gc_engine || !oDict) {
        postMessage(["error", "# Error: grammar checker or dictionary not loaded."]);
        return;
    }
    let dMemoOptions = gc_engine.getOptions();
    if (sGCOptions) {
        gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    }
    let sMsg = "";
    for (let sRes of oTest.testParse()) {
        sMsg += sRes + "\n";
        console.log(sRes);
    }
    gc_engine.setOptions(dMemoOptions);
    postMessage(["tests_results", sMsg]);
}


// Lexicographer

function getListOfTokens (sText) {
    try {
        let aElem = [];
        let aRes = null;
        for (let oToken of oTokenizer.genTokens(sText)) {
            aRes = oLxg.getInfoForToken(oToken);
            if (aRes) {
                aElem.push(aRes);
            }
        }
        postMessage(["tokens", JSON.stringify(aElem)]);
    }
    catch (e) {
        helpers.logerror(e);
        postMessage(["error", e.message]);
    }
    
}
