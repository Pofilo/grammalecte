# Search
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback
import re

import helpers
import sw_strings
import grammalecte.graphspell as sc
import grammalecte.graphspell.ibdawg as ibdawg

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener


from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
# BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
# DEFAULT_BUTTON_OK, DEFAULT_BUTTON_CANCEL, DEFAULT_BUTTON_RETRY, DEFAULT_BUTTON_YES, DEFAULT_BUTTON_NO, DEFAULT_BUTTON_IGNORE
from com.sun.star.awt.MessageBoxType import INFOBOX, ERRORBOX # MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX

def MessageBox (xDocument, sMsg, sTitle, nBoxType=INFOBOX, nBoxButtons=BUTTONS_OK):
    xParentWin = xDocument.CurrentController.Frame.ContainerWindow
    ctx = uno.getComponentContext()
    xToolkit = ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    xMsgBox = xToolkit.createMessageBox(xParentWin, nBoxType, nBoxButtons, sTitle, sMsg)
    return xMsgBox.execute()


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


class SearchWords (unohelper.Base, XActionListener):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xContainer = None
        self.xDialog = None
        self.oSpellChecker = None
        # options node
        self.xSettingNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Other/", True)

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

    def run (self, sLang, oPersonalDicJSON):
        # ui lang
        self.dUI = sw_strings.getUI(sLang)
        self.oPersonalDicJSON = oPersonalDicJSON

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 350
        self.xDialog.Height = 305
        self.xDialog.Title = self.dUI.get('title', "#title#")
        #xWindowSize = helpers.getWindowSize()
        #self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        #self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

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
        nX2 = nX1 + 130

        nY0 = 5
        nY1 = nY0 + 20
        nY2 = nY1 + 60

        nHeight = 10

        #### Search
        self._addWidget("search_section", 'FixedLine', nX1, nY0, 120, nHeight, Label = self.dUI.get("search_section", "#err"), FontDescriptor = xFDTitle)
        self._addWidget("similar_search_section", 'FixedLine', nX1, nY1, 120, nHeight, Label = self.dUI.get("similar_search_section", "#err"), FontDescriptor = xFDSubTitle)
        self.xWord = self._addWidget('word', 'Edit', nX1, nY1+10, 100, nHeight)
        self._addWidget('similar_search_button', 'Button', nX1, nY1+22, 55, 12, Label = self.dUI.get('similar_search_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x005500)


        self._addWidget("regex_search_section", 'FixedLine', nX1, nY2, 120, nHeight, Label = self.dUI.get("regex_search_section", "#err"), FontDescriptor = xFDSubTitle)
        self._addWidget('flexion_label', 'FixedText', nX1, nY2+10, 30, nHeight, Label = self.dUI.get('flexion', "#err"))
        self.xFlexion = self._addWidget('flexion', 'Edit', nX1+35, nY2+10, 85, nHeight)
        self._addWidget('tags_label', 'FixedText', nX1, nY2+22, 30, nHeight, Label = self.dUI.get('tags', "#err"))
        self.xTags = self._addWidget('tags', 'Edit', nX1+35, nY2+22, 85, nHeight)
        self._addWidget('regex_search_button', 'Button', nX1, nY2+34, 55, 12, Label = self.dUI.get('regex_search_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x005500)
        self._addWidget('result_warning', 'FixedText', nX1, nY2+50, 120, nHeight*7, Label = self.dUI.get('result_warning', '#err'), MultiLine = True)

        #### Results
        self._addWidget("result_section", 'FixedLine', nX2, nY0, 200, nHeight, Label = self.dUI.get("result_section", "#err"), FontDescriptor = xFDTitle)
        self.xGridModel = self._addGrid("list_grid_search", nX2, nY0+10, 200, 265, [
            {"Title": self.dUI.get("res_flexion", "#err"), "ColumnWidth": 70},
            {"Title": self.dUI.get("res_lemma", "#err"), "ColumnWidth": 60},
            {"Title": self.dUI.get("res_tags", "#err"), "ColumnWidth": 70}
        ])

        self._addWidget('close_button', 'Button', self.xDialog.Width-50, self.xDialog.Height-20, 40, 12, Label = self.dUI.get('close_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x550000)

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControlSearch = self.xContainer.getControl('list_grid_search')
        self.xGridControlInfo = self.xContainer.getControl('list_grid_info')
        self.xContainer.getControl('similar_search_button').addActionListener(self)
        self.xContainer.getControl('similar_search_button').setActionCommand('SearchSimilar')
        self.xContainer.getControl('regex_search_button').addActionListener(self)
        self.xContainer.getControl('regex_search_button').setActionCommand('SearchRegex')
        self.xContainer.getControl('close_button').addActionListener(self)
        self.xContainer.getControl('close_button').setActionCommand('Close')
        self.xContainer.setVisible(False)
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == "SearchSimilar":
                self.searchSimilar()
            elif xActionEvent.ActionCommand == "SearchRegex":
                self.searchRegex()
            elif xActionEvent.ActionCommand == "Close":
                self.xContainer.endExecute()
        except:
            traceback.print_exc()

    def initSpellChecker (self):
        if not self.oSpellChecker:
            self.oSpellChecker = sc.SpellChecker("fr", "fr-allvars.bdic", "", self.oPersonalDicJSON)

    @_waitPointer
    def searchSimilar (self):
        self.initSpellChecker()
        sWord = self.xWord.Text.strip()
        if sWord:
            xGridDataModel = self.xGridModel.GridDataModel
            xGridDataModel.removeAllRows()
            lResult = self.oSpellChecker.getSimilarEntries(sWord, 20);
            for i, aEntry in enumerate(lResult):
                xGridDataModel.addRow(i, aEntry)

    @_waitPointer
    def searchRegex (self):
        self.initSpellChecker()
        sFlexPattern = self.xFlexion.Text.strip()
        sTagsPattern = self.xTags.Text.strip()
        try:
            if sFlexPattern:
                re.compile(sFlexPattern)
        except:
            MessageBox(self.xDocument, self.dUI.get("regex_error_flexion", "#err"), self.dUI.get("error", "#err"), nBoxType=ERRORBOX)
            sFlexPattern = ""
        try:
            if sTagsPattern:
                re.compile(sTagsPattern)
        except:
            MessageBox(self.xDocument, self.dUI.get("regex_error_tags", "#err"), self.dUI.get("error", "#err"), nBoxType=ERRORBOX)
            sTagsPattern = ""
        xGridDataModel = self.xGridModel.GridDataModel
        xGridDataModel.removeAllRows()
        for i, aEntry in enumerate(self.oSpellChecker.select(sFlexPattern, sTagsPattern)):
            xGridDataModel.addRow(i, aEntry)
            i += 1
            if i >= 2000:
                break
