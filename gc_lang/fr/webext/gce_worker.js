/*
    WORKER:
    https://developer.mozilla.org/en-US/docs/Web/API/Worker
    https://developer.mozilla.org/en-US/docs/Web/API/DedicatedWorkerGlobalScope


    JavaScript still sucks.
    No module available in WebExtension at the moment! :(
    No require, no import/export.

    In Worker, we have importScripts() which imports everything in this scope.

    In order to use the same base of code with XUL-addon for Thunderbird and SDK-addon for Firefox,
    all modules have been “objectified”. And while they are still imported via “require”
    in the previous extensions, they are loaded as background scripts in WebExtension sharing
    the same memory space (it seems)…

    When JavaScript become a modern language, “deobjectify” the modules…

    ATM, import/export are not available by default:
    — Chrome 60 – behind the Experimental Web Platform flag in chrome:flags.
    — Firefox 54 – behind the dom.moduleScripts.enabled setting in about:config.
    — Edge 15 – behind the Experimental JavaScript Features setting in about:flags.

    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export
*/


console.log("GC Engine Worker [start]");
console.log(self);

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
importScripts("grammalecte/tests.js");



helpers.echo("helpers echo");

let oTokenizer = null;
let oLxg = null;

function loadGrammarChecker (sGCOptions="", sContext="JavaScript") {
    if (gc_engine === null) {
        try {
            gc_engine = require("resource://grammalecte/fr/gc_engine.js");
            helpers = require("resource://grammalecte/helpers.js");
            text = require("resource://grammalecte/text.js");
            tkz = require("resource://grammalecte/tokenizer.js");
            lxg = require("resource://grammalecte/fr/lexicographe.js");
            oTokenizer = new tkz.Tokenizer("fr");
            helpers.setLogOutput(console.log);
            gc_engine.load(sContext);
            oDict = gc_engine.getDictionary();
            oLxg = new lxg.Lexicographe(oDict);
            if (sGCOptions !== "") {
                gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
            }
            // we always retrieve options from the gc_engine, for setOptions filters obsolete options
            return gc_engine.getOptions()._toString();
        }
        catch (e) {
            console.log("# Error: " + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
        }
    }
}

function parse (sText, sLang, bDebug, bContext) {
    let aGrammErr = gc_engine.parse(sText, sLang, bDebug, bContext);
    return JSON.stringify(aGrammErr);
}

function parseAndSpellcheck (sText, sLang, bDebug, bContext) {
    let aGrammErr = gc_engine.parse(sText, sLang, bDebug, bContext);
    let aSpellErr = oTokenizer.getSpellingErrors(sText, oDict);
    return JSON.stringify({ aGrammErr: aGrammErr, aSpellErr: aSpellErr });
}

function getOptions () {
    return gc_engine.getOptions()._toString();
}

function getDefaultOptions () {
    return gc_engine.getDefaultOptions()._toString();
}

function setOptions (sGCOptions) {
    gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    return gc_engine.getOptions()._toString();
}

function setOption (sOptName, bValue) {
    gc_engine.setOptions(new Map([ [sOptName, bValue] ]));
    return gc_engine.getOptions()._toString();
}

function resetOptions () {
    gc_engine.resetOptions();
    return gc_engine.getOptions()._toString();
}

function fullTests (sGCOptions='{"nbsp":true, "esp":true, "unit":true, "num":true}') {
    if (!gc_engine || !oDict) {
        return "# Error: grammar checker or dictionary not loaded."
    }
    let dMemoOptions = gc_engine.getOptions();
    if (sGCOptions) {
        gc_engine.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    }
    let oTest = new TestGrammarChecking(gc_engine);
    for (let sRes of oTest.testParse()) {
        helpers.echo(sRes+"\n");
    }
    gc_engine.setOptions(dMemoOptions);
}


// Lexicographer

function getListOfElements (sText) {
    try {
        let aElem = [];
        let aRes = null;
        for (let oToken of oTokenizer.genTokens(sText)) {
            aRes = oLxg.getInfoForToken(oToken);
            if (aRes) {
                aElem.push(aRes);
            }
        }
        return JSON.stringify(aElem);
    }
    catch (e) {
        helpers.logerror(e);
    }
    return JSON.stringify([]);
}


helpers.echo("START");

helpers.echo(conj.getConj("devenir", ":E", ":2s"));

helpers.echo(mfsp.getMasForm("emmerdeuse", true));
helpers.echo(mfsp.getMasForm("pointilleuse", false));

helpers.echo(phonet.getSimil("est"));

let oDict = new IBDAWG("French.json");
helpers.echo(oDict.getMorph("merde"));

gc_engine.load("JavaScript");
let aRes = gc_engine.parse("Je suit...");
for (let oErr of aRes) {
    helpers.echo(text.getReadableError(oErr));
}


//fullTests();


