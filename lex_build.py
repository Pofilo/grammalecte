#!python3

# Lexicon builder

import argparse
from distutils import dir_util

import graphspell.dawg as fsa
from graphspell.ibdawg import IBDAWG


def build (spfSrc, sLangCode, sLangName, sfDict, bJSON=False, sDicName="", sFilter="", cStemmingMethod="S", nCompressMethod=1):
    "transform a text lexicon as a binary indexable dictionary"
    oDAWG = fsa.DAWG(spfSrc, cStemmingMethod, sLangCode, sLangName, sDicName, sFilter)
    dir_util.mkpath("graphspell/_dictionaries")
    oDAWG.writeInfo("graphspell/_dictionaries/" + sfDict + ".info.txt")
    oDAWG.writeBinary("graphspell/_dictionaries/" + sfDict + ".bdic", int(nCompressMethod))
    if bJSON:
        dir_util.mkpath("graphspell-js/_dictionaries")
        oDic = IBDAWG(sfDict + ".bdic")
        oDic.writeAsJSObject("graphspell-js/_dictionaries/" + sfDict + ".json", bBinaryDictAsHexString=True)


def main ():
    xParser = argparse.ArgumentParser()
    xParser.add_argument("src_lexicon", type=str, help="path and file name of the source lexicon")
    xParser.add_argument("lang_code", type=str, help="language code")
    xParser.add_argument("lang_name", type=str, help="language name")
    xParser.add_argument("dic_filename", type=str, help="dictionary file name (without extension)")
    xParser.add_argument("-js", "--json", help="Build dictionary in JSON", action="store_true")
    xParser.add_argument("-s", "--stemming", help="stemming method: S=suffixes, A=affixes, N=no stemming", type=str, choices=["S", "A", "N"], default="S")
    xParser.add_argument("-c", "--compress", help="compression method: 1, 2 (beta), 3, (beta)", type=int, choices=[1, 2, 3], default=1)
    xArgs = xParser.parse_args()
    build(xArgs.src_lexicon, xArgs.lang_code, xArgs.lang_name, xArgs.dic_filename, xArgs.json)
    

if __name__ == '__main__':
    main()
