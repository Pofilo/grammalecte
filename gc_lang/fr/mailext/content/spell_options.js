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
            // main spelling dictionary
            let sMainDicName = prefs.getCharPref('sMainDicName');
            console.log("spelling dictionary:", sMainDicName);
            if (sMainDicName == "fr-classic.json") {
                console.log("classic");
                document.getElementById("classic").checked = true;
            }
            else if (sMainDicName == "fr-reform.json") {
                console.log("reform");
                document.getElementById("reform").checked = true;
            }
            else if (sMainDicName == "fr-allvars.json") {
                console.log("allvars");
                document.getElementById("allvars").checked = true;
            }
            // personal dictionary
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
        //oSpellControl.init();
        // main spelling dictionary
        let sMainDicName;
        if (document.getElementById("classic").checked) {
            console.log("classic");
            sMainDicName = "fr-classic.json";
        }
        else if (document.getElementById("reform").checked) {
            console.log("reform");
            sMainDicName = "fr-reform.json";
        }
        else if (document.getElementById("allvars").checked) {
            console.log("allvars");
            sMainDicName = "fr-allvars.json";
        }
        console.log("selected spelling dictionary:", sMainDicName);
        prefs.setCharPref("sMainDicName", sMainDicName);
        // personal dictionary
        let bActivate = document.getElementById('personal_dic').checked;
        prefs.setBoolPref("bPersonalDictionary", bActivate);
    }
};
