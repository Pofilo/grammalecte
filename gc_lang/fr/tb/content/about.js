// JavaScript

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
//const { require } = Cu.import("resource://gre/modules/commonjs/toolkit/require.js", {});

function echo (...args) {
    Services.console.logStringMessage(args.join(" -- ") + "\n");
}


function openInBrowserURL (sURL) {
    // method found in S3.Google.Translator
    try {
        openURL(sURL);
        // Works in overlay.js, but not here… Seems there is no documentation available about this feature on Mozilla.org
    }
    catch (e) {
        Cu.reportError(e);
    }
}

function openInTabURL (sURL) {
    // method found in S3.Google.Translator
    try {
        let xWM = Cc["@mozilla.org/appshell/window-mediator;1"].getService(Ci.nsIWindowMediator);
        let xWin = xWM.getMostRecentWindow("mail:3pane");
        let xTabmail = xWin.document.getElementById('tabmail');
        xWin.focus();
        if (xTabmail) {
            xTabmail.openTab('contentTab', { contentPage: sURL });
        }
    }
    catch (e) {
        Cu.reportError(e);
    }
}
