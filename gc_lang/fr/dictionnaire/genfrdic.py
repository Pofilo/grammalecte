#!python3

__author__ = "Olivier R."
__license__ = "MPL 2"



import os
import sys
import time
import re
import collections
import zipfile
import math
import argparse
from enum import Enum

from distutils import dir_util
from distutils import file_util
from string import Template

import metagraphe
import metaphone2


# Dictionnaire des caractères pour le tri naturel.
# Ordre souhaitable, mais pose problème pour la recherche, car engendre des égalités de lemmes différents.
# Il faut donc travailler sur un dictionnaire trié *numériquement* et le sauvegarder selon le tri *naturel*             
CHARMAP = str.maketrans({ 'à': 'a',  'À': 'A',  'â': 'a',  'Â': 'A',  'ä': 'a',  'Ä': 'A',  'å': 'a',  'Å': 'A',  'ā': 'a',  'Ā': 'A',
                          'ç': 'c',  'Ç': 'C',
                          'é': 'e',  'É': 'E',  'è': 'e',  'È': 'E',  'ê': 'e',  'Ê': 'E',  'ë': 'e',  'Ë': 'E',  'ē': 'e',  'Ē': 'E',
                          'î': 'i',  'Î': 'I',  'ï': 'i',  'Ï': 'I',  'ī': 'i',  'Ī': 'I',
                          'ñ': 'n',
                          'ô': 'o',  'Ô': 'O',  'ö': 'o',  'Ö': 'O',  'ō': 'o',  'Ō': 'O',
                          'ù': 'u',  'Ù': 'U',  'û': 'u',  'Û': 'U',  'ü': 'u',  'Ü': 'U',  'ū': 'u',  'Ū': 'U',
                          'ÿ': 'y',
                          'æ': 'ae', 'Æ': 'AE', 'œ':'oe', 'Œ': 'OE',
                          '-': None, '.': None, "'": None })


# Les dictionnaires
dSUBDIC = { '*': 'Commun',
            'R': 'Réforme1990',
            'M': 'Moderne',
            'C': 'Classique',
            'A': 'Annexe',
            'P': 'Multimots',
            'X': 'Contributeurs' }

dMODERNE = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS “MODERNE”',
             'shortname': '“Moderne”',
             'asciiName': 'fr-moderne',
             'mozAsciiName': 'fr-FR-modern',
             'subDicts': '*MX',
             'mozId': 'fr-dicollecte-moderne',
             'description': "Dictionnaire français “Moderne”" }

dCLASSIQUE = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS “CLASSIQUE”',
               'shortname': '“Classique”',
               'asciiName': 'fr-classique',
               'mozAsciiName': 'fr-FR-classic',
               'subDicts': '*MCX',
               'mozId': 'fr-dicollecte-classique',
               'description': "Dictionnaire français “Classique”" }

dCLASSIQUEX = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS “CLASSIQUE ÉTENDU”',
                'shortname': '“Classique étendu”',
                'asciiName': 'fr-classique-ext',
                'mozAsciiName': 'fr-FR-classic-ext',
                'subDicts': '*MCX',
                'mozId': 'fr-dicollecte-classique-ext',
                'description': "Dictionnaire français “Classique étendu”" }

dREFORME1990 = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS “RÉFORME 1990”',
                 'shortname': '“Réforme 1990”',
                 'asciiName': 'fr-reforme1990',
                 'mozAsciiName': 'fr-FR-reform',
                 'subDicts': '*RX',
                 'mozId': 'fr-dicollecte-reforme1990',
                 'description': "Dictionnaire français “Réforme 1990”" }

dTOUTESVAR = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS “TOUTES VARIANTES”',
               'shortname': '“Toutes variantes”',
               'asciiName': 'fr-toutesvariantes',
               'mozAsciiName': 'fr-FR-classic-reform',
               'subDicts': '*MCRAX',
               'mozId': 'fr-dicollecte-toutesvariantes',
               'description': "Dictionnaire français “Toutes variantes”" }

dMOZEXT = { 'name': 'DICTIONNAIRE ORTHOGRAPHIQUE FRANÇAIS',
            'mozId': 'fr-dicollecte',
            'description': "Dictionnaire orthographique de la langue française" }


BUILD_PATH = '_build'
PREFIX_DICT_PATH = 'hunspell-french-dictionaries-v'
EXT_PREFIX_OOO = 'lo-oo-ressources-linguistiques-fr-v'
EXT_PREFIX_MOZ = 'moz-hunspell-fr-dicollecte-v'
LEX_PREFIX = 'lexique-dicollecte-fr-v'
STATS_NAME = 'statistiques-v'

MPLHEADER = "# This Source Code Form is subject to the terms of the Mozilla Public\n" + \
            "# License, v. 2.0. If a copy of the MPL was not distributed with this\n" + \
            "# file, You can obtain one at http://mozilla.org/MPL/2.0/.\n\n"


def echo (obj, sep=' ', end='\n', file=sys.stdout, flush=False):
    """ Print for Windows to avoid Python crashes.
        Encoding depends on Windows locale. No useful standard.
        Always returns True (useful for debugging)."""
    if sys.platform != "win32":
        print(obj, sep=sep, end=end, file=file, flush=flush)
        return True
    try:
        print(str(obj).replace("œ", "oe"), sep=sep, end=end, file=file, flush=flush)
    except:
        try:
            print(str(obj).translate(CHARMAP), sep=sep, end=end, file=file, flush=flush)
        except:
            print(str(obj).encode('ascii', 'replace').decode('ascii', 'replace'), sep=sep, end=end, file=file, flush=flush)
    return True


def makeLongFlags (sFlags):
    "renvoie la liste des drapeaux, créés à partir de la chaîne"
    if len(sFlags) % 2 != 0:
        echo(">| erreur: %s" % sFlags)
        sFlags = sFlags + ' '
    return [ sFlags[i:i+2]  for i in range(0, len(sFlags), 2) ]


def makeNumFlags (sFlags):
    return sFlags.split(',')


def makeOneCharFlags (sFlags):
    return list(sFlags)


def fieldToHunspell (sFieldName, sFieldValue):
    "renvoie le texte pour Hunspell de la valeur d’un champ"
    sSep = ' ' + sFieldName + ':'
    return sSep + sFieldValue.replace(' ', sSep)


def getListNgrams (sWord, n):
    return [ sWord[i:i+n]  for i in range(len(sWord)-n-1) ]


def createZipFiles (spSrc, spDst, zipFileName):
    echo(' > Zip  [ {} ]'.format(spSrc))
    def _addDir (_spSrc, _subPath, _zipFile):
        for _fileToZip in os.listdir(_spSrc):
            if os.path.isdir(_spSrc+'/'+_fileToZip):
                _addDir(_spSrc+'/'+_fileToZip, _fileToZip, _zipFile)
            else:
                zipFile.write(_spSrc+'/'+_fileToZip, _subPath+'/'+_fileToZip)
    #
    zipFile = zipfile.ZipFile(spDst+'/'+zipFileName, 'w', zipfile.ZIP_DEFLATED)
    for fileToZip in os.listdir(spSrc):
        if os.path.isdir(spSrc+'/'+fileToZip):
            _addDir(spSrc+'/'+fileToZip, fileToZip, zipFileName)
        else:
            zipFile.write(spSrc+'/'+fileToZip, fileToZip)
    zipFile.close()


def copyTemplate (spSrc, spDst, spf, dVars):
    if spf.endswith('xml') or spf.endswith('rdf'):
        for key in dVars:
            dVars[key] = dVars[key].replace('&', '&amp;')
    xTemplate = Template( open(spSrc+'/'+spf, 'r', encoding='utf-8').read() )
    open(spDst+'/'+spf, 'w', encoding='utf-8', newline="\n").write(xTemplate.safe_substitute(dVars))


def getIfq (f):
    "renvoie l’indice de fréquence (un caractère)"
    if f == 0:         return '0'
    if f < 0.00000001: return '1'
    if f < 0.0000001:  return '2'
    if f < 0.000001:   return '3'
    if f < 0.00001:    return '4'
    if f < 0.0001:     return '5'
    if f < 0.001:      return '6'
    if f < 0.01:       return '7'
    if f < 0.1:        return '8'
    return '9'


def getVerbMultiMorph (s):
    "renvoie la liste des morphologies fusionnées"
    lTag = s.split()
    lRes = []
    for n, sTag in enumerate(lTag, 1):
        if not sTag[0].isdigit():
            sMorph = sTag
            for sTag2 in lTag[n:]:
                if sTag2[0].isdigit():
                    lRes.append(sMorph + " " + sTag2)
        else:
            break
    return lRes


def readfile (spf):
    "generator: returns file line by line"
    if os.path.isfile(spf):
        with open(spf, "r", encoding="utf-8") as hSrc:
            for sLine in hSrc:
                yield sLine
    else:
        print("# Error: file not found.")



class Dictionnaire:
    def __init__ (self, version, name):
        # Dictionary
        self.sName = name
        self.lEntry = []
        self.nEntry = 0
        self.sVersion = version
        # Affixes
        self.sSettings = '' # enregistre tout avant la ligne # END
        self.dFlags = collections.OrderedDict()
        self.bShortenTags = False
        self.dAM = collections.OrderedDict() # étiquettes morphologiques
        self.dAF = collections.OrderedDict() # étiquettes drapeaux
        # Flexions
        self.lFlexions = []           # liste des flexions avec lemme, morphologie et occurrences 
        self.lStatsLex = []
        self.nTotOccurRecognizedWords = 0
        self.aFlexions = None
    
    def readDictionary (self, spf):
        "Lecture du dictionnaire"
        echo('Dictionnaire << [ {} ]'.format(spf), end=' ')
        for sLine in readfile(spf):
            sLine = sLine.strip()
            if not sLine.isdigit() and not sLine.startswith("#"):
                self.lEntry.append(Entree(sLine))
        self.nEntry = len(self.lEntry)
        echo('- {} entrées'.format(self.nEntry))

    def readAffixes (self, spf):
        "Lecture du fichier des affixes"
        echo("Dictionnaire << [ {} ]".format(spf))
        bSettings = True
        for sLine in readfile(spf):
            if sLine.startswith("# END"):
                bSettings = False
            elif sLine.startswith("#"):
                pass
            elif sLine.startswith(("PFX", "SFX")):
                sLine = re.sub(" *#.*$", "", sLine.rstrip(" \n"))
                lElem = sLine.split()
                if len(lElem) >= 4:
                    if lElem[1] not in self.dFlags:
                        # nouveau drapeau
                        oFlag = Flag(lElem[0], lElem[1], lElem[2])
                        self.dFlags[lElem[1]] = oFlag
                    else:
                        # nouvelle règle
                        oFlag.addAffixRule(sLine)
                else:
                    echo("  # erreur de lecture: {}".format(sLine))
            elif bSettings:
                # toutes les lignes non-commentaires avant # END sont enregistrées dans self.sSettings
                self.sSettings += sLine

    def defineAbreviatedTags (self, nMode, spDst):
        "Abrégé des étiquettes grammaticales et des drapeaux"
        echo(" * Dictionnaire - compression Hunspell... ")
        self.bShortenTags = True
        dAF = {}
        dAM = {}
        for oFlag in self.dFlags.values():
            for oRule in oFlag.lRules:
                if oRule.flags:
                    dAF[oRule.flags] = dAF.get(oRule.flags, 0) + 1
                sMorph = oRule.getMorph(nMode).strip()
                if sMorph:
                    dAM[sMorph] = dAM.get(sMorph, 0) + 1
        for oEntry in self.lEntry:
            if oEntry.flags:
                dAF[oEntry.flags] = dAF.get(oEntry.flags, 0) + 1
            sMorph = oEntry.getMorph(nMode).strip()
            if sMorph:
                dAM[sMorph] = dAM.get(sMorph, 0) + 1

        lAF = sorted(dAF.items(), key = lambda x: (x[1], x[0]), reverse=True)
        lAM = sorted(dAM.items(), key = lambda x: (x[1], x[0]), reverse=True)
        
        with open(spDst, 'a', encoding='utf-8', newline="\n") as hDst:
            hDst.write("\n\nDrapeaux :\n")
            for nAF, elem in enumerate(lAF, 1):
                self.dAF[elem[0]] = str(nAF)
                hDst.write("  > {0[1]:>8} : {0[0]}\n".format(elem))
            hDst.write("\n\nMorphologies :\n")
            for nAM, elem in enumerate(lAM, 1):
                self.dAM[elem[0]] = str(nAM)
                hDst.write("  > {0[1]:>8} : {0[0]}\n".format(elem))

    def writeDictionary (self, spDst, dTplVars, nMode, bSimplified):
        "Écrire le fichier dictionnaire (.dic)"
        echo(' * Dictionnaire >> [ {}.dic ] ({})'.format(dTplVars['asciiName'], dTplVars['subDicts']))
        nEntry = 0
        for oEntry in self.lEntry:
            if oEntry.di in dTplVars['subDicts']:
                nEntry += 1
        with open(spDst+'/'+dTplVars['asciiName']+'.dic', 'w', encoding='utf-8', newline="\n") as hDst:
            hDst.write(str(nEntry)+"\n")
            for oEntry in self.lEntry:
                if oEntry.di in dTplVars['subDicts']:
                    hDst.write(oEntry.getEntryLine(self, nMode, bSimplified))
    
    def writeAffixes (self, spDst, dTplVars, nMode, bSimplified):
        "Écrire le fichier des affixes (.aff)"
        echo(' * Dictionnaire >> [ {}.aff ]'.format(dTplVars['asciiName']))
        info = "# This Source Code Form is subject to the terms of the Mozilla Public\n" + \
               "# License, v. 2.0. If a copy of the MPL was not distributed with this\n" + \
               "# file, You can obtain one at http://mozilla.org/MPL/2.0/.\n\n" + \
               "# AFFIXES DU {} v{}\n".format(dTplVars['name'], self.sVersion) + \
               "# par Olivier R. -- licence MPL 2.0\n" + \
               "# Généré le " + time.strftime("%d-%m-%Y à %H:%M") + "\n" \
               "# Pour améliorer le dictionnaire, allez sur http://www.dicollecte.org/\n\n"
               
        with open(spDst+'/'+dTplVars['asciiName']+'.aff', 'w', encoding='utf-8', newline="\n") as hDst:
            hDst.write(info)
            hDst.write(self.sSettings + "\n")
            if self.bShortenTags:
                hDst.write("AM {}\n".format(len(self.dAM)))
                for item in self.dAM.items():
                    hDst.write("AM {}\n".format(item[0]))
                hDst.write("\n")
                hDst.write("AF {}\n".format(len(self.dAF)))
                for item in self.dAF.items():
                    hDst.write("AF {}\n".format(item[0]))
                hDst.write("\n")
            for oFlag in self.dFlags.values():
                hDst.write(oFlag.getFlag(dTplVars['subDicts'], self, nMode, bSimplified))

    def sortEntriesNatural (self):
        echo(' * Dictionnaire - Tri naturel des entrées...')
        self.lEntry = sorted(self.lEntry, key=Entree.keyTriNat)

    def sortEntriesNumerical (self):
        echo(' * Dictionnaire - Tri numérique des entrées...')
        self.lEntry = sorted(self.lEntry, key=Entree.keyTriNum)        

    def sortLexiconByFlexion (self):
        echo(' * Dictionnaire - tri du lexique (par flexion)...')
        self.lFlexions = sorted(self.lFlexions, key=Flexion.keyFlexion)

    def sortLexiconByFreq (self):
        echo(' * Dictionnaire - tri du lexique (par fréquence)...')
        self.lFlexions = sorted(self.lFlexions, key=Flexion.keyFreq)

    def sortLexiconByIdx (self):
        echo(' * Dictionnaire - tri du lexique (par index)...')
        self.lFlexions = sorted(self.lFlexions, key=Flexion.keyIdx)

    def checkEntries (self):
        echo(' * Dictionnaire - contrôle des entrées...')
        for e in self.lEntry:
            e.check()

    def generateFlexions (self):
        echo(' * Lexique - genèse des formes fléchies...')
        for oEntry in self.lEntry:
            oEntry.generateFlexions(self.dFlags)
            self.lFlexions.extend(oEntry.lFlexions)
        # Count flexions in multiple entries
        d = {}
        for oFlex in self.lFlexions:
            if oFlex.sFlexion in d:
                if oFlex.oEntry not in d[oFlex.sFlexion]:
                    d[oFlex.sFlexion].append(oFlex.oEntry)
            else:
                d[oFlex.sFlexion] = [oFlex.oEntry]
        for oFlex in self.lFlexions:
            oFlex.lMulti = list(d[oFlex.sFlexion])
            oFlex.nMulti = len(oFlex.lMulti)
        for oFlex in self.lFlexions:
            oFlex.lMulti.remove(oFlex.oEntry)
            oFlex.nMulti -= 1
        
    def setTagsFrom (self, other):
        echo(' * Dictionnaire - copie des tags...')
        for i in range(self.nEntry):
            for oEntry in other.lEntry:
                if self.lEntry[i].lemma == oEntry.lemma and self.lEntry[i].flags == oEntry.flags:
                    self.lEntry[i].setTagsFrom(oEntry)

    def calculateStats (self, oStatsLex, spfDst):
        echo(" * Dictionnaire - calculs...")
        with open(spfDst, 'w', encoding='utf-8', newline="\n") as hDst:
            # Occurrences brutes des formes fléchies
            echo("   comptage des occurrences...")
            hDst.write(oStatsLex.getInfo())
            for oFlex in self.lFlexions:
                oFlex.setOccur(oStatsLex.getFlexionOccur(oFlex.sFlexion))
            self.nTotOccurRecognizedWords = 0
            for oFlex in self.lFlexions:
                oFlex.calcOccur()
                self.nTotOccurRecognizedWords += oFlex.nOccur
            
            # Report des occurrences
            echo("   report des occurrences des formes fléchies multiples...")
            hDst.write("Report des occurrences des formes fléchies multiples :\n")
            hDst.write("  Légende :\n")
            hDst.write("    >>   le nombre d’occurrences de la flexion est ramené à la moyenne.\n")
            hDst.write("    +>   le nombre d’occurrences de la flexion est augmenté avec le surplus d’occurrences des flexions ramenées à la moyenne.\n")
            hDst.write("    %>   le nombre d’occurrences de la flexion est pondéré avec le poids de la moyenne de l’entrée.\n\n")

            for oEntry in self.lEntry:
                oEntry.calcOccurFromFlexions()
                oEntry.calcAverageKnownOccurrence()
                oEntry.solveOccurMultipleFlexions(hDst, oStatsLex)
                oEntry.calcOccurFromFlexions()
            
            # Fréquences
            echo("   calcul des fréquences et indices de fréquence...")
            for oFlex in self.lFlexions:
                oFlex.calcFreq(self.nTotOccurRecognizedWords)
            for oEntry in self.lEntry:
                oEntry.calcFreq(self.nTotOccurRecognizedWords)
            
            # Entrées, statistiques
            echo("   statistiques...")
            hDst.write("\n\nNatures grammaticales :\n")
            d = {}
            for oEntry in self.lEntry:
                po = re.sub("(?<=v[0-3])[itnpqrmaezx_]+", "", oEntry.po)
                d[po] = d.get(po, 0) + 1
            for e in sorted(d.items(), key = lambda x: (x[1], x[0]), reverse=True):
                hDst.write(" * {0[1]:<15} : {0[0]}\n".format(e))
            
            hDst.write("\n\nVentilation des entrées par indice de fréquence :\n")
            d1 = {}
            d2 = {}
            for oEntry in self.lEntry:
                d1[oEntry.fq] = d1.get(oEntry.fq, 0) + 1
                d2[oEntry.fq] = d2.get(oEntry.fq, 0) + oEntry.fFreq
            for k in sorted(d1.keys()):
                hDst.write(" * {} : {} entrées ({:.2f} %)  → {:.9f} %\n".format(k, d1[k], (d1[k]*100)/self.nEntry, d2[k]))
                    
            hDst.write("\n\nRépartition des entrées par sous-dictionnaire :\n")
            d = {}
            for oEntry in self.lEntry:
                d[oEntry.di] = d.get(oEntry.di, 0) + 1
            for sKey, nVal in d.items():
                hDst.write(" * {0:<15} : {1} entrées ({2:.2f} %)\n".format(dSUBDIC[sKey], nVal, (nVal*100)/self.nEntry))
            
            # Occurrences des lettres
            echo("   occurrences des lettres...")
            d = {}
            for oFlex in self.lFlexions:
                for c in oFlex.sFlexion:
                    d[c] = d.get(c, 0) + oFlex.nOccur
            nTot = 0
            for k in d:
                nTot += d[k]
            hDst.write("\n\nOccurrences des lettres dans le corpus :\n")
            for sKey, nVal in sorted(d.items(), key = lambda x: (x[1], x[0]), reverse=True):
                hDst.write("   {} : {:>16,.0f}  /  {:.8f} %\n".format(sKey, nVal, nVal*100/nTot))

            # Mots par nombre de lettres
            echo("   Nombre de lettres dans les mots...")
            if not self.aFlexions:
                self.aFlexions = set([e.sFlexion for e in self.lFlexions])
            d = {}
            for sFlex in self.aFlexions:
                n = len(sFlex)
                d[n] = d.get(n, 0) + 1
            hDst.write("\n\nNombre de lettres dans les graphies :\n")
            for sKey, nVal in sorted(d.items()):
                hDst.write("   {:>2} lettres : {:>8} graphies\n".format(sKey, nVal))

            hDst.write("\n\nNombre de formes fléchies : {}\n".format(len(self.lFlexions)))
            hDst.write("\n\nNombre de graphies : {}\n".format(len(self.aFlexions)))

    def calcMetagraphe (self):
        echo(" * Lexique - Metagraphe")
        for oFlex in self.lFlexions:
            oFlex.calcMetagraphe()
    
    def calcMetaphone2 (self):
        echo(" * Lexique - Metaphone 2")
        for oFlex in self.lFlexions:
            oFlex.calcMetaphone2()
    
    def createNgrams (self, spDest, n):
        echo(" * Lexique - Ngrams " + str(n))
        if n < 2:
            echo("erreur: n = " + str(n))
            return
        dOccur = {} # ngram:n
        dRefW = {} # ngram:set(idx)
        dWords = {} # word:idx
        for oFlex in self.lFlexions:
            for sNgram in getListNgrams(oFlex.sFlexion, n):
                # words list
                if oFlex.sFlexion not in dWords:
                    dWords[oFlex.sFlexion] = len(dWords)
                idx = dWords[oFlex.sFlexion]
                # ngram occurrence
                dOccur[sNgram] = dOccur.get(sNgram, 0) + 1
                if sNgram not in dRefW:
                    dRefW[sNgram] = set()
                # ngram word reference
                dRefW[sNgram].add(idx)
        with open(spDest+"/ngrams-%d.txt"%n, 'w', encoding='utf-8', newline="\n") as hDst:
            for key, value in dWords.items():
                hDst.write("%d: %s\n"% (value, key))
            for key, value in dOccur.items():
                if value > 1:
                    hDst.write("%s: %d  --  "% (key, value))
                    hDst.write(str(dRefW[key]))
                    hDst.write("\n")

    def writeLexicon (self, spfDst, version, oStatsLex):
        echo(' * Lexique >> [ {} ] '.format(spfDst))
        with open(spfDst, 'w', encoding='utf-8', newline="\n") as hDst:
            hDst.write(MPLHEADER)
            hDst.write("# Lexique des formes fléchies du français - Dicollecte v{}\n# Licence : MPL v2.0\n\n".format(version))
            hDst.write(oStatsLex.getInfo())
            hDst.write(Flexion.header(oStatsLex))
            for oFlex in self.lFlexions:
                hDst.write(oFlex.__str__(oStatsLex))

    def writeGrammarCheckerLexicon (self, spfDst, version):
        echo(' * Lexique simplifié >> [ {} ] '.format(spfDst))
        with open(spfDst[:-4]+".lex", 'w', encoding='utf-8', newline="\n") as hDst:
            hDst.write(MPLHEADER)
            hDst.write("# Lexique simplifié pour Grammalecte - Dicollecte v{}\n# Licence : MPL v2.0\n\n".format(version))
            hDst.write(Flexion.simpleHeader())
            for oFlex in self.lFlexions:
                hDst.write(oFlex.getGrammarCheckerRepr())

    def createFiles (self, spDst, lDictVars, nMode, bSimplified):
        sDicName = PREFIX_DICT_PATH + self.sVersion
        spDic = spDst + '/' + sDicName
        dir_util.mkpath(spDic)
        for dVars in lDictVars:
            # template vars
            dVars['version'] = self.sVersion
            # Dictionaries files (.dic) (.aff)
            self.writeAffixes(spDic, dVars, nMode, bSimplified)
            self.writeDictionary(spDic, dVars, nMode, bSimplified)
        copyTemplate('orthographe', spDic, 'README_dict_fr.txt', dVars)
        createZipFiles(spDic, spDst, sDicName + '.zip')

    def createLibreOfficeExtension (self, spBuild, dTplVars, lDictVars, spDestGL=""):
        # LibreOffice extension
        echo(" * Dictionnaire >> extension pour LibreOffice")
        dTplVars['version'] = self.sVersion
        sExtensionName = EXT_PREFIX_OOO + self.sVersion
        spExt = spBuild + '/' + sExtensionName
        dir_util.mkpath(spExt+'/META-INF')
        dir_util.mkpath(spExt+'/ui')
        dir_util.mkpath(spExt+'/dictionaries')
        dir_util.mkpath(spExt+'/pythonpath')
        file_util.copy_file('_templates/ooo/manifest.xml', spExt+'/META-INF')
        file_util.copy_file('_templates/ooo/DictionarySwitcher.py', spExt)
        file_util.copy_file('_templates/ooo/ds_strings.py', spExt+'/pythonpath')
        file_util.copy_file('_templates/ooo/addons.xcu', spExt+'/ui')
        file_util.copy_file('_templates/ooo/french_flag.png', spExt)
        file_util.copy_file('_templates/ooo/french_flag_16.bmp', spExt+'/ui')
        copyTemplate('_templates/ooo', spExt, 'description.xml', dTplVars)
        copyTemplate('_templates/ooo', spExt, 'dictionaries.xcu', dTplVars)
        #file_util.copy_file('_templates/ooo/dictionaries.xcu.tpl.xml', spExt)
        copyTemplate('_templates/ooo', spExt, 'package-description.txt', dTplVars)
        for dVars in lDictVars:
            dicPath = spBuild + '/' + PREFIX_DICT_PATH + self.sVersion 
            file_util.copy_file(dicPath+'/'+dVars['asciiName']+'.dic', spExt+'/dictionaries/'+dVars['asciiName']+'.dic')
            file_util.copy_file(dicPath+'/'+dVars['asciiName']+'.aff', spExt+'/dictionaries/'+dVars['asciiName']+'.aff')
        copyTemplate('orthographe', spExt+'/dictionaries', 'README_dict_fr.txt', dTplVars)
        # thesaurus
        file_util.copy_file('thesaurus/thes_fr.dat', spExt+'/dictionaries')
        file_util.copy_file('thesaurus/thes_fr.idx', spExt+'/dictionaries')
        file_util.copy_file('thesaurus/README_thes_fr.txt', spExt+'/dictionaries')
        # hyphenation
        file_util.copy_file('césures/hyph_fr.dic', spExt+'/dictionaries')
        file_util.copy_file('césures/hyph_fr.iso8859-1.dic', spExt+'/dictionaries')
        file_util.copy_file('césures/frhyph.tex', spExt+'/dictionaries')
        file_util.copy_file('césures/hyph-fr.tex', spExt+'/dictionaries')
        file_util.copy_file('césures/README_hyph_fr-3.0.txt', spExt+'/dictionaries')
        file_util.copy_file('césures/README_hyph_fr-2.9.txt', spExt+'/dictionaries')
        # zip
        createZipFiles(spExt, spBuild, sExtensionName + '.oxt')
        # copy to Grammalecte Project
        if spDestGL:
            echo("   extension copiée dans Grammalecte...")
            dir_util.copy_tree(spExt+'/dictionaries', spDestGL)
    
    def createMozillaExtensions (self, spBuild, dTplVars, lDictVars, spDestGL=""):
        # Mozilla extension 1
        echo(" * Dictionnaire >> extension pour Mozilla")
        dTplVars['version'] = self.sVersion
        sExtensionName = EXT_PREFIX_MOZ + self.sVersion
        spExt = spBuild + '/' + sExtensionName
        dir_util.mkpath(spExt+'/dictionaries')
        copyTemplate('_templates/moz', spExt, 'install.rdf', dTplVars)
        spDict = spBuild + '/' + PREFIX_DICT_PATH + self.sVersion
        file_util.copy_file(spDict+'/fr-classique.dic', spExt+'/dictionaries/fr-classic.dic')
        file_util.copy_file(spDict+'/fr-classique.aff', spExt+'/dictionaries/fr-classic.aff')
        copyTemplate('orthographe', spExt, 'README_dict_fr.txt', dTplVars)
        createZipFiles(spExt, spBuild, sExtensionName + '.xpi')
        # Grammalecte
        if spDestGL:
            echo(" * Dictionnaire >> copie des dicos dans Grammalecte")
            for dVars in lDictVars:
                file_util.copy_file(spDict+'/'+dVars['asciiName']+'.dic', spDestGL+'/'+dVars['mozAsciiName']+"/"+dVars['mozAsciiName']+'.dic')
                file_util.copy_file(spDict+'/'+dVars['asciiName']+'.aff', spDestGL+'/'+dVars['mozAsciiName']+"/"+dVars['mozAsciiName']+'.aff')
    
    def createFileIfqForDB (self, spBuild):
        echo(" * Dictionnaire >> indices de fréquence pour la DB...")
        with open(spBuild+'/dictIdxIfq-'+self.sVersion+'.diff.txt', 'w', encoding='utf-8', newline="\n") as hDiff, \
             open(spBuild+'/dictIdxIfq-'+self.sVersion+'.notes.txt', 'w', encoding='utf-8', newline="\n") as hNotes:
            for oEntry in self.lEntry:
                if oEntry.fq != oEntry.oldFq:
                    hDiff.write("{0.iD}\t{0.fq}\n".format(oEntry))
                    hNotes.write("{0.lemma}/{0.flags}\t{0.oldFq} > {0.fq}\n".format(oEntry))
        
    def createLexiconPackages (self, spBuild, version, oStatsLex, spDestGL=""):
        sLexName = LEX_PREFIX + version
        spLex = spBuild + '/' + sLexName
        dir_util.mkpath(spLex)
        # write Dicollecte lexicon
        self.sortLexiconByFreq()
        self.writeLexicon(spLex + '/' + sLexName + '.txt', version, oStatsLex)
        self.writeGrammarCheckerLexicon(spBuild + '/' + sLexName + '.lex', version)
        copyTemplate('lexique', spLex, 'README_lexique.txt', {'version': version})
        # zip
        createZipFiles(spLex, spBuild, sLexName + '.zip')
        # copy GC lexicon to Grammalecte
        if spDestGL:
            file_util.copy_file(spBuild + '/' + sLexName + '.lex', spDestGL + '/French.lex')
            file_util.copy_file('lexique/French.tagset.txt', spDestGL)

    def createDictConj (self, spBuild, spDestGL=""):
        echo(" * Dictionnaire >> fichier de conjugaison...")
        with open(spBuild+'/dictConj.txt', 'w', encoding='utf-8', newline="\n") as hDst:
            for oEntry in self.lEntry:
                if oEntry.po.startswith("v"):
                    hDst.write(oEntry.getConjugation())
        if spDestGL:
            echo("   Fichier de conjugaison copié dans Grammalecte...")
            file_util.copy_file(spBuild+'/dictConj.txt', spDestGL)

    def createDictDecl (self, spBuild, spDestGL=""):
        echo(" * Dictionnaire >> fichier de déclinaison...")
        with open(spBuild+'/dictDecl.txt', 'w', encoding='utf-8', newline="\n") as hDst:
            for oEntry in self.lEntry:
                if re.match("[SXFWIA]", oEntry.flags) and (oEntry.po.startswith("nom") or oEntry.po.startswith("adj")):
                    hDst.write(oEntry.getDeclination())
        if spDestGL:
            echo("   Fichier de déclinaison copié dans Grammalecte...")
            file_util.copy_file(spBuild+'/dictDecl.txt', spDestGL)

    def generateSpellVariants (self, nReq, spBuild):
        if nReq < 1: nReq = 1
        if nReq > 2: nReq = 2
        echo(" * Lexique >> variantes par suppression... n = " + str(nReq))
        with open(spBuild+'/dictSpellVariants-'+str(nReq)+'.txt', 'w', encoding='utf-8', newline="\n") as hDst:
            for oFlex in frozenset(self.lFlexions):
                hDst.write(oFlex.sFlexion+"\t_\t_\n")
                if len(oFlex.sFlexion) <= 2:
                    n = 0
                elif len(oFlex.sFlexion) <= 5:
                    n = 1
                else:
                    n = nReq
                #lTup = self._generatePhonetVariants(oFlex.sFlexion)
                lTup = self._generateDeleteVariants(oFlex.sFlexion, oFlex.sFlexion, n)
                for t in lTup:
                    sTag = t[1]  if "\t" in t[1]  else t[1]+"\t_"
                    hDst.write(t[0]+"\t"+sTag+"\n")

    _lTupPhonet = [ ("ph", "f"), ("qu", "k"), ("ss", "c"), ("ss", "ç"), ("ct", "x"),
        ("oe", "œ"), ("ae", "æ"), ("ei", "é"), ("ai", "é"), ("au", "o"), ("eau", "o"),
    ]

    def _generatePhonetVariants (self, s):
        l = []
        for torep, rep in self._lTupPhonet():
            for m in torep.finditer(s):
                l.append( (s[:m.start(0)] + rep + s[m.end(0):], str(m.start(0))+":"+str(m.start(0)+len(rep))+">"+torep) )
        return l

    def _generateDeleteVariants (self, sWord0, sWordCur, n):
        "renvoie une liste de tuples : (forme dégradée de sWord, code de genèse de sWord)"
        # caution: recursive function
        if n == 0:
            return []
        lTup = []
        for i in range(len(sWordCur)):
            sNew = sWordCur[0:i]+sWordCur[i+1:]
            lTup.append( ( sNew, self._generateAddCode(sWord0, sNew) ) )
            lTup += self._generateDeleteVariants(sWord0, sNew, n-1)
        return lTup

    def _generateAddCode (self, sWord, sCrippled):
        "returns addCode to generate sWord from sCrippled"
        sAdd = ""
        for i in range(len(sWord)):
            if sWord[i] != sCrippled[i:i+1]:
                sCrippled = sCrippled[:i] + sWord[i] + sCrippled[i:]
                if sAdd:
                    sAdd += "\t"
                sAdd += str(i)+"+"+sWord[i]
        return sAdd  if sAdd  else "0"



class Entree:
    def __init__ (self, sLine):
        self.lemma = ''
        self.flags = ''
        # champs morphologiques Hunspell
        self.po = ''
        self.iz = ''
        self.ds = ''
        self.ts = ''
        self.ip = ''
        self.dp = ''
        self.tp = ''
        self.sp = ''
        self.pa = ''
        self.st = ''
        self.al = ''
        self.ph = ''
        # champs annexes
        self.lx = ''
        self.se = ''
        self.et = ''
        self.di = '*'
        self.fq = ''
        self.iD = '0'

        # autres
        self.comment = ''
        self.err = ''
        self.nFlexions = 0
        self.lFlexions = []
        self.sRadical = ''
        self.nOccur = 0
        self.nAKO = -1   # Average known occurrences
        self.fFreq = 0
        self.oldFq = ''
        
        sLine = sLine.rstrip(" \n")
        # commentaire
        if '#' in sLine:
            sLine, comment = sLine.split('#', 1)
            self.comment = comment.strip()
        # éléments de la ligne
        elems = sLine.split()
        nElems = len(elems)
        # lemme et drapeaux
        firstElems = elems[0].split('/')
        self.lemma = firstElems[0]
        self.flags = firstElems[1]  if len(firstElems) > 1  else ''
        # morph
        for i in range(1, nElems):
            if len(elems[i]) > 3 and elems[i][2] == ':':
                fields = elems[i].split(':', 1)
                if fields[0] == 'po':
                    self.po = fields[1]  if self.po == ''  else self.po + ' ' + fields[1]
                elif fields[0] == 'is':
                    self.iz = fields[1]  if self.iz == ''  else self.iz + ' ' + fields[1]
                elif fields[0] == 'ds':
                    self.ds = fields[1]  if self.ds == ''  else self.ds + ' ' + fields[1]
                elif fields[0] == 'ts':
                    self.ts = fields[1]  if self.ts == ''  else self.ts + ' ' + fields[1]
                elif fields[0] == 'ip':
                    self.ip = fields[1]  if self.ip == ''  else self.ip + ' ' + fields[1]
                elif fields[0] == 'dp':
                    self.dp = fields[1]  if self.dp == ''  else self.dp + ' ' + fields[1]
                elif fields[0] == 'tp':
                    self.tp = fields[1]  if self.tp == ''  else self.tp + ' ' + fields[1]
                elif fields[0] == 'sp':
                    self.sp = fields[1]  if self.sp == ''  else self.sp + ' ' + fields[1]
                elif fields[0] == 'pa':
                    self.pa = fields[1]  if self.pa == ''  else self.pa + ' ' + fields[1]
                elif fields[0] == 'st':
                    self.st = fields[1]  if self.st == ''  else self.st + ' ' + fields[1]
                elif fields[0] == 'al':
                    self.al = fields[1]  if self.al == ''  else self.al + ' ' + fields[1]
                elif fields[0] == 'ph':
                    self.ph = fields[1]  if self.ph == ''  else self.ph + ' ' + fields[1]
                elif fields[0] == 'lx':
                    self.lx = fields[1]  if self.lx == ''  else self.lx + ' ' + fields[1]
                elif fields[0] == 'se':
                    self.se = fields[1]  if self.se == ''  else self.se + ' ' + fields[1]
                elif fields[0] == 'et':
                    self.et = fields[1]  if self.et == ''  else self.et + ' ' + fields[1]
                elif fields[0] == 'di':
                    self.di = fields[1]
                elif fields[0] == 'fq':
                    self.fq = fields[1]
                elif fields[0] == 'id':
                    self.iD = fields[1]
                else:
                    echo('  ## Champ inconnu: {}  dans  {}/{}'.format(fields[0], self.lemma, self.flags))
            else:
                self.err = self.err + elems[i]
        if self.err:
            echo("\n## Erreur dans le dictionnaire : {}".format(self.err))
            echo("   dans : " + self.lemma)
                
    def __str__ (self):
        return "{0.lemma}/{0.flags} {1}".format(self, self.getMorph(2))

    def check (self):
        sErr = ''
        if self.lemma == '':
            sErr += 'lemme vide'
        if not re.match(r"[a-zA-ZéÉôÔàâÂîÎïèÈêÊÜœŒæÆçÇ0-9µåÅΩ&αβγδεζηθικλμνξοπρστυφχψωΔℓΩ_]", self.lemma):
            sErr += 'premier caractère inconnu: ' + self.lemma[0]
        if re.search(r"\s$", self.lemma):
            sErr += 'espace en fin de lemme'
        if re.match(r"v[0123]", self.po) and not re.match(r"[eas_][ix_][tx_][nx_][pqreuvx_][mx_][ex_z][ax_z]\b", self.po[2:]):
            sErr += 'verbe inconnu: ' + self.po
        if (re.match(r"S[*.]", self.flags) and re.search("[sxz]$", self.lemma)) or (re.match(r"X[*.]", self.flags) and not re.search("[ul]$", self.lemma)):
            sErr += 'drapeau inutile'
        if self.iz == '' and re.match(r"[SXAI](?!=)", self.flags) and self.po:
            sErr += '[is]'
        if re.match(r"pl|sg|inv", self.iz):
            sErr += '[is]'
        if re.match(r"[FW]", self.flags) and re.search(r"epi|mas|fem|inv|sg|pl", self.iz):
            sErr += '[is]'
        if re.match(r"[FW]", self.flags) and re.search(r"[^eë]$", self.lemma):
            sErr += "fin de lemme inapproprié"
        if re.match(r".\*", self.flags) and re.match(r"[bcdfgjklmnpqrstvwxz]", self.lemma):
            sErr += 'drapeau pour lemme commençant par une voyelle'
        if re.search(r"pl|sg|inv", self.iz) and re.match(r"[SXAIFW](?!=)", self.flags):
            sErr += '[is]'
        if re.search(r"nom|adj", self.po) and re.match(r"(?i)[aâàäáeéèêëiîïíìoôöóòuûüúù]", self.lemma) and re.match("[SFWXAI][.]", self.flags) \
           and "pel" not in self.lx:
            sErr += 'le drapeau derait finir avec *'
        if not self.flags and self.iz.endswith(("mas", "fem", "epi")):
            sErr += '[is] incomplet'
        if sErr:
            echo('   error -  id: ' + self.iD, end = "")
            echo('  ' + sErr + '  in  ' + self.__str__())

    def setTagsFrom (self, oEnt):
        self.po = oEnt.po
        self.iz = oEnt.iz
        self.ds = oEnt.ds
        self.ts = oEnt.ts
        self.ip = oEnt.ip
        self.dp = oEnt.dp
        self.tp = oEnt.tp
        self.sp = oEnt.sp
        self.pa = oEnt.pa
        self.st = oEnt.st
        self.al = oEnt.al
        self.ph = oEnt.ph
        self.lx = oEnt.lx
        self.se = oEnt.se
        self.et = oEnt.et
        self.di = oEnt.di
        self.fq = oEnt.fq

    def keyTriNat (self):
        return (self.lemma.translate(CHARMAP), self.flags, self.po)

    def keyTriNum (self):
        return (self.lemma, self.flags, self.po)

    def getEntryLine (self, oDict, nMode, bSimplified=False):    
        sLine = self.lemma
        if self.flags:
            sLine += '/'
            sLine += self.flags  if not oDict.bShortenTags or bSimplified  else oDict.dAF[self.flags]
        if bSimplified:
            return sLine.replace("()", "") + "\n"
        if nMode > 0:
            sMorph = self.getMorph(nMode)
            if sMorph:
                sLine += sMorph  if not oDict.bShortenTags  else "\t" + oDict.dAM[sMorph.strip()]
        return sLine + "\n"

    def getMorph (self, nMode):
        txt = ''
        if self.po: txt += fieldToHunspell('po', self.po)
        if self.iz: txt += fieldToHunspell('is', self.iz)
        if self.ds: txt += fieldToHunspell('ds', self.ds)
        if self.ts: txt += fieldToHunspell('ts', self.ts)
        if self.ip: txt += fieldToHunspell('ip', self.ip)
        if self.dp: txt += fieldToHunspell('dp', self.dp)
        if self.tp: txt += fieldToHunspell('tp', self.tp)
        if self.sp: txt += fieldToHunspell('sp', self.sp)
        if self.pa: txt += fieldToHunspell('pa', self.pa)
        if self.al: txt += fieldToHunspell('al', self.al)
        if self.st: txt += fieldToHunspell('st', self.st)
        if self.ph: txt += fieldToHunspell('ph', self.ph)
        if nMode > 1:
            if self.lx: txt += fieldToHunspell('lx', self.lx)
            if self.se: txt += fieldToHunspell('se', self.se)
            if self.et: txt += fieldToHunspell('et', self.et)
            if self.fq: txt += ' fq:' + self.fq
            if self.di != '*': txt += ' di:' + self.di
        return txt

    def getShortDescr (self):
        txt = self.lemma
        if self.flags:
            txt += '/' + self.flags
        if self.di != '*':
            txt += ' di:' + self.di
        return txt

    def generateFlexions (self, dFlags):
        lTuples = self._flechir(dFlags)
        # création des objects flexions
        self.nFlexions = 0
        self.lFlexions = []
        sReject = ""
        for sFlex, sMorph, sDic in lTuples:
            if '+' not in sMorph:
                sMorph = self.clean(sMorph)
                if not sMorph.endswith((" mas", " fem", " epi")):
                    self.lFlexions.append( Flexion(self, sFlex, sMorph, sDic) )
                    self.nFlexions += 1
                else:
                    #echo(sFlex + " " + sMorph + ", ")
                    pass
        # Drapeaux dont le lemme féminin doit être remplacé par le masculin dans la gestion des formes fléchies
        if self.flags.startswith(("F.", "F*", "W.", "W*")):
            # recherche de la forme masculine
            for t in lTuples:
                sMorph = self.clean(t[1])
                if sMorph.endswith('mas') or sMorph.endswith('mas sg') or sMorph.endswith('mas inv'): 
                    self.sRadical = t[0]
        else:
            self.sRadical = self.lemma
        # Tag duplicates
        d = {}
        for oFlex in self.lFlexions:
            d[oFlex.sFlexion] = d.get(oFlex.sFlexion, 0) + 1
        for oFlex in self.lFlexions:
            oFlex.nDup = d[oFlex.sFlexion]

    def _flechir (self, dFlags, morph='', iPR=0):
        # recursive function!
        "renvoie une liste de tuples (déclinaisons, morphologie), formes fléchies du lemme"
        if iPR == 2:
            return []
        if iPR == 0:
            morph = self.lexMorph()
        lFlexions = [(self.lemma, morph, self.di)]  if iPR == 0 and not self.flags.endswith('()')  else []
        lFlexPrefix = []
        lFlexSuffix = []
        for sFlag in makeLongFlags(self.flags):
            if sFlag not in dFlags:
                if sFlag not in ['**', '()', '||', '--']:
                    lFlexions.append( (self.lemma, '[unknown flag: {}]'.format(sFlag)) )
                    echo("ERROR: "  + self.lemma + ' - unknown flag: ' + sFlag)
            else:
                oFlag = dFlags[sFlag]
                if not oFlag.bSfx:
                    # cas des préfixes
                    for oRule in oFlag.lRules:
                        if oRule.motif.search(self.lemma):
                            ruleMorph = oRule.lexMorph()
                            if oRule.cut == '0':
                                flexion = (oRule.add+self.lemma, ruleMorph+morph, oRule.di)
                                if oFlag.bMix:
                                    lFlexPrefix.append(flexion)
                                    for flex in lFlexSuffix:
                                        lFlexions.append( (oRule.add+flex[0], flex[1]+ruleMorph) )
                                else:
                                    lFlexions.append(flexion)
                            else:
                                flexion = (self.lemma.replace(oRule.cut, oRule.add, 1), ruleMorph+morph, oRule.di)
                                if oFlag.bMix:
                                    lFlexPrefix.append(flexion)
                                    for flex in lFlexSuffix: 
                                        lFlexions.append( (flex[0].replace(oRule.cut, oRule.add, 1), flex[1]+ruleMorph) )
                                else:
                                    lFlexions.append(flexion)
                            if oRule.flags != '' and oRule.flags != '**':
                                lFlexions.extend(Entree(flexion[0]+'/'+oRule.flags)._flechir(dFlags, flexion[1], iPR+1))
                else:
                    # cas des suffixes
                    for oRule in oFlag.lRules:
                        if oRule.motif.search(self.lemma):
                            ruleMorph = oRule.lexMorph()
                            if not oRule.flags.endswith('**') or oRule.flags == '**':
                                # règle ordinaire, pas de circumfix
                                if oRule.cut == '0':
                                    flexion = (self.lemma+oRule.add, morph+ruleMorph, oRule.di)
                                    if oFlag.bMix:
                                        lFlexSuffix.append(flexion)
                                        for flex in lFlexPrefix:
                                            lFlexions.append( (flex[0]+oRule.add, flex[1]+ruleMorph) )
                                    else:
                                        lFlexions.append(flexion)
                                else:
                                    nCut = len(oRule.cut)
                                    flexion = (self.lemma[:-nCut]+oRule.add, morph+ruleMorph, oRule.di)
                                    if oFlag.bMix:
                                        lFlexSuffix.append(flexion)
                                        for flex in lFlexPrefix:
                                            lFlexions.append( (flex[0][:-nCut]+oRule.add, flex[1]+ruleMorph) )
                                    else:
                                        lFlexions.append(flexion)
                                if oRule.flags != '' and oRule.flags != '**':
                                    lFlexions.extend(Entree(flexion[0]+'/'+oRule.flags)._flechir(dFlags, flexion[1], iPR+1))
                            else:
                                # la règle impose un circumfix
                                if oRule.cut == '0':
                                    flexion = (self.lemma+oRule.add, morph+ruleMorph, oRule.di)
                                else:
                                    flexion = (self.lemma[:-len(oRule.cut)]+oRule.add, morph+ruleMorph, oRule.di)
                                lFlexions.extend(Entree(flexion[0]+'/'+oRule.flags)._flechir(dFlags, flexion[1], iPR+1))
        lFlexions = lFlexions + lFlexPrefix + lFlexSuffix
        return lFlexions

    def clean (self, s):
        return s.replace('  ', ' ').strip(' ')

    def lexMorph (self):
        # morphology for lexicon
        txt = ' '
        if self.po: txt += self.po + ' '
        if self.iz: txt += self.iz + ' '
        if self.ds: txt += self.ds + ' '
        if self.ts: txt += self.ts + ' '
        if self.ip: txt += self.ip + ' '
        if self.dp: txt += self.dp + ' '
        if self.tp: txt += self.tp + ' '
        if self.sp: txt += self.sp + ' '
        return txt

    def getConjugation (self):
        sRes = self.lemma + "\t" + self.po[1:10] + "\n"
        for oFlex in self.lFlexions:
            sMorph = oFlex.sMorph[11:].rstrip("!").replace("ppas adj", "ppas").replace("ppas 1jsg", "ppas")
            if not sMorph.startswith("ppas") and sMorph.find(" ") > 1:
                # complex tags
                for s in getVerbMultiMorph(sMorph):
                    sRes += "_\t" + s + "\t" + oFlex.sFlexion + "\n"
            else:
                sRes += "_\t" + sMorph + "\t" + oFlex.sFlexion + "\n"
        return sRes + "$\n"

    def getDeclination (self):
        sRes = self.lemma + "\t" + self.flags + "\n"
        for oFlex in self.lFlexions:
            if "ppas" in oFlex.sMorph:
                sMorph = oFlex.sMorph.replace("ppas adj", "adj").replace("ppas 1jsg", "adj")
                sRes += "_\t" + sMorph + "\t" + oFlex.sFlexion + "\n"
            elif "adj" in oFlex.sMorph or "nom" in oFlex.sMorph:
                sRes += "_\t" + oFlex.sMorph + "\t" + oFlex.sFlexion + "\n"
        return sRes + "$\n"

    def calcOccurFromFlexions (self):
        self.nOccur = 0
        for o in self.lFlexions:
            self.nOccur += o.nOccur

    def calcAverageKnownOccurrence (self):
        # nous calculons la moyenne des occurrences des formes fléchies
        # qui n’ont pas d’équivalent dans les autres entrées (nMulti = 0) 
        nOccur = 0
        nFlex = 0
        for oFlex in self.lFlexions:
            if oFlex.nMulti == 0:
                nOccur += oFlex.nOccur
                nFlex += 1
        # moyenne des formes fléchies sans équivalent ou -1
        self.nAKO = math.ceil(nOccur / nFlex)  if nFlex > 0  else -1
    
    def solveOccurMultipleFlexions (self, hDst, oStatsLex):
        sBlank = "           "
        if self.nAKO >= 0:
            for oFlex in self.lFlexions:
                if oFlex.nMulti > 0 and not oFlex.bBlocked:
                    # on trie les entrées avec AKO et sans AKO
                    lEntWithAKO = []
                    lEntNoAKO = []
                    for oEntry in oFlex.lMulti:
                        if oEntry.nAKO >= 0:
                            lEntWithAKO.append(oEntry)
                        else:
                            lEntNoAKO.append(oEntry)
                    
                    if lEntNoAKO:
                        # on calcule la différence totale occasionnée par du passage des flexions appartenant à des entrées avec AKO au niveau AKO
                        nDiff = (oFlex.nOccur - self.nAKO) * oFlex.nDup
                        for oEntry in lEntWithAKO:
                            for oFlexM in oEntry.lFlexions:
                                if oFlex.sFlexion == oFlexM.sFlexion:
                                    nDiff += oFlexM.nOccur - oEntry.nAKO
                        if nDiff > 0:
                            # on peut passer à les formes fléchies à AKO
                            hDst.write(" * {0.sFlexion}\n".format(oFlex))
                            hDst.write("       moyenne connue\n")
                            for oFlexD in self.lFlexions:
                                if oFlex.sFlexion == oFlexD.sFlexion:
                                    hDst.write(sBlank + "{2:<30} {0.sMorph:<30}  {0.nOccur:>10}  >> {1:>10}\n".format(oFlexD, self.nAKO, self.getShortDescr()))
                                    oFlexD.setOccurAndBlock(self.nAKO)
                            for oEntry in lEntWithAKO:
                                hDst.write("       moyenne connue\n")
                                for oFlexM in oEntry.lFlexions:
                                    if oFlex.sFlexion == oFlexM.sFlexion:
                                        hDst.write(sBlank + "{2:<30} {0.sMorph:<30}  {0.nOccur:>10}  >> {1:>10}\n".format(oFlexM, oEntry.nAKO, oEntry.getShortDescr()))
                                        oFlexM.setOccurAndBlock(oEntry.nAKO)
                            # on répercute nDiff sur les flexions sans AKO
                            for oEntry in lEntNoAKO:
                                hDst.write("       sans moyenne connue\n")
                                for oFlexM in oEntry.lFlexions:
                                    if oFlex.sFlexion == oFlexM.sFlexion:
                                        nNewOccur = oFlexM.nOccur + math.ceil((nDiff / len(lEntNoAKO)) / oFlexM.nDup)
                                        hDst.write(sBlank + "{2:<30} {0.sMorph:<30}  {0.nOccur:>10}  +> {1:>10}\n".format(oFlexM, nNewOccur, oEntry.getShortDescr()))
                                        oFlexM.setOccurAndBlock(nNewOccur)
                    else:
                        # Toutes les entrées sont avec AKO : on pondère
                        nFlexOccur = oStatsLex.getFlexionOccur(oFlex.sFlexion)
                        nTotAKO = self.nAKO
                        for oEnt in oFlex.lMulti:
                            nTotAKO += oEnt.nAKO
                        
                        hDst.write(" = {0.sFlexion}\n".format(oFlex))
                        hDst.write("       moyennes connues\n")
                        for oFlexD in self.lFlexions:
                            if oFlex.sFlexion == oFlexD.sFlexion:
                                nNewOccur = math.ceil((nFlexOccur * (self.nAKO / nTotAKO)) / oFlexD.nDup)  if nTotAKO  else 0
                                hDst.write(sBlank + "{2:<30} {0.sMorph:<30}  {0.nOccur:>10}  %> {1:>10}\n".format(oFlexD, nNewOccur, self.getShortDescr()))
                                oFlexD.setOccurAndBlock(nNewOccur)
                        for oEntry in oFlex.lMulti:
                            for oFlexM in oEntry.lFlexions:
                                if oFlex.sFlexion == oFlexM.sFlexion:
                                    nNewOccur = math.ceil((nFlexOccur * (oEntry.nAKO / nTotAKO)) / oFlexM.nDup)  if nTotAKO  else 0
                                    hDst.write(sBlank + "{2:<30} {0.sMorph:<30}  {0.nOccur:>10}  %> {1:>10}\n".format(oFlexM, nNewOccur, oEntry.getShortDescr()))
                                    oFlexM.setOccurAndBlock(nNewOccur)
        
    def calcFreq (self, nTot):
        self.fFreq = (self.nOccur * 100) / nTot
        self.oldFq = self.fq
        self.fq = getIfq(self.fFreq)



class Flexion:
    def __init__ (self, oEntry, sFlex='', sMorph='', cDic=''):
        self.oEntry = oEntry
        self.sFlexion = sFlex
        self.sMorph = sMorph
        self.cDic    = cDic
        self.nOccur  = 0
        self.bBlocked  = False
        self.nDup    = 0    # duplicates in the same entry
        self.nMulti  = 0    # duplicates with other entries
        self.lMulti  = []   # list of similar flexions
        self.fFreq   = 0
        self.cFq     = ''
        self.metagfx = ''   # métagraphe
        self.metaph2 = ''   # métaphone 2
    
    def setOccur (self, n):
        self.nOccur = n

    def setOccurAndBlock (self, n):
        self.nOccur = n
        self.bBlocked = True

    def calcOccur (self):
        self.nOccur = math.ceil((self.nOccur / (self.nMulti+1)) / self.nDup)
    
    def calcFreq (self, nTot):
        self.fFreq = (self.nOccur * 100) / nTot
        self.cFq = getIfq(self.fFreq)
    
    def calcMetagraphe (self):
        t = metagraphe.getMetagraphe(self.sFlexion, self.sMorph)
        self.metagfx = t[0]  if not t[1]  else t[0]+"/"+t[1]

    def calcMetaphone2 (self):
        t = metaphone2.dm(self.sFlexion)
        self.metaph2 = t[0]  if not t[1]  else t[0]+"/"+t[1]

    @classmethod
    def header (cls, oStatsLex):
        sOccurs = ''
        for t in oStatsLex.lLex:
            sOccurs += t[1] + "\t"
        return "id\tFlexion\tLemme\tÉtiquettes\tMétagraphe (β)\tMetaphone2\tNotes\tSémantique\tÉtymologie\tSous-dictionnaire\t" + sOccurs + "Total occurrences\tDoublons\tMultiples\tFréquence\tIndice de fréquence\n"

    def __str__ (self, oStatsLex):
        sOccurs = ''
        for v in oStatsLex.dFlexions[self.sFlexion]:
            sOccurs += str(v) + "\t"
        return "{0.oEntry.iD}\t{0.sFlexion}\t{0.oEntry.sRadical}\t{0.sMorph}\t{0.metagfx}\t{0.metaph2}\t{0.oEntry.lx}\t{0.oEntry.se}\t{0.oEntry.et}\t{0.oEntry.di}{2}\t{1}{0.nOccur}\t{0.nDup}\t{0.nMulti}\t{0.fFreq:.15f}\t{0.cFq}\n".format(self, sOccurs, "/"+self.cDic if self.cDic != "*" else "")

    @classmethod
    def simpleHeader (cls):
        return "# :POS ;LEX ~SEM =FQ /DIC\n"

    def getGrammarCheckerRepr (self):
        return "{0.sFlexion}\t{0.oEntry.lemma}\t{1}\n".format(self, self._getSimpleTags())

    _dTagReplacement = {
        # POS
        "nom": ":N", "adj": ":A", "adv": ":W", "negadv": ":X", "mg": ":G", "nb": ":B",
        "loc.nom": ":Ñ", "loc.adj": ":Â", "loc.adv": ":Ŵ", "loc.verb": ":Ṽ",
        "interj": ":J", "loc.interj": ":Ĵ", "titr": ":T",
        "mas": ":m", "fem": ":f", "epi": ":e", "sg": ":s", "pl": ":p", "inv": ":i",
        "infi": ":Y",
        "ppre": ":P", "ppas": ":Q",
        "ipre": ":Ip", "iimp": ":Iq", "ipsi": ":Is", "ifut": ":If",
        "spre": ":Sp", "simp": ":Sq", "cond": ":K", "impe": ":E",
        "1sg": ":1s", "1isg": ":1ś", "1jsg": ":1ŝ", "2sg": ":2s", "3sg": ":3s", "1pl": ":1p", "2pl": ":2p", "3pl": ":3p", "3pl!": ":3p!",
        "prepv": ":Rv", "prep": ":R", "loc.prep": ":Ŕ",
        "detpos": ":Dp", "detdem": ":Dd", "detind": ":Di", "detneg": ":Dn", "detex": ":De", "det": ":D",
        "advint": ":U",
        "prodem": ":Od", "proind": ":Oi", "proint": ":Ot", "proneg": ":On", "prorel": ":Or", "proadv": ":Ow",
        "properobj": ":Oo", "propersuj": ":Os", "1pe": ":O1", "2pe": ":O2", "3pe": ":O3",
        "cjco": ":Cc", "cjsub": ":Cs", "cj": ":C", "loc.cj": ":Ĉ", "loc.cjsub": ":Ĉs",
        "prn": ":M1", "patr": ":M2", "npr": ":MP", "nompr": ":NM",
        "pfx": ":Zp", "sfx": ":Zs",
        "div": ":H",
        "err": ":#",
        # LEX
        "symb": ";S"
    }

    def _getSimpleTags (self):
        s = ""
        # POS
        for sTag in self.sMorph.split():
            if sTag.startswith("v"):
                s += ":V" + sTag[1:]
            else:
                if sTag in self._dTagReplacement:
                    s += self._dTagReplacement[sTag]
                else:
                    echo(" # unknown tag: " + sTag + "  on: " + self.oEntry.lemma)
        # LEX
        for sTag in self.oEntry.lx.split():
            if sTag in self._dTagReplacement:
                s += self._dTagReplacement[sTag]
        # SEM
        #s += "~" + self.oEntry.se  if self.oEntry.se and self.oEntry.se != "@"  else ""
        # ETY
        #s += "<" + self.oEntry.et  if self.oEntry.et and self.oEntry.et != "@"  else ""
        # IFQ
        #s += "=" + self.cFq
        # DIC
        s += "/" + self.cDic
        return s

    def keyTriNat (self):
        return (self.sFlexion.translate(CHARMAP), self.sMorph)

    def keyFreq (self):
        return (100-self.fFreq, self.oEntry.sRadical, self.sFlexion)

    def keyOcc (self):
        return (self.nOccur, self.oEntry.sRadical, self.sFlexion)
        
    def keyIdx (self):
        return self.oEntry.iD

    def keyFlexion (self):
        return self.sFlexion



class Flag:
    def __init__ (self, sFlagType, sFlagName, sMix):
        self.sFlagName = sFlagName
        self.bSfx = True  if sFlagType == 'SFX'  else False
        self.bMix = True  if sMix == 'Y'  else False
        self.lRules = []
        self.nRules = 0
        self.nOccur = 0
        
    def addAffixRule (self, line):
        "ajoute une règle au drapeau"
        oRule = AffixRule(line)
        self.lRules.append(oRule)
        self.nRules += 1

    def getFlag (self, subDicts, oDict, nMode, bSimplified):
        nRules = 0
        sRules = ''
        for oRule in self.lRules:
            if oRule.di in subDicts:
                if not (bSimplified and oRule.isReplicationRule()):
                    sRules += oRule.getRuleLine(oDict, nMode, bSimplified)
                    nRules += 1
        if nRules:
            txt = "\n"
            txt += 'SFX'  if self.bSfx  else 'PFX'
            txt += ' ' + self.sFlagName + ' '
            txt += 'Y'  if self.bMix  else 'N'
            txt += ' ' + str(nRules) + "\n"
            txt += sRules
            return txt
        else:
            return ''


class AffixRule:
    def __init__ (self, sLine):
        self.sFlagName = ''
        self.bSfx = True
        self.comment = ''
        # Règle
        self.cut = ''
        self.add = ''
        self.flags = ''
        self.cond = ''
        self.motif = ''
        # champs morphologiques de Hunspell
        self.po = ''
        self.iz = ''
        self.ds = ''
        self.ts = ''
        self.ip = ''
        self.dp = ''
        self.tp = ''
        self.sp = ''
        self.pa = ''
        self.ph = ''
        # champs de Dicollecte
        self.lx = ''
        self.di = '*'
        # erreurs
        self.err = ''
        # autres champs
        self.nOccur = 0
        
        sLine = sLine.rstrip(" \n")
        # commentaire
        if '#' in sLine:
            sLine, comment = sLine.split('#', 1)
            self.comment = comment.strip()
        # éléments de la ligne
        elems = sLine.split()
        nElems = len(elems)
        # type et nom
        self.bSfx = True  if elems[0] == "SFX"  else False
        self.sFlagName = elems[1]
        # lemme et drapeaux
        self.cut = elems[2]
        if '/' in elems[3]:
            self.add, self.flags = elems[3].split('/')
        else:
            self.add = elems[3]
            self.flags = ''
        if self.add == '0':
            self.add = ''
        self.cond = elems[4]
        try:
            self.motif = re.compile(self.cond+'$')  if self.bSfx  else re.compile('^'+self.cond)
        except:
            echo("error:"+self.cond)
        # morph
        for i in range(5, nElems):
            if len(elems[i]) > 3 and elems[i][2] == ':':
                fields = elems[i].split(':',1)
                if fields[0] == 'po':
                    self.po = fields[1]  if self.po == ''  else self.po + ' ' + fields[1]
                elif fields[0] == 'is':
                    self.iz = fields[1]  if self.iz == ''  else self.iz + ' ' + fields[1]
                elif fields[0] == 'ds':
                    self.ds = fields[1]  if self.ds == ''  else self.ds + ' ' + fields[1]
                elif fields[0] == 'ts':
                    self.ts = fields[1]  if self.ts == ''  else self.ts + ' ' + fields[1]
                elif fields[0] == 'ip':
                    self.ip = fields[1]  if self.ip == ''  else self.ip + ' ' + fields[1]
                elif fields[0] == 'dp':
                    self.dp = fields[1]  if self.dp == ''  else self.dp + ' ' + fields[1]
                elif fields[0] == 'tp':
                    self.tp = fields[1]  if self.tp == ''  else self.tp + ' ' + fields[1]
                elif fields[0] == 'sp':
                    self.sp = fields[1]  if self.sp == ''  else self.sp + ' ' + fields[1]
                elif fields[0] == 'pa':
                    self.pa = fields[1]  if self.pa == ''  else self.pa + ' ' + fields[1]
                elif fields[0] == 'ph':
                    self.ph = fields[1]  if self.pa == ''  else self.pa + ' ' + fields[1]
                elif fields[0] == 'lx':
                    self.lx = fields[1]  if self.lx == ''  else self.lx + ' ' + fields[1]
                elif fields[0] == 'di':
                    self.di = fields[1]
                else:
                    echo('Champ inconnu: {}  dans  {}'.format(fields[0], self.sFlagName))
            else:
                echo("  # Erreur affixe : {}".format(line))
    
    def isReplicationRule (self):
        "is this rule used for replication of a virtual lemma"
        return self.flags == "" and ((self.cut == "0" and self.add == "") or self.cut == self.add)

    def getRuleLine (self, oDict, nMode, bSimplified=False):
        sLine = 'SFX'  if self.bSfx  else 'PFX'
        sLine += ' ' + self.sFlagName + ' ' + self.cut + ' '
        sLine += self.add  if self.add  else '0'
        if self.flags != '':
            sLine += '/'
            sLine += self.flags  if not oDict.bShortenTags or bSimplified  else oDict.dAF[self.flags]
            if bSimplified:
                sLine = sLine.replace("()", "")
        sLine += ' ' + self.cond
        if not bSimplified and nMode > 0:
            sMorph = self.getMorph(nMode)
            if sMorph:
                sLine += sMorph  if not oDict.bShortenTags or bSimplified  else ' ' + oDict.dAM[sMorph.strip()]
        return sLine + "\n"
    
    def getMorph (self, nMode):
        # morphology for Hunspell
        txt = ''
        if self.po: txt += fieldToHunspell('po', self.po)
        if self.iz: txt += fieldToHunspell('is', self.iz)
        if self.ds: txt += fieldToHunspell('ds', self.ds)
        if self.ts: txt += fieldToHunspell('ts', self.ts)
        if self.ip: txt += fieldToHunspell('ip', self.ip)
        if self.dp: txt += fieldToHunspell('dp', self.dp)
        if self.tp: txt += fieldToHunspell('tp', self.tp)
        if self.sp: txt += fieldToHunspell('sp', self.sp)
        if self.pa: txt += fieldToHunspell('pa', self.pa)
        if self.ph: txt += fieldToHunspell('ph', self.ph)
        if nMode > 1:
            if self.lx: txt += fieldToHunspell('lx', self.lx)
            if self.di != '*': txt += ' di:' + self.di
        return txt

    def lexMorph (self):
        # morphology for lexicon
        txt = ' '
        if self.po: txt += self.po + ' '
        if self.iz: txt += self.iz + ' '
        if self.ds: txt += self.ds + ' '
        if self.ts: txt += self.ts + ' '
        if self.ip: txt += self.ip + ' '
        if self.dp: txt += self.dp + ' '
        if self.tp: txt += self.tp + ' '
        if self.sp: txt += self.sp + ' '
        return txt



class StatsLex:
    def __init__ (self, oDict):
        echo("Lexique statistique")
        self.dFlexions = { oFlex.sFlexion: []  for oFlex in oDict.lFlexions }
        self.lLex = []
        
    def addLexFromFile (self, sPathFile, cLexID, sLexName):
        if not os.path.isfile(sPathFile):
            echo(' * Lexique statistique - fichier {} introuvable'.format(sPathFile))
            return None
        if len(cLexID) != 1:
            echo(' * Lexique statistique - fichier {} - identifiant incorrect, 1 caractère requis'.format(sPathFile))
            return None
        echo(" * Lexique statistique << [ {} ]".format(sPathFile))
        nTotKnownOccur = 0
        nTotOccur = 0
        for sLine in readfile(sPathFile):
            sWord, sVal = sLine.rstrip().split()
            n = int(sVal)
            if sWord in self.dFlexions:
                self.dFlexions[sWord].append(n)
                nTotKnownOccur += n
            nTotOccur += n
        self.lLex.append((cLexID, sLexName, nTotKnownOccur, nTotOccur))
        # we fill gaps
        nLex = len(self.lLex)
        for sFlex in self.dFlexions:
            if len(self.dFlexions[sFlex]) < nLex:
                self.dFlexions[sFlex].append(0)

    def getFlexionOccur (self, sFlex):
        return sum(self.dFlexions[sFlex])

    def getInfo (self):
        nKnownTot = 0
        nTot = 0
        s = "Corpus :\n"
        for t in self.lLex:
            s += " * {:<20} -> {:>18,} mots reconnus / {:>18,}\n".format(t[1], t[2], t[3])
            nKnownTot += t[2]
            nTot += t[3]
        s += "\n * {:<20} -> {:>18,} mots reconnus / {:>18,}\n\n".format('TOTAL', nKnownTot, nTot)
        return s

    def write (self, sPathFile):
        with open(sPathFile, 'w', encoding='utf-8', newline="\n") as hDst:
            for t in self.lLex:
                hDst.write(str(t)+"\n")
            for e in self.dFlexions.items():
                hDst.write("{} - {}\n".format(e[0], e[1]))



def main ():

    xParser = argparse.ArgumentParser()
    xParser.add_argument("-v", "--verdic", help="set dictionary version, i.e. 5.4", type=str, default="X.Y.z")
    xParser.add_argument("-m", "--mode", help="0: no tags,  1: Hunspell tags (default),  2: All tags", type=int, choices=[0, 1, 2], default=1)
    xParser.add_argument("-u", "--uncompress", help="do not use Hunspell compression", action="store_true")
    xParser.add_argument("-s", "--simplify", help="no virtual lemmas", action="store_true")
    xParser.add_argument("-sv", "--spellvariants", help="generate spell variants", action="store_true")
    xParser.add_argument("-gl", "--grammalecte", help="copy generated files to Grammalecte folders", action="store_true")
    xArgs = xParser.parse_args()

    if xArgs.simplify:
        xArgs.mode = 0
        xArgs.uncompress = True

    echo("Python: " + sys.version)
    echo("Version: " + xArgs.verdic)
    echo("Simplify: " + str(xArgs.simplify))
    echo("Mode: " + str(xArgs.mode))
    echo("Compression: " + str(not(xArgs.uncompress)))
    
    ### création du répertoire
    spBuild = BUILD_PATH + '/' + xArgs.verdic
    dir_util.mkpath(spBuild)
    
    ### Lecture des fichiers et création du dictionnaire
    oFrenchDict = Dictionnaire(xArgs.verdic, "French dictionary")
    for sFile in ['orthographe/FRANCAIS.dic']:
        oFrenchDict.readDictionary(sFile)
    oFrenchDict.readAffixes('orthographe/FRANCAIS_5.aff')
    
    ### Contrôle
    oFrenchDict.sortEntriesNatural()
    oFrenchDict.checkEntries()
    
    ### Lexique
    oFrenchDict.generateFlexions()
    oFrenchDict.calcMetagraphe()
    oFrenchDict.calcMetaphone2()

    #oFrenchDict.createNgrams(spBuild, 3)
    if xArgs.spellvariants:
        oFrenchDict.generateSpellVariants(1, spBuild)

    ### Statistiques
    spfStats = spBuild+'/'+STATS_NAME+xArgs.verdic+'.txt'
    oStatsLex = StatsLex(oFrenchDict)
    oStatsLex.addLexFromFile('lexique/corpus_data/stats_google_ngram_1.txt', 'G', 'Google 1-grams')
    oStatsLex.addLexFromFile('lexique/corpus_data/stats_frwiki.txt', 'W', 'Wikipédia')
    oStatsLex.addLexFromFile('lexique/corpus_data/stats_frwikisource.txt', 'S', 'Wikisource')
    oStatsLex.addLexFromFile('lexique/corpus_data/stats_litterature.txt', 'L', 'Littérature')
    oStatsLex.write(spBuild+'/test_lex.txt')
    oFrenchDict.calculateStats(oStatsLex, spfStats)
    
    ### écriture des paquets
    echo("Création des paquets...")

    spLexiconDestGL = "../../../lexicons"  if xArgs.grammalecte  else ""
    spLibreOfficeExtDestGL = "../oxt/Dictionnaires/dictionaries"  if xArgs.grammalecte  else ""
    spMozillaExtDestGL = "../xpi/data/dictionaries"  if xArgs.grammalecte  else ""
    spDataDestGL = "../data"  if xArgs.grammalecte  else ""

    if not xArgs.uncompress:
        oFrenchDict.defineAbreviatedTags(xArgs.mode, spfStats)
    oFrenchDict.createFiles(spBuild, [dMODERNE, dTOUTESVAR, dCLASSIQUE, dREFORME1990], xArgs.mode, xArgs.simplify)
    oFrenchDict.createLexiconPackages(spBuild, xArgs.verdic, oStatsLex, spLexiconDestGL)
    oFrenchDict.createFileIfqForDB(spBuild)
    oFrenchDict.createLibreOfficeExtension(spBuild, dMOZEXT, [dMODERNE, dTOUTESVAR, dCLASSIQUE, dREFORME1990], spLibreOfficeExtDestGL)
    oFrenchDict.createMozillaExtensions(spBuild, dMOZEXT, [dMODERNE, dTOUTESVAR, dCLASSIQUE, dREFORME1990], spMozillaExtDestGL)
    oFrenchDict.createDictConj(spBuild, spDataDestGL)
    oFrenchDict.createDictDecl(spBuild, spDataDestGL)



if __name__ == '__main__':
    main()
