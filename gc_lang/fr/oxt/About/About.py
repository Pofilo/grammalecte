# -*- coding: utf8 -*-
# About dialog
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback
import sys

import ab_strings
import helpers

from com.sun.star.awt import XActionListener
from com.sun.star.beans import PropertyValue


class AboutGrammalecte (unohelper.Base, XActionListener):
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
        try:
            dUI = ab_strings.getUI(sLang)

            # dialog
            self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
            self.xDialog.Width = 160
            self.xDialog.Height = 320
            self.xDialog.Title = dUI.get('windowtitle', "#err")
            xWindowSize = helpers.getWindowSize()
            self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
            self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))
            
            # xWidgets
            nLblWidth = 140
            nURLcolor = 0x4444FF
            
            xFD0 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFD0.Height = 20
            #xFD0.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFD0.Name = "Verdana"
            
            xFD1 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFD1.Height = 10
            xFD1.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFD1.Name = "Verdana"

            xFD2 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFD2.Height = 10
            xFD2.Name = "Verdana"

            xFD3 = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
            xFD3.Height = 12
            xFD3.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
            xFD3.Name = "Verdana"
            
            # logo
            xDefaultContext = self.ctx.ServiceManager.DefaultContext
            xPackageInfoProvider = xDefaultContext.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
            sExtPath = xPackageInfoProvider.getPackageLocation("French.linguistic.resources.from.Dicollecte.by.OlivierR")
            #imgLogo = self._addWidget('imgLogo', 'ImageControl', 5, 5, 50, 50, ImageURL = sExtPath+"/img/logo100.png", Border = 0, ScaleMode = 1)
            imgMainLogo = self._addWidget('imgMainLogo', 'ImageControl', 5, 5, 150, 80, ImageURL = sExtPath+"/img/logo120_text.png", Border = 0, ScaleMode = 1)

            # Infos
            #lblTitle = self._addWidget('lblTitle', 'FixedText', 60, 5, 100, 20, Label = dUI.get('title', "#err"), Align = 0, FontDescriptor = xFD0)            
            lblVersion = self._addWidget('lblVersion', 'FixedText', 5, 90, nLblWidth, 10, Label = dUI.get('version', "#err"), Align = 1, FontDescriptor = xFD2)
            lblLicense = self._addWidget('lblLicense', 'FixedText', 5, 100, nLblWidth, 10, Label = dUI.get('license', "#err"), Align = 1, FontDescriptor = xFD2)
            lblWebsite = self._addWidget('lblWebsite', 'FixedHyperlink', 5, 110, nLblWidth, 10, Label = dUI.get('website', "#err"), Align = 1, \
                                         URL="http://www.dicollecte.org/?from=grammalecte-lo", FontDescriptor = xFD1, TextColor = nURLcolor)

            # Python version
            self._addWidget('lblpython', 'FixedText', 10, 125, nLblWidth, 10, Align = 1, TextColor = 0x888888, FontDescriptor = xFD2, \
                            Label = dUI.get('pythonver', "#err") + "{0[0]}.{0[1]}.{0[2]}".format(sys.version_info))

            # other
            line = self._addWidget('line', 'FixedLine', 10, 140, nLblWidth, 10)

            # sponsors
            lblMsg = self._addWidget('lblMsg', 'FixedText', 10, 155, nLblWidth, 10, Label = dUI.get('message', "#err"), FontDescriptor = xFD2, Align = 1)
            lblURL1 = self._addWidget('lblURL1', 'FixedHyperlink', 10, 170, nLblWidth, 10, Label = dUI.get('sponsor', "#err"), \
                                      Align = 1, URL="http://lamouette.org/?from=grammalecte-lo", FontDescriptor = xFD3, TextColor = nURLcolor)
            imgSponsor = self._addWidget('imgSponsor', 'ImageControl', 5, 180, 150, 50, ImageURL = sExtPath+"/img/LaMouette_small.png", Border = 0, ScaleMode = 1)
            lblURL2 = self._addWidget('lblURL2', 'FixedHyperlink', 10, 235, nLblWidth, 10, Label = dUI.get('sponsor2', "#err"), \
                                      Align = 1, URL="https://www.algoo.fr/?from=grammalecte-lo", FontDescriptor = xFD3, TextColor = nURLcolor)
            imgSponsor2 = self._addWidget('imgSponsor2', 'ImageControl', 5, 245, 150, 50, ImageURL = sExtPath+"/img/Algoo_logo.png", Border = 0, ScaleMode = 1)
            lblURL3 = self._addWidget('lblURL3', 'FixedHyperlink', 10, 300, nLblWidth, 10, Label = dUI.get('link', "#err"), \
                                      Align = 1, URL="http://www.dicollecte.org/#thanks", FontDescriptor = xFD1, TextColor = nURLcolor)
            # button            
            #button = self._addWidget('close', 'Button', self.xDialog.Width - 25, self.xDialog.Height - 20, 20, 14, \
            #                         Label = dUI.get('close', "#err"), FontDescriptor = xFD1, TextColor = 0x004400)
            
            # container
            self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
            self.xContainer.setModel(self.xDialog)
            #self.xContainer.getControl('close').addActionListener(self)
            self.xContainer.setVisible(False)
            toolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
            self.xContainer.createPeer(toolkit, None)
            self.xContainer.execute()
        except:
            traceback.print_exc()
    
    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            self.xContainer.endExecute()
        except:
            traceback.print_exc()
