# Spellchecker
# Wrapper for the IBDAWG class.
# Useful to check several dictionaries at once.

# To avoid iterating over a pile of dictionaries, it is assumed that 3 are enough:
# - the main dictionary, bundled with the package
# - the extended dictionary
# - the community dictionary, added by an organization
# - the personal dictionary, created by the user for its own convenience


import traceback

from . import ibdawg
from . import tokenizer


dDefaultDictionaries = {
    "fr": "fr.bdic",
    "en": "en.bdic"
}


class SpellChecker ():

    def __init__ (self, sLangCode, sfMainDic="", sfExtendedDic="", sfCommunityDic="", sfPersonalDic=""):
        "returns True if the main dictionary is loaded"
        self.sLangCode = sLangCode
        if not sfMainDic:
            sfMainDic = dDefaultDictionaries.get(sLangCode, "")
        self.oMainDic = self._loadDictionary(sfMainDic, True)
        self.oExtendedDic = self._loadDictionary(sfExtendedDic)
        self.oCommunityDic = self._loadDictionary(sfCommunityDic)
        self.oPersonalDic = self._loadDictionary(sfPersonalDic)
        self.bExtendedDic = bool(self.oExtendedDic)
        self.bCommunityDic = bool(self.oCommunityDic)
        self.bPersonalDic = bool(self.oPersonalDic)
        self.oTokenizer = None

    def _loadDictionary (self, source, bNecessary=False):
        "returns an IBDAWG object"
        if not source:
            return None
        try:
            return ibdawg.IBDAWG(source)
        except Exception as e:
            if bNecessary:
                raise Exception(str(e), "Error: <" + str(source) + "> not loaded.")
            print("Error: <" + str(source) + "> not loaded.")
            traceback.print_exc()
            return None

    def loadTokenizer (self):
        self.oTokenizer = tokenizer.Tokenizer(self.sLangCode)

    def getTokenizer (self):
        if not self.oTokenizer:
            self.loadTokenizer()
        return self.oTokenizer

    def setMainDictionary (self, source):
        "returns True if the dictionary is loaded"
        self.oMainDic = self._loadDictionary(source, True)
        return bool(self.oMainDic)
            
    def setExtendedDictionary (self, source, bActivate=True):
        "returns True if the dictionary is loaded"
        self.oExtendedDic = self._loadDictionary(source)
        self.bExtendedDic = False  if not bActivate  else bool(self.oExtendedDic)
        return bool(self.oExtendedDic)

    def setCommunityDictionary (self, source, bActivate=True):
        "returns True if the dictionary is loaded"
        self.oCommunityDic = self._loadDictionary(source)
        self.bCommunityDic = False  if not bActivate  else bool(self.oCommunityDic)
        return bool(self.oCommunityDic)

    def setPersonalDictionary (self, source, bActivate=True):
        "returns True if the dictionary is loaded"
        self.oPersonalDic = self._loadDictionary(source)
        self.bPersonalDic = False  if not bActivate  else bool(self.oPersonalDic)
        return bool(self.oPersonalDic)

    def activateExtendedDictionary (self):
        self.bExtendedDic = bool(self.oExtendedDic)

    def activateCommunityDictionary (self):
        self.bCommunityDic = bool(self.oCommunityDic)

    def activatePersonalDictionary (self):
        self.bPersonalDic = bool(self.oPersonalDic)

    def deactivateExtendedDictionary (self):
        self.bExtendedDic = False

    def deactivateCommunityDictionary (self):
        self.bCommunityDic = False

    def deactivatePersonalDictionary (self):
        self.bPersonalDic = False


    # parse text functions

    def parseParagraph (self, sText, bSpellSugg=False):
        if not self.oTokenizer:
            self.loadTokenizer()
        aSpellErrs = []
        for dToken in self.oTokenizer.genTokens(sText):
            if dToken['sType'] == "WORD" and not self.isValidToken(dToken['sValue']):
                if bSpellSugg:
                    dToken['aSuggestions'] = []
                    for lSugg in self.suggest(dToken['sValue']):
                        dToken['aSuggestions'].extend(lSugg)
                aSpellErrs.append(dToken)
        return aSpellErrs

    def countWordsOccurrences (self, sText, bByLemma=False, bOnlyUnknownWords=False, dWord={}):
        if not self.oTokenizer:
            self.loadTokenizer()
        for dToken in self.oTokenizer.genTokens(sText):
            if dToken['sType'] == "WORD":
                if bOnlyUnknownWords:
                    if not self.isValidToken(dToken['sValue']):
                        dWord[dToken['sValue']] = dWord.get(dToken['sValue'], 0) + 1
                else:
                    if not bByLemma:
                        dWord[dToken['sValue']] = dWord.get(dToken['sValue'], 0) + 1
                    else:
                        for sLemma in self.getLemma(dToken['sValue']):
                            dWord[sLemma] = dWord.get(sLemma, 0) + 1
        return dWord

    # IBDAWG functions

    def isValidToken (self, sToken):
        "checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)"
        if self.oMainDic.isValidToken(sToken):
            return True
        if self.bExtendedDic and self.oExtendedDic.isValidToken(sToken):
            return True
        if self.bCommunityDic and self.oCommunityDic.isValidToken(sToken):
            return True
        if self.bPersonalDic and self.oPersonalDic.isValidToken(sToken):
            return True
        return False

    def isValid (self, sWord):
        "checks if sWord is valid (different casing tested if the first letter is a capital)"
        if self.oMainDic.isValid(sWord):
            return True
        if self.bExtendedDic and self.oExtendedDic.isValid(sWord):
            return True
        if self.bCommunityDic and self.oCommunityDic.isValid(sToken):
            return True
        if self.bPersonalDic and self.oPersonalDic.isValid(sWord):
            return True
        return False

    def lookup (self, sWord):
        "checks if sWord is in dictionary as is (strict verification)"
        if self.oMainDic.lookup(sWord):
            return True
        if self.bExtendedDic and self.oExtendedDic.lookup(sWord):
            return True
        if self.bCommunityDic and self.oCommunityDic.lookup(sToken):
            return True
        if self.bPersonalDic and self.oPersonalDic.lookup(sWord):
            return True
        return False

    def getMorph (self, sWord):
        "retrieves morphologies list, different casing allowed"
        lResult = self.oMainDic.getMorph(sWord)
        if self.bExtendedDic:
            lResult.extend(self.oExtendedDic.getMorph(sWord))
        if self.bCommunityDic:
            lResult.extend(self.oCommunityDic.getMorph(sWord))
        if self.bPersonalDic:
            lResult.extend(self.oPersonalDic.getMorph(sWord))
        return lResult

    def getLemma (self, sWord):
        return set([ s[1:s.find(" ")]  for s in self.getMorph(sWord) ])

    def suggest (self, sWord, nSuggLimit=10):
        "generator: returns 1, 2 or 3 lists of suggestions"
        yield self.oMainDic.suggest(sWord, nSuggLimit)
        if self.bExtendedDic:
            yield self.oExtendedDic.suggest(sWord, nSuggLimit)
        if self.bCommunityDic:
            yield self.oCommunityDic.suggest(sWord, nSuggLimit)
        if self.bPersonalDic:
            yield self.oPersonalDic.suggest(sWord, nSuggLimit)

    def select (self, sFlexPattern="", sTagsPattern=""):
        "generator: returns all entries which flexion fits <sFlexPattern> and morphology fits <sTagsPattern>"
        yield from self.oMainDic.select(sFlexPattern, sTagsPattern)
        if self.bExtendedDic:
            yield from self.oExtendedDic.select(sFlexPattern, sTagsPattern)
        if self.bCommunityDic:
            yield from self.oCommunityDic.select(sFlexPattern, sTagsPattern)
        if self.bPersonalDic:
            yield from self.oPersonalDic.select(sFlexPattern, sTagsPattern)

    def drawPath (self, sWord):
        self.oMainDic.drawPath(sWord)
        if self.bExtendedDic:
            print("-----")
            self.oExtendedDic.drawPath(sWord)
        if self.bCommunityDic:
            print("-----")
            self.oCommunityDic.drawPath(sWord)
        if self.bPersonalDic:
            print("-----")
            self.oPersonalDic.drawPath(sWord)

    def getSimilarEntries (self, sWord, nSuggLimit=10):
        "return a list of tuples (similar word, stem, morphology)"
        lResult = self.oMainDic.getSimilarEntries(sWord, nSuggLimit)
        if self.bExtendedDic:
            lResult.extend(self.oExtendedDic.getSimilarEntries(sWord, nSuggLimit))
        if self.bCommunityDic:
            lResult.extend(self.oCommunityDic.getSimilarEntries(sWord, nSuggLimit))
        if self.bPersonalDic:
            lResult.extend(self.oPersonalDic.getSimilarEntries(sWord, nSuggLimit))
        return lResult
