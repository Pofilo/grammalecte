"""
Grammar checker default options
"""

# generated code, do not edit

def getUI (sLang):
    "returns dictionary of UI labels"
    if sLang in _dOptLabel:
        return _dOptLabel[sLang]
    return _dOptLabel["fr"]


def getOptions (sContext="Python"):
    "returns dictionary of options"
    if sContext in dOpt:
        return dOpt[sContext]
    return dOpt["Python"]


def getOptionsColors (sContext="Python"):
    "returns dictionary of options"
    if sContext in dOptColor:
        return dOptColor[sContext]
    return dOptColor["Python"]


lStructOpt = ${lStructOpt}


dOpt = {
    "Python": ${dOptPython},
    "Server": ${dOptServer},
    "Writer": ${dOptWriter}
}

dOptColor = {
    "Python": ${dOptColorPython},
    "Server": ${dOptColorServer},
    "Writer": ${dOptColorWriter}
}

_dOptLabel = ${dOptLabel}
