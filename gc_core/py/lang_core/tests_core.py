#! python3

"""
Grammar checker tests for French language
"""

import unittest
import os
import re
import time
from contextlib import contextmanager


from ..graphspell.echo import echo
from . import gc_engine


@contextmanager
def timeblock (label, hDst):
    "performance counter (contextmanager)"
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print('{} : {}'.format(label, end - start))
        if hDst:
            hDst.write("{:<12.6}".format(end-start))


def perf (sVersion, bMemo=False):
    "performance tests"
    print("Performance tests")
    gc_engine.load()
    gc_engine.parse("Text to compile rules before launching real tests.")

    spHere, _ = os.path.split(__file__)
    spfPerfTest = os.path.join(spHere, "perf.txt")
    if not os.path.exists(spfPerfTest):
        print(f"No file <perf.txt> in <{spHere}>")
        return
    with open(spfPerfTest, "r", encoding="utf-8") as hSrc:
        hDst = open("./gc_lang/"+sLang+"/perf_memo.txt", "a", encoding="utf-8", newline="\n")  if bMemo  else None
        if hDst:
            hDst.write("{:<12}{:<20}".format(sVersion, time.strftime("%Y.%m.%d %H:%M")))
        for sText in ( s.strip() for s in hSrc if not s.startswith("#") and s.strip() ):
            with timeblock(sText[:sText.find(".")], hDst):
                gc_engine.parse(sText)
        if hDst:
            hDst.write("\n")


def _fuckBackslashUTF8 (s):
    "fuck that shit"
    return s.replace("\u2019", "'").replace("\u2013", "–").replace("\u2014", "—")


class TestGrammarChecking (unittest.TestCase):
    "Tests du correcteur grammatical"

    @classmethod
    def setUpClass (cls):
        gc_engine.load()
        cls._zError = re.compile(r"\{\{.*?\}\}")
        cls._aTestedRules = set()

    def test_parse (self):
        zOption = re.compile("^__([a-zA-Z0-9]+)__ ")
        spHere, _ = os.path.split(__file__)
        spfParsingTest = os.path.join(spHere, "gc_test.txt")
        if not os.path.exists(spfParsingTest):
            print(f"No file <gc_test.txt> in <{spHere}>")
            return
        with open(spfParsingTest, "r", encoding="utf-8") as hSrc:
            nError = 0
            for sLine in ( s for s in hSrc if not s.startswith("#") and s.strip() ):
                sLineNum = sLine[:10].strip()
                sLine = sLine[10:].strip()
                sOption = None
                m = zOption.search(sLine)
                if m:
                    sLine = sLine[m.end():]
                    sOption = m.group(1)
                if "->>" in sLine:
                    sErrorText, sExceptedSuggs = self._splitTestLine(sLine)
                    if sExceptedSuggs.startswith('"') and sExceptedSuggs.endswith('"'):
                        sExceptedSuggs = sExceptedSuggs[1:-1]
                else:
                    sErrorText = sLine.strip()
                    sExceptedSuggs = ""
                sExpectedErrors = self._getExpectedErrors(sErrorText)
                sTextToCheck = sErrorText.replace("}}", "").replace("{{", "")
                sFoundErrors, sListErr, sFoundSuggs = self._getFoundErrors(sTextToCheck, sOption)
                # tests
                if sExpectedErrors != sFoundErrors:
                    print("\n# Line num: " + sLineNum + \
                          "\n> to check: " + _fuckBackslashUTF8(sTextToCheck) + \
                          "\n  expected: " + sExpectedErrors + \
                          "\n  found:    " + sFoundErrors + \
                          "\n  errors:   \n" + sListErr)
                    nError += 1
                elif sExceptedSuggs:
                    if sExceptedSuggs != sFoundSuggs:
                        print("\n# Line num: " + sLineNum + \
                              "\n> to check: " + _fuckBackslashUTF8(sTextToCheck) + \
                              "\n  expected: " + sExceptedSuggs + \
                              "\n  found:    " + sFoundSuggs + \
                              "\n  errors:   \n" + sListErr)
                        nError += 1
            if nError:
                print("Unexpected errors:", nError)
        # untested rules
        aUntestedRules = set()
        for _, sOpt, sLineId, sRuleId in gc_engine.listRules():
            sRuleId = sRuleId.rstrip("0123456789")
            if sOpt != "@@@@" and sRuleId not in self._aTestedRules and not re.search("^[0-9]+[sp]$|^[pd]_", sRuleId):
                aUntestedRules.add(f"{sLineId}/{sRuleId}")
        if aUntestedRules:
            print()
            for sRule in aUntestedRules:
                echo(sRule)
            echo("  [{} untested rules]".format(len(aUntestedRules)))

    def _splitTestLine (self, sLine):
        sText, sSugg = sLine.split("->>")
        return (sText.strip(), sSugg.strip())

    def _getFoundErrors (self, sLine, sOption):
        if sOption:
            gc_engine.setOption(sOption, True)
            aErrs = gc_engine.parse(sLine)
            gc_engine.setOption(sOption, False)
        else:
            aErrs = gc_engine.parse(sLine)
        sRes = " " * len(sLine)
        sListErr = ""
        lAllSugg = []
        for dErr in aErrs:
            sRes = sRes[:dErr["nStart"]] + "~" * (dErr["nEnd"] - dErr["nStart"]) + sRes[dErr["nEnd"]:]
            sListErr += "    * {sLineId} / {sRuleId}  at  {nStart}:{nEnd}\n".format(**dErr)
            lAllSugg.append("|".join(dErr["aSuggestions"]))
            self._aTestedRules.add(dErr["sRuleId"].rstrip("0123456789"))
            # test messages
            if "<start>" in dErr["sMessage"] or "<end>" in dErr["sMessage"]:
                print("\n# Line num : " + dErr["sLineId"] + \
                      "\n  rule name: " + dErr["sRuleId"] + \
                      "\n  message  : " + dErr["sMessage"])
        return sRes, sListErr, "|||".join(lAllSugg)

    def _getExpectedErrors (self, sLine):
        sRes = " " * len(sLine)
        for i, m in enumerate(self._zError.finditer(sLine)):
            nStart = m.start() - (4 * i)
            nEnd = m.end() - (4 * (i+1))
            sRes = sRes[:nStart] + "~" * (nEnd - nStart) + sRes[nEnd:-4]
        return sRes


def main():
    "start function"
    unittest.main()


if __name__ == '__main__':
    main()
