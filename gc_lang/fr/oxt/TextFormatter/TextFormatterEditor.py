# Text Formatter Editor
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback
import platform
import os
import json
import re

import helpers
import tfe_strings as ui
import grammalecte.graphspell as sc

from com.sun.star.awt import XActionListener
from com.sun.star.awt.grid import XGridSelectionListener

from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_YES_NO_CANCEL
# BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
# DEFAULT_BUTTON_OK, DEFAULT_BUTTON_CANCEL, DEFAULT_BUTTON_RETRY, DEFAULT_BUTTON_YES, DEFAULT_BUTTON_NO, DEFAULT_BUTTON_IGNORE
from com.sun.star.awt.MessageBoxType import INFOBOX, ERRORBOX, QUERYBOX # MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX


def MessageBox (xDocument, sMsg, sTitle, nBoxType=INFOBOX, nBoxButtons=BUTTONS_OK):
    xParentWin = xDocument.CurrentController.Frame.ContainerWindow
    ctx = uno.getComponentContext()
    xToolkit = ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    xMsgBox = xToolkit.createMessageBox(xParentWin, nBoxType, nBoxButtons, sTitle, sMsg)
    return xMsgBox.execute()


def _waitPointer (funcDecorated):
    def wrapper (*args, **kwargs):
        # self is the first parameter if the decorator is applied on a object
        self = args[0]
        # before
        xPointer = self.xSvMgr.createInstanceWithContext("com.sun.star.awt.Pointer", self.ctx)
        xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.WAIT"))
        xWindowPeer = self.xContainer.getPeer()
        xWindowPeer.setPointer(xPointer)
        for x in xWindowPeer.Windows:
            x.setPointer(xPointer)
        # processing
        result = funcDecorated(*args, **kwargs)
        # after
        xPointer.setType(uno.getConstantByName("com.sun.star.awt.SystemPointer.ARROW"))
        xWindowPeer.setPointer(xPointer)
        for x in xWindowPeer.Windows:
            x.setPointer(xPointer)
        self.xContainer.setVisible(True) # seems necessary to refresh the dialog box and text widgets (why?)
        # return
        return result
    return wrapper


class TextFormatterEditor (unohelper.Base, XActionListener, XGridSelectionListener):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
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

    def _addGrid (self, name, x, y, w, h, columns, **kwargs):
        xGridModel = self.xDialog.createInstance('com.sun.star.awt.grid.UnoControlGridModel')
        xGridModel.Name = name
        xGridModel.PositionX = x
        xGridModel.PositionY = y
        xGridModel.Width = w
        xGridModel.Height = h
        xColumnModel = xGridModel.ColumnModel
        for e in columns:
            xCol = xColumnModel.createColumn()
            for k, w in e.items():
                setattr(xCol, k, w)
            xColumnModel.addColumn(xCol)
        for k, w in kwargs.items():
            setattr(xGridModel, k, w)
        self.xDialog.insertByName(name, xGridModel)
        return xGridModel

    def run (self, sLang):
        # lang
        ui.selectLang(sLang)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 400
        self.xDialog.Height = 280
        self.xDialog.Title = ui.get('title')
        xWindowSize = helpers.getWindowSize()
        self.xDialog.PositionX = int((xWindowSize.Width / 2) - (self.xDialog.Width / 2))
        self.xDialog.PositionY = int((xWindowSize.Height / 2) - (self.xDialog.Height / 2))

        # fonts
        xFDTitle = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDTitle.Height = 9
        xFDTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDTitle.Name = "Verdana"

        xFDMono = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDMono.Height = 8
        xFDMono.Name = "Monospace"

        # widget
        nX = 10
        nY1 = 5
        nY2 = nY1 + 200

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # Add
        self._addWidget("new_entry", 'FixedLine', nX, nY1, nWidth, nHeight, Label = ui.get("new_entry"), FontDescriptor = xFDTitle)

        self._addWidget('newnamelbl', 'FixedText', nX, nY1+10, 60, nHeight, Label = ui.get("name"))
        self._addWidget('newreplacelbl', 'FixedText', nX+65, nY1+10, 130, nHeight, Label = ui.get("replace"))
        self._addWidget('newbylbl', 'FixedText', nX+200, nY1+10, 100, nHeight, Label = ui.get("by"))

        self.xNewname = self._addWidget('newname', 'Edit', nX, nY1+20, 60, 10, FontDescriptor = xFDMono)
        self.xNewreplace = self._addWidget('newreplace', 'Edit', nX+65, nY1+20, 130, 10, FontDescriptor = xFDMono)
        self.xNewby = self._addWidget('newby', 'Edit', nX+200, nY1+20, 100, 10, FontDescriptor = xFDMono)
        self.xNewregex = self._addWidget('newregex', 'CheckBox', nX+305, nY1+22, 35, nHeight, Label = ui.get("regex"), HelpText=ui.get("regex_help"))
        self.xNewcasesens = self._addWidget('newcasesens', 'CheckBox', nX+340, nY1+22, 40, nHeight, Label = ui.get("casesens"), HelpText=ui.get("casesens_help"), State=True)

        self._addWidget('add', 'Button', self.xDialog.Width-50, nY1+31, 40, 11, Label = ui.get('add'))

        lColumns = [
            {"Title": ui.get("name"),     "ColumnWidth": 80},
            {"Title": ui.get("replace"),  "ColumnWidth": 140},
            {"Title": ui.get("by"),       "ColumnWidth": 140},
            {"Title": ui.get("regex"),    "ColumnWidth": 60},
            {"Title": ui.get("casesens"), "ColumnWidth": 60},
        ]
        self.xGridModel = self._addGrid("list_grid", nX, nY1+45, nWidth, 150, lColumns)

        # Modify
        self._addWidget("edit_entry", 'FixedLine', nX, nY2, nWidth, nHeight, Label = ui.get("edit_entry"), FontDescriptor = xFDTitle)

        self._addWidget('editnamelbl', 'FixedText', nX, nY2+10, 60, nHeight, Label = ui.get("name"))
        self._addWidget('editreplacelbl', 'FixedText', nX+65, nY2+10, 130, nHeight, Label = ui.get("replace"))
        self._addWidget('editbylbl', 'FixedText', nX+200, nY2+10, 100, nHeight, Label = ui.get("by"))

        self.xEditname = self._addWidget('editname', 'Edit', nX, nY2+20, 60, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditreplace = self._addWidget('editreplace', 'Edit', nX+65, nY2+20, 130, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditby = self._addWidget('editby', 'Edit', nX+200, nY2+20, 100, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditregex = self._addWidget('editregex', 'CheckBox', nX+305, nY2+22, 35, nHeight, Label = ui.get("regex"), HelpText=ui.get("regex_help"), Enabled = False)
        self.xEditcasesens = self._addWidget('editcasesens', 'CheckBox', nX+340, nY2+22, 40, nHeight, Label = ui.get("casesens"), HelpText=ui.get("casesens_help"), Enabled = False)

        self.xDeleteButton = self._addWidget('delete', 'Button', nX, nY2+31, 40, 11, Label = ui.get('delete'), TextColor = 0xAA0000, Enabled = False)
        self.xApplyButton = self._addWidget('apply', 'Button', nX + (self.xDialog.Width/2)-20, nY2+31, 40, 11, Label = ui.get('apply'), HelpText="apply_help", TextColor = 0x0000AA, Enabled = False)
        self.xModifyButton = self._addWidget('modify', 'Button', self.xDialog.Width-50, nY2+31, 40, 11, Label = ui.get('modify'), TextColor = 0x00AA00, Enabled = False)

        # import, export, save, close
        self._addWidget("buttons_line", 'FixedLine', nX, self.xDialog.Height-35, nWidth, nHeight)
        self._addWidget('import', 'Button', nX, self.xDialog.Height-25, 50, 14, Label = ui.get('import'), FontDescriptor = xFDTitle, TextColor = 0x0000AA)
        self._addWidget('export', 'Button', nX+60, self.xDialog.Height-25, 50, 14, Label = ui.get('export'), FontDescriptor = xFDTitle, TextColor = 0x00AA00)
        self._addWidget('save', 'Button', self.xDialog.Width-120, self.xDialog.Height-25, 50, 14, Label = ui.get('save'), FontDescriptor = xFDTitle, TextColor = 0x00AA00)
        self._addWidget('close', 'Button', self.xDialog.Width-60, self.xDialog.Height-25, 50, 14, Label = ui.get('close'), FontDescriptor = xFDTitle, TextColor = 0xAA0000)

        # data
        self.dRules = {}
        self.iSelectedRow = -1


        # load configuration
        self.xGLOptionNode = helpers.getConfigSetting("/org.openoffice.Lightproof_${implname}/Other/", True)
        self.loadRules()

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControl = self.xContainer.getControl('list_grid')
        self.xGridControl.addSelectionListener(self)
        self.xContainer.getControl('add').addActionListener(self)
        self.xContainer.getControl('add').setActionCommand('Add')
        self.xContainer.getControl('delete').addActionListener(self)
        self.xContainer.getControl('delete').setActionCommand('Delete')
        self.xContainer.getControl('modify').addActionListener(self)
        self.xContainer.getControl('modify').setActionCommand('Modify')
        self.xContainer.getControl('import').addActionListener(self)
        self.xContainer.getControl('import').setActionCommand('Import')
        self.xContainer.getControl('export').addActionListener(self)
        self.xContainer.getControl('export').setActionCommand('Export')
        self.xContainer.getControl('save').addActionListener(self)
        self.xContainer.getControl('save').setActionCommand('Save')
        self.xContainer.getControl('close').addActionListener(self)
        self.xContainer.getControl('close').setActionCommand('Close')
        self.xContainer.setVisible(False)    # True for non modal dialog
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        self.xContainer.execute()

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == "Add":
                self.addRule()
            elif xActionEvent.ActionCommand == "Delete":
                self.deleteRule()
            elif xActionEvent.ActionCommand == "Modify":
                self.modifyRule()
            elif xActionEvent.ActionCommand == "Apply":
                self.apply()
            elif xActionEvent.ActionCommand == "Save":
                self.saveRules()
            elif xActionEvent.ActionCommand == "Import":
                self.importRules()
            elif xActionEvent.ActionCommand == "Export":
                self.exportRules()
            elif xActionEvent.ActionCommand == "Close":
                self.xContainer.endExecute()       # Modal dialog
        except:
            traceback.print_exc()

    # XGridSelectionListener
    def selectionChanged (self, xGridSelectionEvent):
        try:
            aRows = self.xGridControl.getSelectedRows()
            if aRows and len(aRows) == 1:
                self.iSelectedRow = aRows[0]
                self.sSelectedRuleName, sReplace, sBy, sRegex, sCaseSens = self.xGridModel.GridDataModel.getRowData(self.iSelectedRow)
                # fill fields
                self.xEditname.Text = self.sSelectedRuleName
                self.xEditreplace.Text = sReplace
                self.xEditby.Text = sBy
                self.xEditregex.State = sRegex == "True"
                self.xEditcasesens.State = sCaseSens == "True"
                # enable widgets
                self.xEditname.Enabled = True
                self.xEditreplace.Enabled = True
                self.xEditby.Enabled = True
                self.xEditregex.Enabled = True
                self.xEditcasesens.Enabled = True
                self.xDeleteButton.Enabled = True
                self.xApplyButton.Enabled = True
                self.xModifyButton.Enabled = True
        except:
            self._clearEditFields()
            traceback.print_exc()

    # Code
    def _clearAddFields (self):
        self.xNewname.Text = ""
        self.xNewreplace.Text = ""
        self.xNewby.Text = ""
        self.xNewregex.State = False
        self.xNewcasesens.State = True

    def _clearEditFields (self):
        self.xEditname.Text = ""
        self.xEditreplace.Text = ""
        self.xEditby.Text = ""
        self.xEditregex.State = False
        self.xEditcasesens.State = True
        # disable widgets
        self.xEditname.Enabled = False
        self.xEditreplace.Enabled = False
        self.xEditby.Enabled = False
        self.xEditregex.Enabled = False
        self.xEditcasesens.Enabled = False
        self.xDeleteButton.Enabled = False
        self.xApplyButton.Enabled = False
        self.xModifyButton.Enabled = False

    def addRule (self):
        if not self._checkRuleName(self.xNewname.Text):
            MessageBox(self.xDocument, ui.get("name_error"), ui.get("name_error_title"), ERRORBOX)
            return
        if not self.xNewname.Text or not self.xNewreplace.Text:
            MessageBox(self.xDocument, ui.get("name_and_replace_error"), ui.get("name_and_replace_error_title"), ERRORBOX)
            return
        sRuleName = self.xNewname.Text
        if sRuleName in self.dRules:
            MessageBox(self.xDocument, ui.get('add_name_error'), ui.get("add_name_error_title"), ERRORBOX)
            return
        self.dRules[sRuleName] = {
            "sReplace": self.xNewreplace.Text,
            "sBy": self.xNewby.Text,
            "bRegex": self.xNewregex.State == 1,
            "bCaseSens": self.xNewcasesens.State == 1
        }
        xGridDataModel = self.xGridModel.GridDataModel
        xGridDataModel.addRow(xGridDataModel.RowCount + 1, self._getValuesForRow(sRuleName))
        self._clearAddFields()

    def _getValuesForRow (self, sRuleName):
        return (sRuleName, self.dRules[sRuleName]["sReplace"], self.dRules[sRuleName]["sBy"], str(self.dRules[sRuleName]["bRegex"]), str(self.dRules[sRuleName]["bCaseSens"]))

    def _checkRuleName (self, sRuleName):
        return re.search(r"^\w[\w_#.,;!?-]*$", sRuleName)

    def modifyRule (self):
        if not self._checkRuleName(self.xEditname.Text):
            MessageBox(self.xDocument, ui.get("name_error"), ui.get("name_error_title"), ERRORBOX)
            return
        sRuleName = self.xEditname.Text
        if self.iSelectedRow < 0 or not sRuleName or not self.xEditreplace.Text:
            MessageBox(self.xDocument, ui.get("name_and_replace_error"), ui.get("name_and_replace_error_title"), ERRORBOX)
            return
        if sRuleName != self.sSelectedRuleName and sRuleName in self.dRules:
            MessageBox(self.xDocument, ui.get("modify_name_error"), ui.get("modify_name_error_title"), ERRORBOX)
            return
        try:
            self.dRules[sRuleName] = {
                "sReplace": self.xEditreplace.Text,
                "sBy": self.xEditby.Text,
                "bRegex": self.xEditregex.State == 1,
                "bCaseSens": self.xEditcasesens.State == 1
            }
            aColumns = (0, 1, 2, 3, 4)
            self.xGridModel.GridDataModel.updateRowData(aColumns, self.iSelectedRow, self._getValuesForRow(sRuleName))
        except:
            traceback.print_exc()

    def deleteRule (self):
        if self.sSelectedRuleName != self.xEditname.Text:
            MessageBox(self.xDocument, ui.get('delete_name_error'), ui.get("delete_name_error_title"), ERRORBOX)
            return
        sRuleName = self.sSelectedRuleName
        if not sRuleName or sRuleName not in self.dRules:
            return
        try:
            self._clearEditFields()
            self.xGridModel.GridDataModel.removeRow(self.iSelectedRow)
            self.iSelectedRow = -1
            del self.dRules[sRuleName]
        except:
            traceback.print_exc()

    @_waitPointer
    def apply (self):
        pass

    def loadRules (self):
        try:
            xChild = self.xGLOptionNode.getByName("o_${lang}")
            sTFEditorOptions = xChild.getPropertyValue("tfe_rules")
            if not sTFEditorOptions:
                return
            self.dRules = json.loads(sTFEditorOptions)
            xGridDataModel = self.xGridModel.GridDataModel
            for sRuleName in self.dRules:
                xGridDataModel.addRow(xGridDataModel.RowCount + 1, self._getValuesForRow(sRuleName))
        except:
            sMessage = traceback.format_exc()
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)

    @_waitPointer
    def saveRules (self):
        try:
            xChild = self.xGLOptionNode.getByName("o_${lang}")
            xChild.setPropertyValue("tfe_rules", json.dumps(self.dRules))
            self.xGLOptionNode.commitChanges()
        except:
            sMessage = traceback.format_exc()
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)

    @_waitPointer
    def importRules (self):
        spfImported = ""
        try:
            xFilePicker = self.xSvMgr.createInstanceWithContext('com.sun.star.ui.dialogs.FilePicker', self.ctx)  # other possibility: com.sun.star.ui.dialogs.SystemFilePicker
            xFilePicker.initialize([uno.getConstantByName("com.sun.star.ui.dialogs.TemplateDescription.FILEOPEN_SIMPLE")]) # seems useless
            xFilePicker.appendFilter("Supported files", "*.json")
            xFilePicker.setDefaultName("grammalecte_tf_trans_rules.json") # useless, doesn’t work
            xFilePicker.setDisplayDirectory("")
            xFilePicker.setMultiSelectionMode(False)
            nResult = xFilePicker.execute()
            if nResult == 1:
                # lFile = xFilePicker.getSelectedFiles()
                lFile = xFilePicker.getFiles()
                #print(lFile)
                spfImported = lFile[0][5:].lstrip("/") # remove file://
                if platform.system() != "Windows":
                    spfImported = "/" + spfImported
        except:
            sMessage = traceback.format_exc()
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)
            return
        if not spfImported or not os.path.isfile(spfImported):
            sMessage = ui.get('file_not_found') + "<" + spfImported + ">"
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)
            return
        try:
            with open(spfImported, "r", encoding="utf-8") as hFile:
                dImportedRules = json.load(hFile)
        except:
            sMessage = traceback.format_exc()
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)
        else:
            nButton = MessageBox(self.xDocument, ui.get('import_question'), ui.get('import_title'), QUERYBOX, BUTTONS_YES_NO_CANCEL)
            if nButton == 0: # cancel
                return
            xGridDataModel = self.xGridModel.GridDataModel
            if nButton == 2: # yes
                self.dRules.update(dImportedRules)
                self.xGridModel.GridDataModel.removeAllRows()
                for sRuleName in self.dRules:
                    xGridDataModel.addRow(xGridDataModel.RowCount + 1, self._getValuesForRow(sRuleName))
            else: # 3 = no
                for sRuleName, dValues in dImportedRules.items():
                    if not sRuleName in self.dRules:
                        self.dRules[sRuleName] = dValues
                        xGridDataModel.addRow(xGridDataModel.RowCount + 1, self._getValuesForRow(sRuleName))

    def exportRules (self):
        if not self.dRules:
            return
        sText = json.dumps(self.dRules, ensure_ascii=False)
        try:
            xFilePicker = self.xSvMgr.createInstanceWithContext('com.sun.star.ui.dialogs.FilePicker', self.ctx)  # other possibility: com.sun.star.ui.dialogs.SystemFilePicker
            xFilePicker.initialize([uno.getConstantByName("com.sun.star.ui.dialogs.TemplateDescription.FILESAVE_SIMPLE")]) # seems useless
            xFilePicker.appendFilter("Supported files", "*.json")
            xFilePicker.setDefaultName("grammalecte_tf_trans_rules.json") # doesn’t work on Windows
            xFilePicker.setDisplayDirectory("")
            xFilePicker.setMultiSelectionMode(False)
            nResult = xFilePicker.execute()
            if nResult == 1:
                # lFile = xFilePicker.getSelectedFiles()
                lFile = xFilePicker.getFiles()
                spfExported = lFile[0][5:].lstrip("/") # remove file://
                if platform.system() != "Windows":
                    spfExported = "/" + spfExported
                #spfExported = os.path.join(os.path.expanduser("~"), "fr.personal.json")
                with open(spfExported, "w", encoding="utf-8") as hDst:
                    hDst.write(sText)
        except:
            sMessage = traceback.format_exc()
            MessageBox(self.xDocument, sMessage, ui.get('error'), ERRORBOX)
