# Enumerator of Words
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback
import platform

import helpers
import enum_strings as ui
import grammalecte.graphspell as sc

from com.sun.star.task import XJobExecutor
from com.sun.star.awt import XActionListener
from com.sun.star.awt import XTopWindowListener

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


def hexToRBG (sHexa):
    r = int(sHexa[:2], 16)
    g = int(sHexa[2:4], 16)
    b = int(sHexa[4:], 16)
    return (r & 255) << 16 | (g & 255) << 8 | (b & 255)


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


class Enumerator (unohelper.Base, XActionListener, XTopWindowListener, XJobExecutor):

    def __init__ (self, ctx):
        self.ctx = ctx
        self.xSvMgr = self.ctx.ServiceManager
        self.xDesktop = self.xSvMgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.xDocument = self.xDesktop.getCurrentComponent()
        self.xContainer = None
        self.xDialog = None
        self.oSpellChecker = None
        self.oTokenizer = None
        self.dWord = {}

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
        ui.selectLang(sLang)

        # dialog
        self.xDialog = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialogModel', self.ctx)
        self.xDialog.Width = 240
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

        xFDSubTitle = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        xFDSubTitle.Height = 8
        xFDSubTitle.Weight = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
        xFDSubTitle.Name = "Verdana"

        # widget
        nX = 10
        nY1 = 5
        nY2 = nY1 + 225

        nWidth = self.xDialog.Width - 20
        nHeight = 10

        # List
        self._addWidget("list_section", 'FixedLine', nX, nY1, nWidth, nHeight, Label = ui.get("list_section"), FontDescriptor = xFDTitle)
        self._addWidget('count_button', 'Button', nX, nY1+12, 70, 11, Label = ui.get('count_button'))
        self._addWidget('count2_button', 'Button', nX+75, nY1+12, 70, 11, Label = ui.get('count2_button'))
        self._addWidget('unknown_button', 'Button', nX+150, nY1+12, 70, 11, Label = ui.get('unknown_button'))
        self.xGridModel = self._addGrid("list_grid", nX, nY1+25, nWidth, 181, \
            [ {"Title": ui.get("words"), "ColumnWidth": 175}, {"Title": "Occurrences", "ColumnWidth": 45} ], \
            SelectionModel = uno.Enum("com.sun.star.view.SelectionType", "MULTI") \
        )
        self._addWidget('num_of_entries', 'FixedText', nX, nY1+210, 30, nHeight, Label = ui.get('num_of_entries'), Align = 2)
        self.xNumWord = self._addWidget('num_of_entries_res', 'FixedText', nX+35, nY1+210, 25, nHeight, Label = "—")
        self._addWidget('tot_of_entries', 'FixedText', nX+60, nY1+210, 30, nHeight, Label = ui.get('tot_of_entries'), Align = 2)
        self.xTotWord = self._addWidget('tot_of_entries_res', 'FixedText', nX+95, nY1+210, 30, nHeight, Label = "—")
        self.xSearch = self._addWidget('search_button', 'Button', nX+145, nY1+210, 30, nHeight, Label = ">>>", HelpText=ui.get('goto'), Enabled = False)
        self.xExport = self._addWidget('export_button', 'Button', nX+180, nY1+210, 40, nHeight, Label = ui.get('export'), Enabled = False)

        # Tag
        # Note: the only way to group RadioButtons is to create them successively
        self._addWidget("charstyle_section", 'FixedLine', nX, nY2, 200, nHeight, Label = ui.get("charstyle_section"), FontDescriptor = xFDTitle)
        self.xAccent = self._addWidget('emphasis', 'RadioButton', nX, nY2+12, 55, nHeight, Label = ui.get('emphasis'))
        self.xStrongAccent = self._addWidget('strong_emphasis', 'RadioButton', nX+60, nY2+12, 70, nHeight, Label = ui.get('strong_emphasis'))
        self.xNoAccent = self._addWidget('nostyle', 'RadioButton', nX+140, nY2+12, 45, nHeight, Label = ui.get('nostyle'))

        self.xTag = self._addWidget('tag_button', 'Button', self.xDialog.Width-40, nY2+10, 30, 11, Label = ui.get('tag_button'), FontDescriptor = xFDTitle, TextColor = 0x55BB55, Enabled=False)

        # Progress bar
        self.xProgressBar = self._addWidget('progress_bar', 'ProgressBar', nX, self.xDialog.Height-25, 160, 14)
        self.xProgressBar.ProgressValueMin = 0
        self.xProgressBar.ProgressValueMax = 1 # to calculate later

        # Close
        self._addWidget('close_button', 'Button', self.xDialog.Width-60, self.xDialog.Height-25, 50, 14, Label = ui.get('close_button'), FontDescriptor = xFDTitle, TextColor = 0xBB5555)

        # container
        self.xContainer = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.UnoControlDialog', self.ctx)
        self.xContainer.setModel(self.xDialog)
        self.xGridControl = self.xContainer.getControl('list_grid')
        self.xContainer.getControl('count_button').addActionListener(self)
        self.xContainer.getControl('count_button').setActionCommand('Count')
        self.xContainer.getControl('count2_button').addActionListener(self)
        self.xContainer.getControl('count2_button').setActionCommand('CountByLemma')
        self.xContainer.getControl('unknown_button').addActionListener(self)
        self.xContainer.getControl('unknown_button').setActionCommand('UnknownWords')
        self.xContainer.getControl('search_button').addActionListener(self)
        self.xContainer.getControl('search_button').setActionCommand('Search')
        self.xContainer.getControl('export_button').addActionListener(self)
        self.xContainer.getControl('export_button').setActionCommand('Export')
        self.xContainer.getControl('tag_button').addActionListener(self)
        self.xContainer.getControl('tag_button').setActionCommand('Tag')
        self.xContainer.getControl('close_button').addActionListener(self)
        self.xContainer.getControl('close_button').setActionCommand('Close')
        self.xContainer.addTopWindowListener(self) # listener with XTopWindowListener methods
        self.xContainer.setVisible(True)    # True for non modal dialog
        xToolkit = self.xSvMgr.createInstanceWithContext('com.sun.star.awt.ExtToolkit', self.ctx)
        self.xContainer.createPeer(xToolkit, None)
        #self.xContainer.execute()          # Don’t excute for non modal dialog

    # XActionListener
    def actionPerformed (self, xActionEvent):
        try:
            if xActionEvent.ActionCommand == "Count":
                self.count(ui.get("words"))
                self.xTag.Enabled = True
                self.xSearch.Enabled = True
                self.xExport.Enabled = True
            elif xActionEvent.ActionCommand == "CountByLemma":
                self.count(ui.get("lemmas"), bByLemma=True)
                self.xTag.Enabled = False
                self.xSearch.Enabled = False
                self.xExport.Enabled = True
            elif xActionEvent.ActionCommand == "UnknownWords":
                self.count(ui.get("unknown_words"), bOnlyUnknownWords=True)
                self.xTag.Enabled = True
                self.xSearch.Enabled = True
                self.xExport.Enabled = True
            elif xActionEvent.ActionCommand == "Search":
                if not self.xGridControl.hasSelectedRows():
                    return
                lRow = self.xGridControl.getSelectedRows()
                aWord = set([ self.xGridModel.GridDataModel.getCellData(0, n)  for n in lRow ])
                self.gotoWord(aWord)
            elif xActionEvent.ActionCommand == "Export":
                self.export()
            elif xActionEvent.ActionCommand == "Tag":
                if not self.xGridControl.hasSelectedRows():
                    return
                lRow = self.xGridControl.getSelectedRows()
                aWord = set([ self.xGridModel.GridDataModel.getCellData(0, n)  for n in lRow ])
                sAction = ""
                if self.xAccent.State:
                    sAction = "emphasis"
                elif self.xStrongAccent.State:
                    sAction = "strong_emphasis"
                elif self.xNoAccent.State:
                    sAction = "nostyle"
                self.tagText(aWord, sAction)
            elif xActionEvent.ActionCommand == "Close":
                self.xContainer.dispose()           # Non modal dialog
                #self.xContainer.endExecute()       # Modal dialog
        except:
            traceback.print_exc()

    # XTopWindowListener (useful for non modal dialog only)
    def windowOpened (self, xEvent):
        return

    def windowClosing (self, xEvent):
        self.xContainer.dispose()           # Non modal dialog

    def windowClosed (self, xEvent):
        return

    def windowMinimized (self, xEvent):
        return

    def windowNormalized (self, xEvent):
        return

    def windowActivated (self, xEvent):
        return

    def windowDeactivated (self, xEvent):
        return

    # XJobExecutor
    def trigger (self, args):
        try:
            xDialog = Enumerator(self.ctx)
            xDialog.run()
        except:
            traceback.print_exc()

    # Code
    def _setTitleOfFirstColumn (self, sTitle):
        xColumnModel = self.xGridModel.ColumnModel
        xColumn = xColumnModel.getColumn(0)
        xColumn.Title = sTitle

    def _getParagraphsFromText (self):
        "generator: returns full document text paragraph by paragraph"
        xCursor = self.xDocument.Text.createTextCursor()
        xCursor.gotoStart(False)
        xCursor.gotoEndOfParagraph(True)
        yield xCursor.getString()
        while xCursor.gotoNextParagraph(False):
            xCursor.gotoEndOfParagraph(True)
            yield xCursor.getString()

    def _countParagraph (self):
        i = 1
        xCursor = self.xDocument.Text.createTextCursor()
        xCursor.gotoStart(False)
        while xCursor.gotoNextParagraph(False):
            i += 1
        return i

    @_waitPointer
    def count (self, sTitle, bByLemma=False, bOnlyUnknownWords=False):
        if not self.oSpellChecker:
            self.oSpellChecker = sc.SpellChecker("fr")
        self._setTitleOfFirstColumn(sTitle)
        self.xProgressBar.ProgressValueMax = self._countParagraph() * 2
        self.xProgressBar.ProgressValue = 0
        xGridDataModel = self.xGridModel.GridDataModel
        xGridDataModel.removeAllRows()
        self.dWord.clear()
        for sParagraph in self._getParagraphsFromText():
            self.dWord = self.oSpellChecker.countWordsOccurrences(sParagraph, bByLemma, bOnlyUnknownWords, self.dWord)
            self.xProgressBar.ProgressValue += 1
        self.xProgressBar.ProgressValueMax += len(self.dWord)
        i = 0
        nTotOccur = 0
        for sWord, nOccur in sorted(self.dWord.items(), key=lambda t: t[1], reverse=True):
            xGridDataModel.addRow(i, (sWord, nOccur))
            self.xProgressBar.ProgressValue += 1
            i += 1
            nTotOccur += nOccur
            sWord = sWord.lower()
            if sWord.endswith(("-le-moi", "-le-toi", "-le-nous", "-le-vous", "le-lui", "-le-leur", \
                               "-la-moi", "-la-toi", "-la-nous", "-la-vous", "la-lui", "-la-leur", \
                               "-les-moi", "-les-toi", "-les-nous", "-les-vous", "les-lui", "-les-leur", \
                               "-m’en", "-t’en", "-lui-en", "-nous-en", "vous-en", "-leur-en")):
                nTotOccur += nOccur + nOccur
            elif sWord.endswith(("-je", "-tu", "-il", "-elle", "-on", "-nous", "-vous", "-ils", "-elles", "-iel", "-iels", "-le", \
                                 "-la", "-les", "-moi", "-toi", "-leur", "-en", "-y")):
                nTotOccur += nOccur
        self.xProgressBar.ProgressValue = self.xProgressBar.ProgressValueMax
        self.xNumWord.Label = str(i)
        self.xTotWord.Label = nTotOccur

    def export (self):
        if not self.dWord:
            return
        sText = ""
        for sWord, nOccur in sorted(self.dWord.items(), key=lambda t: t[1], reverse=True):
            sText += sWord + "\t" + str(nOccur) + "\n"
        try:
            xFilePicker = self.xSvMgr.createInstanceWithContext('com.sun.star.ui.dialogs.FilePicker', self.ctx)  # other possibility: com.sun.star.ui.dialogs.SystemFilePicker
            xFilePicker.initialize([uno.getConstantByName("com.sun.star.ui.dialogs.TemplateDescription.FILESAVE_SIMPLE")]) # seems useless
            xFilePicker.appendFilter("Supported files", "*.txt")
            xFilePicker.setDefaultName("word_count.txt") # doesn’t work on Windows
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
            MessageBox(self.xDocument, sMessage, ui.get('export_title'), ERRORBOX)

    @_waitPointer
    def tagText (self, aWord, sAction=""):
        if not sAction:
            return
        self.xProgressBar.ProgressValueMax = self._countParagraph()
        self.xProgressBar.ProgressValue = 0
        if not self.oTokenizer:
            self.oTokenizer = self.oSpellChecker.getTokenizer()
        xCursor = self.xDocument.Text.createTextCursor()
        xCursor.gotoStart(False)
        self._tagParagraph(xCursor, aWord, sAction)
        while xCursor.gotoNextParagraph(False):
            self._tagParagraph(xCursor, aWord, sAction)
        self.xProgressBar.ProgressValue = self.xProgressBar.ProgressValueMax

    def _tagParagraph (self, xCursor, aWord, sAction):
        xCursor.gotoEndOfParagraph(True)
        sParagraph = xCursor.getString()
        xCursor.gotoStartOfParagraph(False)
        nPos = 0
        for dToken in self.oTokenizer.genTokens(sParagraph):
            if dToken["sValue"] in aWord:
                xCursor.goRight(dToken["nStart"]-nPos, False) # start of token
                nPos = dToken["nEnd"]
                xCursor.goRight(nPos-dToken["nStart"], True) # end of token
                # if sAction == "underline":
                #     xCursor.CharBackColor = hexToRBG("AA0000")
                # elif sAction == "nounderline":
                #     xCursor.CharBackColor = hexToRBG("FFFFFF")
                if sAction == "emphasis":
                    xCursor.CharStyleName = "Emphasis"
                elif sAction == "strong_emphasis":
                    xCursor.CharStyleName = "Strong Emphasis"
                elif sAction == "nostyle":
                    #xCursor.CharStyleName = "Default Style"     # doesn’t work
                    xCursor.setPropertyToDefault("CharStyleName")
        self.xProgressBar.ProgressValue += 1

    @_waitPointer
    def gotoWord (self, aWord):
        try:
            if not aWord:
                return
            if not self.oTokenizer:
                self.oTokenizer = self.oSpellChecker.getTokenizer()
            xViewCursor = self.xDocument.CurrentController.ViewCursor
            if not xViewCursor.isCollapsed():
                xViewCursor.collapseToEnd()
            xRange = xViewCursor.getStart()
            xCursor = self.xDocument.Text.createTextCursor()
            xCursor.gotoRange(xRange, False)
            #xCursor.gotoEndOfWord(False)
            xCursor.gotoEndOfParagraph(True)
            sParagraph = xCursor.getString()
            xCursor.gotoRange(xRange, False)
            tPos = self._searchWordsInText(aWord, sParagraph)
            if not tPos:
                while xCursor.gotoNextParagraph(False):
                    xCursor.gotoEndOfParagraph(True)
                    sParagraph = xCursor.getString()
                    xCursor.gotoStartOfParagraph(False)
                    tPos = self._searchWordsInText(aWord, sParagraph)
                    if tPos:
                        break
            if not tPos:
                xCursor.gotoStart(False)
                xCursor.gotoEndOfParagraph(True)
                sParagraph = xCursor.getString()
                xCursor.gotoStartOfParagraph(True)
                tPos = self._searchWordsInText(aWord, sParagraph)
                while xCursor.gotoNextParagraph(False):
                    xCursor.gotoEndOfParagraph(True)
                    sParagraph = xCursor.getString()
                    xCursor.gotoStartOfParagraph(False)
                    tPos = self._searchWordsInText(aWord, sParagraph)
                    if tPos:
                        break
            if tPos:
                xCursor.goRight(tPos[0], False)
                xRange = xCursor.getStart()
                xViewCursor.gotoRange(xRange, False)
                xViewCursor.goRight(tPos[1], True)
        except:
            traceback.print_exc()

    def _searchWordsInText (self, aWord, sText):
        for dToken in self.oTokenizer.genTokens(sText):
            if dToken["sValue"] in aWord:
                return (dToken["nStart"], dToken["nEnd"]-dToken["nStart"])
        return None

#g_ImplementationHelper = unohelper.ImplementationHelper()
#g_ImplementationHelper.addImplementation(Enumerator, 'net.grammalecte.enumerator', ('com.sun.star.task.Job',))
