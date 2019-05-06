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
        self.lDropDown = ["être", "avoir", "aller", "vouloir", "pouvoir", "devoir", "acquérir", "connaître", "dire", "faire", \
                          "mettre", "partir", "prendre", "répondre", "savoir", "sentir", "tenir", "vaincre", "venir", "voir", \
                          "appeler", "envoyer", "commencer", "manger", "trouver", "accomplir", "agir", "finir", "haïr", "réussir"]
        self.sWarning = "Verbe non vérifié.\nOptions “pronominal” et “temps composés” désactivées."

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
        self.xDialog.Width = 300
        self.xDialog.Title = "Grammalecte · Conjugueur"

        xFDinput = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDinput.Height = 10
        xFDinput.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDinput.Name = "Verdana"

        xFDmode = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDmode.Height = 10
        xFDmode.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDmode.Name = "Verdana"

        xFDtemps = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDtemps.Height = 9
        xFDtemps.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDtemps.Name = "Verdana"

        xFDbold = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDbold.Height = 9
        xFDbold.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDbold.Name = "Verdana"

        xFDinfo = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDinfo.Height = 8
        xFDinfo.Name = "Verdana"

        xFDsmall = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDsmall.Height = 7
        xFDsmall.Name = "Verdana"

        ## widgets
        nWidth = (self.xDialog.Width-30) // 2
        nHeight = 10
        nHeightCj = 8
        nTitleColor = 0x660000
        nSubTitleColor = 0x000033

        # grid
        nX1 = 10; nX2 = nX1+145;
        nY0 = 5; nY1 = nY0+17; nY2 = nY1+2; nY3 = nY2+30; nY4 = nY3+46; nY5 = nY4+55; nY6 = nY5+55; nY7 = nY6+55; nY6b = nY6+13; nY7b = nY6b+55

        # input field + button
        self.input = self._addWidget('input', 'ComboBox', nX1, nY0, 85, 14, \
                                     FontDescriptor = xFDinput, TextColor = 0x666666, Dropdown = True, LineCount = 30)
        for n, s in enumerate(self.lDropDown):
            self.input.insertItemText(n, s)
        # button
        self.cbutton = self._addWidget('cbutton', 'Button', nX1+90, nY0, 50, 14, Label = "Conjuguer", FontDescriptor = xFDinput)
        # options
        self.oneg = self._addWidget('oneg', 'CheckBox', nX2, nY0, 40, nHeight, Label = "négation")
        self.opro = self._addWidget('opro', 'CheckBox', nX2+45, nY0, 55, nHeight, Label = "pronominal")
        self.ofem = self._addWidget('ofem', 'CheckBox', nX2+100, nY0, 50, nHeight, Label = "féminin")
        self.oint = self._addWidget('oint', 'CheckBox', nX2, nY0+8, 60, nHeight, Label = "interrogatif")
        self.otco = self._addWidget('otco', 'CheckBox', nX2+75, nY0+8, 60, nHeight, Label = "temps composés")

        # group box // indicatif
        gb_infi = self._addWidget('groupbox_infi', 'FixedLine', nX1, nY2, nWidth, 10, Label = "Infinitif", \
                                  FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.infi = self._addWidget('infi', 'FixedText', nX1, nY2+10, nWidth, nHeight, Label = "", FontDescriptor = xFDbold)

        # informations
        self.info = self._addWidget('info', 'FixedText', nX2, nY2+5, nWidth, nHeight, FontDescriptor = xFDinfo)
        self.option_msg = self._addWidget('option_msg', 'FixedText', nX2, nY2+15, nWidth, 15, FontDescriptor = xFDsmall, \
                                          MultiLine = True, TextColor = 0x333333, Label = self.sWarning)

        # group box // participe passé
        gb_ppas = self._addWidget('groupbox_ppas', 'FixedLine', nX1, nY3-7, nWidth, 10, Label = "Participes présent et passés", \
                                  FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.ppre = self._addWidget('ppre', 'FixedText', nX1, nY3+5, nWidth, nHeightCj, Label = "")
        self.ppas1 = self._addWidget('ppas1', 'FixedText', nX1, nY3+14, nWidth, nHeightCj, Label = "")
        self.ppas2 = self._addWidget('ppas2', 'FixedText', nX1, nY3+21, nWidth, nHeightCj, Label = "")
        self.ppas3 = self._addWidget('ppas3', 'FixedText', nX1, nY3+28, nWidth, nHeightCj, Label = "")
        self.ppas4 = self._addWidget('ppas4', 'FixedText', nX1, nY3+35, nWidth, nHeightCj, Label = "")

        # group box // impératif
        gb_impe = self._addWidget('groupbox_impe', 'FixedLine', nX2, nY3, nWidth, 10, Label = "Impératif", \
                                  FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.impe = self._addWidget('impe', 'FixedText', nX2, nY3+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.impe1 = self._addWidget('impe1', 'FixedText', nX2, nY3+21, nWidth, nHeightCj, Label = "")
        self.impe2 = self._addWidget('impe2', 'FixedText', nX2, nY3+28, nWidth, nHeightCj, Label = "")
        self.impe3 = self._addWidget('impe3', 'FixedText', nX2, nY3+35, nWidth, nHeightCj, Label = "")

        # group box // indicatif
        gb_ind = self._addWidget('groupbox_ind', 'FixedLine', nX1, nY4, nWidth, 10, Label = "Indicatif", \
                                 FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.ipre = self._addWidget('ipre', 'FixedText', nX1, nY4+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.ipre1 = self._addWidget('ipre1', 'FixedText', nX1, nY4+21, nWidth, nHeightCj, Label = "")
        self.ipre2 = self._addWidget('ipre2', 'FixedText', nX1, nY4+28, nWidth, nHeightCj, Label = "")
        self.ipre3 = self._addWidget('ipre3', 'FixedText', nX1, nY4+35, nWidth, nHeightCj, Label = "")
        self.ipre4 = self._addWidget('ipre4', 'FixedText', nX1, nY4+42, nWidth, nHeightCj, Label = "")
        self.ipre5 = self._addWidget('ipre5', 'FixedText', nX1, nY4+49, nWidth, nHeightCj, Label = "")
        self.ipre6 = self._addWidget('ipre6', 'FixedText', nX1, nY4+56, nWidth, nHeightCj, Label = "")

        self.iimp = self._addWidget('iimp', 'FixedText', nX1, nY5+12, nWidth, nHeight, Label = "Imparfait", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.iimp1 = self._addWidget('iimp1', 'FixedText', nX1, nY5+21, nWidth, nHeightCj, Label = "")
        self.iimp2 = self._addWidget('iimp2', 'FixedText', nX1, nY5+28, nWidth, nHeightCj, Label = "")
        self.iimp3 = self._addWidget('iimp3', 'FixedText', nX1, nY5+35, nWidth, nHeightCj, Label = "")
        self.iimp4 = self._addWidget('iimp4', 'FixedText', nX1, nY5+42, nWidth, nHeightCj, Label = "")
        self.iimp5 = self._addWidget('iimp5', 'FixedText', nX1, nY5+49, nWidth, nHeightCj, Label = "")
        self.iimp6 = self._addWidget('iimp6', 'FixedText', nX1, nY5+56, nWidth, nHeightCj, Label = "")

        self.ipsi = self._addWidget('ipsi', 'FixedText', nX1, nY6+12, nWidth, nHeight, Label = "Passé Simple", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.ipsi1 = self._addWidget('ipsi1', 'FixedText', nX1, nY6+21, nWidth, nHeightCj, Label = "")
        self.ipsi2 = self._addWidget('ipsi2', 'FixedText', nX1, nY6+28, nWidth, nHeightCj, Label = "")
        self.ipsi3 = self._addWidget('ipsi3', 'FixedText', nX1, nY6+35, nWidth, nHeightCj, Label = "")
        self.ipsi4 = self._addWidget('ipsi4', 'FixedText', nX1, nY6+42, nWidth, nHeightCj, Label = "")
        self.ipsi5 = self._addWidget('ipsi5', 'FixedText', nX1, nY6+49, nWidth, nHeightCj, Label = "")
        self.ipsi6 = self._addWidget('ipsi6', 'FixedText', nX1, nY6+56, nWidth, nHeightCj, Label = "")

        self.ifut = self._addWidget('ifut', 'FixedText', nX1, nY7+12, nWidth, nHeight, Label = "Futur", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.ifut1 = self._addWidget('ifut1', 'FixedText', nX1, nY7+21, nWidth, nHeightCj, Label = "")
        self.ifut2 = self._addWidget('ifut2', 'FixedText', nX1, nY7+28, nWidth, nHeightCj, Label = "")
        self.ifut3 = self._addWidget('ifut3', 'FixedText', nX1, nY7+35, nWidth, nHeightCj, Label = "")
        self.ifut4 = self._addWidget('ifut4', 'FixedText', nX1, nY7+42, nWidth, nHeightCj, Label = "")
        self.ifut5 = self._addWidget('ifut5', 'FixedText', nX1, nY7+49, nWidth, nHeightCj, Label = "")
        self.ifut6 = self._addWidget('ifut6', 'FixedText', nX1, nY7+56, nWidth, nHeightCj, Label = "")

        # group box // subjonctif
        gb_sub = self._addWidget('groupbox_sub', 'FixedLine', nX2, nY4, nWidth, 10, Label = "Subjonctif", \
                                 FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.spre = self._addWidget('spre', 'FixedText', nX2, nY4+12, nWidth, nHeight, Label = "Présent", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.spre1 = self._addWidget('spre1', 'FixedText', nX2, nY4+21, nWidth, nHeightCj, Label = "")
        self.spre2 = self._addWidget('spre2', 'FixedText', nX2, nY4+28, nWidth, nHeightCj, Label = "")
        self.spre3 = self._addWidget('spre3', 'FixedText', nX2, nY4+35, nWidth, nHeightCj, Label = "")
        self.spre4 = self._addWidget('spre4', 'FixedText', nX2, nY4+42, nWidth, nHeightCj, Label = "")
        self.spre5 = self._addWidget('spre5', 'FixedText', nX2, nY4+49, nWidth, nHeightCj, Label = "")
        self.spre6 = self._addWidget('spre6', 'FixedText', nX2, nY4+56, nWidth, nHeightCj, Label = "")

        self.simp = self._addWidget('simp', 'FixedText', nX2, nY5+12, nWidth, nHeight, Label = "Imparfait", \
                                    FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.simp1 = self._addWidget('simp1', 'FixedText', nX2, nY5+21, nWidth, nHeightCj, Label = "")
        self.simp2 = self._addWidget('simp2', 'FixedText', nX2, nY5+28, nWidth, nHeightCj, Label = "")
        self.simp3 = self._addWidget('simp3', 'FixedText', nX2, nY5+35, nWidth, nHeightCj, Label = "")
        self.simp4 = self._addWidget('simp4', 'FixedText', nX2, nY5+42, nWidth, nHeightCj, Label = "")
        self.simp5 = self._addWidget('simp5', 'FixedText', nX2, nY5+49, nWidth, nHeightCj, Label = "")
        self.simp6 = self._addWidget('simp6', 'FixedText', nX2, nY5+56, nWidth, nHeightCj, Label = "")

        # group box // conditionnel
        gb_cond = self._addWidget('groupbox_cond', 'FixedLine', nX2, nY6b, nWidth, 10, Label = "Conditionnel", \
                                  FontDescriptor = xFDmode, FontRelief = 0, TextColor = nTitleColor)
        self.conda = self._addWidget('conda', 'FixedText', nX2, nY6b+12, nWidth, nHeight, Label = "Présent", \
                                     FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
        self.conda1 = self._addWidget('conda1', 'FixedText', nX2, nY6b+21, nWidth, nHeightCj, Label = "")
        self.conda2 = self._addWidget('conda2', 'FixedText', nX2, nY6b+28, nWidth, nHeightCj, Label = "")
        self.conda3 = self._addWidget('conda3', 'FixedText', nX2, nY6b+35, nWidth, nHeightCj, Label = "")
        self.conda4 = self._addWidget('conda4', 'FixedText', nX2, nY6b+42, nWidth, nHeightCj, Label = "")
        self.conda5 = self._addWidget('conda5', 'FixedText', nX2, nY6b+49, nWidth, nHeightCj, Label = "")
        self.conda6 = self._addWidget('conda6', 'FixedText', nX2, nY6b+56, nWidth, nHeightCj, Label = "")

        self.condb = self._addWidget('condb', 'FixedText', nX2, nY7b+12, nWidth, nHeight, Label = "", \
                                     FontDescriptor = xFDtemps, FontRelief = 0, TextColor = nSubTitleColor)
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
                if self.oVerb:
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
            self.oVerb = None
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
                self.info.Label = self.oVerb.sInfo
                self.opro.Label = self.oVerb.sProLabel
                if self.oVerb.bUncomplete:
                    self.opro.State = False
                    self.opro.Enabled = False
                    self.otco.State = False
                    self.otco.Enabled = False
                    self.option_msg.Label = self.sWarning
                else:
                    self.otco.Enabled = True
                    if self.oVerb.nPronominable == 0:
                        self.opro.State = False
                        self.opro.Enabled = True
                    elif self.oVerb.nPronominable == 1:
                        self.opro.State = True
                        self.opro.Enabled = False
                    else: # -1 or 1 or error
                        self.opro.State = False
                        self.opro.Enabled = False
                    self.option_msg.Label = ""
                self._displayResults()

    def _displayResults (self):
        try:
            dConjTable = self.oVerb.createConjTable(self.opro.State, self.oneg.State, self.otco.State, self.oint.State, self.ofem.State)
            self.input.Text = ""
            # infinitif
            self.infi.Label = dConjTable["infi"]
            # participe présent
            self.ppre.Label = dConjTable["ppre"]
            # participes passés
            self.ppas1.Label = dConjTable["ppas1"]
            self.ppas2.Label = dConjTable["ppas2"]
            self.ppas3.Label = dConjTable["ppas3"]
            self.ppas4.Label = dConjTable["ppas4"]
            # impératif
            self.impe.Label = dConjTable["t_impe"]
            self.impe1.Label = dConjTable["impe1"]
            self.impe2.Label = dConjTable["impe2"]
            self.impe3.Label = dConjTable["impe3"]
            # présent
            self.ipre.Label = dConjTable["t_ipre"]
            self.ipre1.Label = dConjTable["ipre1"]
            self.ipre2.Label = dConjTable["ipre2"]
            self.ipre3.Label = dConjTable["ipre3"]
            self.ipre4.Label = dConjTable["ipre4"]
            self.ipre5.Label = dConjTable["ipre5"]
            self.ipre6.Label = dConjTable["ipre6"]
            # imparfait
            self.iimp.Label = dConjTable["t_iimp"]
            self.iimp1.Label = dConjTable["iimp1"]
            self.iimp2.Label = dConjTable["iimp2"]
            self.iimp3.Label = dConjTable["iimp3"]
            self.iimp4.Label = dConjTable["iimp4"]
            self.iimp5.Label = dConjTable["iimp5"]
            self.iimp6.Label = dConjTable["iimp6"]
            # passé simple
            self.ipsi.Label = dConjTable["t_ipsi"]
            self.ipsi1.Label = dConjTable["ipsi1"]
            self.ipsi2.Label = dConjTable["ipsi2"]
            self.ipsi3.Label = dConjTable["ipsi3"]
            self.ipsi4.Label = dConjTable["ipsi4"]
            self.ipsi5.Label = dConjTable["ipsi5"]
            self.ipsi6.Label = dConjTable["ipsi6"]
            # futur
            self.ifut.Label = dConjTable["t_ifut"]
            self.ifut1.Label = dConjTable["ifut1"]
            self.ifut2.Label = dConjTable["ifut2"]
            self.ifut3.Label = dConjTable["ifut3"]
            self.ifut4.Label = dConjTable["ifut4"]
            self.ifut5.Label = dConjTable["ifut5"]
            self.ifut6.Label = dConjTable["ifut6"]
            # Conditionnel
            self.conda.Label = dConjTable["t_conda"]
            self.conda1.Label = dConjTable["conda1"]
            self.conda2.Label = dConjTable["conda2"]
            self.conda3.Label = dConjTable["conda3"]
            self.conda4.Label = dConjTable["conda4"]
            self.conda5.Label = dConjTable["conda5"]
            self.conda6.Label = dConjTable["conda6"]
            self.condb.Label = dConjTable["t_condb"]
            self.condb1.Label = dConjTable["condb1"]
            self.condb2.Label = dConjTable["condb2"]
            self.condb3.Label = dConjTable["condb3"]
            self.condb4.Label = dConjTable["condb4"]
            self.condb5.Label = dConjTable["condb5"]
            self.condb6.Label = dConjTable["condb6"]
            # subjonctif présent
            self.spre.Label = dConjTable["t_spre"]
            self.spre1.Label = dConjTable["spre1"]
            self.spre2.Label = dConjTable["spre2"]
            self.spre3.Label = dConjTable["spre3"]
            self.spre4.Label = dConjTable["spre4"]
            self.spre5.Label = dConjTable["spre5"]
            self.spre6.Label = dConjTable["spre6"]
            # subjonctif imparfait
            self.simp.Label = dConjTable["t_simp"]
            self.simp1.Label = dConjTable["simp1"]
            self.simp2.Label = dConjTable["simp2"]
            self.simp3.Label = dConjTable["simp3"]
            self.simp4.Label = dConjTable["simp4"]
            self.simp5.Label = dConjTable["simp5"]
            self.simp6.Label = dConjTable["simp6"]
            # refresh
            self.xContainer.setVisible(True)
        except:
            traceback.print_exc()

# g_ImplementationHelper = unohelper.ImplementationHelper()
# g_ImplementationHelper.addImplementation(Conjugueur, 'dicollecte.Conjugueur', ('com.sun.star.task.Job',))
