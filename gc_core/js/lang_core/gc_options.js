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

    lStructOpt: ${lStructOpt},

    dOpt: {
        "JavaScript": new Map (${dOptJavaScript}),
        "Firefox": new Map (${dOptFirefox}),
        "Thunderbird": new Map (${dOptThunderbird}),
    },

    dOptLabel: ${dOptLabel}
}


if (typeof(exports) !== 'undefined') {
	exports.getOptions = gc_options.getOptions;
	exports.lStructOpt = gc_options.lStructOpt;
    exports.dOpt = gc_options.dOpt;
	exports.dOptLabel = gc_options.dOptLabel;
}
