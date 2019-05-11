"""
Grammar checker default options
"""

# generated code, do not edit

import traceback

def getUI (sLang):
    "returns dictionary of UI labels"
    if sLang in _dOptLabel:
        return _dOptLabel[sLang]
    return _dOptLabel["fr"]


def getOptions (sContext="Python"):
    "returns dictionary of options"
    if sContext in _dOpt:
        return _dOpt[sContext]
    return _dOpt["Python"]


def getOptionsColors (sTheme="Default", sColorType="aRGB"):
    "returns dictionary of options colors"
    dOptColor = _dOptColor[sTheme]  if sTheme in _dOptColor  else  _dOptColor["Default"]
    dColorType = _dColorType[sColorType]  if sColorType in _dColorType  else _dColorType["aRGB"]
    try:
        return {  sOpt: dColorType[sColor] for sOpt, sColor in dOptColor.items() }
    except KeyError:
        traceback.print_exc()
        return {}


lStructOpt = ${lStructOpt}


_dOpt = {
    "Python": ${dOptPython},
    "Server": ${dOptServer},
    "Writer": ${dOptWriter}
}

_dColorType= ${dColorType}

_dOptColor = ${dOptColor}

_dOptLabel = ${dOptLabel}
