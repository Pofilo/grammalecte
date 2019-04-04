# Graphspell
#
# Spellchecker based on a DAWG (Direct Acyclic Word Graph)


import uno
import unohelper
import traceback
import re
import json

import helpers
from grammalecte.graphspell import SpellChecker

from com.sun.star.linguistic2 import XSupportedLocales, XSpellChecker, XSpellAlternatives
from com.sun.star.lang import XServiceInfo, XServiceName, XServiceDisplayName
from com.sun.star.lang import Locale


lLocale = {
    # List of locales in LibreOffice
    # https://cgit.freedesktop.org/libreoffice/core/tree/i18nlangtag/source/isolang/isolang.cxx
    #('la', 'VA', ''),  # Latin (for testing purpose)
    ('fr', 'FR', ''),  # France
    ('fr', 'BE', ''),  # Belgique
    ('fr', 'CA', ''),  # Canada
    ('fr', 'CH', ''),  # Suisse
    ('fr', 'LU', ''),  # Luxembourg
    #('fr', 'MC', ''),  # Monaco
    ('fr', 'BF', ''),  # Burkina Faso
    ('fr', 'BJ', ''),  # Benin
    ('fr', 'CD', ''),  # Congo
    ('fr', 'CI', ''),  # Côte d’Ivoire
    ('fr', 'CM', ''),  # Cameroun
    ('fr', 'MA', ''),  # Maroc
    ('fr', 'ML', ''),  # Mali
    ('fr', 'MU', ''),  # Île Maurice
    ('fr', 'NE', ''),  # Niger
    ('fr', 'RE', ''),  # Réunion
    ('fr', 'SN', ''),  # Sénégal
    ('fr', 'TG', '')   # Togo
}

zElidedWords = re.compile("(?i)^(?:[ldnmtsjcçy]|qu|lorsqu|quoiqu|puisqu|jusqu)['’`‘]")


class Graphspell (unohelper.Base, XSpellChecker, XServiceInfo, XServiceName, XServiceDisplayName, XSupportedLocales):

    def __init__ (self, ctx, *args):
        try:
            self.ctx = ctx
            self.sServiceName = "com.sun.star.linguistic2.SpellChecker"
            self.sImplementationName = "net.grammalecte.graphspell"
            self.tSupportedServiceNames = (self.sServiceName, )
            self.xSvMgr = ctx.ServiceManager
            self.locales = tuple([ Locale(t[0], t[1], t[2])  for t in lLocale ])
            self.xSettingNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Other/", False)
            self.xOptionNode = self.xSettingNode.getByName("o_fr")
            sMainDicName = self.xOptionNode.getPropertyValue("main_dic_name")
            personal_dic = ""
            if (self.xOptionNode.getPropertyValue("use_personal_dic")):
                sPersonalDicJSON = self.xOptionNode.getPropertyValue("personal_dic")
                if sPersonalDicJSON:
                    try:
                        personal_dic = json.loads(sPersonalDicJSON)
                    except:
                        print("Graphspell: wrong personal_dic")
                        traceback.print_exc()
            self.oGraphspell = SpellChecker("fr", "fr-"+sMainDicName+".bdic", "", personal_dic)
            self.loadHunspell()
            # print("Graphspell: init done")
        except:
            print("Graphspell: init failed")
            traceback.print_exc()

    def loadHunspell (self):
        # Hunspell is a fallback spellchecker
        try:
            self.xHunspell = self.xSvMgr.createInstance("org.openoffice.lingu.MySpellSpellChecker")
        except:
            print("Hunspell: init failed")
            traceback.print_exc()
            self.xHunspell = False
            self.bHunspell = False
        else:
            self.xHunspellLocale = Locale('fr', 'MC', '')
            self.bHunspell = not bool(self.xOptionNode.getPropertyValue("use_graphspell_sugg"))

    # XServiceName
    def getServiceName (self):
        return self.sImplementationName     #self.sServiceName

    # XServiceInfo
    def getImplementationName (self):
        return self.sImplementationName

    def supportsService (self, sServiceName):
        return (sServiceName in self.tSupportedServiceNames)

    def getSupportedServiceNames (self):
        return self.tSupportedServiceNames

    # XSupportedLocales
    def hasLocale (self, aLocale):
        if aLocale in self.locales:
            return True
        for e in self.locales:
            if aLocale.Language == e.Language and (e.Country == aLocale.Country or e.Country == ""):
                return True
        return False

    def getLocales (self):
        return self.locales

    # XSpellChecker
    # http://www.openoffice.org/api/docs/common/ref/com/sun/star/linguistic2/XSpellChecker.html
    def isValid (self, aWord, rLocale, aProperties):
        try:
            aWord = zElidedWords.sub("", aWord.rstrip("."), count=1)
            return self.oGraphspell.isValidToken(aWord)
            # return self.xHunspell.isValid(aWord, self.xHunspellLocale, aProperties)
        except:
            traceback.print_exc()
        return False

    def spell (self, aWord, aLocale, aProperties):
        "returns an object SpellAlternatives"
        try:
            if not self.bHunspell:
                lSugg = []
                for l in self.oGraphspell.suggest(aWord):
                    lSugg.extend(l)
                return SpellAlternatives(aWord, tuple(lSugg))
            else:
                # fallback dictionary suggestions (Hunspell)
                return self.xHunspell.spell(aWord, self.xHunspellLocale, aProperties)
        except:
            traceback.print_exc()
        return None

    # XServiceDisplayName
    def getServiceDisplayName(self, aLocale):
        return "Graphspell (fr)"

    # Other
    def listSpellChecker (self):
        xLinguServiceManager = self.xSvMgr.createInstance("com.sun.star.linguistic2.LinguServiceManager")
        lService = xLinguServiceManager.getAvailableServices('com.sun.star.linguistic2.SpellChecker', Locale("fr", "MC", ""))
        for sSpellchecker in lService:
            print(repr(sSpellchecker))
            #if sSpellchecker == self.ImplementationName:
            #    continue
            #self.xFallbackSpellChecker = self.xSvMgr.createInstance(sSpellchecker)
            #if self.xFallbackSpellChecker:
            #    print("Spell checker: %s" % xSpellChecker)
            #    break


class SpellAlternatives (unohelper.Base, XSpellAlternatives):

    def __init__ (self, sWord, lSugg):
        try:
            self.sWord = sWord
            self.lSugg = lSugg
            self.xLocale = Locale('fr', 'FR', '')
        except:
            traceback.print_exc()

    # XSpellAlternatives
    # http://www.openoffice.org/api/docs/common/ref/com/sun/star/linguistic2/XSpellAlternatives.html
    def getWord (self):
        return self.sWord

    def getLocale (self):
        return self.xLocale

    def getFailureType (self):
        return 4
        # IS_NEGATIVE_WORD = 2
        #   The word is a negative one, that is, it should not be used.
        # CAPTION_ERROR = 3
        #   The capitalization of the word is wrong.
        # SPELLING_ERROR = 4
        #   The spelling of the word is wrong (or at least not known to be correct).
        # No difference -> red underline

    def getAlternativesCount (self):
        return len(self.lSugg)

    def getAlternatives (self):
        return self.lSugg


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(Graphspell, "net.grammalecte.graphspell", ("com.sun.star.linguistic2.SpellChecker",),)
