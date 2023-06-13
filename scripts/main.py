def DeleteSysModule(szModuleName):
    import sys
    if szModuleName in sys.modules:
        del sys.modules[szModuleName]
        # logger.info("del module: %s" % szModuleName)
        listUpperModule = szModuleName.split(".")[0:-1]
        while listUpperModule:  # 删除名空间namespace
            szUpperModule = ".".join(listUpperModule)
            if szUpperModule in sys.modules:
                del sys.modules[szUpperModule]

            listUpperModule = listUpperModule[0:-1]

def CleanLogicModule():
    listDelFiles = ["fireflymountain", ]
    listReloadKeys = []
    import sys
    listNeedDel = []
    for szModuleName, ModuleInfoData in sys.modules.items():
        bFound = False
        if szModuleName in listReloadKeys:
            continue
        for szFile in listDelFiles:
            if hasattr(ModuleInfoData, "__file__") and ModuleInfoData.__file__:
                szTmpFile = ModuleInfoData.__file__.replace("\\", "/")
                if szTmpFile.find(szFile) >= 0:
                    bFound = True
        if bFound:
            listNeedDel.append(szModuleName)

    for szModuleName in listNeedDel:
        DeleteSysModule(szModuleName)

    from importlib import reload
    for szModuleName in listReloadKeys:
        reload(sys.modules[szModuleName])

CleanLogicModule()

# ------------------------------------------------------------------------------------------

import sys

import fireflymountain.ui as fireflymountainUI

from modules import script_callbacks

script_callbacks.on_ui_tabs(fireflymountainUI.on_ui_tabs)


