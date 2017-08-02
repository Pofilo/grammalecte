/*
    WARNING.

    JavaScript still sucks.
    No module available in WebExtension at the moment! :(
    No require, no import/export.

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

helpers.echo("START");


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


