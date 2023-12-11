# -*- coding: utf-8 -*-

# @File        :   threadutil_blocking.py
# @Description :   A more powerful, synchronous implementation of run_in_main_thread(...)

# here put the import lib
"""
A more powerful, synchronous implementation of run_in_main_thread(...).
It allows you to receive results from the function invocation:

    @run_in_main_thread
    def return_2():
        return 2
    
    # Runs the above function in the main thread and prints '2':
    print(return_2())
"""

from functools import wraps
from PyQt6.QtCore import pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import QApplication
from threading import Event, get_ident

def run_in_thread(thread_fn):
    """ 将多线程流程: 从线程绑定到获取结果串在一起 """
    def decorator(f):
        @wraps(f)
        def result(*args, **kwargs):
            thread = thread_fn()
            return Executor.instance().run_in_thread(thread, f, args, kwargs)
        return result
    return decorator

def _main_thread():
    """ 获取进程的主线程 """
    app = QApplication.instance()
    if app:
        return app.thread()

    # We reach here in tests that don't (want to) create a QApplication.
    if int(QThread.currentThreadId()) == get_ident():
        return QThread.currentThread()

    raise RuntimeError('Could not determine main thread')

run_in_main_thread = run_in_thread(_main_thread)

def is_in_main_thread():
    return QThread.currentThread() == _main_thread()

class Executor:
    """ 进程 """
    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(QApplication.instance())
        return cls._INSTANCE

    def __init__(self, app):
        self._pending_tasks = []  # 线程
        self._app_is_about_to_quit = False
        app.aboutToQuit.connect(self._about_to_quit)  # 中断

    def _about_to_quit(self):
        """ 中断进程 """
        self._app_is_about_to_quit = True
        for task in self._pending_tasks:
            task.set_exception(SystemExit())
            task.has_run.set()

    def run_in_thread(self, thread, f, args, kwargs):
        """ 执行线程 """
        if QThread.currentThread() == thread:
            return f(*args, **kwargs)
        elif self._app_is_about_to_quit:
            # In this case, the target thread's event loop most likely is not
            # running any more. This would mean that our task (which is
            # submitted to the event loop via signals/slots) is never run.
            raise SystemExit()

        task = Task(f, args, kwargs)  # 初始化新线程
        self._pending_tasks.append(task)

        try:
            receiver = Receiver(task)  # 设置回调函数
            receiver.moveToThread(thread)
            sender = Sender()  # 自定义信号
            sender.signal.connect(receiver.slot)  # 连接信号与槽函数
            sender.signal.emit()
            task.has_run.wait()

            return task.result
        finally:
            self._pending_tasks.remove(task)

class Task:
    def __init__(self, fn, args, kwargs):
        """
        fn     : 函数名
        args   : 参数
        kwargs : 参数
        """
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.has_run = Event()
        self._result = self._exception = None

    def __call__(self):
        """ 调用函数 """
        try:
            self._result = self._fn(*self._args, **self._kwargs)  # 回调结果
        except Exception as e:
            self._exception = e
        finally:
            self.has_run.set()

    def set_exception(self, exception):
        """ 异常 """
        self._exception = exception

    @property
    def result(self):
        """ 获取结果 """
        if not self.has_run.is_set():
            raise ValueError("Hasn't run.")

        if self._exception:
            raise self._exception

        return self._result

class Sender(QObject):
    signal = pyqtSignal()  # 自定义信号

class Receiver(QObject):
    """ 设置并执行回调函数 """
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.callback = callback

    def slot(self):
        """ 槽函数 """
        self.callback()
