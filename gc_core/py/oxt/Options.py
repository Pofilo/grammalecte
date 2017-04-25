# -*- coding: utf8 -*-
# Options Dialog
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback

from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue

import helpers
import op_strings

try:
    import grammalecte.${lang} as gce
except:
    traceback.print_exc()


options = {}


def load (ctx):
    try:
        oGCO = GC_Options(ctx)
        oGCO.load("${lang}")
    except:
        print("# Error. Unable to load options of language: ${lang}")
    return options


class GC_Options (unohelper.Base, XActionListener):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None
        #self.xNode = helpers.getConfigSetting("/org.openoffice.Lightproof_%s/Leaves"%pkg, True)
        self.xNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Leaves", True)
        self.nSecret = 0
        
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

    def run (self, sUI):
        try:
            dUI = op_strings.getUI(sUI)
            dUI2 = gce.gc_options.getUI(sUI)

            # fonts
            xFDTitle = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFDTitle.Height = 9
            xFDTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFDTitle.Name = "Verdana"

            xFDBut = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFDBut.Height = 10
            xFDBut.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFDBut.Name = "Verdana"

            # dialog
            self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
            self.xDialog.Width = 300
            self.xDialog.Height = 400
            self.xDialog.Title = dUI.get('title', "#err")

            # build
            y = 0
            nWidth = self.xDialog.Width - 20
            nHeight = 10
            
            self.lxOptions = []

            for t in gce.gc_options.lStructOpt:
                x = 10
                y += 10
                self._addWidget(t[0], 'FixedLine', x, y, nWidth, nHeight, Label = dUI2.get(t[0], "#err")[0], FontDescriptor= xFDTitle)
                y += 3
                for lOptLine in t[1]:
                    x = 15
                    y += 10
                    n = len(lOptLine)
                    for sOpt in lOptLine:
                        w = self._addWidget(sOpt, 'CheckBox', x, y, nWidth/n, nHeight, State = options.get(sOpt, False), \
                                            Label = dUI2.get(sOpt, "#err")[0], HelpText = dUI2.get(sOpt, "#err")[1])
                        self.lxOptions.append(w)
                        x += nWidth / n
            
            self.xDialog.Height = y + 40

            xWindowSize = helpers.getWindowSize()
            self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
            self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

            but0 = self._addWidget('default', 'Button', 10, self.xDialog.Height-20, 50, 14, \
                                   Label = dUI.get('default', "#err"), FontDescriptor = xFDBut, TextColor = 0x000044)
            but1 = self._addWidget('apply', 'Button', self.xDialog.Width-115, self.xDialog.Height-20, 50, 14, \
                                   Label = dUI.get('apply', "#err"), FontDescriptor = xFDBut, TextColor = 0x004400)
            but2 = self._addWidget('cancel', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14,
                                   Label = dUI.get('cancel', "#err"), FontDescriptor = xFDBut, TextColor = 0x440000)

            # container
            self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
            self.xContainer.setModel(self.xDialog)
            self.xContainer.getControl('default').addActionListener(self)
            self.xContainer.getControl('default').setActionCommand('Default')
            self.xContainer.getControl('apply').addActionListener(self)
            self.xContainer.getControl('apply').setActionCommand('Apply')
            self.xContainer.getControl('cancel').addActionListener(self)
            self.xContainer.getControl('cancel').setActionCommand('Cancel')
            self.xContainer.setVisible(False)
            xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
            self.xContainer.createPeer(xToolkit, None)
            self.xContainer.execute()
        except:
            traceback.print_exc()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == 'Default':
                self._setDefault()
            elif xActionEvent.ActionCommand == 'Apply':
                self._save("fr")
                self.xContainer.endExecute()
            elif xActionEvent.ActionCommand == 'Cancel':
                self.xContainer.endExecute()
            else:
                print("Wrong command: " + xActionEvent.ActionCommand)
        except:
            traceback.print_exc()

    def _setDefault (self):
        for w in self.lxOptions:
            w.State = gce.gc_options.dOpt.get(w.Name, False)

    def load (self, sLang):
        try:
            xChild = self.xNode.getByName(sLang)
            for sKey in gce.gc_options.dOpt:
                sValue = xChild.getPropertyValue(sKey)
                if sValue == '':
                    if gce.gc_options.dOpt[sKey]:
                        sValue = 1
                    else:
                        sValue = 0
                options[sKey] = bool(int(sValue))
        except:
            traceback.print_exc()

    def _save (self, sLang):
        try:
            xChild = self.xNode.getByName(sLang)
            for w in self.lxOptions:
                sKey = w.Name
                bValue = w.State
                xChild.setPropertyValue(sKey, str(bValue))
                options[sKey] = bValue
                gce.setOptions(options)
            self.xNode.commitChanges()
        except:
            traceback.print_exc()
