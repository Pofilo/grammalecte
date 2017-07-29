
// HELPERS

"use strict";

// In Firefox, there is no console.log in PromiseWorker, but there is worker.log.
// In Thunderbird, you can’t access to console directly. So it’s required to pass a log function.
let funcOutput = null;

function setLogOutput (func) {
    funcOutput = func;
}

function echo (obj) {
    if (funcOutput !== null) {
        funcOutput(obj);
    } else {
        console.log(obj);
    }
    return true;
}

function logerror (e, bStack=false) {
    let sMsg = "\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message;
    if (bStack) {
        sMsg += "\n--- Stack ---\n" + e.stack;
    }
    if (funcOutput !== null) {
        funcOutput(sMsg);
    } else {
        console.error(sMsg);
    }
}

function inspect (o) {
    let sMsg = "__inspect__: " + typeof o;
    for (let sParam in o) {
        sMsg += "\n" + sParam + ": " + o.sParam;
    }
    sMsg += "\n" + JSON.stringify(o) + "\n__end__";
    echo(sMsg);
}


// load ressources in workers (suggested by Mozilla extensions reviewers)
// for more options have a look here: https://gist.github.com/Noitidart/ec1e6b9a593ec7e3efed
// if not in workers, use sdk/data.load() instead
function loadFile (spf) {
    try {
        let xRequest;
        if (typeof XMLHttpRequest !== "undefined") {
            xRequest = new XMLHttpRequest();
        }
        else {
            // JS bullshit again… necessary for Thunderbird
            let { Cc, Ci } = require("chrome");
            xRequest = Cc["@mozilla.org/xmlextras/xmlhttprequest;1"].createInstance();
            xRequest.QueryInterface(Ci.nsIXMLHttpRequest);
        }
        xRequest.open('GET', spf, false); // 3rd arg is false for synchronous, sync is acceptable in workers
        xRequest.send();
        return xRequest.responseText;
    }
    catch (e) {
        logerror(e);
        return null
    }
}


// conversions
function objectToMap (obj) {
    let m = new Map();
    for (let param in obj) {
        //console.log(param + " " + obj[param]);
        m.set(param, obj[param]);
    }
    return m;
}

function mapToObject (m) {
    let obj = {};
    for (let [k, v] of m) {
        obj[k] = v;
    }
    return obj;
}


if (typeof(exports) !== 'undefined') {
    exports.setLogOutput = setLogOutput;
    exports.echo = echo;
    exports.logerror = logerror;
    exports.inspect = inspect;
    exports.loadFile = loadFile;
    exports.objectToMap = objectToMap;
    exports.mapToObject = mapToObject;
}
