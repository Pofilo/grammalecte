

/*
try {
    console.log("BEFORE");
    //var myhelpers = require('./grammalecte/helpers.js');
    require(['./grammalecte/helpers.js'], function (foo) {
        console.log("LOADING");
        echo("MODULE LOADED2");
    });
    console.log("AFTER");
}
catch (e) {
    console.log("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    console.error(e);
}*/

echo("VA TE FAIRE FOUTRE");



let gce = null; // module: grammar checker engine
let text = null;
let tkz = null; // module: tokenizer
let lxg = null; // module: lexicographer
let helpers = null;

let oTokenizer = null;
let oDict = null;
let oLxg = null;

function loadGrammarChecker (sGCOptions="", sContext="JavaScript") {
    if (gce === null) {
        try {
            gce = require("resource://grammalecte/fr/gc_engine.js");
            helpers = require("resource://grammalecte/helpers.js");
            text = require("resource://grammalecte/text.js");
            tkz = require("resource://grammalecte/tokenizer.js");
            lxg = require("resource://grammalecte/fr/lexicographe.js");
            oTokenizer = new tkz.Tokenizer("fr");
            helpers.setLogOutput(console.log);
            gce.load(sContext);
            oDict = gce.getDictionary();
            oLxg = new lxg.Lexicographe(oDict);
            if (sGCOptions !== "") {
                gce.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
            }
            // we always retrieve options from the gce, for setOptions filters obsolete options
            return gce.getOptions()._toString();
        }
        catch (e) {
            console.log("# Error: " + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
        }
    }
}

function parse (sText, sLang, bDebug, bContext) {
    let aGrammErr = gce.parse(sText, sLang, bDebug, bContext);
    return JSON.stringify(aGrammErr);
}

function parseAndSpellcheck (sText, sLang, bDebug, bContext) {
    let aGrammErr = gce.parse(sText, sLang, bDebug, bContext);
    let aSpellErr = oTokenizer.getSpellingErrors(sText, oDict);
    return JSON.stringify({ aGrammErr: aGrammErr, aSpellErr: aSpellErr });
}

function getOptions () {
    return gce.getOptions()._toString();
}

function getDefaultOptions () {
    return gce.getDefaultOptions()._toString();
}

function setOptions (sGCOptions) {
    gce.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    return gce.getOptions()._toString();
}

function setOption (sOptName, bValue) {
    gce.setOptions(new Map([ [sOptName, bValue] ]));
    return gce.getOptions()._toString();
}

function resetOptions () {
    gce.resetOptions();
    return gce.getOptions()._toString();
}

function fullTests (sGCOptions="") {
    if (!gce || !oDict) {
        return "# Error: grammar checker or dictionary not loaded."
    }
    let dMemoOptions = gce.getOptions();
    if (sGCOptions) {
        gce.setOptions(helpers.objectToMap(JSON.parse(sGCOptions)));
    }
    let tests = require("resource://grammalecte/tests.js");
    let oTest = new tests.TestGrammarChecking(gce);
    let sAllRes = "";
    for (let sRes of oTest.testParse()) {
        dump(sRes+"\n");
        sAllRes += sRes+"\n";
    }
    gce.setOptions(dMemoOptions);
    return sAllRes;
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


function handleMessage (oRequest, xSender, sendResponse) {
  console.log(`[background] received: ${oRequest.content}`);
  sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);


