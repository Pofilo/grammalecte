# Lexicon editor: Information
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback

import helpers
import ti_strings

import grammalecte.fr.lexicographe as lxg

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener



class TagsInfo (unohelper.Base, XActionListener):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xContainer = None
        self.xDialog = None

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
        # ui lang
        self.dUI = ti_strings.getUI(sLang)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 360
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
        nX2 = 20
        nX3 = 120

        nY0 = 5
        nY1 = nY0 + 13
        nY2 = nY1 + 60
        nY3 = nY2 + 60
        nY4 = nY3 + 80

        nXB = nX1 + 110

        nHeight = 10

        #### Add word
        self._addWidget("add_section", 'FixedLine', nX1, nY0, 100, nHeight, Label = self.dUI.get("information_section", "#err"), FontDescriptor = xFDTitle)
        
        self._addWidget('save_label', 'FixedText', nX1, nY1, 100, nHeight, Label = self.dUI.get('save', "#err"), FontDescriptor = xFDTitle)
        self._addWidget('save_desc_label', 'FixedText', nX1, nY1+10, 100, nHeight*5, Label = self.dUI.get('save_desc', "#err"), MultiLine=True)
        
        self._addWidget('duplicates_label', 'FixedText', nX1, nY2, 100, nHeight, Label = self.dUI.get('duplicates', "#err"), FontDescriptor = xFDTitle)
        self._addWidget('duplicates_desc_label', 'FixedText', nX1, nY2+10, 100, nHeight*5, Label = self.dUI.get('duplicates_desc', "#err"), MultiLine=True)

        self._addWidget('compilation_label', 'FixedText', nX1, nY3, 100, nHeight, Label = self.dUI.get('compilation', "#err"), FontDescriptor = xFDTitle)
        self._addWidget('compilation_desc_label', 'FixedText', nX1, nY3+10, 100, nHeight*7, Label = self.dUI.get('compilation_desc', "#err"), MultiLine=True)
        
        self._addWidget('warning_label', 'FixedText', nX1, nY4, 100, nHeight, Label = self.dUI.get('warning', "#err"), FontDescriptor = xFDTitle)
        self._addWidget('warning_desc_label', 'FixedText', nX1, nY4+10, 100, nHeight*7, Label = self.dUI.get('warning_desc', "#err"), MultiLine=True)

        #### Tags
        self._addWidget("tags_section", 'FixedLine', nXB, nY0, 230, nHeight, Label = self.dUI.get("tags_section", "#err"), FontDescriptor = xFDTitle)
        self.xGridModel = self._addGrid("list_grid_tags", nXB, nY0+10, 230, 265, [
            {"Title": self.dUI.get("tags", "#err"), "ColumnWidth": 40},
            {"Title": self.dUI.get("meaning", "#err"), "ColumnWidth": 190}
        ])

        self._addWidget('close_button', 'Button', self.xDialog.Width-50, self.xDialog.Height-20, 40, 12, Label = self.dUI.get('close_button', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x550000)

        self.loadData()

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControlInfo = self.xContainer.getControl('list_grid_tags')
        self.xContainer.getControl('close_button').addActionListener(self)
        self.xContainer.getControl('close_button').setActionCommand('Close')
        self.xContainer.setVisible(False)
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == "Close":
                self.xContainer.endExecute()
        except:
            traceback.print_exc()

    def loadData (self):
        xGridDataModel = self.xGridModel.GridDataModel
        for i, sKey in enumerate(lxg._dTAGS):
            xGridDataModel.addRow(i, [sKey, lxg._dTAGS[sKey][1]])
