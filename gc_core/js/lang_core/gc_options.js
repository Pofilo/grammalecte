// Options for Grammalecte

${map}

function getOptions (sContext="JavaScript") {
    if (dOpt.hasOwnProperty(sContext)) {
        return dOpt[sContext];
    }
    return dOpt["JavaScript"];
}

const lStructOpt = ${lStructOpt};

const dOpt = {
    "JavaScript": new Map (${dOptJavaScript}),
    "Firefox": new Map (${dOptFirefox}),
    "Thunderbird": new Map (${dOptThunderbird}),
}

const dOptLabel = ${dOptLabel};

exports.getOptions = getOptions;
exports.lStructOpt = lStructOpt;
exports.dOptLabel = dOptLabel;
