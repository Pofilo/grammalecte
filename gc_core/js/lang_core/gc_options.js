// Options for Grammalecte
/*jslint esversion: 6*/
/*global exports*/

${map}


var gc_options = {
    getOptions: function (sContext="JavaScript") {
        if (this.dOpt.hasOwnProperty(sContext)) {
            return this.dOpt[sContext];
        }
        return this.dOpt["JavaScript"];
    },

    getOptionsColors: function (sContext="JavaScript") {
        if (this.dOptColor.hasOwnProperty(sContext)) {
            return this.dOptColor[sContext];
        }
        return this.dOptColor["JavaScript"];
    },

    lStructOpt: ${lStructOpt},

    dOpt: {
        "JavaScript": new Map (${dOptJavaScript}),
        "Firefox": new Map (${dOptFirefox}),
        "Thunderbird": new Map (${dOptThunderbird}),
    },

    dOptColor: {
        "JavaScript": new Map (${dOptColorJavaScript}),
        "Firefox": new Map (${dOptColorFirefox}),
        "Thunderbird": new Map (${dOptColorThunderbird}),
    },

    dOptLabel: ${dOptLabel}
}


if (typeof(exports) !== 'undefined') {
	exports.getOptions = gc_options.getOptions;
    exports.getOptionsColors = gc_options.getOptionsColors;
	exports.lStructOpt = gc_options.lStructOpt;
    exports.dOpt = gc_options.dOpt;
    exports.dOptColor = gc_options.dOptColor;
	exports.dOptLabel = gc_options.dOptLabel;
}
