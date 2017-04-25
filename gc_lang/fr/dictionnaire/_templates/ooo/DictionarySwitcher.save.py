# -*- coding: utf8 -*-
# French Dictionary Switcher
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import sys
import re
#import os.path

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import MODALTOP
from com.sun.star.awt.VclWindowPeerAttribute import OK, OK_CANCEL, YES_NO, YES_NO_CANCEL, RETRY_CANCEL, DEF_OK, DEF_CANCEL, DEF_RETRY, DEF_YES, DEF_NO
from com.sun.star.beans import PropertyValue

# XRay - API explorer
from com.sun.star.uno import RuntimeException as _rtex

def xray(myObject):
    try:
        sm = uno.getComponentContext().ServiceManager
        mspf = sm.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory", uno.getComponentContext())
        scriptPro = mspf.createScriptProvider("")
        xScript = scriptPro.getScript("vnd.sun.star.script:XrayTool._Main.Xray?language=Basic&location=application")
        xScript.invoke((myObject,), (), ())
        return
    except:
        raise _rtex("\nBasic library Xray is not installed", uno.getComponentContext())
# END Xray

DEBUG = False

if DEBUG and sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.open("C:\_multidict_stdout.txt", "w", "utf-8")

def handleException (ctx=None):
    import traceback
    '''Display exception in a message dialog'''
    s = '\n'.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
    if not sys.platform.startswith('win'):
        # also print trace on stdout/stderr on non-Windows platform
        traceback.print_exc()
    else:
        # no default stdout/stderr on Windows
        print(s)
    
    if not ctx:
        return
    xSvMgr = ctx.ServiceManager
    xDesktop = xSvMgr.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
    xDoc = xDesktop.getCurrentComponent()
    xWindow = xDoc.CurrentController.Frame.ContainerWindow
    MessageBox(xWindow, s, 'Exception', 'errorbox')

    
def MessageBox (xParentWin, sMsg, sTitle, sBoxType="messbox", MsgButtons=OK):
    if sBoxType not in ("messbox", "infobox", "errorbox", "warningbox", "querybox"):
        sBoxType = "messbox"

    # window properties
    aDescriptor = WindowDescriptor()
    aDescriptor.Type = MODALTOP
    aDescriptor.WindowServiceName = sBoxType
    aDescriptor.ParentIndex = -1
    aDescriptor.Parent = xParentWin
    #aDescriptor.Bounds = Rectangle()
    aDescriptor.WindowAttributes = MsgButtons

    xTK = xParentWin.getToolkit()
    msgbox = xTK.createWindow(aDescriptor)
    msgbox.setMessageText(sMsg)
    msgbox.setCaptionText(sTitle)

    return msgbox.execute()

LABELDICT = { "moderne": u"Moderne", "classique": u"Classique", "reforme1990": u"Réforme 1990", "toutesvariantes": u"Toutes variantes" }

class FrenchDictionarySwitcher (unohelper.Base, XActionListener, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.container = None
        self.dialog = None
        self.xRB_m = None
        self.xRB_c = None
        self.xRB_r = None
        self.xRB_f = None
        self.sCurrentDic = ''
        self.sSelectedDic = ''

    def addWidget (self, name, wtype, x, y, w, h, **kwargs):
        widget = self.dialog.createInstance('com.sun.star.awt.UnoControl%sModel' % wtype)
        widget.Name = name
        widget.PositionX = x
        widget.PositionY = y
        widget.Width = w
        widget.Height = h
        for k, w in kwargs.items():
            setattr(widget, k, w)
        self.dialog.insertByName(name, widget)
        return widget

    def run (self):
        # what is the current dictionary
        xSettings = getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", True)
        xLocations = xSettings.getByName("Locations")
        m = re.search(r"fr-(\w*)\.(?:dic|aff)", xLocations[0])
        self.sCurrentDic = m.group(1)
    
        # dialog
        self.dialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.dialog.Width = 200
        self.dialog.Height = 280
        self.dialog.Title = u"Orthographe française"
        
        # blabla
        sSubTitle = u"Choisissez un dictionnaire"
        sDicLabel_m = u"“Moderne”"
        sDicDescr_m = u"Ce dictionnaire propose l’orthographe telle qu’elle est écrite aujourd’hui le plus couramment. C’est le dictionnaire recommandé si le français n’est pas votre langue maternelle ou si vous ne désirez qu’une seule graphie correcte par mot."
        sDicLabel_c = u"“Classique” (recommandé)"
        sDicDescr_c = u"Il s’agit du dictionnaire “Moderne”, avec des graphies classiques en sus, certaines encore communément utilisées, d’autres désuètes. C’est le dictionnaire recommandé si le français est votre langue maternelle."
        sDicLabel_r = u"“Réforme 1990”"
        sDicDescr_r = u"Avec ce dictionnaire, seule l’orthographe réformée est reconnue. Attendu que bon nombre de graphies réformées sont considérées comme erronées par beaucoup, ce dictionnaire est déconseillé. Les graphies passées dans l’usage sont déjà incluses dans le dictionnaire “Moderne”."
        sDicLabel_t = u"“Toutes variantes”"
        sDicDescr_t = u"Ce dictionnaire contient les variantes graphiques, classiques, réformées, ainsi que d’autres plus rares encore. Ce dictionnaire est déconseillé à ceux qui ne connaissent pas très bien la langue française."
        
        # widgets
        padding = 10
        hspace = 60
        posY1 = 20; posY2 = posY1 + hspace; posY3 = posY2 + hspace; posY4 = posY3 + hspace; posY5 = posY4 + hspace;
        wwidth = 170
        wheight = 20
        wwidthdescr = 170
        wheightdescr = 40
        
        xFD1 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD1.Height = 12
        xFD1.Name = "Verdana"
        
        xFD2 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFD2.Height = 11
        xFD2.Name = "Verdana"
        
        gbm = self.addWidget('groupbox', 'GroupBox', 5, 5, 190, 250, Label = sSubTitle, FontDescriptor = xFD1)
        
        # Note: the only way to group RadioButtons is to create them successively
        rbm_m = self.addWidget('rb-moderne', 'RadioButton', padding, posY1, wwidth, wheight, Label = sDicLabel_m, FontDescriptor = xFD2)
        self.xRB_m = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_m.setModel(rbm_m)
        rbm_c = self.addWidget('rb-classique', 'RadioButton', padding, posY2, wwidth, wheight, Label = sDicLabel_c, FontDescriptor = xFD2)
        self.xRB_c = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_c.setModel(rbm_c)
        rbm_r = self.addWidget('rb-reforme1990', 'RadioButton', padding, posY3, wwidth, wheight, Label = sDicLabel_r, FontDescriptor = xFD2)
        self.xRB_r = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_r.setModel(rbm_r)
        rbm_t = self.addWidget('rb-toutesvariantes', 'RadioButton', padding, posY4, wwidth, wheight, Label = sDicLabel_t, FontDescriptor = xFD2)
        self.xRB_t = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlRadioButton', self.ctx)
        self.xRB_t.setModel(rbm_t)
        
        label_m = self.addWidget('label_m', 'FixedText', 20, posY1+10, wwidthdescr, wheightdescr, Label = sDicDescr_m, MultiLine = True)
        label_c = self.addWidget('label_c', 'FixedText', 20, posY2+10, wwidthdescr, wheightdescr, Label = sDicDescr_c, MultiLine = True)
        label_r = self.addWidget('label_r', 'FixedText', 20, posY3+10, wwidthdescr, wheightdescr, Label = sDicDescr_r, MultiLine = True)
        label_t = self.addWidget('label_t', 'FixedText', 20, posY4+10, wwidthdescr, wheightdescr, Label = sDicDescr_t, MultiLine = True)
        
        self.setRadioButton(self.sCurrentDic)
        
        button = self.addWidget('select', 'Button', padding+50, posY5, 80, 14, Label = 'Utiliser ce dictionnaire')
        
        # container
        self.container = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.container.setModel(self.dialog)
        self.container.getControl('select').addActionListener(self)
#         if self.sCurrentDic != "moderne":
#             self.container.getControl('rb-moderne').addActionListener(self)
#         if self.sCurrentDic != "classique":
#             self.container.getControl('rb-classique').addActionListener(self)
#         if self.sCurrentDic != "reforme1990":
#             self.container.getControl('rb-reforme1990').addActionListener(self)
#         if self.sCurrentDic != "toutesvariantes":
#             self.container.getControl('rb-toutesvariantes').addActionListener(self)
        self.container.setVisible(False)
        toolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.container.createPeer(toolkit, None)
        self.container.execute()
    
    def setRadioButton (self, sDic):
        if sDic == 'moderne':
            self.xRB_m.setState(True)
        elif sDic == 'classique':
            self.xRB_c.setState(True)
        elif sDic == 'reforme1990':
            self.xRB_r.setState(True)
        elif sDic == 'toutesvariantes':
            self.xRB_t.setState(True)
        else:
            pass
        
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
            self.container.endExecute()
        except:
            handleException(self.ctx)
    
    def trigger (self, args):
        try:
            dialog = FrenchDictionarySwitcher(self.ctx)
            dialog.run()
            
            if dialog.sSelectedDic and dialog.sCurrentDic != dialog.sSelectedDic:
                xSvMgr = uno.getComponentContext().ServiceManager
                xDesktop = xSvMgr.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
                xDoc = xDesktop.getCurrentComponent()
                xWindow = xDoc.CurrentController.Frame.ContainerWindow
                
                if dialog.sCurrentDic:
                    # Modify the registry
                    xSettings = getConfigSetting("/org.openoffice.Office.Linguistic/ServiceManager/Dictionaries/HunSpellDic_fr", True)
                    xLocations = xSettings.getByName("Locations")
                    v1 = xLocations[0].replace(dialog.sCurrentDic, dialog.sSelectedDic)
                    v2 = xLocations[1].replace(dialog.sCurrentDic, dialog.sSelectedDic)
                    #xSettings.replaceByName("Locations", xLocations)  # ERROR, see line below
                    uno.invoke(xSettings, "replaceByName", ("Locations", uno.Any("[]string", (v1, v2))))
                    xSettings.commitChanges()
                    # message box
                    sMsg = u"Vous avez choisi un nouveau dictionnaire\northographique pour la langue française.\n\n“%s” ⇒ “%s”\n\nFermez le logiciel (y compris le démarrage rapide)\net relancez-le." % (LABELDICT[dialog.sCurrentDic], LABELDICT[dialog.sSelectedDic])
                    MessageBox(xWindow, sMsg, u"Sélection d’un nouveau dictionnaire", "infobox")
                    

#                     # get package location (URL of this extension)
#                     xCompCtx = uno.getComponentContext()
#                     xPackageInformationProvider = xCompCtx.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
#                     sURL = xPackageInformationProvider.getPackageLocation("French.linguistic.resources.from.Dicollecte.by.OlivierR")
#                     sDstFile = sURL + '/dictionaries.xcu'
#                     sDstFile = sDstFile.replace('file:///', '').replace('%20', ' ')
#                     sDstFile = os.path.normpath(sDstFile)
#                     sTplFile = sDstFile + '.tpl.xml'
#                     
#                     # rewrite dictionaries.xcu
#                     if os.path.isfile(sTplFile) and os.path.isfile(sDstFile):
#                         with open(sTplFile, 'r') as hFile:
#                             content = hFile.read()
#                         hFile.close()
#                         content = content.replace('{{dictionaryName}}', dialog.sSelectedDic)
#                         with open(sDstFile, 'w') as hFile:
#                             hFile.write(content)
#                         hFile.close()
#                     else:
#                         sErrMsg = ""
#                         if not os.path.isfile(sTplFile):
#                             sErrMsg += u"File not found: %s\n" % sTplFile
#                         if not os.path.isfile(sDstFile):
#                             sErrMsg += u"File not found: %s\n" % sDstFile
#                         if sErrMsg:
#                             MessageBox(xWindow, sErrMsg, "ERROR", "error")
                else:
                    MessageBox(xWindow, u"Couldn’t retrieve informations\nabout the current dictionary.", "ERROR", "errorbox")
                
#                 xSpellChecker = xSvMgr.createInstanceWithContext('com.sun.star.linguistic2.SpellChecker', self.ctx)
#                 xLocale = uno.createUnoStruct('com.sun.star.lang.Locale')
#                 xLocale.Language = "fr"
#                 xLocale.Country = "FR"
#                 l = xSpellChecker.getSupportedServiceNames()
#                 MessageBox(xWindow, " ".join(l), "DEBUG", "infobox")
        except:
            handleException(self.ctx)


def getConfigSetting (sNodeConfig, bForUpdate):
    if bForUpdate:
        sService = "com.sun.star.configuration.ConfigurationUpdateAccess"
    else:
        sService = "com.sun.star.configuration.ConfigurationAccess"
    
    xConfigProvider = createUnoService("com.sun.star.configuration.ConfigurationProvider")
    
    xPropertyValue = PropertyValue()
    xPropertyValue.Name = "nodepath"
    xPropertyValue.Value = sNodeConfig
    
    xSettings = xConfigProvider.createInstanceWithArguments(sService, (xPropertyValue,))
    return xSettings

def createUnoService (serviceName):
    xSvMgr = uno.getComponentContext().ServiceManager
    return xSvMgr.createInstanceWithContext(serviceName, uno.getComponentContext())


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(FrenchDictionarySwitcher, 'dicollecte.FrenchDictionarySwitcher', ('com.sun.star.task.Job',))
