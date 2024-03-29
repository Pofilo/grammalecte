# Modify author field
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import re
import traceback

import ca_strings as ui
import helpers

from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue


class Author (unohelper.Base, XActionListener):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None

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
        try:
            ui.selectLang(sLang)

            # dialog
            self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
            self.xDialog.Width = 160
            self.xDialog.Height = 85
            self.xDialog.Title = ui.get('title')
            xWindowSize = helpers.getWindowSize()
            self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
            self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

            # fonts
            xFDBut = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFDBut.Height = 10
            xFDBut.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFDBut.Name = "Verdana"

            # document
            xDesktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
            self.xDoc = xDesktop.getCurrentComponent()
            sAuthor = self.xDoc.DocumentProperties.Author  if self.xDoc.DocumentProperties.Author  else  ui.get('empty')

            # widgets
            nTextWidth = self.xDialog.Width - 20
            state = self._addWidget('state', 'FixedText', 10, 10, nTextWidth, 10, Label = ui.get('state'))
            value = self._addWidget('value', 'FixedText', 10, 20, nTextWidth, 10, Label = sAuthor, FontSlant = 2, TextColor = 0x559999)

            inputlbl = self._addWidget('inputlbl', 'FixedText', 10, 34, nTextWidth, 10, Label = ui.get('newvalue'))
            self.inputtxt = self._addWidget('input', 'Edit', 10, 45, nTextWidth-20, 12, Text=self.xDoc.DocumentProperties.Author, MaxTextLen=150)
            but0 = self._addWidget('reset', 'Button', self.xDialog.Width-25, 45, 15, 12, Label = "×", FontDescriptor = xFDBut, TextColor = 0xBB5555)

            but1 = self._addWidget('modify', 'Button', self.xDialog.Width-115, self.xDialog.Height-20, 50, 14, \
                                   Label = ui.get('modify'), FontDescriptor = xFDBut, TextColor = 0x55BB55)
            but2 = self._addWidget('cancel', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14, \
                                   Label = ui.get('cancel'), FontDescriptor = xFDBut, TextColor = 0xBB5555)

            # container
            self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
            self.xContainer.setModel(self.xDialog)
            self.xContainer.getControl('reset').addActionListener(self)
            self.xContainer.getControl('reset').setActionCommand('Reset')
            self.xContainer.getControl('modify').addActionListener(self)
            self.xContainer.getControl('modify').setActionCommand('Modify')
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
            if xActionEvent.ActionCommand == 'Reset':
                self.inputtxt.Text = ""
            elif xActionEvent.ActionCommand == 'Modify':
                self.xDoc.DocumentProperties.Author = self.inputtxt.Text.strip()
                self.xContainer.endExecute()
            elif xActionEvent.ActionCommand == 'Cancel':
                self.xContainer.endExecute()
            else:
                print("Wrong command: " + xActionEvent.ActionCommand)
        except:
            traceback.print_exc()
