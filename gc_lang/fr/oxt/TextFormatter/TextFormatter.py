# -*- coding: utf8 -*-
# Text Formatter
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import sys
import os
import traceback
import time

if sys.version_info.major == 3:
    import imp

import tf_strings
import tf_options
import helpers


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
        self.dUI = tf_strings.getUI(sLang)

        ## dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 320
        self.xDialog.Title = self.dUI.get('title', "#title#")

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

        ## widgets
        nGroupBoxWith = (self.xDialog.Width - 15) // 2
        nWidth = nGroupBoxWith-10
        nWidthHalf = (nWidth // 2) - 10
        nHeight = 10
        nColor = 0xAA2200
        
        # close or apply
        self.bClose = False

        # group box // surnumerary spaces
        x = 10; y = 5
        nPosRes = nGroupBoxWith - 22
        gbm1 = self._addWidget('groupbox1', 'GroupBox', x-5, y, nGroupBoxWith, 90, Label = "  " * len(self.dUI.get('ssp', "#err")), FontDescriptor = xFD1)
        self.ssp = self._addWidget('ssp', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('ssp', "#err"), FontDescriptor = xFD1, \
                                   FontRelief = 1, TextColor = nColor, State = True)
        self.ssp1 = self._addWidget('ssp1', 'CheckBox', x, y+15, nWidth, nHeight, Label = self.dUI.get('ssp1', "#err"), State = True)
        self.ssp2 = self._addWidget('ssp2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('ssp2', "#err"), State = True)
        self.ssp3 = self._addWidget('ssp3', 'CheckBox', x, y+35, nWidth, nHeight, Label = self.dUI.get('ssp3', "#err"), State = True)
        self.ssp4 = self._addWidget('ssp4', 'CheckBox', x, y+45, nWidth, nHeight, Label = self.dUI.get('ssp4', "#err"), State = True)
        self.ssp5 = self._addWidget('ssp5', 'CheckBox', x, y+55, nWidth, nHeight, Label = self.dUI.get('ssp5', "#err"), State = True)
        self.ssp6 = self._addWidget('ssp6', 'CheckBox', x, y+65, nWidth, nHeight, Label = self.dUI.get('ssp6', "#err"), State = True)
        self.ssp7 = self._addWidget('ssp7', 'CheckBox', x, y+75, nWidth, nHeight, Label = self.dUI.get('ssp7', "#err"), State = True)
        self.ssp1_res = self._addWidget('ssp1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.ssp2_res = self._addWidget('ssp2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.ssp3_res = self._addWidget('ssp3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.ssp4_res = self._addWidget('ssp4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.ssp5_res = self._addWidget('ssp5_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        self.ssp6_res = self._addWidget('ssp6_res', 'FixedText', nPosRes, y+65, 20, nHeight, Label = "", Align = 2)
        self.ssp7_res = self._addWidget('ssp7_res', 'FixedText', nPosRes, y+75, 20, nHeight, Label = "", Align = 2)

        # group box // missing spaces
        x = 10; y = 100
        gbm2 = self._addWidget('groupbox2', 'GroupBox', x-5, y, nGroupBoxWith, 40, Label = "  " * len(self.dUI.get('space', "#err")), FontDescriptor = xFD1)
        self.space = self._addWidget('space', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('space', "#err"), FontDescriptor = xFD1, \
                                     FontRelief = 1, TextColor = nColor, State = True)
        self.space1 = self._addWidget('space1', 'CheckBox', x, y+15, nWidth, nHeight, Label = self.dUI.get('space1', "#err"), State = True)
        self.space2 = self._addWidget('space2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('space2', "#err"), State = True)
        self.space1_res = self._addWidget('space1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.space2_res = self._addWidget('space2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        
        # group box // non-breaking spaces
        x = 10; y = 145
        gbm3 = self._addWidget('groupbox3', 'GroupBox', x-5, y, nGroupBoxWith, 70, Label = "  " * len(self.dUI.get('nbsp', "#err")), FontDescriptor = xFD1)
        self.nbsp = self._addWidget('nbsp', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('nbsp', "#err"), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self.nbsp1 = self._addWidget('nbsp1', 'CheckBox', x, y+15, 85, nHeight, Label = self.dUI.get('nbsp1', "#err"), State = True)
        self.nbsp2 = self._addWidget('nbsp2', 'CheckBox', x, y+25, 85, nHeight, Label = self.dUI.get('nbsp2', "#err"), State = True)
        self.nbsp3 = self._addWidget('nbsp3', 'CheckBox', x, y+35, nWidth, nHeight, Label = self.dUI.get('nbsp3', "#err"), State = True)
        self.nbsp4 = self._addWidget('nbsp4', 'CheckBox', x, y+45, 85, nHeight, Label = self.dUI.get('nbsp4', "#err"), State = True)
        self.nbsp5 = self._addWidget('nbsp5', 'CheckBox', x, y+55, 85, nHeight, Label = self.dUI.get('nbsp5', "#err"), State = True)
        self.nnbsp1 = self._addWidget('nnbsp1', 'CheckBox', x+85, y+15, 30, nHeight, Label = self.dUI.get('nnbsp', "#err"), HelpText = self.dUI.get('nnbsp_help', "#err"), State = False)
        self.nnbsp2 = self._addWidget('nnbsp2', 'CheckBox', x+85, y+25, 30, nHeight, Label = self.dUI.get('nnbsp', "#err"), State = False)
        self.nnbsp4 = self._addWidget('nnbsp4', 'CheckBox', x+85, y+45, 30, nHeight, Label = self.dUI.get('nnbsp', "#err"), State = False)
        self.nbsp1_res = self._addWidget('nbsp1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.nbsp2_res = self._addWidget('nbsp2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.nbsp3_res = self._addWidget('nbsp3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.nbsp4_res = self._addWidget('nbsp4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.nbsp5_res = self._addWidget('nbsp5_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        
        # group box // deletion
        x = 10; y = 220
        gbm7 = self._addWidget('groupbox7', 'GroupBox', x-5, y, nGroupBoxWith, 50, Label = "  " * len(self.dUI.get('delete', "#err")), FontDescriptor = xFD1)
        self.delete = self._addWidget('delete', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('delete', "#err"), FontDescriptor = xFD1, \
                                      FontRelief = 1, TextColor = nColor, State = True)
        self.delete1 = self._addWidget('delete1', 'CheckBox', x, y+15, nWidth, nHeight, Label = self.dUI.get('delete1', "#err"), State = True)
        self.delete2 = self._addWidget('delete2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('delete2', "#err"), State = True)
        self.delete2a = self._addWidget('delete2a', 'RadioButton', x+10, y+35, 50, nHeight, Label = self.dUI.get('delete2a', "#"))
        self.delete2b = self._addWidget('delete2b', 'RadioButton', x+60, y+35, 60, nHeight, Label = self.dUI.get('delete2b', "#"), State = True)
        self.delete2c = self._addWidget('delete2c', 'RadioButton', x+120, y+35, 40, nHeight, Label = self.dUI.get('delete2c', "#"), \
                                        HelpText = self.dUI.get('delete2c_help', "#err"))
        self.delete1_res = self._addWidget('delete1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.delete2_res = self._addWidget('delete2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)

        # group box // typographical marks
        x = 168; y = 5
        nPosRes = x + nGroupBoxWith - 32
        gbm4 = self._addWidget('groupbox4', 'GroupBox', x-5, y, nGroupBoxWith, 130, Label = "  " * len(self.dUI.get('typo', "#err")), FontDescriptor = xFD1)
        self.typo = self._addWidget('typo', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('typo', "#err"), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self.typo1 = self._addWidget('typo1', 'CheckBox', x, y+15, nWidth, nHeight, Label = self.dUI.get('typo1', "#err"), State = True)
        self.typo2 = self._addWidget('typo2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('typo2', "#err"), State = True)
        self.typo3 = self._addWidget('typo3', 'CheckBox', x, y+35, nWidth, nHeight, Label = self.dUI.get('typo3', "#err"), State = True)
        self.typo3a = self._addWidget('typo3a', 'RadioButton', x+10, y+45, nWidthHalf, nHeight, Label = self.dUI.get('emdash', "#err"))
        self.typo3b = self._addWidget('typo3b', 'RadioButton', x+70, y+45, nWidthHalf, nHeight, Label = self.dUI.get('endash', "#err"), State = True)
        self.typo4 = self._addWidget('typo4', 'CheckBox', x, y+55, nWidth, nHeight, Label = self.dUI.get('typo4', "#err"), State = True)
        self.typo4a = self._addWidget('typo4a', 'RadioButton', x+10, y+65, nWidthHalf, nHeight, Label = self.dUI.get('emdash', "#err"), State = True)
        self.typo4b = self._addWidget('typo4b', 'RadioButton', x+70, y+65, nWidthHalf, nHeight, Label = self.dUI.get('endash', "#err"))
        self.typo5 = self._addWidget('typo5', 'CheckBox', x, y+75, nWidth, nHeight, Label = self.dUI.get('typo5', "#err"), State = True)
        self.typo6 = self._addWidget('typo6', 'CheckBox', x, y+85, nWidth, nHeight, Label = self.dUI.get('typo6', "#err"), State = True)
        self.typo7 = self._addWidget('typo7', 'CheckBox', x, y+95, nWidth, nHeight, Label = self.dUI.get('typo7', "#err"), State = True)
        self.typo8 = self._addWidget('typo8', 'CheckBox', x, y+105, 35, nHeight, Label = self.dUI.get('typo8', "#err"), \
                                     HelpText = self.dUI.get('typo8_help', "#err"), State = True)
        self.typo8a = self._addWidget('typo8a', 'RadioButton', x+45, y+105, 30, nHeight, Label = self.dUI.get('typo8a', "#err"))
        self.typo8b = self._addWidget('typo8b', 'RadioButton', x+75, y+105, 35, nHeight, Label = self.dUI.get('typo8b', "#err"), State = True)
        self.typo_ff = self._addWidget('typo_ff', 'CheckBox', x+10, y+115, 18, nHeight, Label = self.dUI.get('typo_ff', "#err"), State = True)
        self.typo_fi = self._addWidget('typo_fi', 'CheckBox', x+28, y+115, 18, nHeight, Label = self.dUI.get('typo_fi', "#err"), State = True)
        self.typo_ffi = self._addWidget('typo_ffi', 'CheckBox', x+46, y+115, 20, nHeight, Label = self.dUI.get('typo_ffi', "#err"), State = True)
        self.typo_fl = self._addWidget('typo_fl', 'CheckBox', x+66, y+115, 18, nHeight, Label = self.dUI.get('typo_fl', "#err"), State = True)
        self.typo_ffl = self._addWidget('typo_ffl', 'CheckBox', x+84, y+115, 20, nHeight, Label = self.dUI.get('typo_ffl', "#err"), State = True)
        self.typo_ft = self._addWidget('typo_ft', 'CheckBox', x+104, y+115, 18, nHeight, Label = self.dUI.get('typo_ft', "#err"), State = True)
        self.typo_st = self._addWidget('typo_st', 'CheckBox', x+122, y+115, 18, nHeight, Label = self.dUI.get('typo_st', "#err"), State = True)
        self.typo1_res = self._addWidget('typo1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.typo2_res = self._addWidget('typo2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.typo3_res = self._addWidget('typo3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        self.typo4_res = self._addWidget('typo4_res', 'FixedText', nPosRes, y+55, 20, nHeight, Label = "", Align = 2)
        self.typo5_res = self._addWidget('typo5_res', 'FixedText', nPosRes, y+75, 20, nHeight, Label = "", Align = 2)
        self.typo6_res = self._addWidget('typo6_res', 'FixedText', nPosRes, y+85, 20, nHeight, Label = "", Align = 2)
        self.typo7_res = self._addWidget('typo7_res', 'FixedText', nPosRes, y+95, 20, nHeight, Label = "", Align = 2)
        self.typo8_res = self._addWidget('typo8_res', 'FixedText', nPosRes, y+105, 20, nHeight, Label = "", Align = 2)
        
        # group box // misc.
        x = 168; y = 140
        gbm5 = self._addWidget('groupbox5', 'GroupBox', x-5, y, nGroupBoxWith, 70, Label = "  " * len(self.dUI.get('misc', "#err")), FontDescriptor = xFD1)
        self.misc = self._addWidget('misc', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('misc', "#err"), FontDescriptor = xFD1, \
                                    FontRelief = 1, TextColor = nColor, State = True)
        self.misc1 = self._addWidget('misc1', 'CheckBox', x, y+15, 80, nHeight, Label = self.dUI.get('misc1', "#err"), State = True)
        self.misc1a = self._addWidget('misc1a', 'CheckBox', x+80, y+15, 30, nHeight, Label = self.dUI.get('misc1a', "#err"), State = True)
        self.misc2 = self._addWidget('misc2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('misc2', "#err"), State = True)
        self.misc3 = self._addWidget('misc3', 'CheckBox', x, y+35, nWidth, nHeight, Label = self.dUI.get('misc3', "#err"), State = True)
        #self.misc4 = self._addWidget('misc4', 'CheckBox', x, y+45, nWidth, nHeight, Label = self.dUI.get('misc4', "#err"), State = True)
        self.misc5 = self._addWidget('misc5', 'CheckBox', x, y+45, nWidth, nHeight, Label = self.dUI.get('misc5', "#err"), State = True)
        self.misc5b = self._addWidget('misc5b', 'CheckBox', x+10, y+55, nWidth-40, nHeight, Label = self.dUI.get('misc5b', "#err"), State = False)
        self.misc5c = self._addWidget('misc5c', 'CheckBox', x+nWidth-25, y+55, 30, nHeight, Label = self.dUI.get('misc5c', "#err"), State = False)
        self.misc1_res = self._addWidget('misc1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.misc2_res = self._addWidget('misc2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.misc3_res = self._addWidget('misc3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        #self.misc4_res = self._addWidget('misc4_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        self.misc5_res = self._addWidget('misc5_res', 'FixedText', nPosRes, y+45, 20, nHeight, Label = "", Align = 2)
        
        # group box // restructuration
        x = 168; y = 215
        gbm6 = self._addWidget('groupbox6', 'GroupBox', x-5, y, nGroupBoxWith, 50, Label = "  " * len(self.dUI.get('struct', "#err")), FontDescriptor = xFD1)
        self.struct = self._addWidget('struct', 'CheckBox', x, y+2, nWidth, nHeight, Label = self.dUI.get('struct', "#err"), FontDescriptor = xFD1, \
                                      FontRelief = 1, TextColor = nColor, HelpText = self.dUI.get('struct_help', "#err"), State = False)
        self.struct1 = self._addWidget('struct1', 'CheckBox', x, y+15, nWidth, nHeight, Label = self.dUI.get('struct1', "#err"), State = True, Enabled = False)
        self.struct2 = self._addWidget('struct2', 'CheckBox', x, y+25, nWidth, nHeight, Label = self.dUI.get('struct2', "#err"), State = True, Enabled = False)
        self.struct3 = self._addWidget('struct3', 'CheckBox', x, y+35, nWidth, nHeight, Label = self.dUI.get('struct3', "#err"), \
                                       HelpText = self.dUI.get('struct3_help', "#err"), State = False, Enabled = False)
        self.struct1_res = self._addWidget('struct1_res', 'FixedText', nPosRes, y+15, 20, nHeight, Label = "", Align = 2)
        self.struct2_res = self._addWidget('struct2_res', 'FixedText', nPosRes, y+25, 20, nHeight, Label = "", Align = 2)
        self.struct3_res = self._addWidget('struct3_res', 'FixedText', nPosRes, y+35, 20, nHeight, Label = "", Align = 2)
        
        # dialog height
        self.xDialog.Height = 292
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        # lists of checkbox widgets
        self.dCheckboxWidgets = {
            "ssp":      [self.ssp1, self.ssp2, self.ssp3, self.ssp4, self.ssp5, self.ssp6, self.ssp7],
            "space":    [self.space1, self.space2],
            "nbsp":     [self.nbsp1, self.nbsp2, self.nbsp3, self.nbsp4, self.nbsp5, self.nnbsp1, self.nnbsp2, self.nnbsp4],
            "delete":   [self.delete1, self.delete2, self.delete2a, self.delete2b, self.delete2c],
            "typo":     [self.typo1, self.typo2, self.typo3, self.typo3a, self.typo3b, self.typo4, self.typo4a, self.typo4b, self.typo5, self.typo6, \
                         self.typo7, self.typo8, self.typo8a, self.typo8b, self.typo_ff, self.typo_fi, self.typo_ffi, self.typo_fl, self.typo_ffl, \
                         self.typo_ft, self.typo_st],
            "misc":     [self.misc1, self.misc2, self.misc3, self.misc5, self.misc1a, self.misc5b, self.misc5c], #self.misc4, 
            "struct":   [self.struct1, self.struct2, self.struct3]
        }

        # progress bar
        self.pbar = self._addWidget('pbar', 'ProgressBar', 22, self.xDialog.Height-16, 215, 10)
        self.pbar.ProgressValueMin = 0
        self.pbar.ProgressValueMax = 31
        # time counter
        self.time_res = self._addWidget('time_res', 'FixedText', self.xDialog.Width-80, self.xDialog.Height-15, 20, nHeight, Label = "", Align = 2)

        # buttons
        self.bdefault = self._addWidget('default', 'Button', 5, self.xDialog.Height-19, 15, 15, Label = self.dUI.get('default', "#err"), \
                                        HelpText = self.dUI.get('default_help', "#err"), FontDescriptor = xFD2, TextColor = 0x444444)
        #self.bsel = self._addWidget('bsel', 'CheckBox', x, self.xDialog.Height-40, nWidth-55, nHeight, Label = self.dUI.get('bsel', "#err"))        
        self.bapply = self._addWidget('apply', 'Button', self.xDialog.Width-55, self.xDialog.Height-19, 50, 15, Label = self.dUI.get('apply', "#err"), \
                                      FontDescriptor = xFD2, TextColor = 0x004400)
        self.binfo = self._addWidget('info', 'Button', self.xDialog.Width-15, 0, 10, 9, Label = self.dUI.get('info', "#err"), \
                                     HelpText = self.dUI.get('infotitle', "#err"), FontDescriptor = xFDsmall, TextColor = 0x444444)

        # load configuration
        self._loadConfig()

        ## container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.setVisible(False)
        self.xContainer.getControl('info').addActionListener(self)
        self.xContainer.getControl('info').setActionCommand('Info')
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
                        self._saveConfig()
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
            elif xActionEvent.ActionCommand == 'Info':
                xDesktop = self.xSvMgr.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
                xDoc = xDesktop.getCurrentComponent()
                xWindow = xDoc.CurrentController.Frame.ContainerWindow
                MessageBox (xWindow, self.dUI.get('infomsg', "#err"), self.dUI.get('infotitle', "#err"))
            else:
                print("Wrong command: " + xActionEvent.ActionCommand)
        except:
            traceback.print_exc()

    def _loadConfig (self):
        try:
            if sys.version_info.major == 3:
                imp.reload(tf_options)
            else:
                reload(tf_options)
            self._setConfig(tf_options.dOpt)
        except:
            traceback.print_exc()

    def _setConfig (self, d):
        try:
            for key, val in d.items():
                w = getattr(self, key)
                w.State = val
                if key in self.dCheckboxWidgets:
                    self._switchCheckBox(w)
        except:
            raise

    def _saveConfig (self):
        try:
            # create options dictionary
            dOpt = {}
            for key, lWidget in self.dCheckboxWidgets.items():
                w = getattr(self, key)
                dOpt[w.Name] = w.State
                for w in lWidget:
                    dOpt[w.Name] = w.State
            # get extension path
            xDefaultContext = self.ctx.ServiceManager.DefaultContext
            xPackageInfoProvider = xDefaultContext.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
            sExtPath = xPackageInfoProvider.getPackageLocation("French.linguistic.resources.from.Dicollecte.by.OlivierR")
            sExtPath = sExtPath[8:] + "/pythonpath/tf_options.py"  # remove "file:///"
            sExtPath = os.path.abspath(sExtPath)
            # write file
            if os.path.isfile(sExtPath):
                hOpt = open(sExtPath, "w")
                hOpt.write("dDefaultOpt = " + str(tf_options.dDefaultOpt) + "\n")
                hOpt.write("dOpt = " + str(dOpt))
                hOpt.close()
        except:
            traceback.print_exc()

    def _switchCheckBox (self, wGroupCheckbox):
        for w in self.dCheckboxWidgets.get(wGroupCheckbox.Name, []):
            w.Enabled = wGroupCheckbox.State

    def _setApplyButtonLabel (self):
        if self.ssp.State or self.space.State or self.nbsp.State or self.delete.State or self.typo.State or self.misc.State or self.struct.State:
            self.bClose = False
            self.bapply.Label = self.dUI.get('apply', "#err")
            self.bapply.TextColor = 0x004400
        else:
            self.bClose = True
            self.bapply.Label = self.dUI.get('close', "#err")
            self.bapply.TextColor = 0x440000
        self.xContainer.setVisible(True)

    def _replaceAll (self, xElem):
        try:
            nStartTime = time.clock()
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
                    n = self._replaceText(xElem, "\\n", "\\n", True) # end of line => end of paragraph
                    self.struct1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.struct2.State:
                    n = self._replaceText(xElem, "([:alpha:])- *\n([:alpha:])", "$1$2", True)  # EOL
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
                    n = self._replaceText(xElem, "[  ]+$", "", True)
                    self.ssp3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp2.State:
                    n = self._replaceText(xElem, "  ", " ", False) # espace + espace insécable -> espace
                    n += self._replaceText(xElem, "  ", " ", False) # espace insécable + espace -> espace
                    n += self._replaceText(xElem, "  +", " ", True) # espaces surnuméraires
                    n += self._replaceText(xElem, "  +", " ", True) # espaces insécables surnuméraires
                    self.ssp2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp1.State:
                    n = self._replaceText(xElem, "^[  ]+", "", True)
                    self.ssp1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp4.State:
                    n = self._replaceText(xElem, " +(?=[.,…])", "", True)
                    self.ssp4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp5.State:
                    n = self._replaceText(xElem, "\\([  ]+", "(", True)
                    n += self._replaceText(xElem, "[  ]+\\)", ")", True)
                    self.ssp5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp6.State:
                    n = self._replaceText(xElem, "\\[[  ]+", "[", True)
                    n += self._replaceText(xElem, "[  ]+\\]", "]", True)
                    self.ssp6_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.ssp7.State:
                    n = self._replaceText(xElem, "“[  ]+", "“", True)
                    n += self._replaceText(xElem, "[  ]”", "”", True)
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
                        n = self._replaceText(xElem, "(?<=[:alnum:]);", " ;", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])[?][   ]", " ? ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])[?]$", " ?", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])!", " !", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}]);", " ;", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])[?][   ]", " ? ", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])[?]$", " ?", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])!", " !", True)
                        n += self._replaceText(xElem, "[  ]+([;?!])", " $1", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]):[   ]", " : ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]):$", " :", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}]):", " :", True)
                        n += self._replaceText(xElem, "[  ]+:", " :", True)
                    else:
                        # espaces insécables
                        n = self._replaceText(xElem, "(?<=[:alnum:]):[   ]", " : ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]):$", " :", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]);", " ;", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])[?][   ]", " ? ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])[?]$", " ?", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:])!", " !", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}]):", " :", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}]);", " ;", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])[?][   ]", " ? ", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])[?]$", " ?", True)
                        n += self._replaceText(xElem, "(?<=[]…)»}])!", " !", True)
                        n += self._replaceText(xElem, "[  ]+([:;?!])", " $1", True)
                    # réparations
                    n -= self._replaceText(xElem, "([[(])[   ]([!?:;])", "$1$2", True)
                    n -= self._replaceText(xElem, "(?<=http)[   ]://", "://", True)
                    n -= self._replaceText(xElem, "(?<=https)[   ]://", "://", True)
                    n -= self._replaceText(xElem, "(?<=ftp)[   ]://", "://", True)
                    n -= self._replaceText(xElem, "(?<=&)amp[   ];", "amp;", True)          
                    n -= self._replaceText(xElem, "(?<=&)nbsp[   ];", "nbsp;", True)
                    n -= self._replaceText(xElem, "(?<=&)lt[   ];", "lt;", True)
                    n -= self._replaceText(xElem, "(?<=&)gt[   ];", "gt;", True)
                    n -= self._replaceText(xElem, "(?<=&)apos[   ];", "apos;", True)
                    n -= self._replaceText(xElem, "(?<=&)quot[   ];", "quot;", True)
                    n -= self._replaceText(xElem, "(?<=&)thinsp[   ];", "thinsp;", True)
                    self.nbsp1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp2.State:
                    if self.nnbsp2.State:
                        # espaces insécables fines
                        n = self._replaceText(xElem, "«(?=[:alnum:])", "« ", True)
                        n += self._replaceText(xElem, "«[  ]+", "« ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]|[.!?])»", " »", True)
                        n += self._replaceText(xElem, "[  ]+»", " »", True)
                    else:
                        # espaces insécables
                        n = self._replaceText(xElem, "«(?=[:alnum:])", "« ", True)
                        n += self._replaceText(xElem, "«[  ]+", "« ", True)
                        n += self._replaceText(xElem, "(?<=[:alnum:]|[.!?])»", " »", True)
                        n += self._replaceText(xElem, "[  ]+»", " »", True)
                    self.nbsp2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp3.State:
                    n = self._replaceText(xElem, "([:digit:])([%‰€$£¥˚℃])", "$1 $2", True)
                    n += self._replaceText(xElem, "([:digit:]) ([%‰€$£¥˚℃])", "$1 $2", True)
                    self.nbsp3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp4.State:
                    if self.nnbsp4.State:
                        # espaces insécables fines
                        n = self._replaceText(xElem, "([:digit:])[  ]([:digit:])", "$1 $2", True)
                    else:
                        # espaces insécables
                        n = self._replaceText(xElem, "([:digit:])[  ]([:digit:])", "$1 $2", True)
                    self.nbsp4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.nbsp5.State:
                    n = self._replaceText(xElem, "(?<=[0-9⁰¹²³⁴⁵⁶⁷⁸⁹]) ?([kcmµnd]?(?:[slgJKΩΩℓ]|m[²³]?|Wh?|Hz|dB)|[%‰]|°C)\\b", " $1", True, True)
                    self.nbsp5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if False:
                    n = self._replaceText(xElem, "\\b(MM?\\.|Mlle|Mgr) ", "$1 ", True)
                    self.nbsp3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.nbsp.State = False
                self._switchCheckBox(self.nbsp)
            self.pbar.ProgressValue = 15
            # points médians
            if self.typo.State:
                if self.typo6.State:
                    n = self._replaceText(xElem, "\\bN\\.([ms])\\b", "N·$1", True, True) # N·m et N·m-1, N·s
                    n += self._replaceText(xElem, "\\bW\\.h\\b", "W·h", True, True)
                    n += self._replaceText(xElem, "\\bPa\\.s\\b", "Pa·s", True, True)
                    n += self._replaceText(xElem, "\\bA\\.h\\b", "A·h", True, True)
                    n += self._replaceText(xElem, "\\bΩ\\.m\\b", "Ω·m", True, True)
                    n += self._replaceText(xElem, "\\bS\\.m\\b", "S·m", True, True)
                    n += self._replaceText(xElem, "\\bg\\.s(?=-1)\\b", "g·s", True, True)
                    n += self._replaceText(xElem, "\\bm\\.s(?=-[12])\\b", "m·s", True, True)
                    n += self._replaceText(xElem, "\\bg\\.m(?=2|-3)\\b", "g·m", True, True)
                    n += self._replaceText(xElem, "\\bA\\.m(?=-1)\\b", "A·m", True, True)
                    n += self._replaceText(xElem, "\\bJ\\.K(?=-1)\\b", "J·K", True, True)
                    n += self._replaceText(xElem, "\\bW\\.m(?=-2)\\b", "W·m", True, True)
                    n += self._replaceText(xElem, "\\bcd\\.m(?=-2)\\b", "cd·m", True, True)
                    n += self._replaceText(xElem, "\\bC\\.kg(?=-1)\\b", "C·kg", True, True)
                    n += self._replaceText(xElem, "\\bH\\.m(?=-1)\\b", "H·m", True, True)
                    n += self._replaceText(xElem, "\\bJ\\.kg(?=-1)\\b", "J·kg", True, True)
                    n += self._replaceText(xElem, "\\bJ\\.m(?=-3)\\b", "J·m", True, True)
                    n += self._replaceText(xElem, "\\bm[2²]\\.s\\b", "m²·s", True, True)
                    n += self._replaceText(xElem, "\\bm[3³]\\.s(?=-1)\\b", "m³·s", True, True)
                    #n += self._replaceText(xElem, "\\bJ.kg-1.K-1\\b", "J·kg-1·K-1", True, True)
                    #n += self._replaceText(xElem, "\\bW.m-1.K-1\\b", "W·m-1·K-1", True, True)
                    #n += self._replaceText(xElem, "\\bW.m-2.K-1\\b", "W·m-2·K-1", True, True)
                    n += self._replaceText(xElem, "\\b(Y|Z|E|P|T|G|M|k|h|da|d|c|m|µ|n|p|f|a|z|y)Ω\\b", "$1Ω", True, True)
                    self.typo6_res.Label = str(n)
                    self.pbar.ProgressValue += 1
            # espaces manquants
            if self.space.State:
                if self.space1.State:
                    n = self._replaceText(xElem, ";(?=[:alnum:])", "; ", True)
                    n += self._replaceText(xElem, "\\?(?=[A-ZÉÈÊÂÀÎ])", "? ", True, True)
                    n += self._replaceText(xElem, "!(?=[:alnum:])", "! ", True)
                    n += self._replaceText(xElem, "…(?=[:alnum:])", "… ", True)
                    n += self._replaceText(xElem, "\\.(?=[A-ZÉÈÎ][:alpha:])", ". ", True, True)
                    n += self._replaceText(xElem, "\\.(?=À)", ". ", True, True)
                    n += self._replaceText(xElem, ",(?=[:alpha:])", ", ", True)
                    n += self._replaceText(xElem, "([:alpha:]),([0-9])", "$1, $2", True)
                    n += self._replaceText(xElem, ":(?=[:alpha:])", ": ", True)
                    # réparations
                    n -= self._replaceText(xElem, "(?<=DnT), w\\b", ",w", True, True)
                    n -= self._replaceText(xElem, "(?<=DnT), A\\b", ",A", True, True)
                    self.space1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.space2.State:
                    n = self._replaceText(xElem, " -(?=[:alpha:]|[\"«“'‘])", " - ", True)
                    n += self._replaceText(xElem, " –(?=[:alpha:]|[\"«“'‘])", " – ", True) # demi-cadratin
                    n += self._replaceText(xElem, " —(?=[:alpha:]|[\"«“'‘])", " — ", True) # cadratin
                    n += self._replaceText(xElem, "(?<=[:alpha:])– ", " – ", True)
                    n += self._replaceText(xElem, "(?<=[:alpha:])— ", " — ", True)
                    n += self._replaceText(xElem, "(?<=[:alpha:])- ", " - ", True)
                    n += self._replaceText(xElem, "(?<=[\"»”'’])– ", " – ", True)
                    n += self._replaceText(xElem, "(?<=[\"»”'’])— ", " — ", True)
                    n += self._replaceText(xElem, "(?<=[\"»”'’])- ", " - ", True)
                    self.space2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.space.State = False
                self._switchCheckBox(self.space)
            self.pbar.ProgressValue = 17
            # Suppression
            if self.delete.State:
                if self.delete1.State:
                    n = self._replaceText(xElem, "­", "", False) # tiret conditionnel / soft hyphen
                    self.delete1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.delete2.State:
                    n = self._replaceBulletsByEmDash(xElem)
                    self.delete2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                self.delete.State = False
                self._switchCheckBox(self.delete)
            self.pbar.ProgressValue = 20
            # signes typographiques
            if self.typo.State:
                if self.typo1.State:
                    n = self._replaceText(xElem, "\\bl['´‘′`](?=[:alnum:])", "l’", True, True)
                    n += self._replaceText(xElem, "\\bj['´‘′`](?=[:alnum:])", "j’", True, True)
                    n += self._replaceText(xElem, "\\bm['´‘′`](?=[:alnum:])", "m’", True, True)
                    n += self._replaceText(xElem, "\\bt['´‘′`](?=[:alnum:])", "t’", True, True)
                    n += self._replaceText(xElem, "\\bs['´‘′`](?=[:alnum:])", "s’", True, True)
                    n += self._replaceText(xElem, "\\bc['´‘′`](?=[:alnum:])", "c’", True, True)
                    n += self._replaceText(xElem, "\\bd['´‘′`](?=[:alnum:])", "d’", True, True)
                    n += self._replaceText(xElem, "\\bn['´‘′`](?=[:alnum:])", "n’", True, True)
                    n += self._replaceText(xElem, "\\bç['´‘′`](?=[:alnum:])", "ç’", True, True)
                    n += self._replaceText(xElem, "\\bL['´‘′`](?=[:alnum:])", "L’", True, True)
                    n += self._replaceText(xElem, "\\bJ['´‘′`](?=[:alnum:])", "J’", True, True)
                    n += self._replaceText(xElem, "\\bM['´‘′`](?=[:alnum:])", "M’", True, True)
                    n += self._replaceText(xElem, "\\bT['´‘′`](?=[:alnum:])", "T’", True, True)
                    n += self._replaceText(xElem, "\\bS['´‘′`](?=[:alnum:])", "S’", True, True)
                    n += self._replaceText(xElem, "\\bC['´‘′`](?=[:alnum:])", "C’", True, True)
                    n += self._replaceText(xElem, "\\bD['´‘′`](?=[:alnum:])", "D’", True, True)
                    n += self._replaceText(xElem, "\\bN['´‘′`](?=[:alnum:])", "N’", True, True)
                    n += self._replaceText(xElem, "\\bÇ['´‘′`](?=[:alnum:])", "Ç’", True, True)
                    n += self._replaceText(xElem, "(qu|jusqu|lorsqu|puisqu|quoiqu|quelqu|presqu|entr|aujourd|prud)['´‘′`]", "$1’", True)
                    self.typo1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo2.State:
                    n = self._replaceText(xElem, "...", "…", False)
                    n += self._replaceText(xElem, "(?<=…)[.][.]", "…", True)
                    n += self._replaceText(xElem, "…[.](?![.])", "…", True)
                    self.typo2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo3.State:
                    if self.typo3b.State:
                        # demi-cadratin
                        n = self._replaceText(xElem, " - ", " – ", False)
                        n += self._replaceText(xElem, " — ", " – ", False)
                        n += self._replaceText(xElem, " -,", " –,", False)
                        n += self._replaceText(xElem, " —,", " –,", False)
                    else:
                        # cadratin
                        n = self._replaceText(xElem, " - ", " — ", False)
                        n += self._replaceText(xElem, " – ", " — ", False)
                        n += self._replaceText(xElem, " -,", " —,", False)
                        n += self._replaceText(xElem, " –,", " —,", False)
                    self.typo3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo4.State:
                    if self.typo4a.State:
                        # cadratin
                        n = self._replaceText(xElem, "^-[  ]", "— ", True)
                        n += self._replaceText(xElem, "^–[  ]", "— ", True)
                        n += self._replaceText(xElem, "^— ", "— ", True)
                        n += self._replaceText(xElem, "^«[  ][—–-][  ]", "« — ", True)
                        n += self._replaceText(xElem, "^[-–—](?=[:alnum:])", "— ", True)
                    else:
                        # demi-cadratin
                        n = self._replaceText(xElem, "^-[  ]", "– ", True)
                        n += self._replaceText(xElem, "^—[  ]", "– ", True)
                        n += self._replaceText(xElem, "^– ", "– ", True)
                        n += self._replaceText(xElem, "^[-–—](?=[:alnum:])", "– ", True)
                    self.typo4_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo5.State:
                    n = self._replaceText(xElem, '"([:alpha:]+)"', "“$1”", True)
                    n += self._replaceText(xElem, "''([:alpha:]+)''", "“$1”", True)
                    n += self._replaceText(xElem, "'([:alpha:]+)'", "“$1”", True)
                    n += self._replaceText(xElem, '^"(?=[:alnum:])', "« ", True)
                    n += self._replaceText(xElem, "^''(?=[:alnum:])", "« ", True)
                    n += self._replaceText(xElem, ' "(?=[:alnum:])', " « ", True)
                    n += self._replaceText(xElem, " ''(?=[:alnum:])", " « ", True)
                    n += self._replaceText(xElem, '\\("(?=[:alnum:])', "(« ", True)
                    n += self._replaceText(xElem, "\\(''(?=[:alnum:])", "(« ", True)
                    n += self._replaceText(xElem, '(?<=[:alnum:])"$', " »", True)
                    n += self._replaceText(xElem, "(?<=[:alnum:])''$", " »", True)
                    n += self._replaceText(xElem, '(?<=[:alnum:])"(?=[] ,.:;?!…)])', " »", True)
                    n += self._replaceText(xElem, "(?<=[:alnum:])''(?=[] ,.:;?!…)])", " »", True)
                    n += self._replaceText(xElem, '(?<=[.!?…])" ', " » ", True)
                    n += self._replaceText(xElem, '(?<=[.!?…])"$', " »", True)
                    self.typo5_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.typo7.State:
                    # ligatures: no initial cap
                    n = self._replaceText(xElem, "coeur", "cœur", False, True)
                    n += self._replaceText(xElem, "coel([aeio])", "cœl$1", True, True)
                    n += self._replaceText(xElem, "choeur", "chœur", False, True)
                    n += self._replaceText(xElem, "foet", "fœt", False, True)
                    n += self._replaceText(xElem, "oeil", "œil", False, True)
                    n += self._replaceText(xElem, "oeno", "œno", False, True)
                    n += self._replaceText(xElem, "oesoph", "œsoph", False, True)
                    n += self._replaceText(xElem, "oestro", "œstro", False, True)
                    n += self._replaceText(xElem, "oeuf", "œuf", False, True)
                    n += self._replaceText(xElem, "oeuvr", "œuvr", False, True)
                    n += self._replaceText(xElem, "moeur", "mœur", False, True)
                    n += self._replaceText(xElem, "noeu", "nœu", False, True)
                    n += self._replaceText(xElem, "soeur", "sœur", False, True)
                    n += self._replaceText(xElem, "voeu", "vœu", False, True)
                    n += self._replaceText(xElem, "aequo", "æquo", False, True)
                    # ligatures: with initial cap
                    n += self._replaceText(xElem, "Coeur", "Cœur", False, True)
                    n += self._replaceText(xElem, "Coel([aeio])", "Cœl$1", True, True)
                    n += self._replaceText(xElem, "Choeur", "Chœur", False, True)
                    n += self._replaceText(xElem, "Foet", "Fœt", False, True)
                    n += self._replaceText(xElem, "Oeil", "Œil", False, True)
                    n += self._replaceText(xElem, "Oeno", "Œno", False, True)
                    n += self._replaceText(xElem, "Oesoph", "Œsoph", False, True)
                    n += self._replaceText(xElem, "Oestro", "Œstro", False, True)
                    n += self._replaceText(xElem, "Oeuf", "Œuf", False, True)
                    n += self._replaceText(xElem, "Oeuvr", "Œuvr", False, True)
                    n += self._replaceText(xElem, "Moeur", "Mœur", False, True)
                    n += self._replaceText(xElem, "Noeu", "Nœu", False, True)
                    n += self._replaceText(xElem, "Soeur", "Sœur", False, True)
                    n += self._replaceText(xElem, "Voeu", "Vœu", False, True)
                    n += self._replaceText(xElem, "Aequo", "Æquo", False, True)
                    # common words with missing diacritics
                    n += self._replaceText(xElem, "\\bCa\\b", "Ça", True, True)
                    n += self._replaceText(xElem, " ca\\b", " ça", True, True)
                    n += self._replaceText(xElem, "\\bdej[aà]\\b", "déjà", True, True)
                    n += self._replaceText(xElem, "\\bDej[aà]\\b", "Déjà", True, True)
                    n += self._replaceText(xElem, "\\bplutot\\b", "plutôt", True, True)
                    n += self._replaceText(xElem, "\\bPlutot\\b", "Plutôt", True, True)
                    n += self._replaceText(xElem, "\\b([cC]e(?:ux|lles?|lui))-la\\b", "$1-là", True, True)
                    n += self._replaceText(xElem, "\\bmalgre\\b", "malgré", True, True)
                    n += self._replaceText(xElem, "\\bMalgre\\b", "Malgré", True, True)
                    n += self._replaceText(xElem, "\\betre\\b", "être", True, True)
                    n += self._replaceText(xElem, "\\bEtre\\b", "Être", True, True)
                    n += self._replaceText(xElem, "\\btres\\b", "très", True, True)
                    n += self._replaceText(xElem, "\\bTres\\b", "Très", True, True)
                    n += self._replaceText(xElem, "\\bEtai([ts]|ent)\\b", "Étai$1", True, True)
                    n += self._replaceText(xElem, "\\bE(tat|cole|crit|poque|tude|ducation|glise|conomi(?:qu|)e|videmment|lysée|tienne|thiopie|cosse|gypt(?:e|ien)|rythrée|pinal|vreux)", "É$1", True, True)
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
            self.pbar.ProgressValue = 28
            # divers
            if self.misc.State:
                if self.misc1.State:
                    if self.misc1a.State:
                        n = self._replaceText(xElem, "(?<=\\b[0-9][0-9][0-9][0-9])(i?[èe]me|è|e)\\b", "ᵉ", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9][0-9][0-9])(i?[èe]me|è|e)\\b", "ᵉ", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9][0-9])(i?[èe]me|è|e)\\b", "ᵉ", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9])(i?[èe]me|è|e)\\b", "ᵉ", True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL][XVICL][XVICL])(i?[èe]me|è|e)\\b", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL][XVICL])(i?[èe]me|è|e)\\b", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL])(i?[èe]me|è|e)\\b", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL])(i?[èe]me|è)\\b", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b(au|l[ea]|du) [XVICL])e\\b", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVI])e(?= siècle)", "ᵉ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[1I])er\\b", "ᵉʳ", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[1I])re\\b", "ʳᵉ", True, True)
                    else:
                        n = self._replaceText(xElem, "(?<=\\b[0-9][0-9][0-9][0-9])(i?[èe]me|è|ᵉ)\\b", "e", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9][0-9][0-9])(i?[èe]me|è|ᵉ)\\b", "e", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9][0-9])(i?[èe]me|è|ᵉ)\\b", "e", True)
                        n += self._replaceText(xElem, "(?<=\\b[0-9])(i?[èe]me|è|ᵉ)\\b", "e", True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL][XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b", "e", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b", "e", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b", "e", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[XVICL])(i?[èe]me|è|ᵉ)\\b", "e", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[1I])ᵉʳ\\b", "er", True, True)
                        n += self._replaceText(xElem, "(?<=\\b[1I])ʳᵉ\\b", "er", True, True)
                    self.misc1_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc2.State:
                    n = self._replaceText(xElem, "etc(…|[.][.][.]?)", "etc.", True, True)
                    n += self._replaceText(xElem, "(?<!,) etc[.]", ", etc.", True, True)
                    self.misc2_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc3.State:
                    n = self._replaceText(xElem, "[ -]t[’'](?=il\\b|elle|on\\b)", "-t-", True)
                    n += self._replaceText(xElem, " t-(?=il|elle|on)", "-t-", True)
                    n += self._replaceText(xElem, "[ -]t[’'-](?=ils|elles)", "-", True)
                    n += self._replaceText(xElem, "(?<=[td])-t-(?=il|elle|on)", "-", True)
                    n += self._replaceText(xElem, "(celles?|celui|ceux) (ci|là)\\b", "$1-$2", True)
                    n += self._replaceText(xElem, "\\bdix (sept|huit|neuf)", "dix-$1", True)
                    n += self._replaceText(xElem, "quatre vingt", "quatre-vingt", False)
                    n += self._replaceText(xElem, "(soixante|quatre-vingt) dix", "$1-dix", True)
                    n += self._replaceText(xElem, "(vingt|trente|quarante|cinquante|soixante(?:-dix|)|quatre-vingt(?:-dix|)) (deux|trois|quatre|cinq|six|sept|huit|neuf)", "$1-$2", True)
                    n += self._replaceText(xElem, "(?<!-)\\b(ci) (joint|desso?us|contre|devant|avant|après|incluse|g[îi]t|gisent)", "$1-$2", True)
                    n += self._replaceText(xElem, "\\bvis à vis", "vis-à-vis", False, True)
                    n += self._replaceText(xElem, "\\bVis à vis", "Vis-à-vis", False, True)
                    n += self._replaceText(xElem, "week end", "week-end", False, True)
                    n += self._replaceText(xElem, "Week end", "Week-end", False, True)
                    n += self._replaceText(xElem, "(plus|moins) value", "$1-value", True)
                    self.misc3_res.Label = str(n)
                    self.pbar.ProgressValue += 1
                if self.misc5.State:
                    n = self._replaceText(xElem, "(qu|lorsqu|puisqu|quoiqu|presqu|jusqu|aujourd|entr|quelqu) ", "$1’", True, True)
                    if self.misc5b.State:
                        n += self._replaceText(xElem, "\\bj (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "j’", True, True)
                        n += self._replaceText(xElem, "\\bn (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "n’", True, True)
                        n += self._replaceText(xElem, "\\bm (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "m’", True, True)
                        n += self._replaceText(xElem, "\\bt (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "t’", True, True)
                        n += self._replaceText(xElem, "\\bs (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "s’", True, True)
                        n += self._replaceText(xElem, "\\bc (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "c’", True, True)
                        n += self._replaceText(xElem, "\\bç (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "ç’", True, True)
                        n += self._replaceText(xElem, "\\bl (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "l’", True, True)
                        n += self._replaceText(xElem, "\\bd (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "d’", True, True)
                        if self.misc5c.State:
                            n += self._replaceText(xElem, "\\bJ (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "J’", True, True)
                            n += self._replaceText(xElem, "\\bN (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "N’", True, True)
                            n += self._replaceText(xElem, "\\bM (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "M’", True, True)
                            n += self._replaceText(xElem, "\\bT (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "T’", True, True)
                            n += self._replaceText(xElem, "\\bS (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "S’", True, True)
                            n += self._replaceText(xElem, "\\bC (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "C’", True, True)
                            n += self._replaceText(xElem, "\\bÇ (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "Ç’", True, True)
                            n += self._replaceText(xElem, "\\bL (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "L’", True, True)
                            n += self._replaceText(xElem, "\\bD (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "D’", True, True)
                    self.misc5_res.Label = str(n)
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
            nEndTime = time.clock()
            self.time_res.Label = getTimeRes(nEndTime-nStartTime)
        except:
            traceback.print_exc()

    def _replaceText (self, xElem, sPattern, sRep, bRegex, bCaseSensitive=False):
        try:
            xRD = xElem.createReplaceDescriptor()
            xRD.SearchString = sPattern
            xRD.ReplaceString = sRep
            xRD.SearchRegularExpression = bRegex
            xRD.SearchCaseSensitive = bCaseSensitive
            return xElem.replaceAll(xRD)
        except:
            traceback.print_exc()
        return 0

    def _replaceHyphenAtEndOfParagraphs (self, xDoc):
        self._replaceText(xDoc, "-[  ]+$", "-", True) # remove spaces at end of paragraphs if - is the last character
        xHunspell = self.xSvMgr.createInstanceWithContext("com.sun.star.linguistic2.SpellChecker", self.ctx)
        xCursor = xDoc.Text.createTextCursor()
        xCursor.gotoStart(False)
        n = 0
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
        return n

    def _mergeContiguousParagraphs (self, xDoc):
        self._replaceText(xDoc, "^[  ]+$", "", True) # clear empty paragraphs
        xCursor = xDoc.Text.createTextCursor()
        xCursor.gotoStart(False)
        n = 0
        try:
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
        helpers.xray(xCursor)
        xCursor.gotoStart(False)
        sParaStyleName = ""
        if not self.delete2c.State:
            sParaStyleName = "Standard"  if self.delete2a.State  else "Text body"
        n = 0
        try:
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
