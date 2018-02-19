# Dictionary Options
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback

import helpers
import do_strings

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue


class DictOptions (unohelper.Base, XActionListener, XJobExecutor):

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
        dUI = do_strings.getUI(sLang)

        # what is the current dictionary
        xSettings = helpers.getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", False)
        xLocations = xSettings.getByName("Locations")
        
        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 200
        self.xDialog.Height = 255
        self.xDialog.Title = dUI.get('title', "#title#")
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
        nX = 10
        nY1 = 10
        nY2 = nY1 + 50
        nY3 = nY2 + 70

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # Spell checker section
        self._addWidget("spelling_section", 'FixedLine', nX, nY1, nWidth, nHeight, Label = dUI.get("spelling_section", "#err"), FontDescriptor = xFDTitle)
        self.xActivateMain = self._addWidget('activate_main', 'CheckBox', nX, nY1+15, nWidth, nHeight, Label = dUI.get('activate_main', "#err"), State = True)
        self._addWidget('activate_main_descr', 'FixedText', nX, nY1+25, nWidth, nHeight*2, Label = dUI.get('activate_main_descr', "#err"), MultiLine = True)

        # Spell suggestion engine section
        self._addWidget("suggestion_section", 'FixedLine', nX, nY2, nWidth, nHeight, Label = dUI.get("suggestion_section", "#err"), FontDescriptor = xFDTitle)
        self.xActivateSugg = self._addWidget('activate_spell_sugg', 'CheckBox', nX, nY2+15, nWidth, nHeight, Label = dUI.get('activate_spell_sugg', "#err"), State = True)
        self._addWidget('activate_spell_sugg_descr', 'FixedText', nX, nY2+25, nWidth, nHeight*4, Label = dUI.get('activate_spell_sugg_descr', "#err"), MultiLine = True)

        # Personal dictionary section
        self._addWidget("personal_section", 'FixedLine', nX, nY3, nWidth, nHeight, Label = dUI.get("personal_section", "#err"), FontDescriptor = xFDTitle)
        self.xActivatePersonnal = self._addWidget('activate_personal', 'CheckBox', nX, nY3+15, nWidth, nHeight, Label = dUI.get('activate_personal', "#err"), State = True)
        self._addWidget('activate_personnal_descr', 'FixedText', nX, nY3+25, nWidth, nHeight*3, Label = dUI.get('activate_personal_descr', "#err"), MultiLine = True)
        self._addWidget('import_personal', 'FixedText', nX, nY3+55, nWidth-60, nHeight, Label = dUI.get('import_personal', "#err"), FontDescriptor = xFDSubTitle)
        self.xMsg = self._addWidget('msg', 'FixedText', nX, nY3+65, nWidth-50, nHeight, Label = "[néant]")
        self._addWidget('import_button', 'Button', self.xDialog.Width-50, nY3+65, 40, 10, Label = dUI.get('import_button', "#err"), TextColor = 0x005500)
        self._addWidget('create_dictionary', 'FixedText', nX, nY3+75, nWidth, nHeight*2, Label = dUI.get('create_dictionary', "#err"), MultiLine = True)

        # Button
        self._addWidget('apply_button', 'Button', self.xDialog.Width-120, self.xDialog.Height-25, 50, 14, Label = dUI.get('apply_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x005500)
        self._addWidget('cancel_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-25, 50, 14, Label = dUI.get('cancel_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.getControl('apply_button').addActionListener(self)
        self.xContainer.getControl('apply_button').setActionCommand('Apply')
        self.xContainer.getControl('import_button').addActionListener(self)
        self.xContainer.getControl('import_button').setActionCommand('Import')
        self.xContainer.getControl('cancel_button').addActionListener(self)
        self.xContainer.getControl('cancel_button').setActionCommand('Cancel')
        self.xContainer.setVisible(False)
        toolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(toolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == 'Apply':
                if False:
                    # Modify the registry
                    xSettings = helpers.getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", True)
                    xLocations = xSettings.getByName("Locations")
                    v1 = xLocations[0].replace(self.sCurrentDic, self.sSelectedDic)
                    v2 = xLocations[1].replace(self.sCurrentDic, self.sSelectedDic)
                    #xSettings.replaceByName("Locations", xLocations)  # doesn't work, see line below
                    uno.invoke(xSettings, "replaceByName", ("Locations", uno.Any("[]string", (v1, v2))))
                    xSettings.commitChanges()
            elif xActionEvent.ActionCommand == "Import":
                #xFilePicker = uno.createUnoService("com.sun.star.ui.dialogs.FilePicker")
                xFilePicker = self.xSvMgr.createInstanceWithContext('com.sun.star.ui.dialogs.SystemFilePicker', self.ctx)
                xFilePicker.appendFilter("Supported files", "*.json; *.bdic")
                #xFilePicker.setDisplayDirectory("")
                #xFilePicker.setMultiSelectionMode(True)
                nResult = xFilePicker.execute()
                print(nResult)
                if nResult == 1:
                    print("two")
                    lFile = xFilePicker.getSelectedFiles()
                    print("one")
                    lFile = xFilePicker.getFiles()
                    print(lFile)
            else:
                pass
            self.xContainer.endExecute()
        except:
            traceback.print_exc()
    
    # XJobExecutor
    def trigger (self, args):
        try:
            dialog = DictOptions(self.ctx)
            dialog.run()
        except:
            traceback.print_exc()


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(DictOptions, 'net.grammalecte.graphspell.DictOptions', ('com.sun.star.task.Job',))
