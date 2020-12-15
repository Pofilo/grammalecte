"""
Grammalecte AppLauncher
Service to avoid creating a service for each feature (which would slows LO start-up)
"""

# License: MPL 2

import traceback

import unohelper
import uno
from com.sun.star.task import XJobExecutor

import helpers


xDesktop = None
xLEDialog = None       # dialog for Lexicon Editor


class AppLauncher (unohelper.Base, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        # In this extension, French is default language.
        # It is assumed that those who need to use the French dictionaries understand French and may not understand English.
        xSettings = helpers.getConfigSetting("/org.openoffice.Setup/L10N", False)
        sLocale = xSettings.getByName("ooLocale")  # Note: look at ooSetupSystemLocale value?
        self.sLang = sLocale[0:2]

    # XJobExecutor
    def trigger (self, sCmd):
        global xLEDialog
        try:
            if sCmd == "About":
                import About
                xAboutDialog = About.AboutGrammalecte(self.ctx)
                xAboutDialog.run(self.sLang)
            elif sCmd.startswith("CJ"):
                import Conjugueur
                xConjDialog = Conjugueur.Conjugueur(self.ctx)
                if sCmd[2:3] == "/":
                    xConjDialog.run(sCmd[3:])
                else:
                    xConjDialog.run()
            elif sCmd == "TF":
                import TextFormatter
                xTFDialog = TextFormatter.TextFormatter(self.ctx)
                xTFDialog.run(self.sLang)
            elif sCmd == "DI":
                import DictOptions
                xDODialog = DictOptions.DictOptions(self.ctx)
                xDODialog.run(self.sLang)
            elif sCmd.startswith("LE"):
                import LexiconEditor
                if not xLEDialog or xLEDialog.bClosed:
                    xLEDialog = LexiconEditor.LexiconEditor(self.ctx)
                    if sCmd[2:3] == "/":
                        xLEDialog.run(self.sLang, sCmd[3:])
                    else:
                        xLEDialog.run(self.sLang)
                elif sCmd[2:3] == "/":
                    xLEDialog.newEntry(sCmd[3:])
            elif sCmd == "MA":
                import Author
                xAuthorDialog = Author.Author(self.ctx)
                xAuthorDialog.run(self.sLang)
            elif sCmd == "OP":
                import Options
                xGCDialog = Options.GC_Options(self.ctx)
                xGCDialog.run(self.sLang)
            elif sCmd == "EN":
                import Enumerator
                xEnumDialog = Enumerator.Enumerator(self.ctx)
                xEnumDialog.run(self.sLang)
            elif sCmd == "GO":
                import GraphicOptions
                xGODialog = GraphicOptions.GraphicOptions(self.ctx)
                xGODialog.run(self.sLang)
            elif sCmd.startswith("FA/"):
                findAll(sCmd[6:], (sCmd[3:4] == "y"), (sCmd[4:5] == "y"))
            elif sCmd == "Console":
                helpers.startConsole()
            # elif sCmd.startswith("URL/"):
            #     # Call from context menu to launch URL?
            #     # http://opengrok.libreoffice.org/xref/core/sw/source/ui/lingu/olmenu.cxx#785
            #     xSystemShellExecute = self.ctx.getServiceManager().createInstanceWithContext('com.sun.star.system.SystemShellExecute', self.ctx)
            #     xSystemShellExecute.execute(url, "", uno.getConstantByName("com.sun.star.system.SystemShellExecuteFlags.URIS_ONLY"))
            elif sCmd == "None":
                pass
            else:
                print("Unknown command: "+str(sCmd))
        except:
            traceback.print_exc()


def findAll (sText, bCaseSensitive, bFullWord):
    global xDesktop
    if not xDesktop:
        xCurCtx = uno.getComponentContext()
        xDesktop = xCurCtx.getServiceManager().createInstanceWithContext('com.sun.star.frame.Desktop', xCurCtx)
    if sText:
        xDoc = xDesktop.getCurrentComponent()
        xSearchDescr = xDoc.createSearchDescriptor()
        xSearchDescr.SearchString = sText
        xSearchDescr.SearchCaseSensitive = bCaseSensitive
        xSearchDescr.SearchWords = bFullWord
        xSearchDescr.SearchAll = True           # necessary ?
        xFound = xDoc.findAll(xSearchDescr)
        xDoc.CurrentController.select(xFound)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(AppLauncher, 'net.grammalecte.AppLauncher', ('com.sun.star.task.Job',))
