from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QApplication
from PyQt5.QtGui import QStandardItem, QPalette, QFontMetrics
from PyQt5.QtCore import Qt, QEvent

class CheckableComboBox(QComboBox):
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(40)  # Increased height for better visibility
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setEditable(True)
        self.lineEdit().setReadOnly(False)

        palette = QApplication.instance().palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(CheckableComboBox.Delegate())

        self.model().dataChanged.connect(self.updateText)

        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        self.view().viewport().installEventFilter(self)

        self.full_text = ""  # To store the complete text

    def resizeEvent(self, event):
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if obj == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)
        self.updateText()

    def timerEvent(self, event):
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = [self.model().item(i).text() for i in range(self.model().rowCount()) if self.model().item(i).checkState() == Qt.Checked]
        self.full_text = ", ".join(texts)

        # Compute elided text for display in lineEdit
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(self.full_text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def fullText(self):
        return self.full_text

    def addItem(self, text, data=None):
        item = QStandardItem(text)
        item.setData(data if data is not None else text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            data = datalist[i] if datalist and i < len(datalist) else None
            self.addItem(text, data)

    def currentData(self):
        return [self.model().item(i).data() for i in range(self.model().rowCount()) if self.model().item(i).checkState() == Qt.Checked]