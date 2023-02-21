import sys, os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel
)

basedir = os.path.dirname(__file__)

from hackpad_ui import Ui_MainWindow


class FileNotSavedDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet(self.parent.styleSheet())
        self.setupUi()

    def setupUi(self):
        self.setFixedSize(200, 100)
        self.setWindowTitle("File not saved")
        self.setStyleSheet("background-color: #151a1e;")

        label = QLabel(
            "Do you want to save the changes you made to the document?")
        label.setWordWrap(True)
        label.setStyleSheet("color: #d3dae3;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Discard |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.setStyleSheet("border: 3px solid #4fa08b;")

        layout.addWidget(label)
        layout.addWidget(self.buttonBox)

    def setSaveEvent(self, event):
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Save
        ).clicked.connect(event)

    def setDiscardEvent(self, event):
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Discard
        ).clicked.connect(event)

    def setCancelEvent(self, event):
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Cancel
        ).clicked.connect(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.filePath = None
        self.isSaved = True

        self.dialog = FileNotSavedDialog(self)

        self.setShortcuts()

        self.ui.textEdit.textChanged.connect(self._setUnsaved)

        self.ui.textInput.returnPressed.connect(self.addNote)
        self.ui.actionNew.triggered.connect(self._newFile)
        self.ui.actionOpen.triggered.connect(self._openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionExit.triggered.connect(self.close)

    def setShortcuts(self):
        self.ui.actionNew.setShortcut("Ctrl+N")
        self.ui.actionOpen.setShortcut("Ctrl+O")
        self.ui.actionSave.setShortcut("Ctrl+S")
        self.ui.actionExit.setShortcut("Ctrl+Q")

    def _newFile(self):
        if not self.isSaved:
            self._showFileNotSavedDialog()
        else:
            self._dicardChanges()

    def _getFilenameFromPath(self, filePath):
        return filePath.split("/")[-1]

    def _setSaved(self):
        self.isSaved = True
        self._setWindowTitle()

    def _setUnsaved(self):
        if self.ui.textEdit.toPlainText() != "":
            self.isSaved = False
        self._setWindowTitle()

    def _setWindowTitle(self):
        title = "Hackpad"
        if self.filePath is not None:
            title = self._getFilenameFromPath(self.filePath)
            if not self.isSaved:
                title = f"*{title} - Unsaved"
        else:
            if not self.isSaved:
                title = "*Hackpad - Unsaved"
        self.setWindowTitle(title)

    def _showFileNotSavedDialog(self):
        self.dialog.setSaveEvent(self.saveFile)
        self.dialog.setDiscardEvent(self._dicardChanges)
        self.dialog.setCancelEvent(self.dialog.close)
        self.dialog.exec()

    def _dicardChanges(self):
        self.ui.textEdit.clear()
        self.dialog.close()
        self._setSaved()

    def closeEvent(self, a0: QCloseEvent):
        if not self.isSaved:
            a0.ignore()
            self._showFileNotSavedDialog()
        else:
            a0.accept()

    def _openFile(self):
        if not self.isSaved:
            self._showFileNotSavedDialog()
        else:
            fileName, _ = QFileDialog.getOpenFileName(
                self, "Open File", "", "Text Files (*.txt)")
            if fileName:
                self.filePath = fileName
                with open(fileName, "r") as file:
                    self.ui.textEdit.setPlainText(file.read())
                self._setWindowTitle()

    def saveFile(self):
        if self.filePath is None:
            self._openSaveDialog()
        else:
            with open(self.filePath, "w") as file:
                file.write(self.ui.textEdit.toPlainText())
            self._setSaved()

    def _openSaveDialog(self):
        if self.dialog.isVisible():
            self.dialog.close()
        fileName, _ = QFileDialog.getSaveFileName(
            self, 
            "Save File", 
            os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),
            "Text Files (*.txt)"
        )
        if fileName:
            self.filePath = fileName
            self.saveFile()

    def addNote(self):
        if self.ui.textInput.text() != "":
            self.ui.textEdit.appendPlainText(self.ui.textInput.text())
            self.ui.textInput.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, "icon", "hackpad_icon.ico")))
    window = MainWindow()
    window.show()
    app.exec()
