// Grammar checker options manager

/* jshint esversion:6 */
/* jslint esversion:6 */
/* global exports */

${map}


var gc_options = {

    dOptions: new Map(),

    sAppContext: "JavaScript",

    load: function (sContext="JavaScript") {
        this.sAppContext = sContext;
        this.dOptions = this.getDefaultOptions(sContext);
    },

    setOption: function (sOpt, bVal) {
        if (this.dOptions.has(sOpt)) {
            this.dOptions.set(sOpt, bVal);
        }
    },

    setOptions: function (dOpt) {
        this.dOptions.gl_updateOnlyExistingKeys(dOpt);
    },

    getOptions: function () {
        return this.dOptions.gl_shallowCopy();
    },

    resetOptions: function () {
        this.dOptions = this.getDefaultOptions(this._sAppContext);
    },

    getDefaultOptions: function (sContext="") {
        if (!sContext) {
            sContext = this.sAppContext;
        }
        if (this.oDefaultOpt.hasOwnProperty(sContext)) {
            return this.oDefaultOpt[sContext].gl_shallowCopy();
        }
        return this.oDefaultOpt["JavaScript"].gl_shallowCopy();
    },

    getOptionLabels: function (sLang="${sLang}") {
        if (this.oOptLabel.hasOwnProperty(sLang)) {
            return this.oOptLabel[sLang];
        }
        return this.oOptLabel["{$sLang}"];
    },

    getOptionsColors: function (sTheme="Default", sColorType="aRGB") {
        let oOptColor = (this.oOptColor.hasOwnProperty(sTheme)) ? this.oOptColor[sTheme] : this.oOptColor["Default"];
        let oColorType = (this.oColorType.hasOwnProperty(sColorType)) ? this.oColorType[sColorType] : this.oColorType["aRGB"];
        let oColor = {};
        try {
            for (let [sOpt, sColor] of Object.entries(oOptColor)) {
                oColor[sOpt] = oColorType[sColor];
            }
            return oColor;
        }
        catch (e) {
            console.error(e);
            return {};
        }
    },

    lStructOpt: ${lStructOpt},

    oDefaultOpt: {
        "JavaScript": new Map (${dOptJavaScript}),
        "Firefox": new Map (${dOptFirefox}),
        "Thunderbird": new Map (${dOptThunderbird}),
    },

    oColorType: ${dColorType},

    oOptColor: ${dOptColor},

    oOptLabel: ${dOptLabel}
};


if (typeof(exports) !== 'undefined') {
    exports.dOptions = gc_options.dOptions;
    exports.sAppContext = gc_options.sAppContext;
    exports.load = gc_options.load;
    exports.setOption = gc_options.setOption;
    exports.setOptions = gc_options.setOptions;
    exports.resetOptions = gc_options.resetOptions;
    exports.getDefaultOptions = gc_options.getDefaultOptions;
    exports.getOptions = gc_options.getOptions;
    exports.getOptionsColors = gc_options.getOptionsColors;
    exports.lStructOpt = gc_options.lStructOpt;
    exports.oDefaultOpt = gc_options.oDefaultOpt;
    exports.dColorType = gc_options.dColorType;
    exports.oOptColor = gc_options.oOptColor;
    exports.oOptLabel = gc_options.oOptLabel;
}
