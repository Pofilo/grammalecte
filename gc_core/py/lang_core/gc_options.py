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


lStructOpt = ${lStructOpt}


dOpt = {
    "Python": ${dOptPython},
    "Server": ${dOptServer},
    "Writer": ${dOptWriter}
}


_dOptLabel = ${dOptLabel}
