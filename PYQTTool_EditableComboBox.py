from PyQt5.QtWidgets import QComboBox, QLineEdit, QApplication
from PyQt5.QtGui import QPalette

class EditableComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to allow direct text input
        self.setEditable(True)
        self.lineEdit().setReadOnly(False)

        # Make the lineedit the same color as QPushButton
        palette = QApplication.instance().palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Ensure that the user input replaces the current value
        self.lineEdit().editingFinished.connect(self.handleEditingFinished)

    def handleEditingFinished(self):
        # When editing is finished, set the current text of the combo box
        self.setEditText(self.lineEdit().text())

    def addItem(self, text, data=None):
        # Add item to the combobox and set it as not editable
        super().addItem(text, data)

    def addItems(self, texts, datalist=None):
        # Add multiple items to the combobox
        for i, text in enumerate(texts):
            data = datalist[i] if datalist and i < len(datalist) else None
            self.addItem(text, data)

    def getLineEditText(self):
        # Get the text from the line edit
        return self.lineEdit().text()