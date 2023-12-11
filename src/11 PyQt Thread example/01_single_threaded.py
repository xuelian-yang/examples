# -*- coding: utf-8 -*-

# @File        :   01_single_threaded.py
# @Description :   单线程

"""
References
----------
Python 总结 - session 及其用法
    https://www.jianshu.com/p/8c3f63c63c57
"""

# here put the import lib
import os.path as osp

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from requests import Session

# name = input("Please enter your name: ")  # 从控制台读取
name = osp.basename(__file__)

chat_url = "https://build-system.fman.io/chat"
server = Session()

# GUI:
app = QApplication([])

text_area = QPlainTextEdit()
text_area.setReadOnly(True)  # 只读
# text_area.setFocusPolicy(Qt.NoFocus)
message = QLineEdit()

layout = QVBoxLayout()
layout.addWidget(text_area)
layout.addWidget(message)

window = QWidget()
window.setLayout(layout)
window.show()

# Event handlers:
def display_new_messages():
    """ 解析 Session 内容并显示 """
    new_message = server.get(chat_url).text
    if new_message:
        # text_area.appendPlainText(new_message)  # 包含太多 HTML Tag
        text_area.appendHtml(new_message)

def send_message():
    """ 发送消息 """
    server.post(chat_url, {"name": name, "message": message.text()})
    message.clear()

# Signals:
message.returnPressed.connect(send_message)
timer = QTimer()
timer.timeout.connect(display_new_messages)  # 定时获取并显示
timer.start(5000)  # 5 秒发送一次，1 秒发送一次会报错 "429 Too many requests"
app.exec()
