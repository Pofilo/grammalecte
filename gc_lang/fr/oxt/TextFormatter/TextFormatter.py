"""
Text Formatter
For LibreOffice
"""

# License: MPL 2

import traceback
import time
import json

import tf_strings as ui
import tf_options
import tf_tabrep
import helpers

import TextFormatterEditor

import unohelper
import uno
from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener

from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
# BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
# DEFAULT_BUTTON_OK, DEFAULT_BUTTON_CANCEL, DEFAULT_BUTTON_RETRY, DEFAULT_BUTTON_YES, DEFAULT_BUTTON_NO, DEFAULT_BUTTON_IGNORE
from com.sun.star.awt.MessageBoxType import INFOBOX # MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX


def MessageBox (xParentWin, sMsg, sTitle, nBoxType=INFOBOX, nBoxButtons=BUTTONS_OK):
    ctx = uno.getComponentContext()
    xToolkit = ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    xMsgBox = xToolkit.createMessageBox(xParentWin, nBoxType, nBoxButtons, sTitle, sMsg)
    return xMsgBox.execute()


class TextFormatter (unohelper.Base, XActionListener, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None
        self.xDialog = None

    # XJobExecutor
    def trigger (self, args):
        try:
            xTF = TextFormatter(self.ctx)
            xTF.run()
        except:
            traceback.print_exc()

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

    def run (self, sLang):
        self.sLang = sLang

        ui.selectLang(sLang)

        ## dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 310
        self.xDialog.Title = ui.get('title')

        ## fonts
        xFD1 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD1.Height = 12
        xFD1.Name = "Verdana"

        xFD2 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD2.Height = 10
        xFD2.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFD2.Name = "Verdana"

        xFDsmall = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDsmall.Height = 6
        xFDsmall.Name = "Verdana"

        ## widgets position
        x = 10
        x2 = 160
        nRightLimit1 = 150
        nRightLimit2 = 300
        nWidth = 140
        nWidthHalf = (nWidth // 2) - 10
        nHeight = 10
        nColor = 0xAA2200

        # close or apply
        self.bClose = False

        # group box // surnumerary spaces
        y = 10
        nPosRes = nRightLimit1 - 20
        self.ssp = self._addWidget('ssp', 'CheckBox', x, y+2, nWidth, nHeight, Label = ui.get('ssp'), FontDescriptor = xFD1, \
                                   FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section1", 'FixedLine', nRightLimit1-(nWidth//5), y, nWidth//5, nHeight)
        self.ssp1 = self._addWidget('ssp1', 'CheckBox', x, y+15, nWidth, nHeight, Label = ui.get('ssp1'), State = True)
        self.ssp2 = self._addWidget('ssp2', 'CheckBox', x, y+25, nWidth, nHeight, Label = ui.get('ssp2'), State = True)
        self.ssp3 = self._addWidget('ssp3', 'CheckBox', x, y+35, nWidth, nHeight, Label = ui.get('ssp3'), State = True)
        self.ssp4 = self._addWidget('ssp4', 'CheckBox', x, y+45, nWidth, nHeight, Label = ui.get('ssp4'), State = True)
        self.ssp5 = self._addWidget('ssp5', 'CheckBox', x, y+55, nWidth, nHeight, Label = ui.get('ssp5'), State = True)
        self.ssp6 = self._addWidget('ssp6', 'CheckBox', x, y+65, nWidth, nHeight, Label = ui.get('ssp6'), State = True)
        self.ssp7 = self._addWidget('ssp7', 'CheckBox', x, y+75, nWidth, nHeight, Label = ui.get('ssp7'), State = True)
        self.ssp1_res = self._addWidget('ssp1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.ssp2_res = self._addWidget('ssp2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.ssp3_res = self._addWidget('ssp3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.ssp4_res = self._addWidget('ssp4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.ssp5_res = self._addWidget('ssp5_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        self.ssp6_res = self._addWidget('ssp6_res', 'FixedText', nPosRes, y+65, 20, nHeight, Label = "", Align = 2)
        self.ssp7_res = self._addWidget('ssp7_res', 'FixedText', nPosRes, y+75, 20, nHeight, Label = "", Align = 2)

        # group box // missing spaces
        y = y + 85
        self.space = self._addWidget('space', 'CheckBox', x, y+2, nWidth, nHeight, Label = ui.get('space'), FontDescriptor = xFD1, \
                                     FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section2", 'FixedLine', nRightLimit1-(nWidth//3), y, nWidth//3, nHeight)
        self.space1 = self._addWidget('space1', 'CheckBox', x, y+15, nWidth, nHeight, Label = ui.get('space1'), State = True)
        self.space2 = self._addWidget('space2', 'CheckBox', x, y+25, nWidth, nHeight, Label = ui.get('space2'), State = True)
        self.space1_res = self._addWidget('space1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.space2_res = self._addWidget('space2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)

        # group box // non-breaking spaces
        y = y + 35
        self.nbsp = self._addWidget('nbsp', 'CheckBox', x, y+2, nWidth, nHeight, Label = ui.get('nbsp'), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section3", 'FixedLine', nRightLimit1-(nWidth//3), y, nWidth//3, nHeight)
        self.nbsp1 = self._addWidget('nbsp1', 'CheckBox', x, y+15, 85, nHeight, Label = ui.get('nbsp1'), State = True)
        self.nbsp2 = self._addWidget('nbsp2', 'CheckBox', x, y+25, 85, nHeight, Label = ui.get('nbsp2'), State = True)
        self.nbsp3 = self._addWidget('nbsp3', 'CheckBox', x, y+35, nWidth, nHeight, Label = ui.get('nbsp3'), State = True)
        self.nbsp4 = self._addWidget('nbsp4', 'CheckBox', x, y+45, 85, nHeight, Label = ui.get('nbsp4'), State = True)
        self.nbsp5 = self._addWidget('nbsp5', 'CheckBox', x, y+55, 85, nHeight, Label = ui.get('nbsp5'), State = True)
        self.nbsp6 = self._addWidget('nbsp6', 'CheckBox', x, y+65, 85, nHeight, Label = ui.get('nbsp6'), State = True)
        self.nnbsp1 = self._addWidget('nnbsp1', 'CheckBox', x+85, y+15, 30, nHeight, Label = ui.get('nnbsp'), HelpText = ui.get('nnbsp_help'), State = False)
        self.nnbsp2 = self._addWidget('nnbsp2', 'CheckBox', x+85, y+25, 30, nHeight, Label = ui.get('nnbsp'), State = False)
        self.nnbsp4 = self._addWidget('nnbsp4', 'CheckBox', x+85, y+45, 30, nHeight, Label = ui.get('nnbsp'), State = False)
        self.nbsp1_res = self._addWidget('nbsp1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.nbsp2_res = self._addWidget('nbsp2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.nbsp3_res = self._addWidget('nbsp3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.nbsp4_res = self._addWidget('nbsp4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.nbsp5_res = self._addWidget('nbsp5_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        self.nbsp6_res = self._addWidget('nbsp6_res', 'FixedText', nPosRes, y+65, 20, nHeight, Label = "", Align = 2)

        # group box // deletion
        y = y + 75
        self.delete = self._addWidget('delete', 'CheckBox', x, y+2, nWidth, nHeight, Label = ui.get('delete'), FontDescriptor = xFD1, \
                                      FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section7", 'FixedLine', nRightLimit1-(nWidth//2), y, nWidth//2, nHeight)
        self.delete1 = self._addWidget('delete1', 'CheckBox', x, y+15, nWidth, nHeight, Label = ui.get('delete1'), State = True)
        self.delete2 = self._addWidget('delete2', 'CheckBox', x, y+25, nWidth, nHeight, Label = ui.get('delete2'), State = True)
        self.delete2a = self._addWidget('delete2a', 'RadioButton', x+10, y+35, 50, nHeight, Label = ui.get('delete2a'))
        self.delete2b = self._addWidget('delete2b', 'RadioButton', x+60, y+35, 60, nHeight, Label = ui.get('delete2b'), State = True)
        self.delete2c = self._addWidget('delete2c', 'RadioButton', x+120, y+35, 40, nHeight, Label = ui.get('delete2c'), \
                                        HelpText = ui.get('delete2c_help'))
        self.delete1_res = self._addWidget('delete1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.delete2_res = self._addWidget('delete2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)

        # group box // typographical marks
        y = 10
        nPosRes = nRightLimit2 - 20
        self.typo = self._addWidget('typo', 'CheckBox', x2, y+2, nWidth, nHeight, Label = ui.get('typo'), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section4", 'FixedLine', nRightLimit2-(nWidth//5), y, nWidth//5, nHeight)
        self.typo1 = self._addWidget('typo1', 'CheckBox', x2, y+15, nWidth, nHeight, Label = ui.get('typo1'), State = True)
        self.typo2 = self._addWidget('typo2', 'CheckBox', x2, y+25, nWidth, nHeight, Label = ui.get('typo2'), State = True)
        self.typo3 = self._addWidget('typo3', 'CheckBox', x2, y+35, nWidth, nHeight, Label = ui.get('typo3'), State = True)
        self.typo3a = self._addWidget('typo3a', 'RadioButton', x2+10, y+45, nWidthHalf, nHeight, Label = ui.get('emdash'))
        self.typo3b = self._addWidget('typo3b', 'RadioButton', x2+70, y+45, nWidthHalf, nHeight, Label = ui.get('endash'), State = True)
        self.typo4 = self._addWidget('typo4', 'CheckBox', x2, y+55, nWidth, nHeight, Label = ui.get('typo4'), State = True)
        self.typo4a = self._addWidget('typo4a', 'RadioButton', x2+10, y+65, nWidthHalf, nHeight, Label = ui.get('emdash'), State = True)
        self.typo4b = self._addWidget('typo4b', 'RadioButton', x2+70, y+65, nWidthHalf, nHeight, Label = ui.get('endash'))
        self.typo5 = self._addWidget('typo5', 'CheckBox', x2, y+75, nWidth, nHeight, Label = ui.get('typo5'), State = True)
        self.typo6 = self._addWidget('typo6', 'CheckBox', x2, y+85, nWidth, nHeight, Label = ui.get('typo6'), State = True)
        self.typo7 = self._addWidget('typo7', 'CheckBox', x2, y+95, nWidth, nHeight, Label = ui.get('typo7'), State = True)
        self.typo8 = self._addWidget('typo8', 'CheckBox', x2, y+105, 35, nHeight, Label = ui.get('typo8'), \
                                     HelpText = ui.get('typo8_help'), State = True)
        self.typo8a = self._addWidget('typo8a', 'RadioButton', x2+45, y+105, 30, nHeight, Label = ui.get('typo8a'))
        self.typo8b = self._addWidget('typo8b', 'RadioButton', x2+75, y+105, 35, nHeight, Label = ui.get('typo8b'), State = True)
        self.typo_ff = self._addWidget('typo_ff', 'CheckBox', x2+10, y+115, 18, nHeight, Label = ui.get('typo_ff'), State = True)
        self.typo_fi = self._addWidget('typo_fi', 'CheckBox', x2+28, y+115, 18, nHeight, Label = ui.get('typo_fi'), State = True)
        self.typo_ffi = self._addWidget('typo_ffi', 'CheckBox', x2+46, y+115, 20, nHeight, Label = ui.get('typo_ffi'), State = True)
        self.typo_fl = self._addWidget('typo_fl', 'CheckBox', x2+66, y+115, 18, nHeight, Label = ui.get('typo_fl'), State = True)
        self.typo_ffl = self._addWidget('typo_ffl', 'CheckBox', x2+84, y+115, 20, nHeight, Label = ui.get('typo_ffl'), State = True)
        self.typo_ft = self._addWidget('typo_ft', 'CheckBox', x2+104, y+115, 18, nHeight, Label = ui.get('typo_ft'), State = True)
        self.typo_st = self._addWidget('typo_st', 'CheckBox', x2+122, y+115, 18, nHeight, Label = ui.get('typo_st'), State = True)
        self.typo1_res = self._addWidget('typo1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.typo2_res = self._addWidget('typo2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.typo3_res = self._addWidget('typo3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.typo4_res = self._addWidget('typo4_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        self.typo5_res = self._addWidget('typo5_res', 'FixedText', nPosRes, y+75, 20, nHeight, Label = "", Align = 2)
        self.typo6_res = self._addWidget('typo6_res', 'FixedText', nPosRes, y+85, 20, nHeight, Label = "", Align = 2)
        self.typo7_res = self._addWidget('typo7_res', 'FixedText', nPosRes, y+95, 20, nHeight, Label = "", Align = 2)
        self.typo8_res = self._addWidget('typo8_res', 'FixedText', nPosRes, y+105, 20, nHeight, Label = "", Align = 2)

        # group box // misc.
        y = y + 125
        self.misc = self._addWidget('misc', 'CheckBox', x2, y+2, nWidth, nHeight, Label = ui.get('misc'), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self._addWidget("section5", 'FixedLine', nRightLimit2-(nWidth//2), y, nWidth//2, nHeight)
        self.misc1 = self._addWidget('misc1', 'CheckBox', x2, y+15, 80, nHeight, Label = ui.get('misc1'), State = True)
        self.misc1a = self._addWidget('misc1a', 'CheckBox', x2+80, y+15, 30, nHeight, Label = ui.get('misc1a'), State = True)
        self.misc2 = self._addWidget('misc2', 'CheckBox', x2, y+25, nWidth, nHeight, Label = ui.get('misc2'), State = True)
        self.misc3 = self._addWidget('misc3', 'CheckBox', x2, y+35, nWidth, nHeight, Label = ui.get('misc3'), State = True)
        #self.misc4 = self._addWidget('misc4', 'CheckBox', x2, y+45, nWidth, nHeight, Label = ui.get('misc4'), State = True)
        self.misc5 = self._addWidget('misc5', 'CheckBox', x2, y+45, nWidth, nHeight, Label = ui.get('misc5'), State = True)
        self.misc5b = self._addWidget('misc5b', 'CheckBox', x2+10, y+55, nWidth-40, nHeight, Label = ui.get('misc5b'), State = False)
        self.misc5c = self._addWidget('misc5c', 'CheckBox', x2+nWidth-25, y+55, 30, nHeight, Label = ui.get('misc5c'), State = False)
        self.misccustom = self._addWidget('misccustom', "CheckBox", x2, y+65, nWidth-40, nHeight, Label = ui.get('misccustom'), State = False)
        self.beditor = self._addWidget('editor', 'Button', x2+95, y+64, 25, 9, Label = ui.get('editor'), \
                                        HelpText = ui.get('editor_help'), FontDescriptor = xFDsmall)
        self.misc1_res = self._addWidget('misc1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.misc2_res = self._addWidget('misc2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.misc3_res = self._addWidget('misc3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        #self.misc4_res = self._addWidget('misc4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.misc5_res = self._addWidget('misc5_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.misccustom_res = self._addWidget('misccustom_res', 'FixedText', nPosRes, y+65, 20, nHeight, Label = "", Align = 2)

        # group box // restructuration
        y = y + 75
        self.struct = self._addWidget('struct', 'CheckBox', x2, y+2, nWidth, nHeight, Label = ui.get('struct'), FontDescriptor = xFD1, \
                                      FontRelief = 1, TextColor = nColor, HelpText = ui.get('struct_help'), State = False)
        self._addWidget("section6", 'FixedLine', nRightLimit2-(nWidth//3), y, nWidth//3, nHeight)
        self.struct1 = self._addWidget('struct1', 'CheckBox', x2, y+15, nWidth, nHeight, Label = ui.get('struct1'), State = True, Enabled = False)
        self.struct2 = self._addWidget('struct2', 'CheckBox', x2, y+25, nWidth, nHeight, Label = ui.get('struct2'), State = True, Enabled = False)
        self.struct3 = self._addWidget('struct3', 'CheckBox', x2, y+35, nWidth, nHeight, Label = ui.get('struct3'), \
                                       HelpText = ui.get('struct3_help'), State = False, Enabled = False)
        self.struct1_res = self._addWidget('struct1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.struct2_res = self._addWidget('struct2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.struct3_res = self._addWidget('struct3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)

        # dialog height
        self.xDialog.Height = 277
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        # lists of checkbox widgets
        self.dCheckboxWidgets = {
            "ssp":      [self.ssp1, self.ssp2, self.ssp3, self.ssp4, self.ssp5, self.ssp6, self.ssp7],
            "space":    [self.space1, self.space2],
            "nbsp":     [self.nbsp1, self.nbsp2, self.nbsp3, self.nbsp4, self.nbsp5, self.nbsp6, self.nnbsp1, self.nnbsp2, self.nnbsp4],
            "delete":   [self.delete1, self.delete2, self.delete2a, self.delete2b, self.delete2c],
            "typo":     [self.typo1, self.typo2, self.typo3, self.typo3a, self.typo3b, self.typo4, self.typo4a, self.typo4b, self.typo5, self.typo6, \
                         self.typo7, self.typo8, self.typo8a, self.typo8b, self.typo_ff, self.typo_fi, self.typo_ffi, self.typo_fl, self.typo_ffl, \
                         self.typo_ft, self.typo_st],
            "misc":     [self.misc1, self.misc2, self.misc3, self.misc5, self.misc1a, self.misc5b, self.misc5c, self.misccustom], #self.misc4,
            "struct":   [self.struct1, self.struct2, self.struct3]
        }

        # progress bar
        self.pbar = self._addWidget('pbar', 'ProgressBar', 22, self.xDialog.Height-16, 210, 10)
        self.pbar.ProgressValueMin = 0
        self.pbar.ProgressValueMax = 32
        # time counter
        self.time_res = self._addWidget('time_res', 'FixedText', self.xDialog.Width-80, self.xDialog.Height-15, 20, nHeight, Label = "", Align = 2)

        # buttons
        self.bdefault = self._addWidget('default', 'Button', 5, self.xDialog.Height-19, 15, 15, Label = ui.get('default'), \
                                        HelpText = ui.get('default_help'), FontDescriptor = xFD2, TextColor = 0x444444)
        #self.bsel = self._addWidget('bsel', 'CheckBox', x2, self.xDialog.Height-40, nWidth-55, nHeight, Label = ui.get('bsel'))
        self.bapply = self._addWidget('apply', 'Button', self.xDialog.Width-55, self.xDialog.Height-19, 50, 15, Label = ui.get('apply'), \
                                      FontDescriptor = xFD2, TextColor = 0x004400)
        self.binfo = self._addWidget('info', 'Button', self.xDialog.Width-15, 0, 10, 9, Label = ui.get('info'), \
                                     HelpText = ui.get('infotitle'), FontDescriptor = xFDsmall, TextColor = 0x444444)

        # load configuration
        self.dTransRules = {}
        self.xGLOptionNode = helpers.getConfigSetting("/org.openoffice.Lightproof_${implname}/Other/", True)
        self._loadConfig("${lang}")

        ## container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.setVisible(False)
        self.xContainer.getControl('info').addActionListener(self)
        self.xContainer.getControl('info').setActionCommand('Info')
        self.xContainer.getControl('editor').addActionListener(self)
        self.xContainer.getControl('editor').setActionCommand('Editor')
        self.xContainer.getControl('default').addActionListener(self)
        self.xContainer.getControl('default').setActionCommand('Default')
        self.xContainer.getControl('apply').addActionListener(self)
        self.xContainer.getControl('apply').setActionCommand('Apply')
        self.xContainer.getControl('ssp').addActionListener(self)
        self.xContainer.getControl('ssp').setActionCommand('SwitchSsp')
        self.xContainer.getControl('space').addActionListener(self)
        self.xContainer.getControl('space').setActionCommand('SwitchSpace')
        self.xContainer.getControl('nbsp').addActionListener(self)
        self.xContainer.getControl('nbsp').setActionCommand('SwitchNbsp')
        self.xContainer.getControl('delete').addActionListener(self)
        self.xContainer.getControl('delete').setActionCommand('SwitchDelete')
        self.xContainer.getControl('typo').addActionListener(self)
        self.xContainer.getControl('typo').setActionCommand('SwitchTypo')
        self.xContainer.getControl('misc').addActionListener(self)
        self.xContainer.getControl('misc').setActionCommand('SwitchMisc')
        self.xContainer.getControl('struct').addActionListener(self)
        self.xContainer.getControl('struct').setActionCommand('SwitchStruct')
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == 'Apply':
                if self.bClose:
                    self.xContainer.endExecute()
                else:
                    xDesktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
                    xElem = xDesktop.getCurrentComponent()

                    # Writer
                    if True:
                        # no selection
                        self._saveConfig("${lang}")
                        self._replaceAll(xElem)
                    else:
                        # modify selected text only
                        pass
                        #xSelecList = xDoc.getCurrentSelection()
                        #xSel = xSelecList.getByIndex(0)

                    # Impress
                    # Note: impossible to format text on Impress right now as ReplaceDescriptors don’t accept regex!
                    #xPages = xElem.getDrawPages()
                    #for i in range(xPages.Count):
                    #    self._replaceAll(xPages.getByIndex(i))
                    #xPages = xElem.getMasterPages()
                    #for i in range(xPages.Count):
                    #    self._replaceAll(xPages.getByIndex(i))
                    self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchSsp':
                self._switchCheckBox(self.ssp)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchSpace':
                self._switchCheckBox(self.space)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchNbsp':
                self._switchCheckBox(self.nbsp)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchDelete':
                self._switchCheckBox(self.delete)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchTypo':
                self._switchCheckBox(self.typo)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchMisc':
                self._switchCheckBox(self.misc)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'SwitchStruct':
                self._switchCheckBox(self.struct)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'Default':
                self._setConfig(tf_options.dDefaultOpt)
                self._setApplyButtonLabel()
            elif xActionEvent.ActionCommand == 'Editor':
                xDialog = TextFormatterEditor.TextFormatterEditor(self.ctx)
                xDialog.run(self.sLang)
            elif xActionEvent.ActionCommand == 'Info':
                xDesktop = self.xSvMgr.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
                xDoc = xDesktop.getCurrentComponent()
                xWindow = xDoc.CurrentController.Frame.ContainerWindow
                MessageBox(xWindow, ui.get('infomsg'), ui.get('infotitle'))
            else:
                print("Wrong command: " + xActionEvent.ActionCommand)
        except:
            traceback.print_exc()

    def _loadConfig (self, sLang):
        try:
            dOpt = tf_options.dDefaultOpt.copy()
            xChild = self.xGLOptionNode.getByName("o_"+sLang)
            # selected options
            sTFOptionsJSON = xChild.getPropertyValue("tf_options")
            if sTFOptionsJSON:
                dOpt.update(json.loads(sTFOptionsJSON))
            self._setConfig(dOpt)
            # transformation rules
            sTFEditorOptions = xChild.getPropertyValue("tfe_rules")
            if sTFEditorOptions:
                self.dTransRules = json.loads(sTFEditorOptions)
        except:
            traceback.print_exc()
            self._setConfig(tf_options.dDefaultOpt)
            self.misccustom.State = False

    def _setConfig (self, dOpt):
        for sKey, val in dOpt.items():
            try:
                w = getattr(self, sKey)
                if w:
                    w.State = val
                    if sKey in self.dCheckboxWidgets:
                        self._switchCheckBox(w)
            except:
                traceback.print_exc()
                print("option", sKey, "not set.")

    def _saveConfig (self, sLang):
        "save options in LibreOffice profile"
        try:
            # create options dictionary
            dOpt = {}
            for sKey, lWidget in self.dCheckboxWidgets.items():
                w = getattr(self, sKey)
                dOpt[w.Name] = w.State
                for w in lWidget:
                    dOpt[w.Name] = w.State
            # save option to LO profile as JSON string
            xChild = self.xGLOptionNode.getByName("o_"+sLang)
            xChild.setPropertyValue("tf_options", json.dumps(dOpt))
            self.xGLOptionNode.commitChanges()
        except:
            traceback.print_exc()

    def _switchCheckBox (self, wGroupCheckbox):
        for w in self.dCheckboxWidgets.get(wGroupCheckbox.Name, []):
            w.Enabled = wGroupCheckbox.State

    def _setApplyButtonLabel (self):
        if self.ssp.State or self.space.State or self.nbsp.State or self.delete.State or self.typo.State or self.misc.State or self.struct.State:
            self.bClose = False
            self.bapply.Label = ui.get('apply')
            self.bapply.TextColor = 0x004400
        else:
            self.bClose = True
            self.bapply.Label = ui.get('close')
            self.bapply.TextColor = 0x440000
        self.xContainer.setVisible(True)

    def _replaceAll (self, xElem):
        try:
            nStartTime = time.perf_counter()
            self.xContainer.setVisible(True)
            # change pointer
            xPointer = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Pointer", self.ctx)
            xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.WAIT"))
            xWindowPeer = self.xContainer.getPeer()
            xWindowPeer.setPointer(xPointer)
            for x in xWindowPeer.Windows:
                x.setPointer(xPointer)
            # ICU: & is $0 in replacement field
            # NOTE: A LOT OF REGEX COULD BE MERGED IF ICU ENGINE WAS NOT SO BUGGY
            # "([;?!…])(?=[:alnum:])" => "$1 " doesn’t work properly
            # "(?<=[:alnum:])([;?!…])" => " $1 " doesn’t work properly
            self.pbar.ProgressValue = 0
            # Restructuration
            if self.struct.State:
                if self.struct1.State:
                    n = self._replaceList(xElem, "struct1")
                    self.struct1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.struct2.State:
                    n = self._replaceList(xElem, "struct2")
                    n += self._replaceHyphenAtEndOfParagraphs(xElem) # EOP
                    self.struct2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.struct3.State:
                    n = self._mergeContiguousParagraphs(xElem)
                    self.struct3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.struct.State = False
                self._switchCheckBox(self.struct)
            self.pbar.ProgressValue = 3
            # espaces surnuméraires
            if self.ssp.State:
                if self.ssp3.State:
                    n = self._replaceList(xElem, "ssp3")
                    self.ssp3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp2.State:
                    n = self._replaceList(xElem, "ssp2")
                    self.ssp2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp1.State:
                    n = self._replaceList(xElem, "ssp1")
                    self.ssp1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp4.State:
                    n = self._replaceList(xElem, "ssp4")
                    self.ssp4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp5.State:
                    n = self._replaceList(xElem, "ssp5")
                    self.ssp5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp6.State:
                    n = self._replaceList(xElem, "ssp6")
                    self.ssp6_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp7.State:
                    n = self._replaceList(xElem, "ssp7")
                    self.ssp7_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.ssp.State = False
                self._switchCheckBox(self.ssp)
            self.pbar.ProgressValue = 10
            # espaces typographiques
            if self.nbsp.State:
                if self.nbsp1.State:
                    if self.nnbsp1.State:
                        # espaces insécables fines
                        n = self._replaceList(xElem, "nnbsp1")
                    else:
                        # espaces insécables
                        n = self._replaceList(xElem, "nbsp1")
                    # réparations
                    n -= self._replaceList(xElem, "nbsp1_fix")
                    self.nbsp1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp2.State:
                    if self.nnbsp2.State:
                        # espaces insécables fines
                        n = self._replaceList(xElem, "nnbsp2")
                    else:
                        # espaces insécables
                        n = self._replaceList(xElem, "nbsp2")
                    self.nbsp2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp3.State:
                    n = self._replaceList(xElem, "nbsp3")
                    self.nbsp3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp4.State:
                    if self.nnbsp4.State:
                        # espaces insécables fines
                        n = self._replaceList(xElem, "nnbsp4")
                    else:
                        # espaces insécables
                        n = self._replaceList(xElem, "nbsp4")
                    self.nbsp4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp5.State:
                    n = self._replaceList(xElem, "nbsp5")
                    self.nbsp5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp6.State:
                    n = self._replaceList(xElem, "nbsp6")
                    self.nbsp6_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.nbsp.State = False
                self._switchCheckBox(self.nbsp)
            self.pbar.ProgressValue = 16
            # points médians
            if self.typo.State:
                if self.typo6.State:
                    n = self._replaceList(xElem, "typo6")
                    self.typo6_res.Label = str(n)
                    self.pbar.ProgressValue += 1
            # espaces manquants
            if self.space.State:
                if self.space1.State:
                    n = self._replaceList(xElem, "space1")
                    # réparations
                    n -= self._replaceList(xElem, "space1_fix")
                    self.space1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.space2.State:
                    n = self._replaceList(xElem, "space2")
                    self.space2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.space.State = False
                self._switchCheckBox(self.space)
            self.pbar.ProgressValue = 18
            # Suppression
            if self.delete.State:
                if self.delete1.State:
                    n = self._replaceList(xElem, "delete1")
                    self.delete1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.delete2.State:
                    n = self._replaceBulletsByEmDash(xElem)
                    self.delete2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.delete.State = False
                self._switchCheckBox(self.delete)
            self.pbar.ProgressValue = 21
            # signes typographiques
            if self.typo.State:
                if self.typo1.State:
                    n = self._replaceList(xElem, "typo1")
                    self.typo1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo2.State:
                    n = self._replaceList(xElem, "typo2")
                    self.typo2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo3.State:
                    if self.typo3b.State:
                        # demi-cadratin
                        n = self._replaceList(xElem, "typo3b")
                    else:
                        # cadratin
                        n = self._replaceList(xElem, "typo3a")
                    self.typo3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo4.State:
                    if self.typo4a.State:
                        # cadratin
                        n = self._replaceList(xElem, "typo4a")
                    else:
                        # demi-cadratin
                        n = self._replaceList(xElem, "typo4b")
                    self.typo4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo5.State:
                    n = self._replaceList(xElem, "typo5")
                    self.typo5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo7.State:
                    n = self._replaceList(xElem, "typo7")
                    self.typo7_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo8.State:
                    # ligatures typographiques : fi, fl, ff, ffi, ffl, ft, st
                    n = 0
                    if self.typo8a.State:
                        if self.typo_ffi.State:
                            n += self._replaceText(xElem, "ffi", "ﬃ", False, True)
                        if self.typo_ffl.State:
                            n += self._replaceText(xElem, "ffl", "ﬄ", False, True)
                        if self.typo_fi.State:
                            n += self._replaceText(xElem, "fi", "ﬁ", False, True)
                        if self.typo_fl.State:
                            n += self._replaceText(xElem, "fl", "ﬂ", False, True)
                        if self.typo_ff.State:
                            n += self._replaceText(xElem, "ff", "ﬀ", False, True)
                        if self.typo_ft.State:
                            n += self._replaceText(xElem, "ft", "ﬅ", False, True)
                        if self.typo_st.State:
                            n += self._replaceText(xElem, "st", "ﬆ", False, True)
                    if self.typo8b.State:
                        if self.typo_fi.State:
                            n += self._replaceText(xElem, "ﬁ", "fi", False, True)
                        if self.typo_fl.State:
                            n += self._replaceText(xElem, "ﬂ", "fl", False, True)
                        if self.typo_ff.State:
                            n += self._replaceText(xElem, "ﬀ", "ff", False, True)
                        if self.typo_ffi.State:
                            n += self._replaceText(xElem, "ﬃ", "ffi", False, True)
                        if self.typo_ffl.State:
                            n += self._replaceText(xElem, "ﬄ", "ffl", False, True)
                        if self.typo_ft.State:
                            n += self._replaceText(xElem, "ﬅ", "ft", False, True)
                        if self.typo_st.State:
                            n += self._replaceText(xElem, "ﬆ", "st", False, True)
                    self.typo8_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.typo.State = False
                self._switchCheckBox(self.typo)
            self.pbar.ProgressValue = 29
            # divers
            if self.misc.State:
                if self.misc1.State:
                    if self.misc1a.State:
                        n = self._replaceList(xElem, "misc1a")
                    else:
                        n = self._replaceList(xElem, "misc1b")
                    self.misc1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc2.State:
                    n = self._replaceList(xElem, "misc2")
                    self.misc2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc3.State:
                    n = self._replaceList(xElem, "misc3")
                    self.misc3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc5.State:
                    n = self._replaceList(xElem, "misc5a")
                    if self.misc5b.State:
                        n += self._replaceList(xElem, "misc5b")
                        if self.misc5c.State:
                            n += self._replaceList(xElem, "misc5c")
                    self.misc5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misccustom.State:
                    n = self._replaceCustom(xElem)
                    self.misccustom_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.misc.State = False
                self._switchCheckBox(self.misc)
            self.pbar.ProgressValue = self.pbar.ProgressValueMax
            # end of processing
            xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.ARROW"))
            xWindowPeer.setPointer(xPointer)
            for x in xWindowPeer.Windows:
                x.setPointer(xPointer)
            self.xContainer.setVisible(True) # seems necessary to refresh the dialog box and text widgets (why?)
            nEndTime = time.perf_counter()
            self.time_res.Label = getTimeRes(nEndTime-nStartTime)
        except:
            traceback.print_exc()

    def _replaceList (self, xElem, sList):
        if sList not in tf_tabrep.dTableRepl:
            print("# Error. List <"+sList+"> not found")
            return 0
        n = 0
        try:
            for sPattern, sRepl, bRegex, bCaseSensitive in tf_tabrep.dTableRepl[sList]:
                n += self._replaceText(xElem, sPattern, sRepl, bRegex, bCaseSensitive)
        except:
            print("# Error with "+sList)
            traceback.print_exc()
        return n

    def _replaceCustom (self, xElem):
        n = 0
        try:
            for sRuleName, dRule in sorted(self.dTransRules.items()):
                #print(sRuleName, dRule["sPattern"], dRule["sRepl"], dRule["bRegex"], dRule["bCaseSens"])
                n += self._replaceText(xElem, dRule["sPattern"], dRule["sRepl"], dRule["bRegex"], dRule["bCaseSens"])
        except:
            print("# Error with custom transformation rules")
            traceback.print_exc()
        return n

    def _replaceText (self, xElem, sPattern, sRepl, bRegex, bCaseSensitive=False):
        try:
            xRD = xElem.createReplaceDescriptor()
            xRD.SearchString = sPattern
            xRD.ReplaceString = sRepl
            xRD.SearchRegularExpression = bRegex
            xRD.SearchCaseSensitive = bCaseSensitive
            return xElem.replaceAll(xRD)
        except:
            traceback.print_exc()
        return 0

    def _replaceHyphenAtEndOfParagraphs (self, xDoc):
        self._replaceText(xDoc, "-[  ]+$", "-", True) # remove spaces at end of paragraphs if - is the last character
        n = 0
        try:
            xHunspell = self.xSvMgr.createInstanceWithContext("com.sun.star.linguistic2.SpellChecker", self.ctx)
            xCursor = xDoc.Text.createTextCursor()
            xCursor.gotoStart(False)
            while xCursor.gotoNextParagraph(False):
                xCursor.goLeft(2, True)
                if xCursor.String.startswith("-"):
                    xCursor.gotoStartOfWord(False)
                    xLocale = xCursor.CharLocale
                    xCursor.gotoEndOfWord(True)
                    sWord1 = xCursor.String
                    xCursor.gotoNextParagraph(False)
                    xCursor.gotoEndOfWord(True)
                    sWord2 = xCursor.String
                    if sWord1 and sWord2 and xHunspell.isValid(sWord1+sWord2, xLocale, ()):
                        xCursor.gotoStartOfParagraph(False)
                        xCursor.goLeft(2, True)
                        xCursor.setString("")
                        n += 1
                else:
                    xCursor.goRight(2, False)
        except:
            traceback.print_exc()
        return n

    def _mergeContiguousParagraphs (self, xDoc):
        self._replaceText(xDoc, "^[  ]+$", "", True) # clear empty paragraphs
        n = 0
        try:
            xCursor = xDoc.Text.createTextCursor()
            xCursor.gotoStart(False)
            while xCursor.gotoNextParagraph(False):
                xCursor.gotoEndOfParagraph(True)
                if xCursor.String != "":
                    xCursor.gotoStartOfParagraph(False)
                    xCursor.goLeft(1, True)
                    xCursor.setString(" ")
                    n += 1
        except:
            traceback.print_exc()
        self._replaceText(xDoc, "  +", " ", True)
        return n

    def _replaceBulletsByEmDash (self, xDoc):
        xCursor = xDoc.Text.createTextCursor()
        #helpers.xray(xCursor)
        n = 0
        try:
            xCursor.gotoStart(False)
            sParaStyleName = ""
            if not self.delete2c.State:
                sParaStyleName = "Standard"  if self.delete2a.State  else "Text body"
            if xCursor.NumberingStyleName != "":
                xCursor.NumberingStyleName = ""
                if sParaStyleName:
                    xCursor.ParaStyleName = sParaStyleName
                xDoc.Text.insertString(xCursor, "— ", False)
                n += 1
            while xCursor.gotoNextParagraph(False):
                if xCursor.NumberingStyleName != "":
                    xCursor.NumberingStyleName = ""
                    if sParaStyleName:
                        xCursor.ParaStyleName = sParaStyleName
                    xDoc.Text.insertString(xCursor, "— ", False)
                    n += 1
        except:
            traceback.print_exc()
        return n


def getTimeRes (n):
    "returns duration in seconds as string"
    if n < 10:
        return "{:.3f} s".format(n)
    if n < 100:
        return "{:.2f} s".format(n)
    if n < 1000:
        return "{:.1f} s".format(n)
    return str(int(n)) + " s"


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(TextFormatter, 'dicollecte.TextFormatter', ('com.sun.star.task.Job',))
