# -*- coding: utf-8 -*-
# (c) 2009 Finn Gruwier Larsen

import uno
import unohelper
import sys
import traceback

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import MODALTOP
from com.sun.star.awt.VclWindowPeerAttribute import OK, OK_CANCEL, YES_NO, YES_NO_CANCEL, RETRY_CANCEL, DEF_OK, DEF_CANCEL, DEF_RETRY, DEF_YES, DEF_NO
from com.sun.star.beans import PropertyValue

sys.stderr = sys.stdout

class Linguist (unohelper.Base, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx

    def trigger (self, command):
        desktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()
        if command == "ListUnrecognizedWords":
            items = self.collectWords(doc, self.ctx, True)
            outputText = ""
            for item in items:
                outputText = outputText+item[0]+" "+str(item[1])+"\n"
            self.createOutputDocument(outputText, self.ctx)
        elif command == "ListAllWords":
            items = self.collectWords(doc, self.ctx, False)
            outputText = ""
            for item in items:
                outputText = outputText+item[0]+" "+str(item[1])+"\n"
            numDiffWords = len(items)
            outputText = outputText + "\nNumber of different words: " + str(numDiffWords)
            # Do lix processing to get number of words:
            results = self.lixProcessWords(doc, self.ctx)
            numWords = results[0]
            outputText = outputText + "\nTotal number for words: " + str(numWords)
            outputText = outputText + "\nLexical Variety: " + \
                         str(round(numDiffWords * 1.0 / numWords, 2))
            self.createOutputDocument(outputText, self.ctx)
        elif command == "SortWordsOnFrequency":
            items = self.collectWords(doc, self.ctx, False, True)
            outputText = ""
            for item in items:
                if item[1] > 10:
                    outputText = outputText+item[0]+" "+str(item[1])+"\n"
            self.createOutputDocument(outputText, self.ctx)
        elif command == "CalculateLix":
            results = self.lixProcessWords(doc, self.ctx)
            numWords = results[0]
            numFullStops = results[1]
            numLongWords = results[2]
            differentWords = self.collectWords(doc, self.ctx, False, False)
            numDifferentWords = float(len(differentWords))
            if numFullStops == 0:
                outputText = "To make a lix calculation there should be at least one word that is followed  by a full stop."
            else:
                numWordsPerFullStop = numWords / numFullStops
                percentageLongWords = (numLongWords * 100) / numWords
                lix = numWordsPerFullStop + percentageLongWords
                lexicalVariety = numDifferentWords / numWords
                outputText = "Number of words: " + str(numWords) + "\r" \
                + "Number of full stops: " + str(numFullStops) + "\r" \
                + "Number of long words (7 or more characters): " + str(numLongWords) + "\r" \
                + "Number of words per full stop: " + str(numWordsPerFullStop) + "\r" \
                + "Percentage long words: " + str(percentageLongWords) + "\r" \
                + "Lix (readability): " + str(lix) + "\r" \
                + "Number of different words: " + str(numDifferentWords) + "\r" \
                + "Lexical variety: " + str(round(lexicalVariety, 3))
            self.createOutputDocument(outputText, self.ctx)
        elif command == "FormatAll":
            pass
        else:
            print("Bad command!")
    
    def collectWords (self, document, context, unrecWordsOnly=False, sortOnFrequency=False): 
        """Collect words from the current text document and return them in a tuple."""
        cursor = document.Text.createTextCursor()
        smgr = context.ServiceManager
        spellchecker = smgr.createInstanceWithContext("com.sun.star.linguistic2.SpellChecker", context)
        locale = document.getPropertyValue("CharLocale")
        words = {}
        # words[locale] = 0 # Enable this for locale debugging (disable line 87)
        cursor.gotoStart(False)
        while cursor.gotoNextWord(False):
            if cursor.isStartOfWord():
                cursor.gotoEndOfWord(True)
                word = cursor.getString()
                if len(word) > 0:
                    if word[-1]==".":
                            word = word[0:-1]
                    if not word in words:
                        if unrecWordsOnly:
                            if not spellchecker.isValid(word, locale, ()):
                                words[word] = 1
                        else:
                            words[word] = 1
                    else:
                        if unrecWordsOnly:
                            if not spellchecker.isValid(word, locale, ()):
                                words[word] = words[word] + 1
                        else:
                            words[word] = words[word] + 1
        words = list(words.items())
        if sortOnFrequency:
            words.sort(key = lambda x: (x[1], x[0]), reverse=True)
        else:
            words.sort()
        return words
      
    def createOutputDocument (self, outputText, context):
        """Creates a new text document and puts the output text in it."""
        smgr = context.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop",context)
        doc = desktop.loadComponentFromURL("private:factory/swriter","_blank", 0, ())
        text = doc.Text
        cursor = text.createTextCursor()
        text.insertString(cursor, outputText, 0)

    def lixProcessWords (self, document, context):
        """Traverses trough the words in the document, examining each word.
        Returns a tuple containing number of words, number of full-stops and
        number of long words (7 or more characters)."""
        cursor = document.Text.createTextCursor()
        numWords = 1
        numFullStops = 0
        numLongWords = 0
        cursor.gotoStart(False)
        while cursor.gotoNextWord(False):
            if cursor.isStartOfWord():
                cursor.gotoEndOfWord(True)
                word = cursor.getString()
                if len(word) > 0:
                    numWords = numWords + 1
                    if word[-1]==".":
                        word = word[0:-1]
                        numFullStops = numFullStops + 1
                    if len(word)>=7:
                        numLongWords = numLongWords + 1
        return numWords, numFullStops, numLongWords
            
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(Linguist, "dk.gruwier.linguist.Linguist", ("com.sun.star.task.Job",),)
