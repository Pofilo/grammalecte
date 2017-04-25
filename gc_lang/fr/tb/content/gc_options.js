// JavaScript

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const prefs = Cc["@mozilla.org/preferences-service;1"].getService(Ci.nsIPrefService).getBranch("extensions.grammarchecker.");
//const { require } = Cu.import("resource://gre/modules/commonjs/toolkit/require.js", {});

function echo (...args) {
    Services.console.logStringMessage(args.join(" -- ") + "\n");
}

var oOptControl = {
    oOptions: null,
    load: function () {
        this._setDialogOptions(false);
    },
    _setDialogOptions: function (bDefaultOptions=false) {
        try {
            sOptions = bDefaultOptions ? prefs.getCharPref("sGCDefaultOptions") : prefs.getCharPref("sGCOptions");
            //echo(">> " + sOptions);
            this.oOptions = JSON.parse(sOptions);
            for (let sParam in this.oOptions) {
                //echo(sParam + ":" + oOptions[sParam]);
                if (document.getElementById("option_"+sParam) !== null) {
                    document.getElementById("option_"+sParam).checked = this.oOptions[sParam];
                }
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    save: function () {
        try {
            for (let xNode of document.getElementsByClassName("option")) {
                this.oOptions[xNode.id.slice(7)] = xNode.checked;
            }
            prefs.setCharPref("sGCOptions", JSON.stringify(this.oOptions));
            //echo("<< " + JSON.stringify(this.oOptions));
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    reset: function () {
        this._setDialogOptions(true);
    }
}

oOptControl.load();
