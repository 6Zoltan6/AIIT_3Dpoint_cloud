import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QFileDialog, QLabel, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QSplitter, QFrame, qApp


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')
        toolsMenu = menubar.addMenu('工具')
        denoiseMenu = menubar.addMenu('去噪')
        filterMenu = menubar.addMenu('滤波')
        registerMenu = menubar.addMenu('配准')
        segmentationMenu = menubar.addMenu('分割')

        loadCloudAction = QAction('加载点云', self)
        loadCloudAction.triggered.connect(self.loadPointCloud)
        fileMenu.addAction(loadCloudAction)

        exitAction = QAction('退出', self)
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        # 字体设置
        font = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)

        # 分割器来分开属性框架和点云视图
        main_splitter = QSplitter(QtCore.Qt.Vertical)

        # 上部框架包括属性和文件列表
        top_frame = QtWidgets.QFrame(main_splitter)
        top_layout = QVBoxLayout()

        # 属性区域
        properties_label = QLabel("属性")
        properties_label.setFont(font)
        properties_text_edit = QTextEdit()
        top_layout.addWidget(properties_label)
        top_layout.addWidget(properties_text_edit)

        # 文件区域
        files_label = QLabel("文件")
        files_label.setFont(font)
        files_text_edit = QTextEdit()
        top_layout.addWidget(files_label)
        top_layout.addWidget(files_text_edit)

        top_frame.setLayout(top_layout)

        # 点云显示区域（暂时是白色背景的QWidget）
        cloud_widget = QtWidgets.QWidget()
        cloud_widget.setStyleSheet("background-color: white;")

        # 主水平布局管理器
        horizontal_layout = QHBoxLayout(self.main_widget)

        # 中部分割器
        middle_splitter = QSplitter(QtCore.Qt.Horizontal)
        middle_splitter.addWidget(top_frame)
        middle_splitter.addWidget(cloud_widget)

        main_splitter.addWidget(middle_splitter)

        # 底部控制台区域
        console_label = QLabel("控制台")
        console_label.setFont(font)
        console_text_edit = QTextEdit()
        console_text_edit.setMinimumHeight(150)

        console_layout = QVBoxLayout()
        console_layout.addWidget(console_label)
        console_layout.addWidget(console_text_edit)

        console_frame = QFrame(main_splitter)
        console_frame.setLayout(console_layout)

        main_splitter.addWidget(console_frame)

        horizontal_layout.addWidget(main_splitter)

        self.setWindowTitle('点云数据处理软件')
        self.resize(1600, 1200)
        self.show()

    def loadPointCloud(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.path.expanduser("~"))[0]
        if fname:
            # 这里可以加载并处理点云数据
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
