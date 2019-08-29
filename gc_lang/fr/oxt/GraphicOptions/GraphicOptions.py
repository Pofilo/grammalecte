# Graphic Options
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import re
import traceback

import helpers
import go_strings

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue


class GraphicOptions (unohelper.Base, XActionListener, XJobExecutor):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
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

    def run (self, sLang):
        self.dUI = go_strings.getUI(sLang)

        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xGLOptionNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Other/", True)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 200
        self.xDialog.Height = 220
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
        xFDSubTitle.Height = 10
        xFDSubTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDSubTitle.Name = "Verdana"

        # widget
        nX = 10
        nY1 = 10
        nY2 = nY1 + 45
        nY3 = nY2 + 55
        nY4 = nY3 + 65

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # Info
        self._addWidget("graphic_info", 'FixedText', nX, nY1, nWidth, nHeight*2, Label = self.dUI.get("graphic_info", "#err"), MultiLine = True, FontDescriptor = xFDSubTitle)
        self._addWidget("spell_info", 'FixedText', nX, nY1+20, nWidth, nHeight*2, Label = self.dUI.get("spell_info", "#err"), MultiLine = True)

        # Line type
        self._addWidget('linetype_section', 'FixedLine', nX, nY2, nWidth, nHeight, Label = self.dUI.get('linetype_section', "#err"), FontDescriptor = xFDTitle)
        self.xWaveLine = self._addWidget('wave_line', 'RadioButton', nX, nY2+15, nWidth, nHeight, Label = self.dUI.get('wave_line', "#err"))
        self.xBoldWaveLine = self._addWidget('boldwave_line', 'RadioButton', nX, nY2+25, nWidth, nHeight, Label = self.dUI.get('boldwave_line', "#err"))
        self.xBoldLine = self._addWidget('bold_line', 'RadioButton', nX, nY2+35, nWidth, nHeight, Label = self.dUI.get('bold_line', "#err"))

        # Color
        self._addWidget("color_section", 'FixedLine', nX, nY3, nWidth, nHeight, Label = self.dUI.get("color_section", "#err"), FontDescriptor = xFDTitle)
        self.xMulticolor = self._addWidget('multicolor_line', 'CheckBox', nX, nY3+15, nWidth, nHeight, Label = self.dUI.get('multicolor_line', "#err"))
        self._addWidget('multicolor_descr', 'FixedText', nX, nY3+25, nWidth, nHeight*4, Label = self.dUI.get('multicolor_descr', "#err"), MultiLine = True)

        # Restart message
        self._addWidget('restart', 'FixedText', nX, nY4, nWidth, nHeight*2, Label = self.dUI.get('restart', "#err"), FontDescriptor = xFDTitle, MultiLine = True, TextColor = 0x880000)

        # Button
        self._addWidget('apply_button', 'Button', self.xDialog.Width-115, self.xDialog.Height-20, 50, 14, Label = self.dUI.get('apply_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x005500)
        self._addWidget('cancel_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14, Label = self.dUI.get('cancel_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        self._loadOptions()

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.getControl('apply_button').addActionListener(self)
        self.xContainer.getControl('apply_button').setActionCommand('Apply')
        self.xContainer.getControl('cancel_button').addActionListener(self)
        self.xContainer.getControl('cancel_button').setActionCommand('Cancel')
        self.xContainer.setVisible(False)
        toolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(toolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        if xActionEvent.ActionCommand == 'Apply':
            try:
                # Grammalecte options
                xChild = self.xGLOptionNode.getByName("o_fr")
                xChild.setPropertyValue("line_multicolor", self.xMulticolor.State)
                if self.xWaveLine.State:
                    sLineType = "WAVE"
                elif self.xBoldWaveLine.State:
                    sLineType = "BOLDWAVE"
                elif self.xBoldLine.State:
                    sLineType = "BOLD"
                else:
                    sLineType = "BOLDWAVE"
                xChild.setPropertyValue("line_type", sLineType)
                self.xGLOptionNode.commitChanges()
            except:
                traceback.print_exc()
        # Close window
        self.xContainer.endExecute()

    # XJobExecutor
    def trigger (self, args):
        try:
            dialog = GraphicOptions(self.ctx)
            dialog.run()
        except:
            traceback.print_exc()

    def _loadOptions (self):
        try:
            xChild = self.xGLOptionNode.getByName("o_fr")
            self.xMulticolor.State = xChild.getPropertyValue("line_multicolor")
            sLineType = xChild.getPropertyValue("line_type")
            if sLineType == "WAVE":
                self.xWaveLine.State = 1
            elif sLineType == "BOLDWAVE":
                self.xBoldWaveLine.State = 1
            elif sLineType == "BOLD":
                self.xBoldLine.State = 1
            else:
                print("Error. Unknown line type: " + sLineType)
        except:
            traceback.print_exc()


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(GraphicOptions, 'net.grammalecte.GraphicOptions', ('com.sun.star.task.Job',))
