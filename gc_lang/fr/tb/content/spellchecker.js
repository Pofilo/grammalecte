// JavaScript

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

/*
const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const { require } = Cu.import("resource://gre/modules/commonjs/toolkit/require.js", {});
*/


const FileUtils = Cu.import("resource://gre/modules/FileUtils.jsm").FileUtils;
const AddonManager = Cu.import("resource://gre/modules/AddonManager.jsm").AddonManager;

/*
const parser = Cc["@mozilla.org/parserutils;1"].getService(Ci.nsIParserUtils);
const persodict = Cc["@mozilla.org/spellchecker/personaldictionary;1"].getService(Ci.mozIPersonalDictionary);
*/

//const system = require("sdk/system");


var oSpellControl = {
	xSCEngine: null,
	init: function () {
		if (this.xSCEngine === null) {
			try {
				let sSpellchecker = "@mozilla.org/spellchecker/myspell;1";
				if ("@mozilla.org/spellchecker/hunspell;1" in Cc) {
				    sSpellchecker = "@mozilla.org/spellchecker/hunspell;1";
				}
				if ("@mozilla.org/spellchecker/engine;1" in Cc) {
				    sSpellchecker = "@mozilla.org/spellchecker/engine;1";
				}
				this.xSCEngine = Cc[sSpellchecker].getService(Ci.mozISpellCheckingEngine);
			}
			catch (e) {
				echo("Can’t initiate the spellchecker.");
				Cu.reportError(e);
			}
		}
	},
	getDictionariesList: function () {
		this.init();
		try {
			let l = {};
			let c = {};
			this.xSCEngine.getDictionaryList(l, c);
			return l.value;
		}
		catch (e) {
			Cu.reportError(e);
			return [];
		}
	},
	setDictionary: function (sLocale) {
		if (this.getDictionariesList().includes(sLocale)) {
			try {
				this.xSCEngine.dictionary = sLocale; // en-US, fr, etc.
				return true;
			}
			catch (e) {
				Cu.reportError(e);
				return false;
			}
		} else {
			echo("Warning. No dictionary for locale: " + sLocale);
			echo("Existing dictionaries: " + this.getDictionariesList().join(" | "));
		}
		return false;
	},
	check: function (sWord) {
		// todo: check in personal dict?
		try {
			return this.xSCEngine.check(sWord);
		}
		catch (e) {
			Cu.reportError(e);
			return false;
		}
	},
	suggest: function (sWord) {
		try {
			let lSugg = {};
			this.xSCEngine.suggest(sWord, lSugg, {});
			return lSugg.value;
		   	// lSugg.value is a JavaScript Array of strings
		}
		catch (e) {
			Cu.reportError(e);
			return ['#Erreur.'];
		}
	},
	addDirectory: function (sFolder) {
		try {
			let xNsiFolder = new FileUtils.File(sFolder);
			this.xSCEngine.addDirectory(xNsiFolder);
		}
		catch (e) {
			echo("Unable to add directory: " + sFolder);
			Cu.reportError(e);
		}
	},
	removeDirectory: function (sFolder) {
		// does not work but no exception raised (bug?)
		try {
			let xNsiFolder = new FileUtils.File(sFolder);
			this.xSCEngine.removeDirectory(xNsiFolder);
		}
		catch (e) {
			echo("Unable to remove directory: " + sFolder);
			Cu.reportError(e);
		}
	},
	setExtensionDictFolder: function (sDictName, bActivate) {
		try {
			let that = this;
			let sPath = "/content/dictionaries/" + sDictName;
			AddonManager.getAddonByID("French-GC-TB@grammalecte.net", function (addon) {
				let xURI = addon.getResourceURI(sPath);
				console.log("> " + xURI.path);
				let sFolder = xURI.path;
				//if (system.platform === "winnt") {
				if (sFolder) {
					sFolder = sFolder.slice(1).replace(/\//g, "\\\\");
				}
				console.log("> " + sFolder);
				if (bActivate) {
					that.addDirectory(sFolder);
				} else {
					that.removeDirectory(sFolder);
				}
			});
		}
		catch (e) {
			echo("Unable to add extension folder");
			Cu.reportError(e);
		}
	}
};
