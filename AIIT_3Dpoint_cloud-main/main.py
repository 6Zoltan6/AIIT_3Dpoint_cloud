# main.py
import os
import sys

import PySide2
#import qdarkstyle
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon
from mainWindow import MainWindow


if __name__ == "__main__":
    dirname = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.setWindowIcon(QIcon('1.jpg'))
    mainwindow.show()
    sys.exit(app.exec_())
