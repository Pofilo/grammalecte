#!python3

# Lexicon builder

import argparse
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
        oDic.writeAsJSObject("grammalecte-js/_dictionaries/" + sDicName + ".json")


def main ():
    xParser = argparse.ArgumentParser()
    xParser.add_argument("src_lexicon", type=str, help="path and file name of the source lexicon")
    xParser.add_argument("lang_name", type=str, help="language name")
    xParser.add_argument("dic_name", type=str, help="dictionary file name (without extension)")
    xParser.add_argument("-js", "--json", help="Build dictionary in JSON", action="store_true")
    xParser.add_argument("-s", "--stemming", help="stemming method: S=suffixes, A=affixes, N=no stemming", type=str, choices=["S", "A", "N"], default="S")
    xParser.add_argument("-c", "--compress", help="compression method: 1, 2 (beta), 3, (beta)", type=int, choices=[1, 2, 3], default=1)
    xArgs = xParser.parse_args()
    build(xArgs.src_lexicon, xArgs.lang_name, xArgs.dic_name, xArgs.json)
    

if __name__ == '__main__':
    main()
