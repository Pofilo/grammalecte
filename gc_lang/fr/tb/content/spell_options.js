// JavaScript

"use strict";


const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const prefs = Cc["@mozilla.org/preferences-service;1"].getService(Ci.nsIPrefService).getBranch("extensions.grammarchecker.");


var oDialogControl = {
	load: function () {
		try {
			document.getElementById('fr-FR-modern').checked = prefs.getBoolPref('bDictModern');
			document.getElementById('fr-FR-classic').checked = prefs.getBoolPref('bDictClassic');
			document.getElementById('fr-FR-reform').checked = prefs.getBoolPref('bDictReform');
			document.getElementById('fr-FR-classic-reform').checked = prefs.getBoolPref('bDictClassicReform');
			document.getElementById('grammalecte-spelloptions-window').centerWindowOnScreen();
		}
		catch (e) {
			Cu.reportError(e);
		}
	},
	setDictionaries: function () {
		oSpellControl.init();
		this._setDictionary('fr-FR-modern', 'bDictModern');
		this._setDictionary('fr-FR-classic', 'bDictClassic');
		this._setDictionary('fr-FR-reform', 'bDictReform');
		this._setDictionary('fr-FR-classic-reform', 'bDictClassicReform');
	},
	_setDictionary: function (sDicName, sOptName) {
		try {
			let bActivate = document.getElementById(sDicName).checked;
			oSpellControl.setExtensionDictFolder(sDicName, bActivate);
			prefs.setBoolPref(sOptName, bActivate);
		}
		catch (e) {
			Cu.reportError(e);
		}
	}
};


