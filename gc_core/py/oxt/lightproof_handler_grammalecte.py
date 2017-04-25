import uno
import unohelper
import lightproof_opts_${implname} as lp_opt
from gc_engine_${implname} import pkg

from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XContainerWindowEventHandler


options = {}

def load (context):
    try:
        l = LightproofOptionsEventHandler(context)
        for sLang in lp_opt.lopts:
            l.load(sLang)
    except:
        pass


class LightproofOptionsEventHandler (unohelper.Base, XServiceInfo, XContainerWindowEventHandler):
    def __init__ (self, ctx):
        p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        p.Name = "nodepath"
        p.Value = "/org.openoffice.Lightproof_%s/Leaves"%pkg
        self.xConfig = ctx.ServiceManager.createInstance('com.sun.star.configuration.ConfigurationProvider')
        self.node = self.xConfig.createInstanceWithArguments('com.sun.star.configuration.ConfigurationUpdateAccess', (p, ))
        self.service = "org.openoffice.comp.pyuno.LightproofOptionsEventHandler." + pkg
        self.ImplementationName = self.service
        self.services = (self.service, )

    # XContainerWindowEventHandler
    def callHandlerMethod (self, aWindow, aEventObject, sMethod):
        if sMethod == "external_event":
            return self._handleExternalEvent(aWindow, aEventObject)

    def getSupportedMethodNames (self):
        return ("external_event", )

    def _handleExternalEvent (self, aWindow, aEventObject):
        #aEventObject = str(aEventObject)  # unnecessary in Python
        if aEventObject == "ok":
            self._saveData(aWindow)
        elif aEventObject == "back" or aEventObject == "initialize":
            self._loadData(aWindow)
        return True

    def load (self, sWindowName):
        child = self.getChild(sWindowName)
        for i in lp_opt.lopts[sWindowName]:
            sValue = child.getPropertyValue(i)
            if sValue == '':
                if i in lp_opt.lopts_default[sWindowName]:
                    sValue = 1
                else:
                    sValue = 0
            options[i] = bool(int(sValue))

    def _loadData (self, aWindow):
        sWindowName = self.getWindowName(aWindow)
        if (sWindowName == None):
            return
        child = self.getChild(sWindowName)
        for i in lp_opt.lopts[sWindowName]:
            sValue = child.getPropertyValue(i)
            if sValue == '':
                if i in lp_opt.lopts_default[sWindowName]:
                    sValue = 1
                else:
                    sValue = 0
            xControl = aWindow.getControl(i)
            xControl.State = sValue
            options[i] = bool(int(sValue))

    def _saveData (self, aWindow):
        sWindowName = self.getWindowName(aWindow)
        if (sWindowName == None):
            return
        child = self.getChild(sWindowName)
        for i in lp_opt.lopts[sWindowName]:
            xControl = aWindow.getControl(i)
            sValue = xControl.State
            child.setPropertyValue(i, str(sValue))
            options[i] = bool(int(sValue))
        self.commitChanges()

    def getWindowName (self, aWindow):
        sName = aWindow.getModel().Name
        if sName in lp_opt.lopts:
            return sName
        return None

    # XServiceInfo
    def getImplementationName (self):
        return self.ImplementationName

    def supportsService (self, ServiceName):
        return (ServiceName in self.services)

    def getSupportedServiceNames (self):
        return self.services

    def getChild (self, name):
        return self.node.getByName(name)

    def commitChanges (self):
        self.node.commitChanges()
        return True
