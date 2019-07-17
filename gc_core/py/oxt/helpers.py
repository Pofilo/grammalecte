# Helpers for LibreOffice extension

import os
import traceback
import subprocess

import uno

from com.sun.star.beans import PropertyValue
from com.sun.star.uno import RuntimeException as _rtex


def startConsole ():
    "open console from APSO extension"
    try:
        xContext = uno.getComponentContext()
        xContext.ServiceManager.createInstance("apso.python.script.organizer.impl")
        # now we can import apso_utils library
        from apso_utils import console
        console()
    except:
        try:
            xContext = uno.getComponentContext()
            xSvMgr = xContext.getServiceManager()
            xPathSettings = xSvMgr.createInstanceWithContext("com.sun.star.util.PathSettings", xContext)
            spPyInstallion = uno.fileUrlToSystemPath(xPathSettings.Module)
            subprocess.Popen(spPyInstallion + os.sep + "python")  # Start Python interactive Shell
        except:
            traceback.print_exc()


def xray (xObject):
    "XRay - API explorer"
    try:
        xSvMgr = uno.getComponentContext().ServiceManager
        xMSPF = xSvMgr.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory", uno.getComponentContext())
        xScriptProvider = xMSPF.createScriptProvider("")
        xScript = xScriptProvider.getScript("vnd.sun.star.script:XrayTool._Main.Xray?language=Basic&location=application")
        xScript.invoke((xObject,), (), ())
        return
    except:
        raise _rtex("\nBasic library Xray is not installed", uno.getComponentContext())


def mri (xObject):
    "MRI - API Explorer"
    try:
        xContext = uno.getComponentContext()
        xMri = xContext.ServiceManager.createInstanceWithContext("mytools.Mri", xContext)
        xMri.inspect(xObject)
    except:
        raise _rtex("\nPython extension MRI is not installed", uno.getComponentContext())


def getConfigSetting (sNodeConfig, bUpdate=False):
    "get a configuration node"
    # example: xNode = getConfigSetting("/org.openoffice.Office.Common/Path/Current", False)
    xSvMgr = uno.getComponentContext().ServiceManager
    xConfigProvider = xSvMgr.createInstanceWithContext("com.sun.star.configuration.ConfigurationProvider", uno.getComponentContext())
    xPropertyValue = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    xPropertyValue.Name = "nodepath"
    xPropertyValue.Value = sNodeConfig
    if bUpdate:
        sService = "com.sun.star.configuration.ConfigurationUpdateAccess"
    else:
        sService = "com.sun.star.configuration.ConfigurationAccess"
    return xConfigProvider.createInstanceWithArguments(sService, (xPropertyValue,)) # return xNode


def printServices (o):
    for s in o.getAvailableServiceNames():
        print(' > '+s)


def getWindowSize ():
    "return main window size"
    xContext = uno.getComponentContext()
    xDesktop = xContext.getServiceManager().createInstanceWithContext('com.sun.star.frame.Desktop', xContext)
    xContainerWindow = xDesktop.getCurrentComponent().CurrentController.Frame.ContainerWindow
    xWindowSize = xContainerWindow.convertSizeToLogic(xContainerWindow.Size, uno.getConstantByName("com.sun.star.util.MeasureUnit.POINT"))
    #print(xContainerWindow.Size.Width, ">", xWindowSize.Width)
    #print(xContainerWindow.Size.Height, ">", xWindowSize.Height)
    xWindowSize.Width = xWindowSize.Width * 0.666
    xWindowSize.Height = xWindowSize.Height * 0.666
    return xWindowSize


def getAbsolutePathOf (sPath=""):
    xDefaultContext = uno.getComponentContext().ServiceManager.DefaultContext
    xPackageInfoProvider = xDefaultContext.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
    sFullPath = xPackageInfoProvider.getPackageLocation("French.linguistic.resources.from.Dicollecte.by.OlivierR")
    if sPath and not sPath.startswith("/"):
        sPath = "/" + sPath
    sFullPath = sFullPath[8:] + sPath
    return os.path.abspath(sFullPath)


def getProductNameAndVersion ():
    "returns tuple of software name and version"
    xSettings = getConfigSetting("org.openoffice.Setup/Product", False)
    sProdName = xSettings.getByName("ooName")
    sVersion = xSettings.getByName("ooSetupVersion")
    return (sProdName, sVersion)
