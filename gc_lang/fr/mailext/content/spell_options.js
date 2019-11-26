// JavaScript

"use strict";


const Cc = Components.classes;
const Ci = Components.interfaces;
// const Cu = Components.utils;
const prefs = Cc["@mozilla.org/preferences-service;1"].getService(Ci.nsIPrefService).getBranch("extensions.grammarchecker.");


var oDialogControl = {
    load: function () {
        try {
            // center window
            document.getElementById('grammalecte-spelloptions-window').centerWindowOnScreen();
            // Graphspell dictionaries
            document.getElementById('personal_dic').checked = prefs.getBoolPref('bPersonalDictionary');
            this.listen();
        }
        catch (e) {
            console.error(e);
        }
    },
    listen: function () {
        document.addEventListener("dialogaccept", (event) => {
            oDialogControl.setDictionaries();
        });
    },
    setDictionaries: function () {
        oSpellControl.init();
        this._setGraphspellDictionaries();
    },
    _setGraphspellDictionaries: function () {
        let bActivate = document.getElementById('personal_dic').checked;
        prefs.setBoolPref("bPersonalDictionary", bActivate);
    }
};
