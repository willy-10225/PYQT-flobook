import os
import psutil
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication,QMessageBox
from api import UiProjectmailvsid

def showMessageBox(title, message):
    # 创建一个消息框
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(message)
    msgBox.setWindowTitle(title)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()
    
username=os.getlogin()
 # 获取物理 CPU 核心数
logical_cpu_count = psutil.cpu_count(logical=False) 
userid =0
app = QApplication([])
try:
    # 获取 userid，并处理不存在的情况
    maildict = UiProjectmailvsid()  # 假设这个函数存在并返回一个字典
    if 'error' in maildict:
        showMessageBox("连接错误", "連接不到後端")
    else:
        userid = maildict['keyword'].get(f'{username}@cadmen.com')
        if userid is None:
            showMessageBox("用户未找到", f"User '{username}@cadmen.com' not found.")
        else:
            userid = int(userid)
except (ValueError, TypeError) as e:
    showMessageBox("获取用户ID错误", f"Error getting userid: {e}")

class CpuMonitorThread(QThread):
    cpu_usage_signal = pyqtSignal(float)  # 自定义信号，传递 CPU 使用率
    def __init__(self):
        super().__init__()
        self.monitoring = True
        self.interval = 5
        
    def run(self):
        global username, logical_cpu_count
        psutil.cpu_percent(interval=None)  # 初始化 CPU 使用百分比计算
        while self.monitoring:
            cpu_usage = 0
            for proc in psutil.process_iter(['pid', 'username', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    user = proc_info['username']
                    if user and username in user:
                        cpu_usage += proc_info['cpu_percent']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            total_cpu_usage = cpu_usage / logical_cpu_count
            print(f"当前用户的 CPU 使用率: {total_cpu_usage:.2f}%")
            self.cpu_usage_signal.emit(total_cpu_usage)  # 发送信号
            time.sleep(self.interval)  # 每 5分鐘检测一次 CPU 使用率
    def stop_monitoring(self):
        self.monitoring = False  # 停止监控
    def start_monitoring(self):
        self.monitoring = True   # 停止监控
        if not self.isRunning():  # 如果线程未运行，启动线程
            self.start()
    def settime(self,Second):
        self.interval=Second

