// JavaScript

"use strict";


console.log("1");

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const prefs = Cc["@mozilla.org/preferences-service;1"].getService(Ci.nsIPrefService).getBranch("extensions.grammarchecker.");


var oOptControl = {

    load: function () {
    	console.log("load");
        try {
            document.getElementById('check_signature').checked = prefs.getBoolPref('bCheckSignature');
        }
        catch (e) {
            Cu.reportError(e);
        }
    },

    save: function () {
    	console.log("save");
        try {
            prefs.setBoolPref('bCheckSignature', document.getElementById('check_signature').checked);
        }
        catch (e) {
            Cu.reportError(e);
        }
    }
}

console.log("2");
oOptControl.load();
console.log("3");