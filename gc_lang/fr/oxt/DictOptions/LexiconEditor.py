# Lexicon Editor
# by Olivier R.
# License: GPL 3

import unohelper
import uno
import traceback

import helpers
import lxe_strings
import grammalecte.graphspell as sc

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
        self.xDialog.Height = 300
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
        nY5 = nY4 + 70 # adverbe
        nY6 = nY5 + 15 # autre

        nXB = nX1 + 195
        nXC = nXB + 205

        nHeight = 10

        #### Add word
        self._addWidget("add_section", 'FixedLine', nX1, nY1, 190, nHeight, Label = self.dUI.get("add_section", "#err"), FontDescriptor = xFDTitle)
        #self._addWidget('main_lemma_label', 'FixedText', nX1, nY1+10, 30, nHeight, Label = self.dUI.get('lemma', "#err"))
        self.xLemma = self._addWidget('main_lemma', 'Edit', nX1, nY1+10, 120, nHeight+2)
        
        # Radio buttons: main POS tag
        # Note: the only way to group RadioButtons is to create them successively
        self.xNA = self._addWidget('nom_adj', 'RadioButton', nX1, nY2+12, 60, nHeight, Label = self.dUI.get("nom_adj", "#err"))
        self.xN = self._addWidget('nom', 'RadioButton', nX1, nY2+22, 60, nHeight, Label = self.dUI.get("nom", "#err"))
        self.xA = self._addWidget('adj', 'RadioButton', nX1, nY2+32, 60, nHeight, Label = self.dUI.get("adj", "#err"))
        self.xM1 = self._addWidget('M1', 'RadioButton', nX1, nY3+12, 60, nHeight, Label = self.dUI.get("M1", "#err"))
        self.xM2 = self._addWidget('M2', 'RadioButton', nX1, nY3+22, 60, nHeight, Label = self.dUI.get("M2", "#err"))
        self.xMP = self._addWidget('MP', 'RadioButton', nX1, nY3+32, 60, nHeight, Label = self.dUI.get("MP", "#err"))
        self.xV = self._addWidget('verb', 'RadioButton', nX1, nY4+2, 10, nHeight)
        self.xW = self._addWidget('adv', 'RadioButton', nX1, nY5+2, 10, nHeight)
        self.xX = self._addWidget('other', 'RadioButton', nX1, nY6+2, 10, nHeight)
        
        # Nom, adjectif
        self._addWidget("fl_nom_adj", 'FixedLine', nX1, nY2, 190, nHeight, Label = self.dUI.get("common_name", "#err"), FontDescriptor = xFDSubTitle)
        self.xSepi = self._addWidget('Sepi', 'RadioButton', nX1+65, nY2+12, 50, nHeight, Label = self.dUI.get("epi", "#err"))
        self.xSmas = self._addWidget('Smas', 'RadioButton', nX1+65, nY2+22, 50, nHeight, Label = self.dUI.get("mas", "#err"))
        self.xSfem = self._addWidget('Sfem', 'RadioButton', nX1+65, nY2+32, 50, nHeight, Label = self.dUI.get("fem", "#err"))
        self.xSs = self._addWidget('S-s', 'RadioButton', nX1+120, nY2+12, 50, nHeight, Label = self.dUI.get("-s", "#err"))
        self.xSx = self._addWidget('S-x', 'RadioButton', nX1+120, nY2+22, 50, nHeight, Label = self.dUI.get("-x", "#err"))
        self.xSinv = self._addWidget('Sinv', 'RadioButton', nX1+120, nY2+32, 50, nHeight, Label = self.dUI.get("inv", "#err"))

        self._addWidget("alt_lemma_label", 'FixedLine', nX1+10, nY2+42, 180, nHeight, Label = self.dUI.get("alt_lemma", "#err"))
        self.xAltLemma = self._addWidget('alt_lemma', 'Edit', nX1+10, nY2+52, 120, nHeight)
        self.xNA2 = self._addWidget('nom_adj2', 'RadioButton', nX1+10, nY2+65, 60, nHeight, Label = self.dUI.get("nom_adj", "#err"))
        self.xN2 = self._addWidget('nom2', 'RadioButton', nX1+10, nY2+75, 60, nHeight, Label = self.dUI.get("nom", "#err"))
        self.xA2 = self._addWidget('adj2', 'RadioButton', nX1+10, nY2+85, 60, nHeight, Label = self.dUI.get("adj", "#err"))
        self.xSepi2 = self._addWidget('Sepi2', 'RadioButton', nX1+75, nY2+65, 50, nHeight, Label = self.dUI.get("epi", "#err"))
        self.xSmas2 = self._addWidget('Smas2', 'RadioButton', nX1+75, nY2+75, 50, nHeight, Label = self.dUI.get("mas", "#err"))
        self.xSfem2 = self._addWidget('Sfem2', 'RadioButton', nX1+75, nY2+85, 50, nHeight, Label = self.dUI.get("fem", "#err"))
        self.xSs2 = self._addWidget('S-s2', 'RadioButton', nX1+130, nY2+65, 50, nHeight, Label = self.dUI.get("-s", "#err"))
        self.xSx2 = self._addWidget('S-x2', 'RadioButton', nX1+130, nY2+75, 50, nHeight, Label = self.dUI.get("-x", "#err"))
        self.xSinv2 = self._addWidget('Sinv2', 'RadioButton', nX1+130, nY2+85, 50, nHeight, Label = self.dUI.get("inv", "#err"))

        # Nom propre
        self._addWidget("fl_M", 'FixedLine', nX1, nY3, 190, nHeight, Label = self.dUI.get("proper_name", "#err"), FontDescriptor = xFDSubTitle)
        self.xMepi = self._addWidget('Mepi', 'RadioButton', nX1+65, nY3+12, 50, nHeight, Label = self.dUI.get("epi", "#err"))
        self.xMmas = self._addWidget('Mmas', 'RadioButton', nX1+65, nY3+22, 50, nHeight, Label = self.dUI.get("mas", "#err"))
        self.xMfem = self._addWidget('Mfem', 'RadioButton', nX1+65, nY3+32, 50, nHeight, Label = self.dUI.get("fem", "#err"))

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
        self.xGridModelNew = self._addGrid("list_grid_gwords", nXB, nY1+10, 200, 200, [
            {"Title": self.dUI.get("lex_flex", "#err"), "ColumnWidth": 80},
            {"Title": self.dUI.get("lex_lemma", "#err"), "ColumnWidth": 50},
            {"Title": self.dUI.get("lex_tags", "#err"), "ColumnWidth": 50}
        ])
        self._addWidget("dictionary_section", 'FixedLine', nXB, nY1+210, 200, nHeight, Label = self.dUI.get("dictionary_section", "#err"), FontDescriptor = xFDTitle)

        #### Lexicon section
        self._addWidget("lexicon_section", 'FixedLine', nXC, nY1, 200, nHeight, Label = self.dUI.get("lexicon_section", "#err"), FontDescriptor = xFDTitle)
        self.xGridModelLex = self._addGrid("list_grid_lexicon", nXC, nY1+10, 200, 255, [
            {"Title": self.dUI.get("lex_flex", "#err"), "ColumnWidth": 80},
            {"Title": self.dUI.get("lex_lemma", "#err"), "ColumnWidth": 50},
            {"Title": self.dUI.get("lex_tags", "#err"), "ColumnWidth": 50}
        ])
        
        # Close
        self._addWidget('close_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14, Label = self.dUI.get('close_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControlNew = self.xContainer.getControl('list_grid_gwords')
        self.xGridControlLex = self.xContainer.getControl('list_grid_lexicon')
        #self.xContainer.getControl('add_button').addActionListener(self)
        #self.xContainer.getControl('add_button').setActionCommand('Add')
        #self.xContainer.getControl('delete_button').addActionListener(self)
        #self.xContainer.getControl('delete_button').setActionCommand('Delete')
        #self.xContainer.getControl('save_button').addActionListener(self)
        #self.xContainer.getControl('save_button').setActionCommand('Save')
        self.xContainer.getControl('close_button').addActionListener(self)
        self.xContainer.getControl('close_button').setActionCommand('Close')
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
    @_waitPointer
    def add (self):
        pass

    @_waitPointer
    def loadLexicon (self):
        pass



#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(LexiconEditor, 'net.grammalecte.LexiconEditor', ('com.sun.star.task.Job',))
