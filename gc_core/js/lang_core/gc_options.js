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

    getOptionsColors: function (sTheme="Default", sColorType="aRGB") {
        let dOptColor = (this.dOptColor.hasOwnProperty(sTheme)) ? this.dOptColor[sTheme] : this.dOptColor["Default"];
        let dColorType = (this.dColorType.hasOwnProperty(sColorType)) ? this.dColorType[sColorType] : this.dColorType["aRGB"];
        let dColor = {};
        try {
            for (let [sOpt, sColor] of Object.entries(dOptColor)) {
                dColor[sOpt] = dColorType[sColor];
            }
            return dColor;
        }
        catch (e) {
            console.error(e);
            return {}
        }
    },

    lStructOpt: ${lStructOpt},

    dOpt: {
        "JavaScript": new Map (${dOptJavaScript}),
        "Firefox": new Map (${dOptFirefox}),
        "Thunderbird": new Map (${dOptThunderbird}),
    },

    dColorType: ${dColorType},

    dOptColor: ${dOptColor},

    dOptLabel: ${dOptLabel}
}


if (typeof(exports) !== 'undefined') {
	exports.getOptions = gc_options.getOptions;
    exports.getOptionsColors = gc_options.getOptionsColors;
	exports.lStructOpt = gc_options.lStructOpt;
    exports.dOpt = gc_options.dOpt;
    exports.dColorType = gc_options.dColorType;
    exports.dOptColor = gc_options.dOptColor;
	exports.dOptLabel = gc_options.dOptLabel;
}
