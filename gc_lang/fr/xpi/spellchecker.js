/*
	Hunspell wrapper

	XPCOM obsolete (?), but there is nothing else...
	Overly complicated and weird. To throw away ASAP if possible.

	And you can’t access to this from a PromiseWorker (it sucks).

	https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/mozISpellCheckingEngine
	https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XUL/Using_spell_checking_in_XUL
	https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsIFile
	https://developer.mozilla.org/en-US/docs/Mozilla/JavaScript_code_modules/FileUtils.jsm
*/

"use strict";


const {Cc, Ci, Cu} = require("chrome");

const FileUtils = Cu.import("resource://gre/modules/FileUtils.jsm").FileUtils;
const AddonManager = Cu.import("resource://gre/modules/AddonManager.jsm").AddonManager;

/*
const parser = Cc["@mozilla.org/parserutils;1"].getService(Ci.nsIParserUtils);
const persodict = Cc["@mozilla.org/spellchecker/personaldictionary;1"].getService(Ci.mozIPersonalDictionary);
*/

const system = require("sdk/system");

const helpers = require("resource://grammalecte/helpers.js");


let xSCEngine = null;


function initSpellChecker () {
	if (xSCEngine === null) {
		try {
			let sSpellchecker = "@mozilla.org/spellchecker/myspell;1";
			if ("@mozilla.org/spellchecker/hunspell;1" in Cc) {
			    sSpellchecker = "@mozilla.org/spellchecker/hunspell;1";
			}
			if ("@mozilla.org/spellchecker/engine;1" in Cc) {
			    sSpellchecker = "@mozilla.org/spellchecker/engine;1";
			}
			xSCEngine = Cc[sSpellchecker].getService(Ci.mozISpellCheckingEngine);
		}
		catch (e) {
			console.error("Can’t initiate the spellchecker.");
			helpers.logerror(e);
		}
	}
}

function getDictionariesList () {
	initSpellChecker();
	try {
		let l = {};
		let c = {};
		xSCEngine.getDictionaryList(l, c);
		return l.value;
	}
	catch (e) {
		helpers.logerror(e);
		return [];
	}
}

function setDictionary (sLocale) {
	if (getDictionariesList().includes(sLocale)) {
		try {
			xSCEngine.dictionary = sLocale; // en-US, fr, etc.
			return true;
		}
		catch (e) {
			helpers.logerror(e);
			return false;
		}
	} else {
		console.error("Warning. No dictionary for locale: " + sLocale);
		console.error("Existing dictionaries: " + getDictionariesList().join(" | "));
	}
	return false;
}

function check (sWord) {
	// todo: check in personal dict?
	try {
		return xSCEngine.check(sWord);
	}
	catch (e) {
		helpers.logerror(e);
		return false;
	}
}

function suggest (sWord) {
	try {
		let lSugg = {};
		xSCEngine.suggest(sWord, lSugg, {});
		return lSugg.value;
	   	// lSugg.value is a JavaScript Array of strings
	}
	catch (e) {
		helpers.logerror(e);
		return ['#Erreur.'];
	}
}

function addDirectory (sFolder) {
	try {
		let xNsiFolder = new FileUtils.File(sFolder);
		xSCEngine.addDirectory(xNsiFolder);
	}
	catch (e) {
		console.error("Unable to add directory: " + sFolder);
		helpers.logerror(e);
	}
}

function removeDirectory (sFolder) {
	// does not work but no exception raised (bug?)
	try {
		let xNsiFolder = new FileUtils.File(sFolder);
		xSCEngine.removeDirectory(xNsiFolder);
	}
	catch (e) {
		console.error("Unable to remove directory: " + sFolder);
		helpers.logerror(e);
	}
}


function setExtensionDictFolder (sDictName, bActivate) {
	try {
		let sPath = "/data/dictionaries/" + sDictName;
		AddonManager.getAddonByID("French-GC@grammalecte.net", function(addon) {
			let xURI = addon.getResourceURI(sPath);
			//console.log("> " + xURI.path);
			let sFolder = xURI.path;
			if (system.platform === "winnt") {
				sFolder = sFolder.slice(1).replace(/\//g, "\\\\");
			}
			//console.log("> " + sFolder);
			if (bActivate) {
				addDirectory(sFolder);
			} else {
				removeDirectory(sFolder);
			}
		});
	}
	catch (e) {
		console.error("Unable to add extension folder");
		helpers.logerror(e);
	}
}


exports.initSpellChecker = initSpellChecker;
exports.getDictionariesList = getDictionariesList;
exports.setDictionary = setDictionary;
exports.check = check;
exports.suggest = suggest;
exports.addDirectory = addDirectory;
exports.removeDirectory = removeDirectory;
exports.setExtensionDictFolder = setExtensionDictFolder;
