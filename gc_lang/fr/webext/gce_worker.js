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


//console.log("[Worker] GC Engine Worker [start]");
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


function createResponse (sActionDone, result, dInfo, bEnd, bError=false) {
    return {
        "sActionDone": sActionDone,
        "result": result, // can be of any type
        "dInfo": dInfo,
        "bEnd": bEnd,
        "bError": bError
    };
}

function createErrorResult (e, sDescr="no description") {
    return {
        "sType": "error",
        "sDescription": sDescr,
        "sMessage": e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message
    };
}

function showData (e) {
    for (let sParam in e) {
        console.log(sParam);
        console.log(e[sParam]);
    }
}


/*
    Message Event Object
    https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
*/
onmessage = function (e) {
    let {sCommand, dParam, dInfo} = e.data;
    switch (sCommand) {
        case "init":
            init(dParam.sExtensionPath, dParam.sOptions, dParam.sContext, dInfo);
            break;
        case "parse":
            parse(dParam.sText, dParam.sCountry, dParam.bDebug, dParam.bContext, dInfo);
            break;
        case "parseAndSpellcheck":
            parseAndSpellcheck(dParam.sText, dParam.sCountry, dParam.bDebug, dParam.bContext, dInfo);
            break;
        case "parseAndSpellcheck1":
            parseAndSpellcheck1(dParam.sText, dParam.sCountry, dParam.bDebug, dParam.bContext, dInfo);
        case "getOptions":
            getOptions(dInfo);
            break;
        case "getDefaultOptions":
            getDefaultOptions(dInfo);
            break;
        case "setOptions":
            setOptions(dParam.sOptions, dInfo);
            break;
        case "setOption":
            setOption(dParam.sOptName, dParam.bValue, dInfo);
            break;
        case "resetOptions":
            resetOptions(dInfo);
            break;
        case "textToTest":
            textToTest(dParam.sText, dParam.sCountry, dParam.bDebug, dParam.bContext, dInfo);
            break;
        case "fullTests":
            fullTests('{"nbsp":true, "esp":true, "unit":true, "num":true}', dInfo);
            break;
        case "getListOfTokens":
            getListOfTokens(dParam.sText, dInfo);
            break;
        default:
            console.log("Unknown command: " + sCommand);
            showData(e.data);
    }
}



let bInitDone = false;

let oDict = null;
let oTokenizer = null;
let oLxg = null;
let oTest = null;


/*
    Technical note:
    This worker don’t work as a PromiseWorker (which returns a promise),  so when we send request
    to this worker, we can’t wait the return of the answer just after the request made.
    The answer is received by the background in another function (onmessage).
    That’s why the full text to analyze is send in one block, but analyse is returned paragraph
    by paragraph.
*/

function init (sExtensionPath, sGCOptions="", sContext="JavaScript", dInfo={}) {
    try {
        if (!bInitDone) {
            //console.log("[Worker] Loading… Extension path: " + sExtensionPath);
            conj.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/conj_data.json"));
            phonet.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/phonet_data.json"));
            mfsp.init(helpers.loadFile(sExtensionPath + "/grammalecte/fr/mfsp_data.json"));
            //console.log("[Worker] Modules have been initialized…");
            gc_engine.load(sContext, sExtensionPath+"grammalecte/_dictionaries");
            oDict = gc_engine.getDictionary();
            oTest = new TestGrammarChecking(gc_engine, sExtensionPath+"/grammalecte/fr/tests_data.json");
            oLxg = new Lexicographe(oDict);
            if (sGCOptions !== "") {
                gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
            }
            oTokenizer = new Tokenizer("fr");
            //tests();
            bInitDone = true;
        } else {
            console.log("[Worker] Already initialized…")
        }
        // we always retrieve options from the gc_engine, for setOptions filters obsolete options
        postMessage(createResponse("init", gc_engine.getOptions().gl_toString(), dInfo, true));
    }
    catch (e) {
        helpers.logerror(e);
        postMessage(createResponse("init", createErrorResult(e, "init failed"), dInfo, true, true));
    }
}


function parse (sText, sCountry, bDebug, bContext, dInfo={}) {
    for (let sParagraph of text.getParagraph(sText)) {
        let aGrammErr = gc_engine.parse(sParagraph, sCountry, bDebug, bContext);
        postMessage(createResponse("parse", aGrammErr, dInfo, false));
    }
    postMessage(createResponse("parse", null, dInfo, true));
}

function parseAndSpellcheck (sText, sCountry, bDebug, bContext, dInfo={}) {
    let i = 0;
    for (let sParagraph of text.getParagraph(sText)) {
        let aGrammErr = gc_engine.parse(sParagraph, sCountry, bDebug, bContext);
        let aSpellErr = oTokenizer.getSpellingErrors(sParagraph, oDict);
        postMessage(createResponse("parseAndSpellcheck", {sParagraph: sParagraph, iParaNum: i, aGrammErr: aGrammErr, aSpellErr: aSpellErr}, dInfo, false));
        i += 1;
    }
    postMessage(createResponse("parseAndSpellcheck", null, dInfo, true));
}

function parseAndSpellcheck1 (sParagraph, sCountry, bDebug, bContext, dInfo={}) {
    let aGrammErr = gc_engine.parse(sParagraph, sCountry, bDebug, bContext);
    let aSpellErr = oTokenizer.getSpellingErrors(sParagraph, oDict);
    postMessage(createResponse("parseAndSpellcheck1", {sParagraph: sParagraph, aGrammErr: aGrammErr, aSpellErr: aSpellErr}, dInfo, true));
}

function getOptions (dInfo={}) {
    postMessage(createResponse("getOptions", gc_engine.getOptions().gl_toString(), dInfo, true));
}

function getDefaultOptions (dInfo={}) {
    postMessage(createResponse("getDefaultOptions", gc_engine.getDefaultOptions().gl_toString(), dInfo, true));
}

function setOptions (sGCOptions, dInfo={}) {
    gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    postMessage(createResponse("setOptions", gc_engine.getOptions().gl_toString(), dInfo, true));
}

function setOption (sOptName, bValue, dInfo={}) {
    gc_engine.setOptions(new Map([ [sOptName, bValue] ]));
    postMessage(createResponse("setOption", gc_engine.getOptions().gl_toString(), dInfo, true));
}

function resetOptions (dInfo={}) {
    gc_engine.resetOptions();
    postMessage(createResponse("resetOptions", gc_engine.getOptions().gl_toString(), dInfo, true));
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

function textToTest (sText, sCountry, bDebug, bContext, dInfo={}) {
    if (!gc_engine || !oDict) {
        postMessage(createResponse("textToTest", "# Grammar checker or dictionary not loaded.", dInfo, true));
        return;
    }
    let aGrammErr = gc_engine.parse(sText, sCountry, bDebug, bContext);
    let sMsg = "";
    for (let oErr of aGrammErr) {
        sMsg += text.getReadableError(oErr) + "\n";
    }
    postMessage(createResponse("textToTest", sMsg, dInfo, true));
}

function fullTests (sGCOptions="", dInfo={}) {
    if (!gc_engine || !oDict) {
        postMessage(createResponse("fullTests", "# Grammar checker or dictionary not loaded.", dInfo, true));
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
    postMessage(createResponse("fullTests", sMsg, dInfo, true));
}



// Lexicographer

function getListOfTokens (sText, dInfo={}) {
    try {
        for (let sParagraph of text.getParagraph(sText)) {
            if (sParagraph.trim() !== "") {
                let aElem = [];
                let aRes = null;
                for (let oToken of oTokenizer.genTokens(sParagraph)) {
                    aRes = oLxg.getInfoForToken(oToken);
                    if (aRes) {
                        aElem.push(aRes);
                    }
                }
                postMessage(createResponse("getListOfTokens", aElem, dInfo, false));
            }
        }
        postMessage(createResponse("getListOfTokens", null, dInfo, true));
    }
    catch (e) {
        helpers.logerror(e);
        postMessage(createResponse("getListOfTokens", createErrorResult(e, "no tokens"), dInfo, true, true));
    }
}
