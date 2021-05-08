import config
from qtpy.QtWidgets import QInputDialog, QLineEdit
from qtpy.QtWebEngineWidgets import QWebEnginePage

def findText(found):
    if not found:
        config.mainWindow.displayMessage("Not found!")

text, ok = QInputDialog.getText(config.mainWindow, "QInputDialog.getText()",
        "Find in Study Window:", QLineEdit.Normal,
        "")
if ok and text != '':
    config.mainWindow.studyPage.findText(text, QWebEnginePage.FindBackward, findText)
