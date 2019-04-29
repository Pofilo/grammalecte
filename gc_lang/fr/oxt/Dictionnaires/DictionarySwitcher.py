# French Dictionary Switcher
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import re
import traceback

import helpers
import ds_strings

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue


class FrenchDictionarySwitcher (unohelper.Base, XActionListener, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None
        self.xDialog = None
        self.xRB_m = None
        self.xRB_c = None
        self.xRB_r = None
        self.xRB_f = None
        self.sCurrentDic = ''
        self.sSelectedDic = ''

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
        dUI = ds_strings.getUI(sLang)

        # what is the current dictionary
        xSettings = helpers.getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", False)
        xLocations = xSettings.getByName("Locations")
        m = re.search(r"fr-(\w*)\.(?:dic|aff)", xLocations[0])
        self.sCurrentDic = m.group(1)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 200
        self.xDialog.Height = 290
        self.xDialog.Title = dUI.get('title', "#title#")
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        # xWidgets
        padding = 10
        hspace = 60
        posY1 = 20; posY2 = posY1 + hspace; posY3 = posY2 + hspace; posY4 = posY3 + hspace; posY5 = posY4 + hspace + 10;
        nLblWidth = 170
        nLblHeight = 20
        nDescWidth = 170
        nDescHeight = 40

        xFD1 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD1.Height = 12
        xFD1.Name = "Verdana"

        xFD2 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD2.Height = 11
        xFD2.Name = "Verdana"

        xFD3 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD3.Height = 10
        xFD3.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFD3.Name = "Verdana"

        gbm = self._addWidget('groupbox', 'GroupBox', 5, 5, 190, 260, Label = dUI.get('choose', "#choose#"), FontDescriptor = xFD1, FontRelief = 1, TextColor = 0xAA2200)

        # Note: the only way to group RadioButtons is to create them successively
        rbm_m = self._addWidget('rb-moderne', 'RadioButton', padding, posY1, nLblWidth, nLblHeight, Label = dUI.get('moderne', "#moderne#"), FontDescriptor = xFD2, FontRelief = 1, TextColor = 0x0022AA)
        self.xRB_m = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_m.setModel(rbm_m)
        rbm_c = self._addWidget('rb-classique', 'RadioButton', padding, posY2, nLblWidth, nLblHeight, Label = dUI.get('classique', "#classique#"), FontDescriptor = xFD2, FontRelief = 1, TextColor = 0x0022AA)
        self.xRB_c = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_c.setModel(rbm_c)
        rbm_r = self._addWidget('rb-reforme1990', 'RadioButton', padding, posY3, nLblWidth, nLblHeight, Label = dUI.get('reforme1990', "#reforme1990#"), FontDescriptor = xFD2, FontRelief = 1, TextColor = 0x0022AA)
        self.xRB_r = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_r.setModel(rbm_r)
        rbm_t = self._addWidget('rb-toutesvariantes', 'RadioButton', padding, posY4, nLblWidth, nLblHeight, Label = dUI.get('toutesvariantes', "#toutesvariantes#"), FontDescriptor = xFD2, FontRelief = 1, TextColor = 0x0022AA)
        self.xRB_t = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_t.setModel(rbm_t)

        self._addWidget('label_m', 'FixedText', 20, posY1+10, nDescWidth, nDescHeight, Label = dUI.get('descModern', "#descModern#"), MultiLine = True)
        self._addWidget('label_c', 'FixedText', 20, posY2+10, nDescWidth, nDescHeight, Label = dUI.get('descClassic', "#descClassic#"), MultiLine = True)
        self._addWidget('label_r', 'FixedText', 20, posY3+10, nDescWidth, nDescHeight, Label = dUI.get('descReform', "#descReform#"), MultiLine = True)
        self._addWidget('label_t', 'FixedText', 20, posY4+10, nDescWidth, nDescHeight, Label = dUI.get('descAllvar', "#descAllvar#"), MultiLine = True)

        if self.sCurrentDic:
            self.setRadioButton()
            sMsgLabel = dUI.get('restart', "#restart#")
            bButtonActive = True
        else:
            sMsgLabel = dUI.get('error', "#error#")
            bButtonActive = False

        label_info = self._addWidget('label_info', 'FixedText', 10, posY4+50, 180, 10, Label = sMsgLabel, TextColor = 0xAA2200, MultiLine = True)
        button = self._addWidget('select', 'Button', padding+40, posY5, 100, 14, Label = dUI.get('select', "#select#"), FontDescriptor = xFD3, TextColor = 0x004400, Enabled = bButtonActive)

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.getControl('select').addActionListener(self)
        self.xContainer.setVisible(False)
        toolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(toolkit, None)
        self.xContainer.execute()

    def setRadioButton (self):
        print(self.sCurrentDic)
        if self.sCurrentDic == 'moderne':
            self.xRB_m.State = 1
        elif self.sCurrentDic == 'classique':
            self.xRB_c.State = 1
        elif self.sCurrentDic == 'reforme1990':
            self.xRB_r.State = 1
        elif self.sCurrentDic == 'toutesvariantes':
            self.xRB_t.State = 1
        else:
            pass

    # XActionListener
    def actionPerformed (self, actionEvent):
        try:
            if self.xRB_m.getState():
                self.sSelectedDic = 'moderne'
            elif self.xRB_c.getState():
                self.sSelectedDic = 'classique'
            elif self.xRB_r.getState():
                self.sSelectedDic = 'reforme1990'
            elif self.xRB_t.getState():
                self.sSelectedDic = 'toutesvariantes'
            else:
                # no dictionary selected
                pass
            if self.sSelectedDic and self.sSelectedDic != self.sCurrentDic :
                # Modify the registry
                xSettings = helpers.getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", True)
                xLocations = xSettings.getByName("Locations")
                v1 = xLocations[0].replace(self.sCurrentDic, self.sSelectedDic)
                v2 = xLocations[1].replace(self.sCurrentDic, self.sSelectedDic)
                #xSettings.replaceByName("Locations", xLocations)  # doesn't work, see line below
                uno.invoke(xSettings, "replaceByName", ("Locations", uno.Any("[]string", (v1, v2))))
                xSettings.commitChanges()
            self.xContainer.endExecute()
        except:
            traceback.print_exc()

    # XJobExecutor
    def trigger (self, args):
        try:
            dialog = FrenchDictionarySwitcher(self.ctx)
            dialog.run()
        except:
            traceback.print_exc()


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(FrenchDictionarySwitcher, 'dicollecte.FrenchDictionarySwitcher', ('com.sun.star.task.Job',))
