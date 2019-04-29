# Dictionary Options
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import re
import traceback

import helpers
import do_strings

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue

from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
# BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
# DEFAULT_BUTTON_OK, DEFAULT_BUTTON_CANCEL, DEFAULT_BUTTON_RETRY, DEFAULT_BUTTON_YES, DEFAULT_BUTTON_NO, DEFAULT_BUTTON_IGNORE
from com.sun.star.awt.MessageBoxType import INFOBOX, ERRORBOX # MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX

def MessageBox (xDocument, sMsg, sTitle, nBoxType=INFOBOX, nBoxButtons=BUTTONS_OK):
    xParentWin = xDocument.CurrentController.Frame.ContainerWindow
    ctx = uno.getComponentContext()
    xToolkit = ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    xMsgBox = xToolkit.createMessageBox(xParentWin, nBoxType, nBoxButtons, sTitle, sMsg)
    return xMsgBox.execute()


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
        self.dUI = do_strings.getUI(sLang)

        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xGLOptionNode = helpers.getConfigSetting("/org.openoffice.Lightproof_grammalecte/Other/", True)

        # what is the current Hunspell dictionary
        self.xHunspellNode = helpers.getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", True)
        xLocations = self.xHunspellNode.getByName("Locations")
        m = re.search(r"fr-(\w*)\.(?:dic|aff)", xLocations[0])
        self.sHunspellCurrentDic = m.group(1)  if m  else ""

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 200
        self.xDialog.Height = 285
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
        nY2 = nY1 + 60
        nY3 = nY2 + 25
        nY4 = nY3 + 45
        nY5 = nY4 + 95

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # Graphspell dictionary section
        self._addWidget("graphspell_section", 'FixedLine', nX, nY1, nWidth, nHeight, Label = self.dUI.get("graphspell_section", "#err"), FontDescriptor = xFDTitle)
        self.xMainDic = self._addWidget('activate_main', 'CheckBox', nX, nY1+15, nWidth, nHeight, Label = self.dUI.get('activate_main', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088, State = True)
        self._addWidget('activate_main_descr', 'FixedText', nX+10, nY1+25, nWidth-10, nHeight*2, Label = self.dUI.get('activate_main_descr', "#err"), MultiLine = True)
        self._addWidget('spelling', 'FixedText', nX+10, nY1+45, nWidth-80, nHeight, Label = self.dUI.get('spelling', "#err"), FontDescriptor = xFDSubTitle)
        self.xInfoDicButton = self._addWidget('info_dic_button', 'Button', nX+160, nY1+45, 12, 9, Label = "‹i›")
        self.xSelClassic = self._addWidget('classic', 'RadioButton', nX+10, nY1+55, 50, nHeight, Label = self.dUI.get('classic', "#err"))
        self.xSelReform = self._addWidget('reform', 'RadioButton', nX+65, nY1+55, 55, nHeight, Label = self.dUI.get('reform', "#err"))
        self.xSelAllvars = self._addWidget('allvars', 'RadioButton', nX+120, nY1+55, 60, nHeight, Label = self.dUI.get('allvars', "#err"))
        self.xCommunityDic = self._addWidget('activate_community', 'CheckBox', nX, nY2+15, nWidth, nHeight, Label = self.dUI.get('activate_community', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088, Enabled = False)
        self._addWidget('activate_community_descr', 'FixedText', nX+10, nY2+25, nWidth-10, nHeight*1, Label = self.dUI.get('activate_community_descr', "#err"), MultiLine = True)
        self.xPersonalDic = self._addWidget('activate_personal', 'CheckBox', nX, nY3+15, nWidth, nHeight, Label = self.dUI.get('activate_personal', "#err"), FontDescriptor = xFDSubTitle, TextColor = 0x000088)
        self._addWidget('activate_personal_descr', 'FixedText', nX+10, nY3+25, nWidth-10, nHeight*1, Label = self.dUI.get('activate_personal_descr', "#err"), MultiLine = True)

        # Spell suggestion engine section
        self._addWidget("suggestion_section", 'FixedLine', nX, nY4, nWidth, nHeight, Label = self.dUI.get("suggestion_section", "#err"), FontDescriptor = xFDTitle)
        self.xGraphspellSugg = self._addWidget('activate_spell_sugg', 'CheckBox', nX, nY4+15, nWidth, nHeight, Label = self.dUI.get('activate_spell_sugg', "#err"))
        self._addWidget('activate_spell_sugg_descr', 'FixedText', nX, nY4+25, nWidth, nHeight*6, Label = self.dUI.get('activate_spell_sugg_descr', "#err"), MultiLine = True)

        # Restart message
        self._addWidget('restart', 'FixedText', nX, nY5, nWidth, nHeight*2, Label = self.dUI.get('restart', "#err"), FontDescriptor = xFDTitle, MultiLine = True, TextColor = 0x880000)

        # Button
        self._addWidget('apply_button', 'Button', self.xDialog.Width-115, self.xDialog.Height-20, 50, 14, Label = self.dUI.get('apply_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x005500)
        self._addWidget('cancel_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-20, 50, 14, Label = self.dUI.get('cancel_button', "#err"), FontDescriptor = xFDTitle, TextColor = 0x550000)

        self._loadOptions()

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.getControl('info_dic_button').addActionListener(self)
        self.xContainer.getControl('info_dic_button').setActionCommand('InfoDic')
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
                # Grammalecte options
                xChild = self.xGLOptionNode.getByName("o_fr")
                #xChild.setPropertyValue("use_community_dic", self.xCommunityDic.State)
                xChild.setPropertyValue("use_personal_dic", self.xPersonalDic.State)
                xChild.setPropertyValue("use_graphspell_sugg", self.xGraphspellSugg.State)
                if self.xSelClassic.State:
                    sMainDic = "classic"
                    sHunspellDic = "classique"
                elif self.xSelReform.State:
                    sMainDic = "reform"
                    sHunspellDic = "reforme1990"
                elif self.xSelAllvars.State:
                    sMainDic = "allvars"
                    sHunspellDic = "toutesvariantes"
                else:
                    sMainDic = "classic"
                    sHunspellDic = "classique"
                xChild.setPropertyValue("main_dic_name", sMainDic)
                self.xGLOptionNode.commitChanges()

                # Hunspell options
                xLocations = self.xHunspellNode.getByName("Locations")
                v1 = xLocations[0].replace(self.sHunspellCurrentDic, sHunspellDic)
                v2 = xLocations[1].replace(self.sHunspellCurrentDic, sHunspellDic)
                #self.xHunspellNode.replaceByName("Locations", xLocations)  # doesn't work, see line below
                uno.invoke(self.xHunspellNode, "replaceByName", ("Locations", uno.Any("[]string", (v1, v2))))
                self.xHunspellNode.commitChanges()

                # Close window
                self.xContainer.endExecute()
            elif xActionEvent.ActionCommand == 'InfoDic':
                MessageBox(self.xDocument, self.dUI.get('spelling_descr', "#err"), "Orthographe du français", nBoxType=INFOBOX, nBoxButtons=BUTTONS_OK)
            else:
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
            xChild = self.xGLOptionNode.getByName("o_fr")
            #self.xGraphspell.State = xChild.getPropertyValue("use_graphspell")
            self.xGraphspellSugg.State = xChild.getPropertyValue("use_graphspell_sugg")
            #self.xCommunityDic.State = xChild.getPropertyValue("use_community_dic")
            self.xPersonalDic.State = xChild.getPropertyValue("use_personal_dic")
            sMainDicName = xChild.getPropertyValue("main_dic_name")
            if sMainDicName == "classic":
                self.xSelClassic.State = 1
            elif sMainDicName == "reform":
                self.xSelReform.State = 1
            elif sMainDicName == "allvars":
                self.xSelAllvars.State = 1
            else:
                print("Error. Unknown dictionary: " + sMainDicName)
        except:
            traceback.print_exc()


#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(DictOptions, 'net.grammalecte.graphspell.DictOptions', ('com.sun.star.task.Job',))
