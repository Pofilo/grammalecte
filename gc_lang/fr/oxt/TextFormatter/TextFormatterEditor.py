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

from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_YES_NO_CANCEL, BUTTONS_YES_NO
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
        self._addWidget('newreplacelbl', 'FixedText', nX+65, nY1+10, 130, nHeight, Label = ui.get("pattern"))
        self._addWidget('newbylbl', 'FixedText', nX+200, nY1+10, 100, nHeight, Label = ui.get("repl"))

        self.xNewName = self._addWidget('newname', 'Edit', nX, nY1+20, 60, 10, FontDescriptor = xFDMono)
        self.xNewPattern = self._addWidget('newreplace', 'Edit', nX+65, nY1+20, 130, 10, FontDescriptor = xFDMono)
        self.xNewRepl = self._addWidget('newby', 'Edit', nX+200, nY1+20, 100, 10, FontDescriptor = xFDMono)
        self.xNewRegex = self._addWidget('newregex', 'CheckBox', nX+305, nY1+22, 35, nHeight, Label = ui.get("regex"), HelpText=ui.get("regex_help"))
        self.xNewCaseSens = self._addWidget('newcasesens', 'CheckBox', nX+340, nY1+22, 40, nHeight, Label = ui.get("casesens"), HelpText=ui.get("casesens_help"), State=True)

        self._addWidget('order_info', 'FixedText', nX, nY1+32, 300, nHeight, Label = ui.get("order_info"))
        self._addWidget('add', 'Button', self.xDialog.Width-50, nY1+31, 40, 11, Label = ui.get('add'))

        lColumns = [
            {"Title": ui.get("name"),     "ColumnWidth": 80},
            {"Title": ui.get("pattern"),  "ColumnWidth": 160},
            {"Title": ui.get("repl"),     "ColumnWidth": 120},
            {"Title": ui.get("regex"),    "ColumnWidth": 60},
            {"Title": ui.get("casesens"), "ColumnWidth": 60},
        ]
        self.xGridModel = self._addGrid("list_grid", nX, nY1+45, nWidth, 150, lColumns)

        # Modify
        self._addWidget("edit_entry", 'FixedLine', nX, nY2, nWidth, nHeight, Label = ui.get("edit_entry"), FontDescriptor = xFDTitle)
        self._addWidget('editnamelbl', 'FixedText', nX, nY2+10, 60, nHeight, Label = ui.get("name"))
        self._addWidget('editreplacelbl', 'FixedText', nX+65, nY2+10, 130, nHeight, Label = ui.get("pattern"))
        self._addWidget('editbylbl', 'FixedText', nX+200, nY2+10, 100, nHeight, Label = ui.get("repl"))

        self.xEditName = self._addWidget('editname', 'Edit', nX, nY2+20, 60, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditPattern = self._addWidget('editreplace', 'Edit', nX+65, nY2+20, 130, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditRepl = self._addWidget('editby', 'Edit', nX+200, nY2+20, 100, 10, FontDescriptor = xFDMono, Enabled = False)
        self.xEditRegex = self._addWidget('editregex', 'CheckBox', nX+305, nY2+22, 35, nHeight, Label = ui.get("regex"), HelpText=ui.get("regex_help"), Enabled = False)
        self.xEditCaseSens = self._addWidget('editcasesens', 'CheckBox', nX+340, nY2+22, 40, nHeight, Label = ui.get("casesens"), HelpText=ui.get("casesens_help"), Enabled = False)

        self.xDeleteButton = self._addWidget('delete', 'Button', nX, nY2+31, 40, 11, Label = ui.get('delete'), TextColor = 0xBB5555, Enabled = False)
        self.xApplyButton = self._addWidget('apply', 'Button', nX + (self.xDialog.Width/2)-20, nY2+31, 40, 11, Label = ui.get('apply'), HelpText=ui.get("apply_help"), Enabled = False)
        self.xApplyRes = self._addWidget('apply_res', 'FixedText', nX + (self.xDialog.Width/2)+30, nY2+33, 60, 10, Label = "", Align = 2, Enabled = False)
        self.xModifyButton = self._addWidget('modify', 'Button', self.xDialog.Width-50, nY2+31, 40, 11, Label = ui.get('modify'), TextColor = 0x55BB55, Enabled = False)

        # import, export, save, close
        self._addWidget("buttons_line", 'FixedLine', nX, self.xDialog.Height-30, nWidth, nHeight)
        self._addWidget('import', 'Button', nX, self.xDialog.Height-20, 50, 14, Label = ui.get('import'), FontDescriptor = xFDTitle)
        self._addWidget('export', 'Button', nX+55, self.xDialog.Height-20, 50, 14, Label = ui.get('export'), FontDescriptor = xFDTitle)
        self._addWidget('delete_all', 'Button', nX + (self.xDialog.Width/2)-35, self.xDialog.Height-20, 70, 14, Label = ui.get('delete_all'), FontDescriptor = xFDTitle, TextColor = 0xBB5555)
        self._addWidget('save_and_close', 'Button', self.xDialog.Width-110, self.xDialog.Height-20, 100, 14, Label = ui.get('save_and_close'), FontDescriptor = xFDTitle, TextColor = 0x55BB55)

        # data
        self.dRules = {}
        self.iSelectedRow = -1
        self.nFieldMaxLen = 250

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
        self.xContainer.getControl('apply').addActionListener(self)
        self.xContainer.getControl('apply').setActionCommand('Apply')
        self.xContainer.getControl('modify').addActionListener(self)
        self.xContainer.getControl('modify').setActionCommand('Modify')
        self.xContainer.getControl('import').addActionListener(self)
        self.xContainer.getControl('import').setActionCommand('Import')
        self.xContainer.getControl('export').addActionListener(self)
        self.xContainer.getControl('export').setActionCommand('Export')
        self.xContainer.getControl('delete_all').addActionListener(self)
        self.xContainer.getControl('delete_all').setActionCommand('DeleteAll')
        self.xContainer.getControl('save_and_close').addActionListener(self)
        self.xContainer.getControl('save_and_close').setActionCommand('SaveAndClose')
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
                self.applyRule()
            elif xActionEvent.ActionCommand == "Import":
                self.importRules()
            elif xActionEvent.ActionCommand == "Export":
                self.exportRules()
            elif xActionEvent.ActionCommand == "DeleteAll":
                self.deleteAll()
            elif xActionEvent.ActionCommand == "SaveAndClose":
                self.saveRules()
                self.xContainer.endExecute()       # Modal dialog
        except:
            traceback.print_exc()

    # XGridSelectionListener
    def selectionChanged (self, xGridSelectionEvent):
        try:
            aRows = self.xGridControl.getSelectedRows()
            if aRows and len(aRows) == 1:
                self.iSelectedRow = aRows[0]
                self.sSelectedRuleName, *_ = self.xGridModel.GridDataModel.getRowData(self.iSelectedRow)
                # fill fields
                dRule = self.dRules[self.sSelectedRuleName]
                self.xEditName.Text = self.sSelectedRuleName
                self.xEditPattern.Text = dRule["sPattern"]
                self.xEditRepl.Text = dRule["sRepl"]
                self.xEditRegex.State = dRule["bRegex"]
                self.xEditCaseSens.State = dRule["bCaseSens"]
                # enable widgets
                self.xEditName.Enabled = True
                self.xEditPattern.Enabled = True
                self.xEditRepl.Enabled = True
                self.xEditRegex.Enabled = True
                self.xEditCaseSens.Enabled = True
                self.xDeleteButton.Enabled = True
                self.xApplyButton.Enabled = True
                self.xModifyButton.Enabled = True
                self.xApplyRes.Enabled = True
                self.xApplyRes.Label = ""
        except:
            self._clearEditFields()
            traceback.print_exc()

    # Code
    def _clearAddFields (self):
        self.xNewName.Text = ""
        self.xNewPattern.Text = ""
        self.xNewRepl.Text = ""
        self.xNewRegex.State = False
        self.xNewCaseSens.State = True

    def _clearEditFields (self):
        self.xEditName.Text = ""
        self.xEditPattern.Text = ""
        self.xEditRepl.Text = ""
        self.xEditRegex.State = False
        self.xEditCaseSens.State = True
        # disable widgets
        self.xEditName.Enabled = False
        self.xEditPattern.Enabled = False
        self.xEditRepl.Enabled = False
        self.xEditRegex.Enabled = False
        self.xEditCaseSens.Enabled = False
        self.xDeleteButton.Enabled = False
        self.xApplyButton.Enabled = False
        self.xModifyButton.Enabled = False
        self.xApplyRes.Enabled = False
        self.xApplyRes.Label = ""

    def addRule (self):
        if not self._checkRuleName(self.xNewName.Text):
            MessageBox(self.xDocument, ui.get("name_error"), ui.get("name_error_title"), ERRORBOX)
            return
        if not self.xNewName.Text or not self.xNewPattern.Text:
            MessageBox(self.xDocument, ui.get("name_and_replace_error"), ui.get("name_and_replace_error_title"), ERRORBOX)
            return
        if len(self.xNewPattern.Text) > self.nFieldMaxLen or len(self.xNewRepl.Text) > self.nFieldMaxLen:
            MessageBox(self.xDocument, ui.get("max_len_error"), ui.get("max_len_error_title"), ERRORBOX)
            return
        sRuleName = self.xNewName.Text
        if sRuleName in self.dRules:
            MessageBox(self.xDocument, ui.get('add_name_error'), ui.get("add_name_error_title"), ERRORBOX)
            return
        self.dRules[sRuleName] = {
            "sPattern": self.xNewPattern.Text,
            "sRepl": self.xNewRepl.Text,
            "bRegex": self.xNewRegex.State == 1,
            "bCaseSens": self.xNewCaseSens.State == 1
        }
        xGridDataModel = self.xGridModel.GridDataModel
        xGridDataModel.addRow(xGridDataModel.RowCount + 1, self._getValuesForRow(sRuleName))
        xGridDataModel.sortByColumn(0, True)
        self._clearAddFields()

    def _getValuesForRow (self, sRuleName):
        return (sRuleName, self.dRules[sRuleName]["sPattern"],
                self.dRules[sRuleName]["sRepl"],
                "✓"  if self.dRules[sRuleName]["bRegex"]  else "",
                "✓"  if self.dRules[sRuleName]["bCaseSens"]  else "")

    def _checkRuleName (self, sRuleName):
        return re.search(r"^\w[\w_#.,;!?-]{,14}$", sRuleName)

    def modifyRule (self):
        if not self._checkRuleName(self.xEditName.Text):
            MessageBox(self.xDocument, ui.get("name_error"), ui.get("name_error_title"), ERRORBOX)
            return
        sRuleName = self.xEditName.Text
        if self.iSelectedRow < 0 or not sRuleName or not self.xEditPattern.Text:
            MessageBox(self.xDocument, ui.get("name_and_replace_error"), ui.get("name_and_replace_error_title"), ERRORBOX)
            return
        if len(self.xEditPattern.Text) > self.nFieldMaxLen or len(self.xEditRepl.Text) > self.nFieldMaxLen:
            MessageBox(self.xDocument, ui.get("max_len_error"), ui.get("max_len_error_title"), ERRORBOX)
            return
        if sRuleName != self.sSelectedRuleName and sRuleName in self.dRules:
            MessageBox(self.xDocument, ui.get("modify_name_error"), ui.get("modify_name_error_title"), ERRORBOX)
            return
        try:
            self.dRules[sRuleName] = {
                "sPattern": self.xEditPattern.Text,
                "sRepl": self.xEditRepl.Text,
                "bRegex": self.xEditRegex.State == 1,
                "bCaseSens": self.xEditCaseSens.State == 1
            }
            aColumns = (0, 1, 2, 3, 4)
            self.xGridModel.GridDataModel.updateRowData(aColumns, self.iSelectedRow, self._getValuesForRow(sRuleName))
        except:
            traceback.print_exc()

    def deleteRule (self):
        if self.sSelectedRuleName != self.xEditName.Text:
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

    def deleteAll (self):
        nButton = MessageBox(self.xDocument, ui.get('delete_all_confirm'), ui.get('delete_all'), QUERYBOX, BUTTONS_YES_NO)
        if nButton == 2: # ok
            self.dRules.clear()
            self.xGridModel.GridDataModel.removeAllRows()

    @_waitPointer
    def applyRule (self):
        if self.xEditPattern.Text == "":
            return
        try:
            xRD = self.xDocument.createReplaceDescriptor()
            xRD.SearchString = self.xEditPattern.Text
            xRD.ReplaceString = self.xEditRepl.Text
            xRD.SearchRegularExpression = self.xEditRegex.State
            xRD.SearchCaseSensitive = self.xEditCaseSens.State
            n = self.xDocument.replaceAll(xRD)
            self.xApplyRes.Label = str(n) + " " + ui.get("modif")
        except:
            traceback.print_exc()

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
            xGridDataModel.sortByColumn(0, True)
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
            xGridDataModel.sortByColumn(0, True)

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
