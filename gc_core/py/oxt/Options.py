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


def loadOptions (sLang):
    "load options from Grammalecte and change them according to LibreOffice settings, returns a dictionary {option_name: boolean}"
    try:
        xNode = helpers.getConfigSetting("/org.openoffice.Lightproof_${implname}/Leaves", False)
        xChild = xNode.getByName(sLang)
        dOpt = gce.gc_options.getOptions("Writer")
        for sKey in dOpt:
            sValue = xChild.getPropertyValue(sKey)
            if sValue != '':
                dOpt[sKey] = bool(int(sValue))
        return dOpt
    except:
        print("# Error. Unable to load options of language:", sLang)
        traceback.print_exc()
        return gce.gc_options.getOptions("Writer")


def saveOptions (sLang, dOpt):
    "save options in LibreOffice profile"
    try:
        xNode = helpers.getConfigSetting("/org.openoffice.Lightproof_${implname}/Leaves", True)
        xChild = xNode.getByName(sLang)
        for sKey, value in dOpt.items():
            xChild.setPropertyValue(sKey, value)
        xNode.commitChanges()
    except:
        traceback.print_exc()


class GC_Options (unohelper.Base, XActionListener):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None

    def _addWidget (self, name, wtype, x, y, w, h, **kwargs):
        if wtype.startswith("com."):
            xWidget = self.xDialog.createInstance(wtype)
        else:
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
            dOptionUI = gce.gc_options.getUI(sUI)

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

            self.lOptionWidgets = []

            sProdName, sVersion = helpers.getProductNameAndVersion()
            if True:
                # no tab available (bug)
                for sOptionType, lOptions in gce.gc_options.lStructOpt:
                    x = 10
                    y += 10
                    self._addWidget(sOptionType, 'FixedLine', x, y, nWidth, nHeight, Label = dOptionUI.get(sOptionType, "#err")[0], FontDescriptor= xFDTitle)
                    y += 3
                    for lOptLine in lOptions:
                        x = 15
                        y += 10
                        n = len(lOptLine)
                        for sOpt in lOptLine:
                            sLabel, sHelpText = dOptionUI.get(sOpt, "#err")
                            xOpt = self._addWidget(sOpt, 'CheckBox', x, y, nWidth//n, nHeight, Label = sLabel, HelpText = sHelpText)
                            self.lOptionWidgets.append(xOpt)
                            x += nWidth // n
                self.xDialog.Height = y + 40
            else:
                # we can use tabs
                print("1")
                xTabPageContainer = self._addWidget("tabs", "com.sun.star.awt.tab.UnoControlTabPageContainerModel", 10, 10, nWidth, 100)
                xTabPage1 = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.tab.UnoControlTabPageModel', self.ctx)
                xTabPage2 = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.tab.UnoControlTabPageModel', self.ctx)
                #xTabPage1 = xTabPageContainer.createTabPage(1)
                #xTabPage2 = xTabPageContainer.createTabPage(2)
                xTabPage1.Title = "Page 1"
                xTabPage2.Title = "Page 2"
                xTabPageContainer.insertByIndex(0, xTabPage1)
                xTabPageContainer.insertByIndex(1, xTabPage2)
                self.xDialog.Height = 300

            xWindowSize = helpers.getWindowSize()
            self.xDialog.PositionX = int((xWindowSize.Width // 2) - (self.xDialog.Width // 2))
            self.xDialog.PositionY = int((xWindowSize.Height // 2) - (self.xDialog.Height // 2))

            self._addWidget('default', 'Button', 10, self.xDialog.Height-20, 50, 14, \
                            Label = dUI.get('default', "#err"), FontDescriptor = xFDBut, TextColor = 0x000044)
            self._addWidget('apply', 'Button', self.xDialog.Width-115, self.xDialog.Height-20, 50, 14, \
                            Label = dUI.get('apply', "#err"), FontDescriptor = xFDBut, TextColor = 0x004400)
            self._addWidget('cancel', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14,
                            Label = dUI.get('cancel', "#err"), FontDescriptor = xFDBut, TextColor = 0x440000)

            dOpt = loadOptions("${lang}")
            self._setWidgets(dOpt)

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
                self._setWidgets(gce.gc_options.getOptions("Writer"))
            elif xActionEvent.ActionCommand == 'Apply':
                self._save("${lang}")
                self.xContainer.endExecute()
            elif xActionEvent.ActionCommand == 'Cancel':
                self.xContainer.endExecute()
            else:
                print("Wrong command: " + xActionEvent.ActionCommand)
        except:
            traceback.print_exc()

    # Other
    def _setWidgets (self, dOpt):
        for w in self.lOptionWidgets:
            w.State = dOpt.get(w.Name, False)

    def _save (self, sLang):
        try:
            saveOptions(sLang, { w.Name: str(w.State)  for w in self.lOptionWidgets })
            gce.setOptions({ w.Name: bool(w.State)  for w in self.lOptionWidgets })
        except:
            traceback.print_exc()
