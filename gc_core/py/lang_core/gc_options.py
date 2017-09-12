# generated code, do not edit

def getUI (sLang):
    if sLang in _dOptLabel:
        return _dOptLabel[sLang]
    return _dOptLabel["fr"]


def getOptions (sContext="Python"):
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
