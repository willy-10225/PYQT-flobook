import sys
import os
import time
from datetime import datetime
from PyQt5.QtCore import QDate, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import uic
from api import AddProjectInit, AddProject,ProjectListInit
from PYQTTool_EditableComboBox import EditableComboBox
from cpumonitor import CpuMonitorThread,userid

def checkcasetime():
    global userid
    # 初始设定为所有项目都已过期
    # 假设你已经有 userid 的获取逻辑
    listprojects = ProjectListInit(userid)  # 获取项目列表
    if listprojects:  # 如果项目列表不为空
        for dict1 in listprojects:
            # 将字符串 'close_time' 转换为 datetime 对象，并比较时间
            if datetime.now() < datetime.strptime(dict1['close_time'], '%Y/%m/%d %H:%M:%S'):
                return True  # 在项目時間內，设为 True
    return False

def replace_CheckableComboBox(combo_box, items=None,type="Check", font_size=20):
    # 获取原来 combo_box 所在的布局
    layout = combo_box.parentWidget().layout()
    # 确定 combo_box 在 QGridLayout 中的行和列位置
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if widget == combo_box:
            row, col, _, _ = layout.getItemPosition(i)
            break
    checkable_combo_box = EditableComboBox(combo_box.parentWidget())
    # 设置字体大小
    font = checkable_combo_box.font()
    font.setPointSize(font_size)
    checkable_combo_box.setFont(font)
    # 将新的 CheckableComboBox 放在相同的位置
    layout.addWidget(checkable_combo_box, row, col)
    # 删除旧的 combo_box
    combo_box.deleteLater()
    # 如果提供了项目列表，则添加到 CheckableComboBox
    if items:
        checkable_combo_box.addItems(items)
    # 返回新的 CheckableComboBox 以便继续使用
    return checkable_combo_box


            
class Ui_Form(QMainWindow):
    def __init__(self):
        global userid
        super().__init__()
        self.payload={'projectType': "",
            'customerName': "",
            'product': "",
            'domain': None,
            'industryType': None,
            'projectName': "",
            'projectDescription': "",
            'checkPoint': "",
            'startTime': "",  # 确保日期格式为 "YYYY/MM/DD HH:MM:SS"
            'closeTime': "",  # 确保日期格式为 "YYYY/MM/DD HH:MM:SS"
            'projectCreater': "",
            'executor': "",
            'manager': "",
            'teammates': None,
            'software': None,
            'fileNames': "",
            'fileDescriptions': "",
            'security': "無",
            'status': "PROCESSING"  }
        if getattr(sys, 'frozen', False):
            # 如果脚本被打包成可执行文件，则获取临时目录路径
            base_path = sys._MEIPASS
        else:
            # 否则获取脚本所在的目录
            base_path = os.path.dirname(os.path.abspath(__file__))

        # 指定 UI 文件路径
        ui_path = os.path.join(base_path, 'ProjectCreate2.ui')
        if not os.path.exists(ui_path):
            self.showMessageBox('(error)ui路徑錯誤',f"UI file '{ui_path}' not found.")
        else:
            uic.loadUi(ui_path, self)
            
        project=AddProjectInit()
        
        if 'error' in project:
            self.showMessageBox('(error)Flobook網站地址錯誤','Please check the environment variables and FloBook operation status\n請檢察環境變數和FloBook運行情況')
            sys.exit()
        else:
            # 将新的 CheckableComboBox 命名为 comboBox_Type
            self.comboBox_Type = replace_CheckableComboBox(self.comboBox_Type,project['keyword']['type'])
            self.comboBox_Executor.addItems(project['member'])
            self.comboBox_Executor.setCurrentText(project['member'][userid-1])
            now = datetime.now()
            self.dateEdit_startTime.setDate(QDate(now.year, now.month, now.day))
            self.pushButton_Add.clicked.connect(self.savetoflobook)
            self.pushButton_close.clicked.connect(self.exitclose)
        
       # 初始化 CPU 监控线程
        self.monitor_thread = CpuMonitorThread()
        self.monitor_thread.cpu_usage_signal.connect(self.on_cpu_usage_detected)
        self.monitor_thread.start()

        # 隐藏窗口
        self.hide()

    def savetoflobook(self):
        start_date = self.dateEdit_startTime.date()
        self.payload['startTime']=start_date.toString("yyyy/MM/dd 00:00:00")
        days_to_add = self.spinBox_day.value()
        added_days = 0
        while added_days < days_to_add:
            start_date = start_date.addDays(1)
            if start_date.dayOfWeek() not in [Qt.Saturday, Qt.Sunday]:
                added_days += 1
        self.payload['closeTime']=start_date.toString("yyyy/MM/dd 23:59:59")
        self.payload['projectType']=self.comboBox_Type.getLineEditText()

        self.payload['security']=self.comboBox_Security.currentText()
        self.payload['executor']=self.comboBox_Executor.currentText()
        
        self.payload['customerName']=self.lineEdit_Customer.text()
        self.payload['projectName']=self.lineEdit_Subject.text()
        
        response = AddProject(self.payload)
        if 'error' in response:
            self.showMessageBox('(error)Flobook網站資料錯誤','資料輸入格式不對')
            sys.exit()
        self.showMessageBox("輸入成功","想觀看填寫請到FloBook上看")

    def showMessageBox(self, Title: str, Text: str):
        # 創建一個警告框
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(Text)
        msgBox.setWindowTitle(Title)
        msgBox.setStandardButtons(QMessageBox.Ok)

        # 顯示警告框並捕獲返回值
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print("OK clicked")

    def exitclose(self):
        self.hide()# 隱藏窗口
        self.monitor_thread.start_monitoring()

    def openUI(self):
        self.show()  # 显示窗口
        self.showMaximized()  # 最大化窗口
        self.monitor_thread.stop_monitoring()
        
    def on_cpu_usage_detected(self, cpu_usage):
        if cpu_usage > 25 and self.isHidden():
            if checkcasetime():
                self.monitor_thread.settime(300)
            else:
                self.monitor_thread.settime(5)
                self.openUI()
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Ui_Form()
    sys.exit(app.exec_())