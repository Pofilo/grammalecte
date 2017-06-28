#!python3

import sys
import os.path
import argparse
import json

import grammalecte.fr as gce
import grammalecte.fr.lexicographe as lxg
import grammalecte.fr.textformatter as tf
import grammalecte.text as txt
import grammalecte.tokenizer as tkz
from grammalecte.echo import echo


_EXAMPLE = "Quoi ? Racontes ! Racontes-moi ! Bon sangg, parles ! Oui. Il y a des menteur partout. " \
           "Je suit sidéré par la brutales arrogance de cette homme-là. Quelle salopard ! Un escrocs de la pire espece. " \
           "Quant sera t’il châtiés pour ses mensonge ?             Merde ! J’en aie marre."

_HELP = """
    /help                       /h      show this text
    ?word1 [word2] ...                  words analysis
    !word                               suggestion
    /lopt                       /lo     list options
    /+ option1 [option2] ...            activate grammar checking options
    /- option1 [option2] ...            deactivate grammar checking options
    /lrules [pattern]           /lr     list rules
    /--rule1 [rule2] ...                deactivate grammar checking rule
    /++rule1 [rule2] ...                reactivate grammar checking rule
    /quit                       /q      exit
"""


def _getText (sInputText):
    sText = input(sInputText)
    if sText == "*":
        return _EXAMPLE
    if sys.platform == "win32":
        # Apparently, the console transforms «’» in «'».
        # So we reverse it to avoid many useless warnings.
        sText = sText.replace("'", "’")
    return sText


def _getErrors (sText, oTokenizer, oDict, bContext=False, bDebug=False):
    "returns a tuple: (grammar errors, spelling errors)"
    aGrammErrs = gce.parse(sText, "FR", bDebug=bDebug, bContext=bContext)
    aSpellErrs = []
    for dToken in oTokenizer.genTokens(sText):
        if dToken['sType'] == "WORD" and not oDict.isValidToken(dToken['sValue']):
            aSpellErrs.append(dToken)
    return aGrammErrs, aSpellErrs


def generateText (sText, oTokenizer, oDict, bDebug=False, bEmptyIfNoErrors=False, nWidth=100):
    aGrammErrs, aSpellErrs = _getErrors(sText, oTokenizer, oDict, False, bDebug)
    if bEmptyIfNoErrors and not aGrammErrs and not aSpellErrs:
        return ""
    return txt.generateParagraph(sText, aGrammErrs, aSpellErrs, nWidth)


def generateJSON (iIndex, sText, oTokenizer, oDict, bContext=False, bDebug=False, bEmptyIfNoErrors=False, lLineSet=None, bReturnText=False):
    aGrammErrs, aSpellErrs = _getErrors(sText, oTokenizer, oDict, bContext, bDebug)
    aGrammErrs = list(aGrammErrs)
    if bEmptyIfNoErrors and not aGrammErrs and not aSpellErrs:
        return ""
    if lLineSet:
        aGrammErrs, aSpellErrs = txt.convertToXY(aGrammErrs, aSpellErrs, lLineSet)
        return json.dumps({ "lGrammarErrors": aGrammErrs, "lSpellingErrors": aSpellErrs }, ensure_ascii=False)
    if bReturnText:
        return json.dumps({ "iParagraph": iIndex, "sText": sText, "lGrammarErrors": aGrammErrs, "lSpellingErrors": aSpellErrs }, ensure_ascii=False)
    return json.dumps({ "iParagraph": iIndex, "lGrammarErrors": aGrammErrs, "lSpellingErrors": aSpellErrs }, ensure_ascii=False)


def readfile (spf):
    "generator: returns file line by line"
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                yield sLine
    else:
        print("# Error: file not found.")


def readfileAndConcatLines (spf):
    "generator: returns text by list of lines not separated by an empty line"
    lLine = []
    for i, sLine in enumerate(readfile(spf), 1):
        if sLine.strip():
            lLine.append((i, sLine))
        elif lLine:
            yield lLine
            lLine = []
    if lLine:
        yield lLine


def output (sText, hDst=None):
    if not hDst:
        echo(sText, end="")
    else:
        hDst.write(sText)


def main ():
    xParser = argparse.ArgumentParser()
    xParser.add_argument("-f", "--file", help="parse file (UTF-8 required!) [on Windows, -f is similar to -ff]", type=str)
    xParser.add_argument("-ff", "--file_to_file", help="parse file (UTF-8 required!) and create a result file (*.res.txt)", type=str)
    xParser.add_argument("-owe", "--only_when_errors", help="display results only when there are errors", action="store_true")
    xParser.add_argument("-j", "--json", help="generate list of errors in JSON (only with option --file or --file_to_file)", action="store_true")
    xParser.add_argument("-cl", "--concat_lines", help="concatenate lines not separated by an empty paragraph (only with option --file or --file_to_file)", action="store_true")
    xParser.add_argument("-tf", "--textformatter", help="auto-format text according to typographical rules (unavailable with option --concat_lines)", action="store_true")
    xParser.add_argument("-tfo", "--textformatteronly", help="auto-format text and disable grammar checking (only with option --file or --file_to_file)", action="store_true")
    xParser.add_argument("-ctx", "--context", help="return errors with context (only with option --json)", action="store_true")
    xParser.add_argument("-w", "--width", help="width in characters (40 < width < 200; default: 100)", type=int, choices=range(40,201,10), default=100)
    xParser.add_argument("-lo", "--list_options", help="list options", action="store_true")
    xParser.add_argument("-lr", "--list_rules", nargs="?", help="list rules [regex pattern as filter]", const="*")
    xParser.add_argument("-on", "--opt_on", nargs="+", help="activate options")
    xParser.add_argument("-off", "--opt_off", nargs="+", help="deactivate options")
    xParser.add_argument("-roff", "--rule_off", nargs="+", help="deactivate rules")
    xParser.add_argument("-d", "--debug", help="debugging mode (only in interactive mode)", action="store_true")
    xArgs = xParser.parse_args()

    gce.load()
    if not xArgs.json:
        echo("Grammalecte v{}".format(gce.version))
    oDict = gce.getDictionary()
    oTokenizer = tkz.Tokenizer("fr")
    oLexGraphe = lxg.Lexicographe(oDict)
    if xArgs.textformatter or xArgs.textformatteronly:
        oTF = tf.TextFormatter()

    if xArgs.list_options or xArgs.list_rules:
        if xArgs.list_options:
            gce.displayOptions("fr")
        if xArgs.list_rules:
            gce.displayRules(None  if xArgs.list_rules == "*"  else xArgs.list_rules)
        exit()

    if not xArgs.json:
        xArgs.context = False

    gce.setOptions({"html": True, "latex": True})
    if xArgs.opt_on:
        gce.setOptions({ opt:True  for opt in xArgs.opt_on  if opt in gce.getOptions() })
    if xArgs.opt_off:
        gce.setOptions({ opt:False  for opt in xArgs.opt_off  if opt in gce.getOptions() })

    if xArgs.rule_off:
        for sRule in xArgs.rule_off:
            gce.ignoreRule(sRule)

    sFile = xArgs.file or xArgs.file_to_file
    if sFile:
        # file processing
        hDst = open(sFile[:sFile.rfind(".")]+".res.txt", "w", encoding="utf-8", newline="\n")  if xArgs.file_to_file or sys.platform == "win32"  else None
        bComma = False
        if xArgs.json:
            output('{ "grammalecte": "'+gce.version+'", "lang": "'+gce.lang+'", "data" : [\n', hDst)
        if not xArgs.concat_lines:
            # pas de concaténation des lignes
            for i, sText in enumerate(readfile(sFile), 1):
                if xArgs.textformatter or xArgs.textformatteronly:
                    sText = oTF.formatText(sText)
                if xArgs.textformatteronly:
                    output(sText, hDst)
                else:
                    if xArgs.json:
                        sText = generateJSON(i, sText, oTokenizer, oDict, bContext=xArgs.context, bDebug=False, bEmptyIfNoErrors=xArgs.only_when_errors, bReturnText=xArgs.textformatter)
                    else:
                        sText = generateText(sText, oTokenizer, oDict, bDebug=False, bEmptyIfNoErrors=xArgs.only_when_errors, nWidth=xArgs.width)
                    if sText:
                        if xArgs.json and bComma:
                            output(",\n", hDst)
                        output(sText, hDst)
                        bComma = True
                if hDst:
                    echo("§ %d\r" % i, end="", flush=True)
        else:
            # concaténation des lignes non séparées par une ligne vide
            for i, lLine in enumerate(readfileAndConcatLines(sFile), 1):
                sText, lLineSet = txt.createParagraphWithLines(lLine)
                if xArgs.json:
                    sText = generateJSON(i, sText, oTokenizer, oDict, bContext=xArgs.context, bDebug=False, bEmptyIfNoErrors=xArgs.only_when_errors, lLineSet=lLineSet)
                else:
                    sText = generateText(sText, oTokenizer, oDict, bDebug=False, bEmptyIfNoErrors=xArgs.only_when_errors, nWidth=xArgs.width)
                if sText:
                    if xArgs.json and bComma:
                        output(",\n", hDst)
                    output(sText, hDst)
                    bComma = True
                if hDst:
                    echo("§ %d\r" % i, end="", flush=True)
        if xArgs.json:
            output("\n]}\n", hDst)
    else:
        # pseudo-console
        sInputText = "\n~==========~ Enter your text [/h /q] ~==========~\n"
        sText = _getText(sInputText)
        while True:
            if sText.startswith("?"):
                for sWord in sText[1:].strip().split():
                    if sWord:
                        echo("* " + sWord)
                        for sMorph in oDict.getMorph(sWord):
                            echo("  {:<32} {}".format(sMorph, oLexGraphe.formatTags(sMorph)))
            elif sText.startswith("!"):
                for sWord in sText[1:].strip().split():
                    if sWord:
                        echo(" | ".join(oDict.suggest(sWord)))
            elif sText.startswith(">"):
                oDict.drawPath(sText[1:].strip())
            elif sText.startswith("/+ "):
                gce.setOptions({ opt:True  for opt in sText[3:].strip().split()  if opt in gce.getOptions() })
                echo("done")
            elif sText.startswith("/- "):
                gce.setOptions({ opt:False  for opt in sText[3:].strip().split()  if opt in gce.getOptions() })
                echo("done")
            elif sText.startswith("/-- "):
                for sRule in sText[3:].strip().split():
                    gce.ignoreRule(sRule)
                echo("done")
            elif sText.startswith("/++ "):
                for sRule in sText[3:].strip().split():
                    gce.reactivateRule(sRule)
                echo("done")
            elif sText == "/debug" or sText == "/d":
                xArgs.debug = not(xArgs.debug)
                echo("debug mode on"  if xArgs.debug  else "debug mode off")
            elif sText == "/textformatter" or sText == "/tf":
                xArgs.textformatter = not(xArgs.textformatter)
                echo("textformatter on"  if xArgs.debug  else "textformatter off")
            elif sText == "/help" or sText == "/h":
                echo(_HELP)
            elif sText == "/lopt" or sText == "/lo":
                gce.displayOptions("fr")
            elif sText.startswith("/lr"):
                sText = sText.strip()
                sFilter = sText[sText.find(" "):].strip()  if sText != "/lr" and sText != "/rules"  else None
                gce.displayRules(sFilter)
            elif sText == "/quit" or sText == "/q":
                break
            elif sText.startswith("/rl"):
                # reload (todo)
                pass
            else:
                for sParagraph in txt.getParagraph(sText):
                    if xArgs.textformatter:
                        sText = oTF.formatText(sText)
                    sRes = generateText(sText, oTokenizer, oDict, bDebug=xArgs.debug, bEmptyIfNoErrors=xArgs.only_when_errors, nWidth=xArgs.width)
                    if sRes:
                        echo("\n" + sRes)
                    else:
                        echo("\nNo error found.")
            sText = _getText(sInputText)


if __name__ == '__main__':
    main()
