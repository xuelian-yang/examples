# -*- coding: utf-8 -*-

# @File        :   threadutil.py
# @Description :   多线程

# here put the import lib
from PyQt6.QtCore import QObject, pyqtSignal

class CurrentThread(QObject):

    _on_execute = pyqtSignal(object, tuple, dict)  # 自定义信号

    def __init__(self):
        super(QObject, self).__init__()
        self._on_execute.connect(self._execute_in_thread)  # 连接信号与槽函数

    def execute(self, f, args, kwargs):
        self._on_execute.emit(f, args, kwargs)  # 发送信号

    def _execute_in_thread(self, f, args, kwargs):
        f(*args, **kwargs)  # 执行函数

main_thread = CurrentThread()

def run_in_main_thread(f):
    def result(*args, **kwargs):
        main_thread.execute(f, args, kwargs)  # 执行
    return result