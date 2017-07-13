/*
    GRAMMALECTE [fr] FOR FIREFOX
    Author: Olivier R.
    License: GPL 3
    Website: http://www.dicollecte.org/grammalecte
*/

//// FIREFOX UI

"use strict";


const tabs = require("sdk/tabs");
const toggle = require("sdk/ui/button/toggle");
const panel = require("sdk/panel");
const self = require("sdk/self");
const core = require("sdk/view/core");
const contextmenu = require("sdk/context-menu");
const _ = require("sdk/l10n").get;
const hotkeys = require("sdk/hotkeys");
const sp = require("sdk/simple-prefs");
const clipboard = require("sdk/clipboard");
//const selection = require("sdk/selection");

const { Cu } = require("chrome");
const { BasePromiseWorker } = Cu.import('resource://gre/modules/PromiseWorker.jsm', {});

// Grammalecte
const sce = require("./spellchecker.js");
const text = require("./grammalecte/text.js");
const helpers = require("./grammalecte/helpers.js");
const tests = require("./grammalecte/tests.js");


/*
    Add dictionaries
*/
sce.initSpellChecker();
if (sp.prefs['bDictClassic']) sce.setExtensionDictFolder("fr-FR-classic", true);
if (sp.prefs['bDictModern']) sce.setExtensionDictFolder("fr-FR-modern", true);
if (sp.prefs['bDictReform']) sce.setExtensionDictFolder("fr-FR-reform", true);
if (sp.prefs['bDictClassicReform']) sce.setExtensionDictFolder("fr-FR-classic-reform", true);

function setExtensionDictFolder (sDictOption, bValue) {
    sce.setExtensionDictFolder(sDictOption, bValue);
    switch (sDictOption) {
        case "fr-FR-classic": sp.prefs["bDictClassic"] = bValue; break;
        case "fr-FR-modern": sp.prefs["bDictModern"] = bValue; break;
        case "fr-FR-reform": sp.prefs["bDictReform"] = bValue; break;
        case "fr-FR-classic-reform": sp.prefs["bDictClassicReform"] = bValue; break;
        default: console.error("# Unknown dictionary: " + sDictOption);
    }
    if (sp.prefs["bDictClassic"]) {
        sp.prefs["sDictSuggestLocale"] = "fr-FR-classic";
    } else if (sp.prefs["bDictClassicReform"]) {
        sp.prefs["sDictSuggestLocale"] = "fr-FR-classic-reform";
    } else if (sp.prefs["bDictReform"]) {
        sp.prefs["sDictSuggestLocale"] = "fr-FR-reform";
    } else if (sp.prefs["bDictModern"]) {
        sp.prefs["sDictSuggestLocale"] = "fr-FR-modern";
    } else {
        sp.prefs["sDictSuggestLocale"] = "";
    }
}


/*
    lazy loading
*/
let ibdawg = null   // module: indexable binary direct acyclic word graph
let lxg = null;     // module: lexicographer
let tf = null;      // module: text formatter

let xGCEWorker = null;  // PromiseWorker to get jobs done in a separate thread (it’s 20 times faster too!!!)
let oDict = null;
let oLxg = null;
let oTF = null;


function loadGrammarChecker (bSetPanelOptions=false) {
    if (xGCEWorker === null) {
        // Grammar checker
        xGCEWorker = new BasePromiseWorker('chrome://promiseworker/content/gce_worker.js');
        let xPromise = xGCEWorker.post('loadGrammarChecker', [sp.prefs["sGCOptions"], "Firefox"]);
        xPromise.then(
            function (aVal) {
                sp.prefs["sGCOptions"] = aVal;
                if (bSetPanelOptions) {
                    xAboutPanel.port.emit("sendGrammarOptionsToPanel", aVal);
                }
            },
            function (aReason) {
                console.error('Promise rejected - ', aReason);
            }
        ).catch(
            function (aCaught) {
                console.error('Promise Error - ', aCaught);
            }
        );
    } else if (bSetPanelOptions) {
        xAboutPanel.port.emit("sendGrammarOptionsToPanel", sp.prefs["sGCOptions"]);
    }
    return true;
}

function loadLexicographe () {
    if (ibdawg === null || lxg === null || oDict === null || oLxg === null) {
        lxg = require("./grammalecte/fr/lexicographe.js");
        ibdawg = require("resource://grammalecte/ibdawg.js");
        oDict = new ibdawg.IBDAWG("fr");
        oLxg = new lxg.Lexicographe(oDict);
    }
}

function loadTextFormatter () {
    if (tf === null || oTF === null) {
        tf = require("./grammalecte/fr/textformatter.js");
        oTF = new tf.TextFormatter();
    }
}


/*
    Current state
*/
let xActiveWorker = null;
let bDictActive = false;


/*
    Main Button
*/
const xMainButton = toggle.ToggleButton({
    id: "grammalecte-mainbutton",
    label: _("mainTitle"),
    tooltip: _("buttonTooltip"),
    icon: {
        "16": "./img/icon-16.png",
        "32": "./img/icon-32.png",
        "64": "./img/icon-64.png"
    },
    // Note: it is not possible to distinguish between left/right click
    // https://blog.mozilla.org/addons/2014/03/13/new-add-on-sdk-australis-ui-features-in-firefox-29/comment-page-1/#comment-178621,
    onClick: function (state) {
        createAboutPanel();
        xAboutPanel.show({position: xMainButton});
    }
});


/*
    About
*/

let xAboutPanel = null;

function createAboutPanel () {
    if (xAboutPanel === null) {
        xAboutPanel = panel.Panel({
            contentURL: self.data.url("about_panel.html"),
            contentScriptFile: self.data.url("about_panel.js"),
            onHide: function () {
                xMainButton.state("window", {checked: false});
                xAboutPanel.port.emit("showHelp");
            },
            position: {
                right: 0,
                bottom: 0
            },
            width: 340,
            height: 670
        });

        xAboutPanel.port.emit("calcDefaultPanelHeight");

        xAboutPanel.port.on("setHeight", function (n) {
            xAboutPanel.resize(320, n);
        });

        xAboutPanel.port.on("openConjugueur", function () {
            createConjPanel();
            xConjPanel.show({position: xMainButton});
            xConjPanel.port.emit("conjugate", "être");
        });

        xAboutPanel.port.on("openURL", function (sURL) {
            tabs.open(sURL);
        });

        xAboutPanel.port.on("loadGrammarOptions", function () {
            loadGrammarChecker(true);
        });

        xAboutPanel.port.on("loadSpellingOptions", function () {
            xAboutPanel.port.emit("sendSpellingOptionsToPanel",
                                  sp.prefs["bDictModern"], sp.prefs["bDictClassic"],
                                  sp.prefs["bDictReform"], sp.prefs["bDictClassicReform"]);
        });

        xAboutPanel.port.on("changeDictSetting", function (sDictOption, bValue) {
            setExtensionDictFolder(sDictOption, bValue);
        });

        xAboutPanel.port.on("setOption", function (sOptionId, bValue) {
            let xPromise = xGCEWorker.post('setOption', [sOptionId, bValue]);
            xPromise.then(
                function (aVal) {
                    sp.prefs["sGCOptions"] = aVal;
                },
                function (aReason) {
                    console.error('Promise rejected - ', aReason);
                }
            ).catch(
                function (aCaught) {
                    console.error('Promise Error - ', aCaught);
                }
            );
        });

        xAboutPanel.port.on("resetOptions", function () {
            let xPromise = xGCEWorker.post('resetOptions');
            xPromise.then(
                function (aVal) {
                    sp.prefs["sGCOptions"] = aVal;
                    xAboutPanel.port.emit("sendGrammarOptionsToPanel", sp.prefs["sGCOptions"]);
                },
                function (aReason) {
                    console.error('Promise rejected - ', aReason);
                }
            ).catch(
                function (aCaught) {
                    console.error('Promise Error - ', aCaught);
                }
            );
        });
    }
}


/*
    Grammar Checker
*/

let xGCPanel = null;

function createGCPanel () {
    if (xGCPanel === null) {
        xGCPanel = panel.Panel({
            contentURL: self.data.url("gc_panel.html"),
            contentScriptFile: self.data.url("gc_panel.js"),
            onShow: function () {
                xGCPanel.port.emit("setPanelWidth", sp.prefs["nGCPanelWidth"]);
                if (sp.prefs["sDictSuggestLocale"] !== "") {
                    bDictActive = sce.setDictionary(sp.prefs["sDictSuggestLocale"]);
                }
                if (!bDictActive) {
                    bDictActive = sce.setDictionary("fr"); // default dictionary in French version of Firefox
                }
            },
            onHide: function () {
                xGCPanel.port.emit("clearErrors");
                xGCPanel.resize(sp.prefs["nGCPanelWidth"], sp.prefs["nGCPanelHeight"]);
                xMainButton.state("window", {checked: false});
            },
            //contextMenu: true, /* ugly, look for contextMenuContentData */
            position: {
                right: 0,
                bottom: 0
            },
            width: sp.prefs["nGCPanelWidth"],
            height: sp.prefs["nGCPanelHeight"]
        });

        core.getActiveView(xGCPanel).setAttribute("noautohide", true);
        //core.getActiveView(xGCPanel).setAttribute("backdrag", true);
        //core.getActiveView(xGCPanel).setAttribute("level", 'floating');

        xGCPanel.port.on("closePanel", function () {
            if (xActiveWorker) {
                xActiveWorker.port.emit("clear");
                xActiveWorker = null;
            }
            xGCPanel.hide();
        });

        xGCPanel.port.on("openURL", function (sURL) {
            tabs.open(sURL);
        });

        xGCPanel.port.on("correction", function (sIdParagraph, sText) {
            if (xActiveWorker) {
                xActiveWorker.port.emit("setParagraph", parseInt(sIdParagraph), sText);
                xActiveWorker.port.emit("rewrite");
            }
        });

        xGCPanel.port.on("modifyAndCheck", function (sIdParagraph, sText) {
            if (checkConsistency(sText)) {
                if (xActiveWorker) {
                    xActiveWorker.port.emit("setParagraph", parseInt(sIdParagraph), sText);
                    xActiveWorker.port.emit("rewrite");
                }
                checkAndSendToPanel(sIdParagraph, sText);
            } else {
                if (xActiveWorker) {
                    xActiveWorker.port.emit("getParagraph", parseInt(sIdParagraph));
                }
                xGCPanel.port.emit("showMessage", _("edit_error"));
            }
        });

        xGCPanel.port.on("getSuggestionsForTo", function (sWord, sTooltipId) {
            if (bDictActive) {
                let lSugg = sce.suggest(sWord);
                xGCPanel.port.emit("suggestionsFor", sWord, lSugg.join('|'), sTooltipId);
            } else {
                xGCPanel.port.emit("suggestionsFor", sWord, "# Erreur : dictionnaire orthographique introuvable.", sTooltipId);
            }
        });

        xGCPanel.port.on("copyToClipboard", function (sText) {
            clipboard.set(sText);
        });

        xGCPanel.port.on("resize", function(sCmd, n) {
            if (sCmd == "expand") {
                xGCPanel.resize(sp.prefs["nGCPanelWidth"], sp.prefs["nGCPanelHeight"]);
            } else if (sCmd == "reduce") {
                xGCPanel.resize(280, 50);
            } else {
                switch (sCmd) {
                    case "resize_h_bigger":  if (sp.prefs["nGCPanelHeight"] < 1200) { sp.prefs["nGCPanelHeight"] += n; } break;
                    case "resize_h_smaller": if (sp.prefs["nGCPanelHeight"] > 250)  { sp.prefs["nGCPanelHeight"] -= n } break;
                    case "resize_w_bigger":  if (sp.prefs["nGCPanelWidth"]  < 1200) { sp.prefs["nGCPanelWidth"] += n; } break;
                    case "resize_w_smaller": if (sp.prefs["nGCPanelWidth"]  > 400)  { sp.prefs["nGCPanelWidth"] -= n; } break;
                }
                xGCPanel.resize(sp.prefs["nGCPanelWidth"], sp.prefs["nGCPanelHeight"]);
                xGCPanel.port.emit("setPanelWidth", sp.prefs["nGCPanelWidth"]);
            }
        });
    }
}

function checkConsistency (sText) {
    if (sText.includes("<!-- err_end -->") || sText.includes('<span id="tooltip') || sText.includes('<u id="err')) {
        return false;
    }
    return true;
}

function checkAndSendToPanel (sIdParagraph, sText) {
    let xPromise = xGCEWorker.post('parseAndTag', [sText, parseInt(sIdParagraph), "FR", false]);
    xPromise.then(
        function (aVal) {
            xGCPanel.port.emit("refreshParagraph", sIdParagraph, aVal);
        },
        function (aReason) {
            console.error('Promise rejected - ', aReason);
        }
    ).catch(
        function (aCaught) {
            console.error('Promise Error - ', aCaught);
        }
    );
}

const xHotkeyGrammarChecker = hotkeys.Hotkey({
    combo: "accel-shift-f7",
    onPress: function () {
        createGCPanel();
        xActiveWorker = tabs.activeTab.attach({
            contentScriptFile: self.data.url("replace_text.js")
        });
        xActiveWorker.port.emit("setActiveElement", true);
        xActiveWorker.port.on("yesThisIsTextZone", function (sText) {
            if (!xGCPanel.isShowing) {
                xGCPanel.show({position: xMainButton});
            }
            sendTextToPanel(sText);
        });
        xActiveWorker.port.on("emitParagraph", function (iParagraph, sParagraph) {
            checkAndSendToPanel(iParagraph.toString(), sParagraph);
        });
        xActiveWorker.port.on("closeGCPanel", function() {
            xActiveWorker = null;
            xGCPanel.hide();
        });
    }
});

const xHotkeyGC = hotkeys.Hotkey({
    // Quick test
    combo: "accel-shift-f11",
    onPress: function () {
        createGCPanel();
        if (!xGCPanel.isShowing) {
            xGCPanel.show({position: xMainButton});
        }
        xActiveWorker = null;
        sendTextToPanel("Je connait ma <i>destinées</i>. Un jour s'attachera à mon nom le souvenir de quelque chose de formidable, "
                      + "- le souvenir d’une crise comme il n'y en eut jamaiss sur terre, le souvenir de la plus profonde collision des consciences, "
                      + "le souvenirs d’un jugement prononcé contre tout tout ce qui jusqu’à présent à été cru, exigé, sanctifié. "
                      + "Je ne suis pas un homme, je suis de la dynamite. Et, avec cela, il n’y a en moi rien d’un fondateur de religion. "
                      + "Les religions sont les affaires de la populace. "
                      + "J’aie besoin de me laver les mains, après avoir été en contact avec des hommes religieux...\n"
                      + "Vous, je parie que vous n’appriéciez guère le concept de vidéoprotection. Y a t’il pourtant rien de plus sécurisant ?");
    }
});

async function sendTextToPanel (sText) {
    xGCPanel.port.emit("clearErrors");
    xGCPanel.port.emit("start");
    loadGrammarChecker();
    let iParagraph = 0; // index of paragraphs, used for identification
    let nParagraph = 0; // non empty paragraphs
    let sRes = "";
    try {
        sText = sText.normalize("NFC"); // remove combining diacritics
        for (let sParagraph of text.getParagraph(sText)) {
            if (sParagraph.trim() !== "") {
                sRes = await xGCEWorker.post('parseAndSpellcheck', [sParagraph, "FR", false, false]);
                xGCPanel.port.emit("addParagraph", sParagraph, iParagraph, sRes);
                nParagraph += 1;
            }
            iParagraph += 1;
        }
        xGCPanel.port.emit("addMessage", 'message', _("numberOfParagraphs") + " " + nParagraph);
    }
    catch (e) {
        xGCPanel.port.emit("addMessage", 'bug', e.message);
    }
    xGCPanel.port.emit("end");
}


/*
    Text Formatter
*/

let xTFPanel = null;

function createTFPanel () {
    if (xTFPanel === null) {
        xTFPanel = panel.Panel({
            contentURL: self.data.url("tf_panel.html"),
            contentScriptFile: [self.data.url("tf_panel.js"), self.data.url("../grammalecte/fr/textformatter.js")],
            onShow: function () {
                xTFPanel.port.emit("start", sp.prefs["sTFOptions"]);
            },
            position: {
                bottom: 30,
                right: 30
            },
            width: 800,
            height: 595
        });

        core.getActiveView(xTFPanel).setAttribute("noautohide", true);

        xTFPanel.port.on("setHeight", function (n) {
            xTFPanel.resize(800, n);
        });

        xTFPanel.port.on("saveOptions", function (sOptions) {
            sp.prefs["sTFOptions"] = sOptions;
        });

        xTFPanel.port.on("getTextToFormat", function () {
            if (xActiveWorker) {
                xActiveWorker.port.emit("getText");
            } else {
                xTFPanel.hide();
            }
        });

        xTFPanel.port.on("applyFormattedText", function (sText) {
            if (xActiveWorker) {
                xActiveWorker.port.emit("write", sText);
            } else {
                xTFPanel.hide();
            }
        });

        xTFPanel.port.on("closePanel", function () {
            if (xActiveWorker) {
                xActiveWorker.port.emit("clear");
                xActiveWorker = null;
            }
            xTFPanel.hide();
        });
    }
}

const xHotkeyTextFormatter = hotkeys.Hotkey({
    combo: "accel-shift-f6",
    onPress: function () {
        loadTextFormatter();
        createTFPanel();
        xActiveWorker = tabs.activeTab.attach({
            contentScriptFile: self.data.url("replace_text.js")
        });
        xActiveWorker.port.emit("setActiveElement", false);
        xActiveWorker.port.on("yesThisIsTextZone", function (sText) {
            xTFPanel.show({position: xMainButton});
        });
        xActiveWorker.port.on("emitText", function (sText) {
            xTFPanel.port.emit("receiveTextToFormat", sText);
        });
        xActiveWorker.port.on("closeTFPanel", function() {
            xActiveWorker = null;
            xTFPanel.hide();
        });
    }
});


/*
    Lexicographer
*/

let xLxgPanel = null;

function createLxgPanel () {
    if (xLxgPanel === null) {
        xLxgPanel = panel.Panel({
            contentURL: self.data.url("lxg_panel.html"),
            contentScriptFile: self.data.url("lxg_panel.js"),
            onHide: function () {
                xLxgPanel.port.emit("clear");
                xMainButton.state("window", {checked: false});
            },
            position: {
                bottom: 20,
                right: 30
            },
            width: sp.prefs["nLxgPanelWidth"],
            height: sp.prefs["nLxgPanelHeight"]
        });

        core.getActiveView(xLxgPanel).setAttribute("noautohide", true);

        xLxgPanel.port.on("closePanel", function () {
            xLxgPanel.resize(sp.prefs["nLxgPanelWidth"], sp.prefs["nLxgPanelHeight"]);
            xLxgPanel.hide();
        });

        xLxgPanel.port.on("resize", function(sCmd, n) {
            if (sCmd == "expand") {
                xLxgPanel.resize(sp.prefs["nLxgPanelWidth"], sp.prefs["nLxgPanelHeight"]);
            } else if (sCmd == "reduce") {
                xLxgPanel.resize(280, 50);
            } else {
                switch (sCmd) {
                    case "resize_h_bigger":  if (sp.prefs["nLxgPanelHeight"] < 1200) { sp.prefs["nLxgPanelHeight"] += n; } break;
                    case "resize_h_smaller": if (sp.prefs["nLxgPanelHeight"] > 250)  { sp.prefs["nLxgPanelHeight"] -= n } break;
                    case "resize_w_bigger":  if (sp.prefs["nLxgPanelWidth"]  < 1200) { sp.prefs["nLxgPanelWidth"] += n; } break;
                    case "resize_w_smaller": if (sp.prefs["nLxgPanelWidth"]  > 300)  { sp.prefs["nLxgPanelWidth"] -= n; } break;
                }
                xLxgPanel.resize(sp.prefs["nLxgPanelWidth"], sp.prefs["nLxgPanelHeight"]);
            }
        });
    }
}

async function analyzeWords (sText) {
    xLxgPanel.port.emit("startWaitIcon");
    xLxgPanel.port.emit("addSeparator", _("separator"));
    loadGrammarChecker();
    let nParagraph = 0; // non empty paragraphs
    let sRes = "";
    try {
        for (let sParagraph of text.getParagraph(sText)) {
            if (sParagraph.trim() !== "") {
                sRes = await xGCEWorker.post('getListOfElements', [sParagraph]);
                xLxgPanel.port.emit("addParagraphElems", sRes);
                nParagraph += 1;
            }
        }
        xLxgPanel.port.emit("addMessage", 'message', _("numberOfParagraphs") + " " + nParagraph);
    }
    catch (e) {
        xLxgPanel.port.emit("addMessage", 'bug', e.message);
    }
    xLxgPanel.port.emit("stopWaitIcon");
}


/*
    Conjugueur
*/

let xConjPanel = null;

function createConjPanel () {
    if (xConjPanel === null) {
        let sConjData = self.data.load("../grammalecte/fr/conj_data.json");

        xConjPanel = panel.Panel({
            contentURL: self.data.url("conj_panel.html"),
            contentScriptFile: [self.data.url("conj_panel.js"), self.data.url("../grammalecte/fr/conj.js")],
            onShow: function () {
                xConjPanel.port.emit("start");
            },
            onHide: function () {
                xMainButton.state("window", {checked: false});
            },
            position: {
                bottom: 30,
                right: 30
            },
            width: 550,
            height: 880
        });

        core.getActiveView(xConjPanel).setAttribute("noautohide", true);

        xConjPanel.port.on("show", function () {
            if (!xConjPanel.isShowing) {
                xConjPanel.show({position: xMainButton});
            }
        });

        xConjPanel.port.on("setHeight", function (n) {
            xConjPanel.resize(550, n);
        });

        xConjPanel.port.on("closePanel", function () {
            xConjPanel.hide();
        });

        xConjPanel.port.emit("provideConjData", sConjData);
    }
}

const xHotkeyConj = hotkeys.Hotkey({
    combo: "accel-shift-f8",
    onPress: function () {
        createConjPanel();
        xConjPanel.port.emit("conjugate", "être");
    }
});


/*
    Tests
*/

let xTestPanel = null;

function createTestPanel () {
    if (xTestPanel === null) {
        xTestPanel = panel.Panel({
            contentURL: self.data.url("test_panel.html"),
            contentScriptFile: self.data.url("test_panel.js"),
            onHide: function () {
                xMainButton.state("window", {checked: false});
            },
            position: {
                bottom: 30,
                right: 30
            },
            width: 350,
            height: 700
        });

        core.getActiveView(xTestPanel).setAttribute("noautohide", true);

        xTestPanel.port.on("checkText", function (sText) {
            loadGrammarChecker();
            xTestPanel.port.emit("clear");
            let xPromise = xGCEWorker.post('parse', [sText, "FR", true, false]);
            xPromise.then(
                function (aVal) {
                    let lErr = JSON.parse(aVal);
                    if (lErr.length > 0) {
                        for (let dErr of lErr) {
                            xTestPanel.port.emit("addElem", text.getReadableError(dErr));
                        }
                    } else {
                        xTestPanel.port.emit("addElem", _('noErrorFound'));
                    }
                },
                function (aReason) {
                    xTestPanel.port.emit("addElem", 'Promise rejected');
                    xTestPanel.port.emit("addElem", aReason);
                }
            ).catch(
                function (aCaught) {
                    xTestPanel.port.emit("addElem", 'Promise Error');
                    xTestPanel.port.emit("addElem", aCaught);
                }
            );
        });

        xTestPanel.port.on("allGCTests", function () {
            xTestPanel.port.emit("clear");
            xTestPanel.port.emit("addElem", 'Performing tests… Wait…');
            loadGrammarChecker();
            let xPromise = xGCEWorker.post('fullTests', ['{"nbsp":true, "esp":true, "unit":true, "num":true}']);
            xPromise.then(
                function (aVal) {
                    xTestPanel.port.emit("addElem", 'Done.');
                    xTestPanel.port.emit("addElem", aVal);
                },
                function (aReason) {
                    xTestPanel.port.emit("addElem", 'Promise rejected');
                    xTestPanel.port.emit("addElem", aReason);
                }
            ).catch(
                function (aCaught) {
                    xTestPanel.port.emit("addElem", 'Promise Error');
                    xTestPanel.port.emit("addElem", aCaught);
                }
            )
        });

        xTestPanel.port.on("closePanel", function () {
            xTestPanel.hide();
        });
    }
}

const xHotkeyFullTests = hotkeys.Hotkey({
    combo: "accel-shift-f12",
    onPress: function () {
        createTestPanel();
        xTestPanel.show({position: xMainButton});
    }
});



/*
    Context menu
*/

// Grammar checker
const xMenuItemTextAreaGC = contextmenu.Item ({
    label: _("checkText"),
    image: self.data.url("./img/icon-16.png"),
    contentScript: 'self.on("click", function (node, data) {' +
                   '  self.postMessage(node.value);' +
                   '});',
    accessKey: "g",
    onMessage: function (sText) {
        createGCPanel();
        if (!xGCPanel.isShowing) {
            xGCPanel.show({position: xMainButton});
        } else {
            xGCPanel.port.emit("clearErrors");
        }
        xActiveWorker = tabs.activeTab.attach({
            contentScriptFile: self.data.url("replace_text.js")
        });
        xActiveWorker.port.emit("setActiveElement", false);
        xActiveWorker.port.on("emitParagraph", function (iParagraph, sParagraph) {
            checkAndSendToPanel(iParagraph.toString(), sParagraph);
        });
        xActiveWorker.port.on("closeGCPanel", function() {
            xActiveWorker = null;
            xGCPanel.hide();
        });
        sendTextToPanel(sText);
    }
});

const xMenuItemSelectionGC = contextmenu.Item ({
    label: _("checkText"),
    image: self.data.url("./img/icon-16.png"),
    contentScript: 'self.on("click", function () {' +
                   '  let sText = window.getSelection().toString();' +
                   '  self.postMessage(sText);' +
                   '});',
    accessKey: "g",
    onMessage: function (sText) {
        createGCPanel();
        if (!xGCPanel.isShowing) {
            xGCPanel.show({position: xMainButton});
        } else {
            xGCPanel.port.emit("clearErrors");
        }
        xActiveWorker = null;
        sendTextToPanel(sText);
    }
});

// Text Formatter
const xMenuItemTextFormatter = contextmenu.Item ({
    label: _("textFormatter"),
    image: self.data.url("./img/icon-16.png"),
    context: contextmenu.SelectorContext("textarea"),
    contentScript: 'self.on("click", function (node, data) {' +
                   '  self.postMessage(node.value);' +
                   '});',
    accessKey: "c",
    onMessage: function (sValue) {
        loadTextFormatter();
        createTFPanel();
        xActiveWorker = tabs.activeTab.attach({
            contentScriptFile: self.data.url("replace_text.js")
        });
        xActiveWorker.port.emit("setActiveElement", false);
        xActiveWorker.port.on("emitText", function (sText) {
            xTFPanel.port.emit("receiveTextToFormat", sText);
        });
        xActiveWorker.port.on("closeTFPanel", function() {
            xActiveWorker = null;
            xTFPanel.hide();
        });
        xTFPanel.show({position: xMainButton});
    }
});

// Lexicographer
const xMenuItemSelectionLxg = contextmenu.Item ({
    label: _("lexicographer"),
    image: self.data.url("./img/icon-16.png"),
    contentScript: 'self.on("click", function () {' +
                   '  let sText = window.getSelection().toString();' +
                   '  self.postMessage(sText);' +
                   '});',
    accessKey: "l",
    onMessage: function (sText) {
        createLxgPanel();
        xLxgPanel.show({position: xMainButton});
        analyzeWords(sText);
    }
});

const xMenuItemTextAreaLxg = contextmenu.Item ({
    label: _("lexicographer"),
    image: self.data.url("./img/icon-16.png"),
    contentScript: 'self.on("click", function (node, data) {' +
                   '  self.postMessage(node.value);' +
                   '});',
    accessKey: "l",
    onMessage: function (sText) {
        createLxgPanel();
        xLxgPanel.show({position: xMainButton});
        analyzeWords(sText);
    }
});


// TextArea
const xMenuTextArea = contextmenu.Menu({
    label: "Grammalecte",
    image: self.data.url("./img/icon-16.png"),
    context: contextmenu.SelectorContext("textarea, input[type='text']"),
    accessKey: "g",
    items: [xMenuItemTextAreaGC, xMenuItemTextFormatter, xMenuItemTextAreaLxg]
});

// Selection
const xMenuSelection = contextmenu.Menu({
    label: "Grammalecte",
    image: self.data.url("./img/icon-16.png"),
    context: [contextmenu.SelectionContext(), contextmenu.PredicateContext(function (context) {
        if (context.targetName === "textarea" || context.targetName == "input") {
            return false;
        }
        return true;
    })],
    accessKey: "g",
    items: [xMenuItemSelectionGC, xMenuItemSelectionLxg]
});
