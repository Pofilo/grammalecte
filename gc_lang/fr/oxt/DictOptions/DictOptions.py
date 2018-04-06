# Dictionary Options
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback
import time

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

        self.xSettingNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Other/", True)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 200
        self.xDialog.Height = 230
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
        xFDSubTitle.Height = 10
        xFDSubTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDSubTitle.Name = "Verdana"

        # widget
        nX = 10
        nY1 = 10
        nY2 = nY1 + 40
        nY3 = nY2 + 40
        nY4 = nY3 + 40
        nY5 = nY4 + 50

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # Spell checker section
        #self._addWidget("spelling_section", 'FixedLine', nX, nY1, nWidth, nHeight, Label = dUI.get("spelling_section", "#err"), FontDescriptor = xFDTitle)
        #self.xGraphspell = self._addWidget('activate_main', 'CheckBox', nX, nY1+15, nWidth, nHeight, Label = dUI.get('activate_main', "#err"))
        #self._addWidget('activate_main_descr', 'FixedText', nX, nY1+25, nWidth, nHeight*2, Label = dUI.get('activate_main_descr', "#err"), MultiLine = True)

        # Spell suggestion engine section
        #self._addWidget("suggestion_section", 'FixedLine', nX, nY2, nWidth, nHeight, Label = dUI.get("suggestion_section", "#err"), FontDescriptor = xFDTitle)
        #self.xGraphspellSugg = self._addWidget('activate_spell_sugg', 'CheckBox', nX, nY2+15, nWidth, nHeight, Label = dUI.get('activate_spell_sugg', "#err"))
        #self._addWidget('activate_spell_sugg_descr', 'FixedText', nX, nY2+25, nWidth, nHeight*4, Label = dUI.get('activate_spell_sugg_descr', "#err"), MultiLine = True)

        # Graphspell dictionary section
        self._addWidget("graphspell_section", 'FixedLine', nX, nY1, nWidth, nHeight, Label = dUI.get("graphspell_section", "#err"), FontDescriptor = xFDTitle)
        self.xMainDic = self._addWidget('activate_main', 'CheckBox', nX, nY1+15, nWidth, nHeight, Label = dUI.get('activate_main', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088, State = True)
        self._addWidget('activate_main_descr', 'FixedText', nX+10, nY1+25, nWidth-10, nHeight*2, Label = dUI.get('activate_main_descr', "#err"), MultiLine = True)
        self.xExtendedDic = self._addWidget('activate_extended', 'CheckBox', nX, nY2+15, nWidth, nHeight, Label = dUI.get('activate_extended', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088, Enabled = False)
        self._addWidget('activate_extended_descr', 'FixedText', nX+10, nY2+25, nWidth-10, nHeight*2, Label = dUI.get('activate_extended_descr', "#err"), MultiLine = True)
        self.xCommunityDic = self._addWidget('activate_community', 'CheckBox', nX, nY3+15, nWidth, nHeight, Label = dUI.get('activate_community', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088, Enabled = False)
        self._addWidget('activate_community_descr', 'FixedText', nX+10, nY3+25, nWidth-10, nHeight*2, Label = dUI.get('activate_community_descr', "#err"), MultiLine = True)
        self.xPersonalDic = self._addWidget('activate_personal', 'CheckBox', nX, nY4+15, nWidth, nHeight, Label = dUI.get('activate_personal', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088)
        self._addWidget('activate_personal_descr', 'FixedText', nX+10, nY4+25, nWidth-10, nHeight*2, Label = dUI.get('activate_personal_descr', "#err"), MultiLine = True)
        
        # Restart message
        self._addWidget('restart', 'FixedText', nX, nY5, nWidth, nHeight*2, Label = dUI.get('restart', "#err"), FontDescriptor = xFDTitle, MultiLine = True, TextColor = 0x880000)

        # Button
        self._addWidget('apply_button', 'Button', self.xDialog.Width-115, self.xDialog.Height-25, 50, 14, Label = dUI.get('apply_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x005500)
        self._addWidget('cancel_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-25, 50, 14, Label = dUI.get('cancel_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

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
        try:
            if xActionEvent.ActionCommand == 'Apply':
                xChild = self.xSettingNode.getByName("o_fr")
                #xChild.setPropertyValue("use_graphspell", self.xGraphspell.State)
                #xChild.setPropertyValue("use_graphspell_sugg", self.xGraphspellSugg.State)
                #xChild.setPropertyValue("use_extended_dic", self.xExtendedDic.State)
                #xChild.setPropertyValue("use_community_dic", self.xCommunityDic.State)
                xChild.setPropertyValue("use_personal_dic", self.xPersonalDic.State)
                self.xSettingNode.commitChanges()
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

    def _loadOptions (self):
        try:
            xChild = self.xSettingNode.getByName("o_fr")
            #self.xGraphspell.State = xChild.getPropertyValue("use_graphspell")
            #self.xGraphspellSugg.State = xChild.getPropertyValue("use_graphspell_sugg")
            #self.xExtendedDic.State = xChild.getPropertyValue("use_extended_dic")
            #self.xCommunityDic.State = xChild.getPropertyValue("use_community_dic")
            self.xPersonalDic.State = xChild.getPropertyValue("use_personal_dic")
        except:
            traceback.print_exc()


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(DictOptions, 'net.grammalecte.graphspell.DictOptions', ('com.sun.star.task.Job',))
