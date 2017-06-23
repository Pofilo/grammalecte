#!python3

# Lexicon builder

from distutils import dir_util

import grammalecte.dawg as fsa
from grammalecte.ibdawg import IBDAWG


def build (spfSrc, sLangName, sDicName, bJSON=False, cStemmingMethod="S", nCompressMethod=1):
    "transform a text lexicon as a binary indexable dictionary"
    oDAWG = fsa.DAWG(spfSrc, sLangName, cStemmingMethod)
    dir_util.mkpath("grammalecte/_dictionaries")
    oDAWG.writeInfo("grammalecte/_dictionaries/" + sDicName + ".info.txt")
    oDAWG.createBinary("grammalecte/_dictionaries/" + sDicName + ".bdic", int(nCompressMethod))
    if bJSON:
        dir_util.mkpath("grammalecte-js/_dictionaries")
        oDic = IBDAWG(sDicName + ".bdic")
        #oDic.writeAsJSObject("gc_lang/"+sLang+"/modules-js/dictionary.js")
        oDic.writeAsJSObject("grammalecte-js/_dictionaries/" + sDicName + ".json")


def main ():
    print("todo")


if __name__ == '__main__':
    main()
