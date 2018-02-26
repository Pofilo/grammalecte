# Lexicon Editor
# by Olivier R.
# License: GPL 3

import unohelper
import uno
import re
import traceback

import helpers
import lxe_strings
import lxe_conj_data
import grammalecte.graphspell as sc
import grammalecte.fr.conj as conj

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener


def _waitPointer (funcDecorated):
    def wrapper (*args, **kwargs):
        # self is the first parameter if the decorator is applied on a object
        self = args[0]
        # before
        xPointer = self.xSvMgr.createInstanceWithContext("com.sun.star.awt.Pointer", self.ctx)
        xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.WAIT"))
        xWindowPeer = self.xContainer.getPeer()
        xWindowPeer.setPointer(xPointer)
        for x in xWindowPeer.Windows:
            x.setPointer(xPointer)
        # processing
        result = funcDecorated(*args, **kwargs)
        # after
        xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.ARROW"))
        xWindowPeer.setPointer(xPointer)
        for x in xWindowPeer.Windows:
            x.setPointer(xPointer)
        self.xContainer.setVisible(True) # seems necessary to refresh the dialog box and text widgets (why?)
        # return
        return result
    return wrapper


class LexiconEditor (unohelper.Base, XActionListener, XJobExecutor):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xContainer = None
        self.xDialog = None
        self.oSpellChecker = None
        # data
        self.lGeneratedFlex = []

    def _addWidget (self, name, wtype, x, y, w, h, **kwargs):
        xWidget = self.xDialog.createInstance('com.sun.star.awt.UnoControl%sModel' % wtype)
        xWidget.Name = name
        xWidget.PositionX = x
        xWidget.PositionY = y
        xWidget.Width = w
        xWidget.Height = h
        for k, w in kwargs.items():
            setattr(xWidget, k, w)
        self.xDialog.insertByName(name, xWidget)
        return xWidget

    def _addGrid (self, name, x, y, w, h, columns, **kwargs):
        xGridModel = self.xDialog.createInstance('com.sun.star.awt.grid.UnoControlGridModel')
        xGridModel.Name = name
        xGridModel.PositionX = x
        xGridModel.PositionY = y
        xGridModel.Width = w
        xGridModel.Height = h
        xColumnModel = xGridModel.ColumnModel
        for e in columns:
            xCol = xColumnModel.createColumn()
            for k, w in e.items():
                setattr(xCol, k, w)
            xColumnModel.addColumn(xCol)
        for k, w in kwargs.items():
            setattr(xGridModel, k, w)
        self.xDialog.insertByName(name, xGridModel)
        return xGridModel

    def run (self, sLang):
        self.dUI = lxe_strings.getUI(sLang)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 620
        self.xDialog.Height = 292
        self.xDialog.Title = self.dUI.get('title', "#title#")
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        # fonts
        xFDTitle = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDTitle.Height = 9
        xFDTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDTitle.Name = "Verdana"
        
        xFDSubTitle = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDSubTitle.Height = 8
        xFDSubTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDSubTitle.Name = "Verdana"

        # widget
        nX1 = 10
        nX2 = 20

        nY1 = 5
        nY2 = nY1 + 25 # nom commun
        nY3 = nY2 + 95 # nom propre
        nY4 = nY3 + 45 # verbe
        nY5 = nY4 + 68 # adverbe
        nY6 = nY5 + 13 # autre

        nXB = nX1 + 195
        nXC = nXB + 205

        nHeight = 10

        #### Add word
        self._addWidget("add_section", 'FixedLine', nX1, nY1, 190, nHeight, Label = self.dUI.get("add_section", "#err"), FontDescriptor = xFDTitle)
        #self._addWidget('main_lemma_label', 'FixedText', nX1, nY1+10, 30, nHeight, Label = self.dUI.get('lemma', "#err"))
        self.xLemma = self._addWidget('main_lemma', 'Edit', nX1, nY1+10, 120, 14, FontDescriptor = xFDTitle)
        self._addWidget('generate_button', 'Button', nX1+130, nY1+10, 60, 14, Label = self.dUI.get('generate_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        # Radio buttons: main POS tag
        # Note: the only way to group RadioButtons is to create them successively
        self.xNA = self._addWidget('nom_adj', 'RadioButton', nX1, nY2+12, 60, nHeight, Label = self.dUI.get("nom_adj", "#err"), HelpText = ":N:A")
        self.xN = self._addWidget('nom', 'RadioButton', nX1, nY2+22, 60, nHeight, Label = self.dUI.get("nom", "#err"), HelpText = ":N")
        self.xA = self._addWidget('adj', 'RadioButton', nX1, nY2+32, 60, nHeight, Label = self.dUI.get("adj", "#err"), HelpText = ":A")
        self.xM1 = self._addWidget('M1', 'RadioButton', nX1, nY3+12, 60, nHeight, Label = self.dUI.get("M1", "#err"), HelpText = ":M1")
        self.xM2 = self._addWidget('M2', 'RadioButton', nX1, nY3+22, 60, nHeight, Label = self.dUI.get("M2", "#err"), HelpText = ":M2")
        self.xMP = self._addWidget('MP', 'RadioButton', nX1, nY3+32, 60, nHeight, Label = self.dUI.get("MP", "#err"), HelpText = ":MP")
        self.xV = self._addWidget('verb', 'RadioButton', nX1, nY4+2, 10, nHeight, HelpText = ":V")
        self.xW = self._addWidget('adv', 'RadioButton', nX1, nY5+2, 10, nHeight, HelpText = ":W")
        self.xX = self._addWidget('other', 'RadioButton', nX1, nY6+2, 10, nHeight, HelpText = ":X")
        
        # Nom, adjectif
        self._addWidget("fl_nom_adj", 'FixedLine', nX1, nY2, 190, nHeight, Label = self.dUI.get("common_name", "#err"), FontDescriptor = xFDSubTitle)
        self.xSepi = self._addWidget('Sepi', 'RadioButton', nX1+65, nY2+12, 50, nHeight, Label = self.dUI.get("epi", "#err"), HelpText = ":e")
        self.xSmas = self._addWidget('Smas', 'RadioButton', nX1+65, nY2+22, 50, nHeight, Label = self.dUI.get("mas", "#err"), HelpText = ":m")
        self.xSfem = self._addWidget('Sfem', 'RadioButton', nX1+65, nY2+32, 50, nHeight, Label = self.dUI.get("fem", "#err"), HelpText = ":f")
        self._addWidget("fl_sep1", 'FixedLine', nX1, nY2, 1, nHeight)
        self.xSs = self._addWidget('S-s', 'RadioButton', nX1+120, nY2+12, 50, nHeight, Label = self.dUI.get("-s", "#err"), HelpText = "·s")
        self.xSx = self._addWidget('S-x', 'RadioButton', nX1+120, nY2+22, 50, nHeight, Label = self.dUI.get("-x", "#err"), HelpText = "·x")
        self.xSinv = self._addWidget('Sinv', 'RadioButton', nX1+120, nY2+32, 50, nHeight, Label = self.dUI.get("inv", "#err"), HelpText = ":i")

        self._addWidget("alt_lemma_label", 'FixedLine', nX1+10, nY2+42, 180, nHeight, Label = self.dUI.get("alt_lemma", "#err"))
        self.xAltLemma = self._addWidget('alt_lemma', 'Edit', nX1+10, nY2+52, 120, nHeight)
        self.xNA2 = self._addWidget('nom_adj2', 'RadioButton', nX1+10, nY2+65, 60, nHeight, Label = self.dUI.get("nom_adj", "#err"), HelpText = ":N:A")
        self.xN2 = self._addWidget('nom2', 'RadioButton', nX1+10, nY2+75, 60, nHeight, Label = self.dUI.get("nom", "#err"), HelpText = ":N")
        self.xA2 = self._addWidget('adj2', 'RadioButton', nX1+10, nY2+85, 60, nHeight, Label = self.dUI.get("adj", "#err"), HelpText = ":A")
        self._addWidget("fl_sep2", 'FixedLine', nX1, nY2, 1, nHeight)
        self.xSepi2 = self._addWidget('Sepi2', 'RadioButton', nX1+75, nY2+65, 50, nHeight, Label = self.dUI.get("epi", "#err"), HelpText = ":e")
        self.xSmas2 = self._addWidget('Smas2', 'RadioButton', nX1+75, nY2+75, 50, nHeight, Label = self.dUI.get("mas", "#err"), HelpText = ":m")
        self.xSfem2 = self._addWidget('Sfem2', 'RadioButton', nX1+75, nY2+85, 50, nHeight, Label = self.dUI.get("fem", "#err"), HelpText = ":f")
        self._addWidget("fl_sep3", 'FixedLine', nX1, nY2, 1, nHeight)
        self.xSs2 = self._addWidget('S-s2', 'RadioButton', nX1+130, nY2+65, 50, nHeight, Label = self.dUI.get("-s", "#err"), HelpText = "·s")
        self.xSx2 = self._addWidget('S-x2', 'RadioButton', nX1+130, nY2+75, 50, nHeight, Label = self.dUI.get("-x", "#err"), HelpText = "·x")
        self.xSinv2 = self._addWidget('Sinv2', 'RadioButton', nX1+130, nY2+85, 50, nHeight, Label = self.dUI.get("inv", "#err"), HelpText = ":i")

        # Nom propre
        self._addWidget("fl_M", 'FixedLine', nX1, nY3, 190, nHeight, Label = self.dUI.get("proper_name", "#err"), FontDescriptor = xFDSubTitle)
        self.xMepi = self._addWidget('Mepi', 'RadioButton', nX1+65, nY3+12, 50, nHeight, Label = self.dUI.get("epi", "#err"), HelpText = ":e")
        self.xMmas = self._addWidget('Mmas', 'RadioButton', nX1+65, nY3+22, 50, nHeight, Label = self.dUI.get("mas", "#err"), HelpText = ":m")
        self.xMfem = self._addWidget('Mfem', 'RadioButton', nX1+65, nY3+32, 50, nHeight, Label = self.dUI.get("fem", "#err"), HelpText = ":f")

        # Verbe
        self._addWidget("fl_verb", 'FixedLine', nX2, nY4, 180, nHeight, Label = self.dUI.get("verb", "#err"), FontDescriptor = xFDSubTitle)
        self.xV_i = self._addWidget('v_i', 'CheckBox', nX2, nY4+12, 60, nHeight, Label = self.dUI.get("v_i", "#err"))
        self.xV_t = self._addWidget('v_t', 'CheckBox', nX2, nY4+20, 60, nHeight, Label = self.dUI.get("v_t", "#err"))
        self.xV_n = self._addWidget('v_n', 'CheckBox', nX2, nY4+28, 60, nHeight, Label = self.dUI.get("v_n", "#err"))
        self.xV_p = self._addWidget('v_p', 'CheckBox', nX2, nY4+36, 60, nHeight, Label = self.dUI.get("v_p", "#err"))
        self.xV_m = self._addWidget('v_m', 'CheckBox', nX2, nY4+44, 60, nHeight, Label = self.dUI.get("v_m", "#err"))

        self._addWidget('aux', 'FixedText', nX2+75, nY4+10, 90, nHeight, Label = self.dUI.get("aux", "#err"))
        self.xV_ae = self._addWidget('v_ae', 'CheckBox', nX2+75, nY4+20, 90, nHeight, Label = self.dUI.get("v_ae", "#err"))
        self.xV_aa = self._addWidget('v_aa', 'CheckBox', nX2+75, nY4+28, 90, nHeight, Label = self.dUI.get("v_aa", "#err"))

        self.xV_pp = self._addWidget('v_pp', 'CheckBox', nX2+75, nY4+44, 90, nHeight, Label = self.dUI.get("v_pp", "#err"))

        self._addWidget('v_pattern_label', 'FixedText', nX2+10, nY4+56, 70, nHeight, Label = self.dUI.get('v_pattern', "#err"), Align = 2)
        self.xVpattern = self._addWidget('v_pattern', 'Edit', nX2+85, nY4+56, 80, nHeight)

        # Adverbe
        self._addWidget("fl_adv", 'FixedLine', nX2, nY5, 180, nHeight, Label = self.dUI.get("adverb", "#err"), FontDescriptor = xFDSubTitle)

        # Autre
        self._addWidget("fl_other", 'FixedLine', nX2, nY6, 180, nHeight, Label = self.dUI.get("other", "#err"), FontDescriptor = xFDSubTitle)
        self._addWidget('flexion_label', 'FixedText', nX2, nY6+10, 85, nHeight, Label = self.dUI.get('flexion', "#err"))
        self.xFlexion = self._addWidget('flexion', 'Edit', nX2, nY6+20, 85, nHeight)
        self._addWidget('tags_label', 'FixedText', nX2+90, nY6+10, 85, nHeight, Label = self.dUI.get('tags', "#err"))
        self.xTags = self._addWidget('tags', 'Edit', nX2+90, nY6+20, 85, nHeight)

        #### Generated words
        self._addWidget("gwords_section", 'FixedLine', nXB, nY1, 200, nHeight, Label = self.dUI.get("new_section", "#err"), FontDescriptor = xFDTitle)
        self.xGridModelNew = self._addGrid("list_grid_gwords", nXB, nY1+10, 200, 175, [
            {"Title": self.dUI.get("lex_flex", "#err"), "ColumnWidth": 65},
            {"Title": self.dUI.get("lex_lemma", "#err"), "ColumnWidth": 50},
            {"Title": self.dUI.get("lex_tags", "#err"), "ColumnWidth": 65}
        ])
        self.xAdd = self._addWidget('add_button', 'Button', nXB, nY1+190, 95, 12, Label = self.dUI.get('add_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x005500, Enabled = False)
        self.xDelete = self._addWidget('delete_button', 'Button', nXB+100, nY1+190, 100, 12, Label = self.dUI.get('delete_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        nY2b = nY1 + 205
        # lexicon info section
        self._addWidget("lexicon_info_section", 'FixedLine', nXB, nY2b, 200, nHeight, Label = self.dUI.get("lexicon_info_section", "#err"), FontDescriptor = xFDTitle)
        self._addWidget("added_entries_label", 'FixedText', nXB, nY2b+10, 90, nHeight, Label = self.dUI.get("added_entries_label", "#err"))
        self._addWidget("deleted_entries_label", 'FixedText', nXB, nY2b+20, 90, nHeight, Label = self.dUI.get("deleted_entries_label", "#err"))
        self._addWidget("num_of_entries_label1", 'FixedText', nXB, nY2b+30, 90, nHeight, Label = self.dUI.get("num_of_entries_label", "#err"))
        self.xSave = self._addWidget('save_button', 'Button', nXB+150, nY2b+10, 50, 12, Label = self.dUI.get('save_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x005500)
        # dictionary section
        self._addWidget("dictionary_section", 'FixedLine', nXB, nY2b+45, 200, nHeight, Label = self.dUI.get("dictionary_section", "#err"), FontDescriptor = xFDTitle)
        self._addWidget("save_date_label", 'FixedText', nXB, nY2b+55, 90, nHeight, Label = self.dUI.get("save_date_label", "#err"))
        self._addWidget("num_of_entries_label2", 'FixedText', nXB, nY2b+65, 90, nHeight, Label = self.dUI.get("num_of_entries_label", "#err"))
        self.xExport = self._addWidget('export_button', 'Button', nXB+150, nY2b+55, 50, 12, Label = self.dUI.get('export_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x005500)

        #### Lexicon section
        self._addWidget("lexicon_section", 'FixedLine', nXC, nY1, 200, nHeight, Label = self.dUI.get("lexicon_section", "#err"), FontDescriptor = xFDTitle)
        self.xGridModelLex = self._addGrid("list_grid_lexicon", nXC, nY1+10, 200, 270, [
            {"Title": self.dUI.get("lex_flex", "#err"), "ColumnWidth": 65},
            {"Title": self.dUI.get("lex_lemma", "#err"), "ColumnWidth": 50},
            {"Title": self.dUI.get("lex_tags", "#err"), "ColumnWidth": 65}
        ])

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControlNew = self.xContainer.getControl('list_grid_gwords')
        self.xGridControlLex = self.xContainer.getControl('list_grid_lexicon')
        self.xContainer.getControl('add_button').addActionListener(self)
        self.xContainer.getControl('add_button').setActionCommand('Add')
        self.xContainer.getControl('delete_button').addActionListener(self)
        self.xContainer.getControl('delete_button').setActionCommand('Delete')
        self.xContainer.getControl('save_button').addActionListener(self)
        self.xContainer.getControl('save_button').setActionCommand('Save')
        self.xContainer.getControl('generate_button').addActionListener(self)
        self.xContainer.getControl('generate_button').setActionCommand('Update')
        self.xContainer.setVisible(False)
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == "Add":
                pass
            elif xActionEvent.ActionCommand == "Delete":
                pass
            elif xActionEvent.ActionCommand == "Save":
                pass
            elif xActionEvent.ActionCommand == "Update":
                self.updateGenWords()
            elif xActionEvent.ActionCommand == "Close":
                self.xContainer.endExecute()
        except:
            traceback.print_exc()
    
    # XJobExecutor
    def trigger (self, args):
        try:
            xDialog = LexiconEditor(self.ctx)
            xDialog.run()
        except:
            traceback.print_exc()

    # Code
    def getRadioValue (self, *args):
        for x in args:
            if x.State:
                return x.HelpText
        return None

    def updateGenWords (self):
        self.lGeneratedFlex = []
        sLemma = self.xLemma.Text.strip()
        if sLemma:
            if self.getRadioValue(self.xNA, self.xN, self.xA):
                # Substantif
                sPOS = self.getRadioValue(self.xNA, self.xN, self.xA)
                sGenderTag = self.getRadioValue(self.xSepi, self.xSmas, self.xSfem)
                if sGenderTag:
                    if self.xSs.State:
                        self.lGeneratedFlex.append((sLemma, sLemma, sPOS+sGenderTag+":s/*"))
                        self.lGeneratedFlex.append((sLemma+"s", sLemma, sPOS+sGenderTag+":p/*"))
                    elif self.xSx.State:
                        self.lGeneratedFlex.append((sLemma, sLemma, sPOS+sGenderTag+":s/*"))
                        self.lGeneratedFlex.append((sLemma+"x", sLemma, sPOS+sGenderTag+":p/*"))
                    elif self.xSinv.State:
                        self.lGeneratedFlex.append((sLemma, sLemma, sPOS+sGenderTag+":i/*"))
                    sLemma2 = self.xAltLemma.Text.strip()
                    if sLemma2 and self.getRadioValue(self.xNA2, self.xN2, self.xA2) and self.getRadioValue(self.xSepi2, self.xSmas2, self.xSfem2):
                        sTag2 = self.getRadioValue(self.xNA2, self.xN2, self.xA2) + self.getRadioValue(self.xSepi2, self.xSmas2, self.xSfem2)
                        if self.xSs2.State:
                            self.lGeneratedFlex.append((sLemma2, sLemma, sTag2+":s/*"))
                            self.lGeneratedFlex.append((sLemma2+"s", sLemma, sTag2+":p/*"))
                        elif self.xSx2.State:
                            self.lGeneratedFlex.append((sLemma2, sLemma, sTag2+":s/*"))
                            self.lGeneratedFlex.append((sLemma2+"x", sLemma, sTag2+":p/*"))
                        elif self.xSinv2.State:
                            self.lGeneratedFlex.append((sLemma2, sLemma, sTag2+":i/*"))
            elif self.getRadioValue(self.xM1, self.xM2, self.xMP):
                # Nom propre
                sPOS = self.getRadioValue(self.xM1, self.xM2, self.xMP)
                sLemma = sLemma[0:1].upper() + sLemma[1:];
                sGenderTag = self.getRadioValue(self.xMepi, self.xMmas, self.xMfem)
                if sGenderTag:
                    self.lGeneratedFlex.append((sLemma, sLemma, sPOS+sGenderTag+":i/*"))
            elif self.xV.State:
                # Verbe
                if sLemma.endswith(("er", "ir", "re")):
                    sLemma = sLemma.lower()
                    c_i = "i"  if self.xV_i.State  else "_"
                    c_t = "t"  if self.xV_t.State  else "_"
                    c_n = "n"  if self.xV_n.State  else "_"
                    c_p = "p"  if self.xV_p.State  else "_"
                    c_m = "m"  if self.xV_m.State  else "_"
                    c_ae = "e"  if self.xV_ae.State  else "_"
                    c_aa = "a"  if self.xV_aa.State  else "_"
                    sVerbTag = c_i + c_t + c_n + c_p + c_m + c_ae + c_aa
                    if not sVerbTag.endswith("__") and not sVerbTag.startswith("____"):
                        sVerbPattern = self.xVpattern.Text.strip()
                        if not sVerbPattern:
                            if sLemma.endswith("er") or sLemma.endswith("ir"):
                                # tables de conjugaison du 1er et du 2e groupe
                                cGroup = "1"  if sLemma.endswith("er")  else "2"
                                for nCut, sAdd, sFlexTags, sPattern in self._getConjRules(sLemma):
                                    if not sPattern or re.search(sPattern, sLemma):
                                        self.lGeneratedFlex.append((sLemma[0:-nCut]+sAdd, sLemma, ":V" + cGroup + "_" + sVerbTag + sFlexTags))
                                # participes passés
                                bPpasVar = "var"  if self.xV_pp.State  else "invar"
                                lPpasRules = lxe_conj_data.oConj["V1_ppas"][bPpasVar]  if sLemma.endswith("er")  else lxe_conj_data.oConj["V2_ppas"][bPpasVar]
                                for nCut, sAdd, sFlexTags, sPattern in lPpasRules:
                                    if not sPattern or re.search(sPattern, sLemma):
                                        self.lGeneratedFlex.append((sLemma[0:-nCut]+sAdd, sLemma, ":V" + cGroup + "_" + sVerbTag + sFlexTags))
                        else:
                            # copie du motif d’un autre verbe : utilisation du conjugueur
                            if conj.isVerb(sVerbPattern):
                                oVerb = conj.Verb(sLemma, sVerbPattern)
                                for sTag1, dFlex in oVerb.dConj.items():
                                    if sTag1 != ":Q":
                                        for sTag2, sConj in dFlex.items():
                                            if sTag2.startswith(":") and sConj:
                                                self.lGeneratedFlex.append((sConj, sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + sTag1 + sTag2))
                                    else:
                                        # participes passés
                                        if dFlex[":Q3"]:
                                            if dFlex[":Q2"]:
                                                self.lGeneratedFlex.append((dFlex[":Q1"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:s/*"))
                                                self.lGeneratedFlex.append((dFlex[":Q2"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:p/*"))
                                            else:
                                                self.lGeneratedFlex.append((dFlex[":Q1"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:i/*"))
                                            self.lGeneratedFlex.append((dFlex[":Q3"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:s/*"))
                                            self.lGeneratedFlex.append((dFlex[":Q4"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:p/*"))
                                        else:
                                            self.lGeneratedFlex.append((dFlex[":Q1"], sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:e:i/*"))
            elif self.xW.State:
                # Adverbe
                sLemma = sLemma.lower();
                self.lGeneratedFlex.append((sLemma, sLemma, ":W/*"))
            elif self.xX.State:
                # Autre
                sFlexion = self.xFlexion.Text.strip()
                sTags = self.xTags.Text.strip()
                if sFlexion and sTags.startswith(":"):
                    self.lGeneratedFlex.append((sFlexion, sLemma, sTags))
        self.showGenWords()

    def _getConjRules (self, sVerb):
        if sVerb.endswith("ir"):
            # deuxième groupe
            return lxe_conj_data.oConj["V2"]
        elif sVerb.endswith("er"):
            # premier groupe, conjugaison en fonction de la terminaison du lemme
            # 5 lettres
            if sVerb[-5:] in lxe_conj_data.oConj["V1"]:
                return lxe_conj_data.oConj["V1"][sVerb[-5:]]
            # 4 lettres
            if sVerb[-4:] in lxe_conj_data.oConj["V1"]:
                if sVerb.endswith(("eler", "eter")):
                    return lxe_conj_data.oConj["V1"][sVerb[-4:]]["1"]
                return lxe_conj_data.oConj["V1"][sVerb[-4:]]
            # 3 lettres
            if sVerb[-3:] in lxe_conj_data.oConj["V1"]:
                return lxe_conj_data.oConj["V1"][sVerb[-3:]]
            return lxe_conj_data.oConj["V1"]["er"]
        else:
            # troisième groupe
            return [ [0, "", ":Y/*", false] ]

    def showGenWords (self):
        xGridDataModel = self.xGridModelNew.GridDataModel
        xGridDataModel.removeAllRows()
        if not self.lGeneratedFlex:
            self.xAdd.Enabled = False
            return
        for i, (sFlexion, sLemma, sTag) in enumerate(self.lGeneratedFlex):
            xGridDataModel.addRow(i, (sFlexion, sLemma, sTag))
        self.xAdd.Enabled = True

    @_waitPointer
    def add (self):
        pass

    @_waitPointer
    def delete (self):
        pass

    @_waitPointer
    def loadLexicon (self):
        pass

    @_waitPointer
    def saveLexicon (self):
        pass    


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(LexiconEditor, 'net.grammalecte.LexiconEditor', ('com.sun.star.task.Job',))


# const oFlexGen = {

#     cMainTag: "",

#     lFlexion: [],

#     clear: function () {
#         this.lFlexion = [];
#         oWidgets.hideElement("actions");
#     },

#     addToLexicon: function () {
#         try {
#             oLexicon.addFlexions(this.lFlexion);
#             document.getElementById("lemma").value = "";
#             document.getElementById("lemma").focus();
#             oWidgets.showSection("section_vide");
#             oWidgets.hideElement("editor");
#             oWidgets.hideElement("actions");
#             oWidgets.clear();
#             oWidgets.showElement("save_button");
#             this.clear();
#             this.cMainTag = "";
#         }
#         catch (e) {
#             showError(e);
#         }
#     }
# }