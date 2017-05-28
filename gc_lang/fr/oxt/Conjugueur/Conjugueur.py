# -*- coding: utf8 -*-
# Conjugueur
# by Olivier R.
# License: GPL 3

import unohelper
import uno
import traceback

import grammalecte.fr.conj as conj_fr
import helpers

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener


class Conjugueur (unohelper.Base, XActionListener, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xContainer = None
        self.xDialog = None
        self.lDropDown = ["être", "avoir", "aller", "vouloir", "pouvoir", "devoir", "faire", "envoyer", "prendre", "connaître", \
                          "savoir", "partir", "répondre", "dire", "voir", "mettre", "tenir", "sentir", "finir", "manger"]
        self.sWarning = "Ce verbe n’a pas encore été vérifié. " \
                        "C’est pourquoi les options “pronominal” et “temps composés” sont désactivées."

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

    def run (self, sArgs=""):
        ## dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 250
        self.xDialog.Title = "Grammalecte · Conjugueur"

        xFDinput = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDinput.Height = 10
        xFDinput.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDinput.Name = "Verdana"

        xFDmode = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDmode.Height = 12
        xFDmode.Name = "Constantia"

        xFDtemps = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDtemps.Height = 9
        xFDtemps.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDtemps.Name = "Constantia"

        xFDbold = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDbold.Height = 10
        xFDbold.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDbold.Name = "Verdana"

        xFDinfo = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDinfo.Height = 7
        xFDinfo.Name = "Verdana"

        xFDsmall = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDsmall.Height = 6
        xFDsmall.Name = "Verdana"

        ## widgets
        nGroupBoxWith = (self.xDialog.Width - 16) // 2
        nWidth = nGroupBoxWith-10
        nHeight = 10
        nHeightCj = 8
        nColorHead = 0xAA2200
        nColorHead2 = 0x0022AA

        # grid
        nX1 = 10; nX2 = nX1+123;
        nY0 = 2; nY1 = nY0+26; nY2 = nY1-4; nY3 = nY1+17; nY4 = nY3+50; nY5 = nY4+55; nY6 = nY5+55; nY7 = nY6+55; nY6b = nY6+17; nY7b = nY6b+55

        # group box // indicatif
        gb_infi = self._addWidget('groupbox_infi', 'GroupBox', nX1-5, nY0, nGroupBoxWith, 23, Label = "Infinitif", \
                                  FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.infi = self._addWidget('infi', 'FixedText', nX1, nY0+10, nWidth, nHeight, Label = "", FontDescriptor = xFDbold)

        # input field + button
        self.input = self._addWidget('input', 'ComboBox', nX2-5, nY0+5, 68, 14, \
                                     FontDescriptor = xFDinput, TextColor = 0x666666, Dropdown = True, LineCount = 20)
        for n, s in enumerate(self.lDropDown):
            self.input.insertItemText(n, s)
        self.cbutton = self._addWidget('cbutton', 'Button', nX2+66, nY0+5, 46, 14, Label = "Conjuguer", FontDescriptor = xFDinput)

        # informations
        self.info = self._addWidget('info', 'FixedText', nX1, nY1, nWidth, nHeight, FontDescriptor = xFDinfo)

        # options
        self.oneg = self._addWidget('oneg', 'CheckBox', nX2-5, nY2, 35, nHeight, Label = "négation")
        self.opro = self._addWidget('opro', 'CheckBox', nX2+33, nY2, 50, nHeight, Label = "pronominal")
        self.ofem = self._addWidget('ofem', 'CheckBox', nX2+80, nY2, 45, nHeight, Label = "féminin")
        self.oint = self._addWidget('oint', 'CheckBox', nX2-5, nY2+9, 55, nHeight, Label = "interrogatif")
        self.otco = self._addWidget('otco', 'CheckBox', nX2+55, nY2+9, 60, nHeight, Label = "temps composés")

        # group box // participe passé
        gb_ppas = self._addWidget('groupbox_ppas', 'GroupBox', nX1-5, nY3-7, nGroupBoxWith, 55, Label = "Participes présent et passés", \
                                  FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.ppre = self._addWidget('ppre', 'FixedText', nX1, nY3+5, nWidth, nHeightCj, Label = "")
        self.ppas1 = self._addWidget('ppas1', 'FixedText', nX1, nY3+14, nWidth, nHeightCj, Label = "")
        self.ppas2 = self._addWidget('ppas2', 'FixedText', nX1, nY3+21, nWidth, nHeightCj, Label = "")
        self.ppas3 = self._addWidget('ppas3', 'FixedText', nX1, nY3+28, nWidth, nHeightCj, Label = "")
        self.ppas4 = self._addWidget('ppas4', 'FixedText', nX1, nY3+35, nWidth, nHeightCj, Label = "")

        # group box // impératif
        gb_impe = self._addWidget('groupbox_impe', 'GroupBox', nX2-5, nY3, nGroupBoxWith, 48, Label = "Impératif", \
                                  FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.impe = self._addWidget('impe', 'FixedText', nX2, nY3+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.impe1 = self._addWidget('impe1', 'FixedText', nX2, nY3+21, nWidth, nHeightCj, Label = "")
        self.impe2 = self._addWidget('impe2', 'FixedText', nX2, nY3+28, nWidth, nHeightCj, Label = "")
        self.impe3 = self._addWidget('impe3', 'FixedText', nX2, nY3+35, nWidth, nHeightCj, Label = "")

        # group box // indicatif
        gb_ind = self._addWidget('groupbox_ind', 'GroupBox', nX1-5, nY4, nGroupBoxWith, 234, Label = "Indicatif", \
                                 FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.ipre = self._addWidget('ipre', 'FixedText', nX1, nY4+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.ipre1 = self._addWidget('ipre1', 'FixedText', nX1, nY4+21, nWidth, nHeightCj, Label = "")
        self.ipre2 = self._addWidget('ipre2', 'FixedText', nX1, nY4+28, nWidth, nHeightCj, Label = "")
        self.ipre3 = self._addWidget('ipre3', 'FixedText', nX1, nY4+35, nWidth, nHeightCj, Label = "")
        self.ipre4 = self._addWidget('ipre4', 'FixedText', nX1, nY4+42, nWidth, nHeightCj, Label = "")
        self.ipre5 = self._addWidget('ipre5', 'FixedText', nX1, nY4+49, nWidth, nHeightCj, Label = "")
        self.ipre6 = self._addWidget('ipre6', 'FixedText', nX1, nY4+56, nWidth, nHeightCj, Label = "")

        self.iimp = self._addWidget('iimp', 'FixedText', nX1, nY5+12, nWidth, nHeight, Label = "Imparfait", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.iimp1 = self._addWidget('iimp1', 'FixedText', nX1, nY5+21, nWidth, nHeightCj, Label = "")
        self.iimp2 = self._addWidget('iimp2', 'FixedText', nX1, nY5+28, nWidth, nHeightCj, Label = "")
        self.iimp3 = self._addWidget('iimp3', 'FixedText', nX1, nY5+35, nWidth, nHeightCj, Label = "")
        self.iimp4 = self._addWidget('iimp4', 'FixedText', nX1, nY5+42, nWidth, nHeightCj, Label = "")
        self.iimp5 = self._addWidget('iimp5', 'FixedText', nX1, nY5+49, nWidth, nHeightCj, Label = "")
        self.iimp6 = self._addWidget('iimp6', 'FixedText', nX1, nY5+56, nWidth, nHeightCj, Label = "")

        self.ipsi = self._addWidget('ipsi', 'FixedText', nX1, nY6+12, nWidth, nHeight, Label = "Passé Simple", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.ipsi1 = self._addWidget('ipsi1', 'FixedText', nX1, nY6+21, nWidth, nHeightCj, Label = "")
        self.ipsi2 = self._addWidget('ipsi2', 'FixedText', nX1, nY6+28, nWidth, nHeightCj, Label = "")
        self.ipsi3 = self._addWidget('ipsi3', 'FixedText', nX1, nY6+35, nWidth, nHeightCj, Label = "")
        self.ipsi4 = self._addWidget('ipsi4', 'FixedText', nX1, nY6+42, nWidth, nHeightCj, Label = "")
        self.ipsi5 = self._addWidget('ipsi5', 'FixedText', nX1, nY6+49, nWidth, nHeightCj, Label = "")
        self.ipsi6 = self._addWidget('ipsi6', 'FixedText', nX1, nY6+56, nWidth, nHeightCj, Label = "")

        self.ifut = self._addWidget('ifut', 'FixedText', nX1, nY7+12, nWidth, nHeight, Label = "Futur", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.ifut1 = self._addWidget('ifut1', 'FixedText', nX1, nY7+21, nWidth, nHeightCj, Label = "")
        self.ifut2 = self._addWidget('ifut2', 'FixedText', nX1, nY7+28, nWidth, nHeightCj, Label = "")
        self.ifut3 = self._addWidget('ifut3', 'FixedText', nX1, nY7+35, nWidth, nHeightCj, Label = "")
        self.ifut4 = self._addWidget('ifut4', 'FixedText', nX1, nY7+42, nWidth, nHeightCj, Label = "")
        self.ifut5 = self._addWidget('ifut5', 'FixedText', nX1, nY7+49, nWidth, nHeightCj, Label = "")
        self.ifut6 = self._addWidget('ifut6', 'FixedText', nX1, nY7+56, nWidth, nHeightCj, Label = "")

        self.infomsg = self._addWidget('infomsg', 'FixedText', nX1-5, nY7+73, 120, 20, FontDescriptor = xFDinfo, \
                                       MultiLine = True, TextColor = 0x333333, Label = self.sWarning)

        # group box // subjonctif
        gb_sub = self._addWidget('groupbox_sub', 'GroupBox', nX2-5, nY4, nGroupBoxWith, 123, Label = "Subjonctif", \
                                 FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.spre = self._addWidget('spre', 'FixedText', nX2, nY4+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.spre1 = self._addWidget('spre1', 'FixedText', nX2, nY4+21, nWidth, nHeightCj, Label = "")
        self.spre2 = self._addWidget('spre2', 'FixedText', nX2, nY4+28, nWidth, nHeightCj, Label = "")
        self.spre3 = self._addWidget('spre3', 'FixedText', nX2, nY4+35, nWidth, nHeightCj, Label = "")
        self.spre4 = self._addWidget('spre4', 'FixedText', nX2, nY4+42, nWidth, nHeightCj, Label = "")
        self.spre5 = self._addWidget('spre5', 'FixedText', nX2, nY4+49, nWidth, nHeightCj, Label = "")
        self.spre6 = self._addWidget('spre6', 'FixedText', nX2, nY4+56, nWidth, nHeightCj, Label = "")

        self.simp = self._addWidget('simp', 'FixedText', nX2, nY5+12, nWidth, nHeight, Label = "Imparfait", \
                                    FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.simp1 = self._addWidget('simp1', 'FixedText', nX2, nY5+21, nWidth, nHeightCj, Label = "")
        self.simp2 = self._addWidget('simp2', 'FixedText', nX2, nY5+28, nWidth, nHeightCj, Label = "")
        self.simp3 = self._addWidget('simp3', 'FixedText', nX2, nY5+35, nWidth, nHeightCj, Label = "")
        self.simp4 = self._addWidget('simp4', 'FixedText', nX2, nY5+42, nWidth, nHeightCj, Label = "")
        self.simp5 = self._addWidget('simp5', 'FixedText', nX2, nY5+49, nWidth, nHeightCj, Label = "")
        self.simp6 = self._addWidget('simp6', 'FixedText', nX2, nY5+56, nWidth, nHeightCj, Label = "")

        # group box // conditionnel
        gb_cond = self._addWidget('groupbox_cond', 'GroupBox', nX2-5, nY6b, nGroupBoxWith, 123, Label = "Conditionnel", \
                                  FontDescriptor = xFDmode, FontRelief = 1, TextColor = nColorHead)
        self.conda = self._addWidget('conda', 'FixedText', nX2, nY6b+12, nWidth, nHeight, Label = "Présent", \
                                     FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.conda1 = self._addWidget('conda1', 'FixedText', nX2, nY6b+21, nWidth, nHeightCj, Label = "")
        self.conda2 = self._addWidget('conda2', 'FixedText', nX2, nY6b+28, nWidth, nHeightCj, Label = "")
        self.conda3 = self._addWidget('conda3', 'FixedText', nX2, nY6b+35, nWidth, nHeightCj, Label = "")
        self.conda4 = self._addWidget('conda4', 'FixedText', nX2, nY6b+42, nWidth, nHeightCj, Label = "")
        self.conda5 = self._addWidget('conda5', 'FixedText', nX2, nY6b+49, nWidth, nHeightCj, Label = "")
        self.conda6 = self._addWidget('conda6', 'FixedText', nX2, nY6b+56, nWidth, nHeightCj, Label = "")

        self.condb = self._addWidget('condb', 'FixedText', nX2, nY7b+12, nWidth, nHeight, Label = "", \
                                     FontDescriptor = xFDtemps, FontRelief = 1, TextColor = nColorHead2)
        self.condb1 = self._addWidget('condb1', 'FixedText', nX2, nY7b+21, nWidth, nHeightCj, Label = "")
        self.condb2 = self._addWidget('condb2', 'FixedText', nX2, nY7b+28, nWidth, nHeightCj, Label = "")
        self.condb3 = self._addWidget('condb3', 'FixedText', nX2, nY7b+35, nWidth, nHeightCj, Label = "")
        self.condb4 = self._addWidget('condb4', 'FixedText', nX2, nY7b+42, nWidth, nHeightCj, Label = "")
        self.condb5 = self._addWidget('condb5', 'FixedText', nX2, nY7b+49, nWidth, nHeightCj, Label = "")
        self.condb6 = self._addWidget('condb6', 'FixedText', nX2, nY7b+56, nWidth, nHeightCj, Label = "")

        # dialog height
        self.xDialog.Height = 350
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        ## container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xContainer.setVisible(False)

        #self.xContainer.getControl('input').addEventListener(self)
        #self.xContainer.getControl('input').addEventCommand('New')
        self.xContainer.getControl('cbutton').addActionListener(self)
        self.xContainer.getControl('cbutton').setActionCommand('New')
        self.xContainer.getControl('oneg').addActionListener(self)
        self.xContainer.getControl('oneg').setActionCommand('Change')
        self.xContainer.getControl('opro').addActionListener(self)
        self.xContainer.getControl('opro').setActionCommand('Change')
        self.xContainer.getControl('oint').addActionListener(self)
        self.xContainer.getControl('oint').setActionCommand('Change')
        self.xContainer.getControl('otco').addActionListener(self)
        self.xContainer.getControl('otco').setActionCommand('Change')
        self.xContainer.getControl('ofem').addActionListener(self)
        self.xContainer.getControl('ofem').setActionCommand('Change')

        ## set verb
        self.input.Text = sArgs  if sArgs  else "être"
        self._newVerb()

        ## mysterious action
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == 'Close':
                self.xContainer.endExecute()
            elif xActionEvent.ActionCommand == 'New':
                self._newVerb()
            elif xActionEvent.ActionCommand == 'Change':
                self._displayResults()
            else:
                print(str(xActionEvent))
        except:
            traceback.print_exc()

    # XJobExecutor
    def trigger (self, args):
        try:
            xDialog = Conjugueur(self.ctx)
            xDialog.run(args)
        except:
            traceback.print_exc()

    def _newVerb (self):
        self.oneg.State = False
        self.opro.State = False
        self.oint.State = False
        self.otco.State = False
        self.ofem.State = False
        # request analyzing
        sVerb = self.input.Text.strip().lower().replace(u"’", "'").replace("  ", " ")
        if sVerb:
            if sVerb.startswith("ne pas "):
                self.oneg.State = True
                sVerb = sVerb[7:]
            if sVerb.startswith("se "):
                self.opro.State = True
                sVerb = sVerb[3:]
            elif sVerb.startswith("s'"):
                self.opro.State = True
                sVerb = sVerb[2:]
            if sVerb.endswith("?"):
                self.oint.State = True
                sVerb = sVerb.rstrip(" ?")
            if not conj_fr.isVerb(sVerb):
                self.input.TextColor = 0xAA2200
            else:
                self.input.TextColor = 0x666666
                self.oVerb = conj_fr.Verb(sVerb)
                sRawInfo = conj_fr.getVtyp(sVerb)
                self.info.Label = self.oVerb.sInfo
                self.opro.Label = "pronominal"
                if sRawInfo.endswith("zz"):
                    self.opro.State = False
                    self.opro.Enabled = False
                    self.otco.State = False
                    self.otco.Enabled = False
                    self.infomsg.Label = self.sWarning
                else:
                    self.infomsg.Label = ""
                    if sRawInfo[5] == "_":
                        self.opro.State = False
                        self.opro.Enabled = False
                    elif sRawInfo[5] in ["q", "u", "v", "e"]:
                        self.opro.State = False
                        self.opro.Enabled = True
                    elif sRawInfo[5] == "p" or sRawInfo[5] == "r":
                        self.opro.State = True
                        self.opro.Enabled = False
                    elif sRawInfo[5] == "x":
                        self.opro.Label = "cas particuliers"
                        self.opro.State = False
                        self.opro.Enabled = False
                    else:
                        self.opro.Label = "# erreur #"
                        self.opro.State = False
                        self.opro.Enabled = False
                    self.otco.Enabled = True
                self._displayResults()

    def _displayResults (self):
        try:
            self._setTitles()
            # participes passés
            self.ppas1.Label = self.oVerb.participePasse(":Q1")
            self.ppas2.Label = self.oVerb.participePasse(":Q2")
            self.ppas3.Label = self.oVerb.participePasse(":Q3")
            self.ppas4.Label = self.oVerb.participePasse(":Q4")
            # infinitif
            self.infi.Label = self.oVerb.infinitif(self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            # participe présent
            self.ppre.Label = self.oVerb.participePresent(self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            # conjugaisons
            self.ipre1.Label = self.oVerb.conjugue(":Ip", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipre2.Label = self.oVerb.conjugue(":Ip", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipre3.Label = self.oVerb.conjugue(":Ip", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipre4.Label = self.oVerb.conjugue(":Ip", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipre5.Label = self.oVerb.conjugue(":Ip", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipre6.Label = self.oVerb.conjugue(":Ip", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp1.Label = self.oVerb.conjugue(":Iq", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp2.Label = self.oVerb.conjugue(":Iq", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp3.Label = self.oVerb.conjugue(":Iq", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp4.Label = self.oVerb.conjugue(":Iq", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp5.Label = self.oVerb.conjugue(":Iq", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.iimp6.Label = self.oVerb.conjugue(":Iq", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi1.Label = self.oVerb.conjugue(":Is", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi2.Label = self.oVerb.conjugue(":Is", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi3.Label = self.oVerb.conjugue(":Is", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi4.Label = self.oVerb.conjugue(":Is", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi5.Label = self.oVerb.conjugue(":Is", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ipsi6.Label = self.oVerb.conjugue(":Is", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut1.Label = self.oVerb.conjugue(":If", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut2.Label = self.oVerb.conjugue(":If", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut3.Label = self.oVerb.conjugue(":If", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut4.Label = self.oVerb.conjugue(":If", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut5.Label = self.oVerb.conjugue(":If", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.ifut6.Label = self.oVerb.conjugue(":If", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda1.Label = self.oVerb.conjugue(":K", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda2.Label = self.oVerb.conjugue(":K", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda3.Label = self.oVerb.conjugue(":K", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda4.Label = self.oVerb.conjugue(":K", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda5.Label = self.oVerb.conjugue(":K", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.conda6.Label = self.oVerb.conjugue(":K", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            if not self.oint.State:
                self.spre1.Label = self.oVerb.conjugue(":Sp", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.spre2.Label = self.oVerb.conjugue(":Sp", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.spre3.Label = self.oVerb.conjugue(":Sp", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.spre4.Label = self.oVerb.conjugue(":Sp", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.spre5.Label = self.oVerb.conjugue(":Sp", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.spre6.Label = self.oVerb.conjugue(":Sp", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp1.Label = self.oVerb.conjugue(":Sq", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp2.Label = self.oVerb.conjugue(":Sq", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp3.Label = self.oVerb.conjugue(":Sq", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp4.Label = self.oVerb.conjugue(":Sq", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp5.Label = self.oVerb.conjugue(":Sq", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.simp6.Label = self.oVerb.conjugue(":Sq", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.impe1.Label = self.oVerb.imperatif(":2s", self.opro.State, self.oneg.State, self.otco.State, self.ofem.State)
                self.impe2.Label = self.oVerb.imperatif(":1p", self.opro.State, self.oneg.State, self.otco.State, self.ofem.State)
                self.impe3.Label = self.oVerb.imperatif(":2p", self.opro.State, self.oneg.State, self.otco.State, self.ofem.State)
            else:
                self.spre.Label = ""
                self.spre1.Label = ""
                self.spre2.Label = ""
                self.spre3.Label = ""
                self.spre4.Label = ""
                self.spre5.Label = ""
                self.spre6.Label = ""
                self.simp.Label = ""
                self.simp1.Label = ""
                self.simp2.Label = ""
                self.simp3.Label = ""
                self.simp4.Label = ""
                self.simp5.Label = ""
                self.simp6.Label = ""
                self.impe.Label = ""
                self.impe1.Label = ""
                self.impe2.Label = ""
                self.impe3.Label = ""
            if self.otco.State:
                self.condb1.Label = self.oVerb.conjugue(":Sq", ":1s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.condb2.Label = self.oVerb.conjugue(":Sq", ":2s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.condb3.Label = self.oVerb.conjugue(":Sq", ":3s", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.condb4.Label = self.oVerb.conjugue(":Sq", ":1p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.condb5.Label = self.oVerb.conjugue(":Sq", ":2p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
                self.condb6.Label = self.oVerb.conjugue(":Sq", ":3p", self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            else:
                self.condb1.Label = ""
                self.condb2.Label = ""
                self.condb3.Label = ""
                self.condb4.Label = ""
                self.condb5.Label = ""
                self.condb6.Label = ""
            self.input.Text = ""
            # refresh
            self.xContainer.setVisible(True)
        except:
            traceback.print_exc()

    def _setTitles (self):
        if not self.otco.State:
            self.ipre.Label = "Présent"
            self.ifut.Label = "Futur"
            self.iimp.Label = "Imparfait"
            self.ipsi.Label = "Passé simple"
            self.spre.Label = "Présent"
            self.simp.Label = "Imparfait"
            self.conda.Label = "Présent"
            self.condb.Label = ""
            self.impe.Label = "Présent"
        else:
            self.ipre.Label = "Passé composé"
            self.ifut.Label = "Futur antérieur"
            self.iimp.Label = "Plus-que-parfait"
            self.ipsi.Label = "Passé antérieur"
            self.spre.Label = "Passé"
            self.simp.Label = "Plus-que-parfait"
            self.conda.Label = "Passé (1ʳᵉ forme)"
            self.condb.Label = "Passé (2ᵉ forme)"
            self.impe.Label = "Passé"


# g_ImplementationHelper = unohelper.ImplementationHelper()
# g_ImplementationHelper.addImplementation(Conjugueur, 'dicollecte.Conjugueur', ('com.sun.star.task.Job',))
