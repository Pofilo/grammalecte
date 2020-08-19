"""
Grammar checker options manager
"""

# generated code, do not edit
# template: <gc_core/py/lang_core/gc_options.py>
# variables generated in <compile_rules.py>


import traceback


dOptions = {}

_sAppContext = "Python"


def load (sContext="Python"):
    global dOptions
    global _sAppContext
    _sAppContext = sContext
    dOptions = getDefaultOptions(sContext)


def setOption (sOpt, bVal):
    "set option <sOpt> with <bVal> if it exists"
    if sOpt in dOptions:
        dOptions[sOpt] = bVal


def setOptions (dOpt):
    "update the dictionary of options with <dOpt>, only known options are updated"
    for sKey, bVal in dOpt.items():
        if sKey in dOptions:
            dOptions[sKey] = bVal


def getOptions ():
    "return a copy of options as dictionary"
    return dOptions.copy()


def resetOptions ():
    "set options to default values"
    global dOptions
    dOptions = getDefaultOptions()


def displayOptions (sLang="${lang}"):
    "display the list of grammar checking options"
    print("Options:")
    print("\n".join( [ k+":\t"+str(v)+"\t"+getOptionLabels(sLang).get(k, ("?", ""))[0]  for k, v  in sorted(dOptions.items()) ] ))
    print("")


def getOptionLabels (sLang="${sLang}"):
    "returns dictionary of UI labels"
    if sLang in _dOptLabel:
        return _dOptLabel[sLang]
    return _dOptLabel["${sLang}"]


def getDefaultOptions (sContext=""):
    "returns dictionary of options"
    if not sContext:
        sContext = _sAppContext
    if sContext in _dDefaultOpt:
        return _dDefaultOpt[sContext].copy()    # duplication necessary, to be able to reset to default
    return _dDefaultOpt["Python"].copy()        # duplication necessary, to be able to reset to default


def getOptionsColors (sTheme="Default", sColorType="aRGB"):
    "returns dictionary of options colors"
    dOptColor = _dOptColor[sTheme]  if sTheme in _dOptColor  else  _dOptColor["Default"]
    dColorType = _dColorType[sColorType]  if sColorType in _dColorType  else _dColorType["aRGB"]
    try:
        return { sOpt: dColorType[sColor] for sOpt, sColor in dOptColor.items() }
    except KeyError:
        traceback.print_exc()
        return {}


lStructOpt = ${lStructOpt}


_dDefaultOpt = {
    "Python": ${dOptPython},
    "Server": ${dOptServer},
    "Writer": ${dOptWriter}
}

_dColorType= ${dColorType}

_dOptColor = ${dOptColor}

_dOptLabel = ${dOptLabel}
